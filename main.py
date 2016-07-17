#!/usr/bin/python
from selenium import webdriver
from cal import process_cal
from leumi import process_leumi
import drive
import unicodecsv
from io import BytesIO, StringIO
from datetime import datetime
import json, os
from functools import partial
from credentials_store import ServiceCLICrdentialsStore
import leumi, cal
def parse_date_from_tuple(tpl):
    return datetime.strptime(tpl[0], '%m/%d/%Y')


FINANCE_FOLDER_ID = '0B0wuHO2v2ASEUl83Zml2cmhwaWc'
TRANSACTIONS_FILE_ID = '1-ATYq7dEan0pRkBh3gxGFXw_2s4B8HlqY338UojhQYs'
def main():
    store = ServiceCLICrdentialsStore('bills')
    leumi = store.get_credentials('leumi')
    cal = store.get_credentials('cal')
    gdrive = store.get_credentials('gdrive')
    driver = webdriver.Chrome()
    leumi.login(driver, leumi.get_username(), leumi.get_password())
    leumi_tuples, leumi_origs = leumi.download_trnasactions(driver)
    #   #'ti7lKbezX')
    
    cal.login(driver, cal.get_username(), cal.get_password())
    cal_tuples, cal_origs = cal.download_transactions(driver)
    # cal_tuples = [] 
    drive_service = drive.get_drive_service(
      gdrive.get_username(),
      gdrive.get_password())
      # '39331867715-sgrmts10v5a1n5ttqf6q4qknthb05vn2.apps.googleusercontent.com',
      # 'AIiGeNeuAsmm29zxYe19q2ou')
    history = drive.get_csv_file(drive_service, TRANSACTIONS_FILE_ID)
    input_csv_io = BytesIO(history)
    csv_reader = unicodecsv.reader(input_csv_io, encoding='utf-8')
    historic_tuples = list(csv_reader)
    unique_updated_tuples = list(set(map(tuple, map(partial(map, unicode), historic_tuples + leumi_tuples + cal_tuples))))
    sorted_updated_tuples = sorted(unique_updated_tuples, key=parse_date_from_tuple)
    csv_io = BytesIO()
    writer = unicodecsv.writer(csv_io)
    writer.writerows(sorted_updated_tuples)
    drive.update_csv_stream(drive_service, TRANSACTIONS_FILE_ID, csv_io)
    for k, content in list(leumi_origs.iteritems()) + list(cal_origs.iteritems()):
        name = k + '.txt'
        file_id = drive.find_file_id_by_name(drive_service, name)
        if file_id:
            print file_id
            drive.update_raw_file(drive_service, file_id, content)
        else:
            drive.create_raw_file(drive_service, name, content, parents=[FINANCE_FOLDER_ID])


if __name__ == '__main__':
  main()