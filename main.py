#!/usr/bin/python
from selenium import webdriver
import drive
import unicodecsv
from io import BytesIO, StringIO
from datetime import datetime
import os
from functools import partial
from credentials_store import ServiceCLICrdentialsStore
import leumi, cal, poalim
import pickle
import logging

FINANCE_FOLDER_ID = '0B0wuHO2v2ASEUl83Zml2cmhwaWc'
TRANSACTIONS_FILE_ID = '1-ATYq7dEan0pRkBh3gxGFXw_2s4B8HlqY338UojhQYs'

LOG_FILENAME = '/home/oded/work/bills/accounting.log'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/home/oded/work/bills/accounting.log')
def main():
    logging.info('Starting to run')
    store = ServiceCLICrdentialsStore('bills')
    gdrive = store.get_credentials('gdrive')
    driver = webdriver.Chrome()
    poalim_cred = store.get_credentials('poalim')
    poalim.login(driver, poalim_cred.get_username(), poalim_cred.get_password())
    poalim_tuples = poalim.download_transactions(driver, 1)
    leumi_cred = store.get_credentials('leumi')
    leumi.login(driver, leumi_cred.get_username(), leumi_cred.get_password())
    leumi_tuples, leumi_origs = leumi.download_transactions(driver, 0)
    logging.info('Read leumi')
    cal_cred = store.get_credentials('cal')
    cal.login(driver, cal_cred.get_username(), cal_cred.get_password())    
    cal_tuples, cal_origs = cal.download_transactions(driver, 0)
    logging.info('Read CAL')
    with open('backup.pickle', 'w') as f:
      pickle.dump({
          'leumi_tuples': leumi_tuples,
          'leumi_origs': leumi_origs,
          'cal_tuples': cal_tuples,
          'cal_origs': cal_origs,
        }, f)
    driver.close()

    drive_service = drive.get_drive_service(gdrive.get_username(),
                                            gdrive.get_password())
    history = drive.get_csv_file(drive_service, TRANSACTIONS_FILE_ID)
    input_csv_io = BytesIO(history)
    csv_reader = unicodecsv.reader(input_csv_io, encoding='utf-8')
    historic_tuples = list(map(read_gdrive_tuple, csv_reader))
    unique_updated_tuples = list(set(map(tuple, historic_tuples +
                                                leumi_tuples +
                                                cal_tuples + 
                                                poalim_tuples)))
    sorted_updated_tuples = map(write_gdrive_tuple, sorted(unique_updated_tuples, key=lambda tpl: tpl[0]))

    csv_io = BytesIO()
    writer = unicodecsv.writer(csv_io)
    writer.writerows(sorted_updated_tuples)
    drive.update_csv_stream(drive_service, TRANSACTIONS_FILE_ID, csv_io)
    logging.info('Updated Google Drive')
    for k, content in leumi_origs + cal_origs:
        name = k + '.txt'
        file_id = drive.find_file_id_by_name(drive_service, name)
        if file_id:
            logging.info('Updating file of name {} and id {}'.format(name, file_id))
            drive.update_raw_file(drive_service, file_id, content)
        else:
            file_id = drive.create_raw_file(drive_service, name, content, parents=[FINANCE_FOLDER_ID])['id']
            logging.info('Created file of name {} and id {}'.format(name, file_id))

def read_gdrive_tuple(tpl):
    return (datetime.strptime(tpl[0], '%m/%d/%Y'), tpl[1], float(tpl[2].replace(',', '')), tpl[3])

def write_gdrive_tuple(tpl):
    return (datetime.strftime(tpl[0], '%m/%d/%Y'),
            tpl[1],
            tpl[2],
            tpl[3],
            datetime.strftime(tpl[4], '%m/%d/%Y') if len(tpl) > 4 and tpl[4] else None,
            tpl[5]  if len(tpl) > 5 else None)

if __name__ == '__main__':
    main()
