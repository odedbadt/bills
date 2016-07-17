import glob, os, xml
from time import sleep
from utils import strip_ns
from munch import munchify
from xmljson import badgerfish as bf
import xml.etree.ElementTree as ET
from datetime import datetime
import re


def login(driver, username, password):
    driver.get('https://online.leumi-card.co.il/Anonymous/Login/CardHoldersLogin.aspx')
    driver.find_element_by_name('ctl00$PlaceHolderMain$CardHoldersLogin1$txtUserName').send_keys(username)
    driver.find_element_by_name('ctl00$PlaceHolderMain$CardHoldersLogin1$txtPassword').send_keys(password)
    driver.find_element_by_name('ctl00$PlaceHolderMain$CardHoldersLogin1$btnLogin').click()


def download_transactions(driver):
    for filename in glob.glob('/home/oded/Downloads/Deals*.*'):
        os.remove(filename)
    driver.get('https://online.leumi-card.co.il/Registred/Transactions/ChargesDeals.aspx')    

    download_links = driver.find_elements_by_class_name('downloadLink')
    tuples = []
    orig_contents = {}
    for link in download_links:
        containing_div = link.find_element_by_xpath(
            "ancestor::div[contains(concat(' ', @class, ' '), 'creditCard_results')][1]")
        title_span = containing_div.find_element_by_css_selector('h2 span')
        date_indicator = containing_div.find_element_by_css_selector('.creditCard_results_dates2')
        span_content = title_span.get_attribute('innerHTML')
        date_content = date_indicator.get_attribute('innerHTML')
        card_number = re.search(r'\d+', span_content).group(0)
        link.click()
        sleep(2)
        with open('/home/oded/Downloads/Deals.xls') as f:
            content = f.read()
            orig_tuples = xml_to_tuples(content)
            tuples = tuples + process_tuples(card_number, orig_tuples)
            if len(orig_tuples) > 1:
                date_token = datetime.strftime(datetime.strptime(orig_tuples[1][1], '%Y-%m-%dT%H:%M:%S'), '%Y%m')
                orig_contents['leumi_{}_{}'.format(card_number, date_token)] = content.decode('utf-8')
        os.remove('/home/oded/Downloads/Deals.xls')
    return tuples, orig_contents


def xml_to_tuples(content):
    m = strip_ns(bf.data(ET.fromstring(content)))
    return [[c['Data'].get('$') for c in r['Cell']] for r in m['Workbook']['Worksheet']['Table']['Row']]
  
def convert_time(input_time):
    as_date = datetime.strptime(input_time, '%Y-%m-%dT%H:%M:%S')
    return datetime.strftime(as_date, '%m/%d/%Y')

def process_tuples(card_number, tuples):
    return [(convert_time(t[0]), t[2], t[6], 'Leumi # {}'.format(card_number)) for t in tuples[1:]]    
