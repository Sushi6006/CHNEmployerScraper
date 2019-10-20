# Scraper for BBE Training
# Code written by Terry
# July, 2019

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

N = 3              # times of scrolling down to the bottom so the page refreshes
TIME_TO_REFRESH = 5  # time to scroll down so the website doesnt ban me
TIME_TO_LOAD = 0     # time allowed to load each page in seconds

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
        self._newpage = None


class MainDriver:
    def __init__(self, source):
        self.driver = webdriver.Chrome()
        self.source = source
        self.driver.get(self.source.url)
        self.main_page = self.driver.current_window_handle
        self.job_items = None

    def load_content(self):
        start_time = time.time()
        for i in range(N):
            time.sleep(TIME_TO_REFRESH)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("scrolling...   {}/{}   time: {:.2f}s".format(i, N, time.time() - start_time))

    def switch_to_new_tab(self):
        self._new_page = self.driver.window_handles[-1]
        self.driver.switch_to_window(self._new_page)  # re-focus
        time.sleep(TIME_TO_LOAD)  # wait for the web to load

    def switch_back(self):
        self.driver.close()
        self.driver.switch_to_window(self.main_page)

    def get_main_page(self):
        return self.main_page

    def get_job_elements(self):
        self.job_items = self.driver.find_elements_by_xpath("//*[@class='{}']".format(self.source.class_name))
        for job_item in self.job_items:
            if "Melbourne" not in job_item.get_attribute('innerHTML'):
                self.job_items.remove(job_item)
        return self.job_items

    def get_content(self):
        return self.driver.page_source


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
        print("NO PHONE NUMBER")
        return False

    comp_name = soup.find('div', {"class": "info-table mobile-job-detail"}).find_all('div', {"class": "info-table-row"})[0].find('div', {"class": "info-table-data"}).text.strip()
    industry = soup.find('div', {"class": "info-table mobile-job-detail"}).find_all('div', {"class": "info-table-row"})[3].find('div', {"class": "info-table-data"}).text.strip()
    name = soup.find('div', {"class": "panel-body"}).find_all('div')[5].text.strip()

    if name == "1688澳洲用户":
        name = ""

    return Info(name, phone, industry, comp_name)


def main():
    # init content
    source = Source("https://www.1688living.com/job",
                    "itemDisplay mobile-item-cell cursor-pointer col-lg-6 col-md-8 col-sm-12 col-xs-24 ng-scope")
    driver = MainDriver(source)
    driver.load_content()
    job_items = driver.get_job_elements()

    # prepare to record
    recorded_phone_no = set()

    # TODO: UNCOMMENT THIS AFTER THE 1ST RUN
    f = open('db.csv', 'r')
    for line in f.readlines():
        print(line)
        recorded_phone_no.add(line.split(',')[1])

    # init recording process
    with open('db.csv', 'a') as f:
        total_recorded = 0
        total_checked = 0
        total = len(job_items)
        start_time = time.time()

        for job_item in job_items:
            total_checked += 1
            job_item.click()
            driver.switch_to_new_tab()

            # store info
            one_info = get_info(driver.get_content())
            if one_info and one_info.phone not in recorded_phone_no:
                recorded_phone_no.add(one_info.phone)
                total_recorded += 1
                f.write(f'{one_info.name},{one_info.phone},{one_info.industry},{one_info.company}\n')
            print("Writing: {}   Checked: {}/{}   Time: {:.2f}s".format(total_recorded, total_checked, total, time.time() - start_time))

            # close the tab
            driver.switch_back()

        print("Total {} pieces recorded".format(total_recorded))

if __name__ == '__main__':
    main()
