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


def scrape_tuples(driver):
    tuples = []
    orig_contents = []
    download_links = driver.find_elements_by_class_name('downloadLink')
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
    for filename in glob.glob('/home/oded/Downloads/Deals*.*'):
        os.remove(filename)
    driver.get('https://online.leumi-card.co.il/Registred/Transactions/ChargesDeals.aspx')
    tuples, orig_contents = scrape_tuples(driver)
    date_select = driver.find_element_by_name('ctl00$PlaceHolderMain$CD$CardsFilter1$ctl02$ddlActionType')
    date_select.find_element_by_css_selector('option[value = "2"]').click()
    month_select = driver.find_element_by_name('ctl00$PlaceHolderMain$CD$CardsFilter1$ctl02$ddlMonthCharge')
    month_options = month_select.find_elements_by_tag_name('option')
    month_option_values = [x.get_attribute('value') for x in month_options]
    for option_value in month_option_values[0:history_depth]:
        driver.find_element_by_name('ctl00$PlaceHolderMain$CD$CardsFilter1$ddlCardsPresentor').find_elements_by_tag_name('option')[0].click()
        date_select = driver.find_element_by_name('ctl00$PlaceHolderMain$CD$CardsFilter1$ctl02$ddlActionType')
        date_select.find_element_by_css_selector('option[value = "2"]').click()
        month_select = driver.find_element_by_name('ctl00$PlaceHolderMain$CD$CardsFilter1$ctl02$ddlMonthCharge')
        option = month_select.find_element_by_css_selector('option[value = "{}"]'.format(option_value))
        option.click()
        driver.find_element_by_name('ctl00$PlaceHolderMain$CD$CardsFilter1$btnShow').click()
        month_tuples, month_orig_contents = scrape_tuples(driver)
        tuples = tuples + month_tuples
        orig_contents = orig_contents + month_orig_contents 
    return tuples, orig_contents


def xml_to_tuples(content):
    m = strip_ns(bf.data(ET.fromstring(content.replace('&', '&amp;'))))
    return [[c['Data'].get('$') for c in r['Cell']] for r in m['Workbook']['Worksheet']['Table']['Row']]

  
def convert_time(input_time):
    return datetime.strptime(input_time, '%Y-%m-%dT%H:%M:%S')


def process_tuples(card_number, tuples):
    return [(convert_time(t[0]),
             t[2],
             float(t[6]),
             'Leumi # {}'.format(card_number),
             convert_time(t[1]))
            for t in tuples[1:]]
