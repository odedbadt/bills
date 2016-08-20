import glob, os
import logging
import time
from bs4 import BeautifulSoup
from datetime import datetime
import re
from selenium.common.exceptions import NoSuchElementException

def login(driver, username, password):
    driver.get('https://services.cal-online.co.il/card-holders/Screens/AccountManagement/login.aspx')
    driver.find_element_by_name('ctl00$FormAreaNoBorder$FormArea$lgnLogin$UserName').send_keys(username)
    driver.find_element_by_name('ctl00$FormAreaNoBorder$FormArea$lgnLogin$Password').send_keys(password)
    driver.find_element_by_name('ctl00$FormAreaNoBorder$FormArea$lgnLogin$LoginImageButton').click()



def list_date_options(driver):
  lis = driver.find_elements_by_css_selector(
    '#ctl00_FormAreaNoBorder_FormArea_clndrDebitDateScope_OptionList li')
  texts = [li.get_attribute('innerHTML') for li in lis]
  return texts

def scrape_tuples(driver):
    tuples = []
    orig_contents = []
    card_items = driver.find_elements_by_class_name('categoryItem')
    card_number = 3271
    # for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
    #     print filename
    #     with open(filename) as f:
    #         content = f.read()
    #         orig_tuples = html_to_tuples(content)
    #         tuples = tuples + process_tuples(card_number, orig_tuples)            
    #         date_token = re.search(r'<span class="b">(\d{2}/\d{4})</span>', content.decode('UTF-16')).group(1)
    #         orig_contents.append(('Cal_{}_{}'.format(card_number, date_token), content.decode('UTF-16')))
    return tuples, orig_contents
    for i in range(len(card_items)):
        driver.find_element_by_name('ctl00$ContentTop$cboCardList$categoryList$lblCollapse').click()
        card_items = driver.find_elements_by_class_name('categoryItem')
        card_item = card_items[i]
        try:
            card_text = card_item.get_attribute('innerHTML')
            card_number = int(re.search(r'\d+$', card_text).group(0))
            card_item.click()    
            date_token = driver.find_element_by_name(
              'ctl00$FormAreaNoBorder$FormArea$clndrDebitDateScope$TextBox').get_attribute('value')
            logging.info('Downloading CAL for date {}'.format(date_token))
            driver.find_element_by_id('ctl00_FormAreaNoBorder_FormArea_ctlSubmitRequest').click()
            driver.find_element_by_id('ctl00_FormAreaNoBorder_FormArea_ctlMainToolBar_btnExcel').click()
            time.sleep(3)
            for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
                with open(filename) as f:
                    content = f.read()
                    orig_tuples = html_to_tuples(content)
                    tuples = tuples + process_tuples(datetime.strftime('%d/%m/%Y', '02/' + date_token), card_number, orig_tuples)            
                    orig_contents.append(('Cal_{}_{}'.format(card_number, date_token), content.decode('UTF-16')))
        except NoSuchElementException as e:
            pass
    return tuples, orig_contents

def download_transactions(driver, history_depth=0):
    for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
        os.remove(filename)
    driver.get('https://services.cal-online.co.il/Card-Holders/SCREENS/Transactions/Transactions.aspx')
    tuples, orig_contents = scrape_tuples(driver)
    if history_depth > 0:
        driver.find_element_by_name('ctl00$FormAreaNoBorder$FormArea$clndrDebitDateScope$TextBox').click()
        month_lis = driver.find_elements_by_css_selector('#ctl00_FormAreaNoBorder_FormArea_ctlDateScopeStart_ctlMonthYearList_OptionList li')
        for li in month_lis:
            li.click()
            driver.find_element_by_id('ctl00_FormAreaNoBorder_FormArea_ctlSubmitRequest').click()
            month_tuples, month_orig_contents = scrape_tuples(driver)
            orig_contents = orig_contents + month_orig_contents
            tuples = tuples + month_tuples
    return tuples, orig_contents

def html_to_tuples(content):
    soup = BeautifulSoup(content, 'html.parser')
    rows = soup.select('table tbody tr')
    return [tuple([td.get_text() for td in row.select('td')]) for row in rows]
  

def convert_time(input_time):
    return datetime.strptime(input_time, '%d/%m/%y')


def process_tuples(for_date, card_number, tuples):
    return [(convert_time(t[0]),
            t[1],
            float(t[4].replace(',', '')),
           'CAL # {}'.format(card_number),
           for_date) for t in tuples[:-1]]


def mock_cal():
    for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
        with open(filename) as f:
          return process_tuples(html_to_tuples(f.read()))
