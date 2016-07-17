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


def convert_time(input_time):
    as_date = datetime.strptime(input_time, '%d/%m/%y')
    return datetime.strftime(as_date, '%m/%d/%Y')

def list_date_options(driver):
  lis = driver.find_elements_by_css_selector(
    '#ctl00_FormAreaNoBorder_FormArea_clndrDebitDateScope_OptionList li')
  texts = [li.get_attribute('innerHTML') for li in lis]
  return texts


def download_transactions(driver):
    for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
        os.remove(filename)
    driver.get('https://services.cal-online.co.il/Card-Holders/SCREENS/Transactions/Transactions.aspx')
    card_items = driver.find_elements_by_class_name('categoryItem')
    driver.find_element_by_name('ctl00$ContentTop$cboCardList$categoryList$lblCollapse').click()
    tuples = []
    orig_contents = {}
    for card_item in card_items:
        try:
            card_text = card_item.get_attribute('innerHTML')
            card_number = int(re.search(r'\d+$', card_text).group(0))
            card_item.click()    
            date_token = driver.find_element_by_name(
              'ctl00$FormAreaNoBorder$FormArea$clndrDebitDateScope$TextBox').get_attribute('value')
            logging.info('Downloading CAL for date {}'.format(date_token))
            driver.find_element_by_id('ctl00_FormAreaNoBorder_FormArea_ctlSubmitRequest').click()
            driver.find_element_by_id('ctl00_FormAreaNoBorder_FormArea_ctlMainToolBar_btnExcel').click()
            time.sleep(2)
            for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
                tuples = tuples + process_tuples(card_number, orig_tuples)            
                with open(filename) as f:
                    content = f.read()
                    print type(content)
                    orig_tuples = html_to_tuples(content)
                    tuples = tuples + process_tuples(orig_tuples, card_number)
                    orig_contents['cal_{}_{}'.format(card_number, date_token)] = content.decode('utf-8')
        except NoSuchElementException as e:
            pass
        return tuples, orig_contents

def html_to_tuples(content):
    soup = BeautifulSoup(content, 'html.parser')
    rows = soup.select('table tbody tr')
    return [tuple([td.get_text() for td in row.select('td')]) for row in rows]
  

def process_tuples(card_number, tuples):
    formatted = [(convert_time(t[0]), t[1], t[4], 'CAL # {}'.format(card_number)) for t in tuples[:-1]]
    return formatted, tuples


def mock_cal():
    for filename in glob.glob('/home/oded/Downloads/Transactions*.*'):
        with open(filename) as f:
          return process_tuples(html_to_tuples(f.read()))
