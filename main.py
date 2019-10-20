# Scraper for BBE Training
# Code written by Terry
# July, 2019
# Updated in October, 2019

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

# a valid source
class Source:
    def __init__(self, url, class_name):
        self.url = url
        self.class_name = class_name


# piece of acceptable information
class Info:
    def __init__(self, name, phone, industry, company):
        self.name = name
        phone = phone.replace(" ", "")
        self.phone = phone[0:4] + ' ' + phone[4:7] + ' ' + phone[7:]
        self.industry = industry
        self.company = company


# get information from a given webpage
def get_info(html):
    soup = BeautifulSoup(html, 'lxml')

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

    return Info(name, phone, industry, comp_name)

# some constants
N = 150              # times of scrolling down to the bottom so the page refreshes
TIME_TO_REFRESH = 5  # time to scroll down so the website doesnt ban me
TIME_TO_LOAD = 1     # time allowed to load each page in seconds

# source: 1688living.com/job
# job item class: itemDisplay mobile-item-cell cursor-pointer col-lg-6 col-md-8 col-sm-12 col-xs-24 ng-scope
source = Source("https://www.1688mel.com/job",
                "itemDisplay mobile-item-cell cursor-pointer col-lg-6 col-md-8 col-sm-12 col-xs-24 ng-scope")

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


# init
f = open('db.csv', 'w')
total_recorded = 0
total_checked = 0
total = len(job_items)
start_time = time.time()

for job_item in job_items:
    card_content = job_item.get_attribute('innerHTML')
    total_checked += 1
    city = ""
    if ("2000" in card_content):
        city = "Sydney"
    elif ("3000" in card_content):
        city = "Melbourne"
    else:
        continue
    # job_item.send_keys(Keys.COMMAND + Keys.RETURN)  # open up new tab with the job
    job_item.click()

    # switch to new tab
    new_page = driver.window_handles[-1]
    driver.switch_to_window(new_page)  # re-focus
    time.sleep(TIME_TO_LOAD)  # wait for the web to load

    # store info
    one_info = get_info(driver.page_source)
    total_recorded += 1
    f.write(f'{one_info.name},{one_info.phone},{one_info.industry},{one_info.company},{city}\n')
    print("Writing: {}   Checked: {}/{}   Time: {:.2f}s".format(total_recorded, total_checked, total, time.time() - start_time))

    # close the tab
    driver.close()
    driver.switch_to_window(main_page)

print("Total {} / {} pieces recorded".format(total_recorded, total))

f.close()
