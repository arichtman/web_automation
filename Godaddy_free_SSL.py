from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import glob
import os
import autoit
import zipfile
import yaml

with open(r'config.yml', 'r') as config_file:
  config_data = yaml.load(config_file, Loader=yaml.FullLoader)

def get_latest_downloads(filter):
  files_path = os.path.join(config_data['download_directory'], filter)
  files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
  return files

domains = "+".join(config_data['urls'])

free_ssl = webdriver.Chrome(config_data['chromedriver_path'])
free_ssl.set_window_position(0,0)
free_ssl.get("https://www.sslforfree.com/create?domains=" + domains)
time.sleep(10)

#select manual ftp
free_ssl.find_element_by_xpath('//*[@id="content_create_validation_methods"]/div[1]/a[2]').click()

#click manually verify
free_ssl.find_element_by_xpath('//*[@id="content_create_validation_methods"]/div[2]/div[2]/form/button').click()
time.sleep(5)

#download files
for x in range(1,len(config_data['urls'])+1):
  free_ssl.find_element_by_xpath('//*[@id="content_create_manual_output"]/ol/li[1]/ol/li[%d]/a' % x)
  elems[0].click()
  time.sleep(5)

#get paths of downloaded files
files = get_latest_downloads('*')

godaddy = webdriver.Chrome(config_data['chromedriver_path'])
godaddy.get(config_data['cpanel']['url']) #POPULATE
time.sleep(5)

#account for chrome cert warning
godaddy.find_element_by_xpath('//*[@id="details-button"]').click()
godaddy.find_element_by_xpath('//*[@id="proceed-link"]').click()
time.sleep(5)

godaddy.find_element_by_xpath('//*[@id="user"]').send_keys(config_data['cpanel']['username'])
godaddy.find_element_by_xpath('//*[@id="pass"]').send_keys(config_data['cpanel']['password'])
godaddy.find_element_by_xpath('//*[@id="login_submit"]').click()
time.sleep(20)
godaddy.find_element_by_xpath('//*[@id="item_file_manager"]').click()
time.sleep(5)

# move to file manager window
# TODO: move off deprecated - to driver.switchto().window
godaddy.switch_to_window(godaddy.window_handles[1])

#switch to public_html/.well-known/acme-challenge
godaddy.find_element_by_xpath('//*[@id="location"]').send_keys("/.well-known/acme-challenge")
godaddy.find_element_by_xpath('//*[@id="btnGo"]').click()
time.sleep(2)

#delete anything existing
godaddy.find_element_by_xpath('//*[@id="action-selectall"]').click()
godaddy.find_element_by_xpath('//*[@id="action-delete"]').click()
godaddy.find_element_by_xpath('//*[@id="trash"]/div[3]/span/button[1]').click()
time.sleep(2)

godaddy.find_element_by_xpath('//*[@id="action-upload"]/a').click()

#upload files
# TODO: deprecated method/member
godaddy.switch_to_window(godaddy.window_handles[2])
time.sleep(2)

godaddy.find_element_by_xpath('//*[@id="overwrite_checkbox"]').click()

for x in range(0,len(config_data['urls'])):
  godaddy.find_element_by_xpath('//*[@id="uploader_button"]').click()
  time.sleep(2)
  autoit.win_active("Open")
  autoit.control_send("Open","Edit1",files[x])
  autoit.control_send("Open","Edit1","{ENTER}")
  time.sleep(5)

godaddy.find_element_by_xpath('//*[@id="lnkReturn"]').click()
godaddy.switch_to_window(godaddy.window_handles[1])
godaddy.close()

#back to ssl for free to generate
free_ssl.find_element_by_xpath('//*[@id="content_create_manual_output"]/form/button').click()

time.sleep(30)
#now to download all those
free_ssl.find_element_by_xpath('//*[@id="certificate_download"]').click()
time.sleep(5)

#extract our download
files = get_latest_downloads('*.zip')

zip_ref = zipfile.ZipFile(files[0], 'r')
zip_ref.extractall(config_data['download_directory'])
zip_ref.close()

#back to cpanel to install the files
godaddy.switch_to_window(godaddy.window_handles[0])

godaddy.find_element_by_xpath('//*[@id="item_ssl_tls"]').click()
godaddy.find_element_by_xpath('//*[@id="lnkCRT"]').click()

# delete any existing
# TODO: improve that check
while len(godaddy.find_elements(By.XPATH, '(//*[@id="del-cert-0"])')) > 0:
  godaddy.find_element_by_xpath('(//*[@id="del-cert-0"])').click()
  time.sleep(2)
  godaddy.find_element_by_xpath('//*[@id="btnDelete"]').click()
  time.sleep(1)
  godaddy.find_element_by_xpath('//*[@id="lnkReturn"]').click()

files = get_latest_downloads('certificate.crt')
with open(files[0], 'r') as myfile:
    data=myfile.read()

godaddy.find_element_by_xpath( '//*[@id="crt"]').send_keys(data)
time.sleep(30)
godaddy.find_element_by_xpath('//*[@id="save-certificate"]').click()

godaddy.find_element_by_xpath('//*[@id="lnkReturn"]').click()

#manage/install ssl
# TODO: improve installation button xpath
godaddy.find_element_by_xpath('//*[@id="ssltable"]/tbody/tr/td[6]/a[3]').click()
godaddy.find_element_by_xpath('//*[@id="ssldomain"]').send_keys(Keys.DOWN)
godaddy.find_element_by_xpath('//*[@id="fetch-cert"]').click()
time.sleep(15)

files = get_latest_downloads('certificate.crt')
with open(files[0], 'r') as myfile:
    data=myfile.read()

godaddy.find_element_by_xpath('//*[@id="sslcrt"]').clear()
time.sleep(2)
godaddy.find_element_by_xpath('//*[@id="sslcrt"]').send_keys(data)
time.sleep(15)

#click populate from cert
godaddy.find_element_by_xpath('//*[@id="fetch-cert"]').click()
time.sleep(5)

files = get_latest_downloads('private.key')
with open(files[0], 'r') as myfile:
    data=myfile.read()

godaddy.find_element_by_xpath('//*[@id="sslkey"]').clear()
time.sleep(2)
godaddy.find_element_by_xpath('//*[@id="sslkey"]').send_keys(data)
time.sleep(15)

godaddy.find_element_by_xpath('//*[@id="btnInstall"]').click()
time.sleep(15)
godaddy.find_element_by_xpath('//*[starts-with(@id,"yui-gen")]/div[3]/span/button').click()

godaddy.close()
free_ssl.close()
free_ssl.close()