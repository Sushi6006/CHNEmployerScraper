# Scraper for BBE Training
# Code written by Terry
# July, 2019


# TODO: 演绎/公关/模特
# TODO: 群发
# TODO: 点击率, 分类, Distribution

# import libraries / functions for scraping
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

# lib to store the info
import csv

# import other stuff
import time
import re

N = 100              # times of scrolling down to the bottom so the page refreshes
TIME_TO_REFRESH = 5  # time to scroll down so the website doesnt ban me
TIME_TO_LOAD = 2     # time allowed to load each page in seconds

# a valid source
class Source:
    def __init__(self, url, class_name):
        self.url = url
        self.class_name = class_name


# piece of acceptable information
class Info:
    def __init__(self, name, phone, industry, company):
        self.name = name
        self.phone = phone[0:4] + ' ' + phone[4:7] + ' ' + phone[7:]
        self.industry = industry
        self.company = company


# source: 1688living.com/job
# job item class: itemDisplay mobile-item-cell cursor-pointer col-lg-6 col-md-8 col-sm-12 col-xs-24 ng-scope
source = Source("https://www.1688mel.com/job",
                "list-group mobile-job-padding mobile-list-group pc-title-height")

# get information from a given webpage
def get_info(html):
    soup = BeautifulSoup(html, 'lxml')

    # return False if it's not in melb
    if 'Melbourne' not in html:
        return False

    phone_divs = soup.select('div:contains("04")')
    if phone_divs:
        phone = phone_divs[-1].text.strip()
    else:
        return False

    comp_name = soup.find('div', {"class": "info-table mobile-job-detail"}).find_all('div', {"class": "info-table-row"})[0].find('div', {"class": "info-table-data"}).text.strip()
    industry = soup.find('div', {"class": "info-table mobile-job-detail"}).find_all('div', {"class": "info-table-row"})[3].find('div', {"class": "info-table-data"}).text.strip()
    name = soup.find('div', {"class": "panel-body"}).find_all('div')[5].text.strip()

    if name == "1688澳洲用户":
        name = ""

    """
    industry_dict = {"厨师/帮厨/服务员": "Restaurant", "IT/通讯/编程": "IT", "家政/清洁/保姆": "Housekeeping",
                     "物流/司机/仓管": "Logistics", "客服/店员/收银": "Services", "零售/销售/推销": "Sales",
                     "投资/房产/业务": "Investments", "建筑/装修/工程": "Constructions", "操作/技术/维修": "Technicians",
                     "导游/旅游/酒店": "Traveling", "财务/金融/人力资源": "Finance": }
    if industry = "厨师/帮厨/服务员":
        industry = "Restaurant"
    elif
    """

    return Info(name, phone, industry, comp_name)


#########################################
## prepare the driver and the web page ##
#########################################
driver = webdriver.Chrome()
driver.get(source.url)
main_page = driver.current_window_handle


#######################
## load web contents ##
#######################
for i in range(N):
    time.sleep(TIME_TO_REFRESH)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# job_items = driver.find_elements_by_class_name("itemDisplay mobile-item-cell")
job_items = driver.find_elements_by_xpath("//*[@class='{}']".format(source.class_name))

recorded_phone_no = set()

# TODO: UNCOMMENT THIS AFTER THE FIRST TIME
"""
f = open('db.csv', 'r')
for line in f.readlines():
    recorded_phone_no.add(line.split(',')[1])
print(recorded_phone_no)
"""

# init
f = open('db.csv', 'w')
total_recorded = 0
total_checked = 0
total = len(job_items)
start_time = time.time()

for job_item in job_items:
    total_checked += 1
    # job_item.send_keys(Keys.COMMAND + Keys.RETURN)  # open up new tab with the job
    job_item.click()
    # driver.find_element_by_tag_name("body").send_keys(Keys.COMMAND + '2')

    # switch to new tab
    # actions = ActionChains(driver)
    # actions.key_down(Keys.CONTROL).key_down(Keys.TAB).key_up(Keys.TAB).key_up(Keys.CONTROL).perform()
    new_page = driver.window_handles[-1]
    driver.switch_to_window(new_page)  # re-focus
    time.sleep(TIME_TO_LOAD)  # wait for the web to load

    # store info
    # w = csv.writer(f)
    one_info = get_info(driver.page_source)
    if one_info and one_info.phone not in recorded_phone_no:
        recorded_phone_no.add(one_info.phone)
        total_recorded += 1
        f.write(f'{one_info.name},{one_info.phone},{one_info.industry},{one_info.company}\n')
    print("Writing: {}   Checked: {}/{}   Time: {:.2f}s".format(total_recorded, total_checked, total, time.time() - start_time))

    # close the tab
    driver.close()
    driver.switch_to_window(main_page)
    # actions = ActionChains(driver)
    # actions.key_down(Keys.COMMAND).key_down('w').key_up(Keys.COMMAND).key_up('w').perform()

print("Total {} / {} pieces recorded".format(total_recorded, total))

f.close()
