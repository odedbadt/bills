import glob, os, xml
from time import sleep
from utils import strip_ns
from munch import munchify
from xmljson import badgerfish as bf
import xml.etree.ElementTree as ET
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


def login(driver, username, password):
    driver.get('https://login.bankhapoalim.co.il/cgi-bin/poalwwwc?reqName=getLogonPage')
    driver.find_element_by_css_selector('#userIdContent input').send_keys(username)
    driver.find_element_by_id('userPassword').click()
    driver.find_element_by_id('userPassword').send_keys(password)
    driver.find_element_by_css_selector('.SignBtn input').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".menu-icon-profile")))    
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, "userPassword")))


def scrape_tuples(driver):
    tuples = []
    orig_contents = []
    download_links = driver.find_elements_by_class_name('downloadLink')
    driver.find_element_by_css_selector('.button.dropdown-toggle1.dropdown-toggle').click()

    for link in download_links:
        containing_div = link.find_element_by_xpath(
            "ancestor::div[contains(concat(' ', @class, ' '), 'creditCard_results')][1]")
        title_span = containing_div.find_element_by_css_selector('h2 span')
        date_indicator = containing_div.find_element_by_css_selector('.creditCard_results_dates2')
        span_content = title_span.get_attribute('innerHTML')
        date_content = date_indicator.get_attribute('innerHTML')
        card_number = re.search(r'\d+', span_content).group(0)
        link.click()
        sleep(3)
        with open('/home/oded/Downloads/Deals.xls') as f:
            content = f.read()
            orig_tuples = xml_to_tuples(content)
            tuples = tuples + process_tuples(card_number, orig_tuples)
            if len(orig_tuples) > 1:
                date_token = datetime.strftime(datetime.strptime(orig_tuples[1][1], '%Y-%m-%dT%H:%M:%S'), '%Y%m')
                orig_contents.append(('Leumi_{}_{}'.format(card_number, date_token), content.decode('utf-8')))
        os.remove('/home/oded/Downloads/Deals.xls')
    return tuples, orig_contents

def download_transactions(driver, history_depth=0):
    driver.get('https://login.bankhapoalim.co.il/portalserver/currentaccount')
    if history_depth > 0:
        periodFilter = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".periodFilter button")))
        periodFilter.click()
        lis = driver.find_elements_by_css_selector('.periodFilter li')
        lis[-2].click()
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
    rows = table.find_elements_by_css_selector('tbody tr.collapse-toggle')
    return [process_row(row) for row in rows]


def rows_to_cells(rows):
    return [row.find_element_by_name('td') for row in rows]

  
def convert_time(input_time):
    return datetime.strptime(input_time, '%d.%m.%y')

def get_span_text(cell):
    spans = cell.find_elements_by_tag_name('span')
    if len(spans) == 0:
        return None 
    return spans[0].text

def get_span_number(cell):
    as_str = get_span_text(cell)
    if as_str is None or as_str == '':
        return 0
    return float(as_str.replace(',', ''))

def process_row(row):
    import re
    cells = row.find_elements_by_tag_name('td')
    date_portion = re.search('([0-9.]+)', get_span_text(cells[0])).group(0)
    n = get_span_number(cells[3])
    p = get_span_number(cells[4])
    t = get_span_number(cells[5])
    return (convert_time(date_portion),
            cells[2].text,
            n - p,
            'Poalim',
            None,
            t)
             
