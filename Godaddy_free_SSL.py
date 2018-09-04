from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import glob
import os

download_directory = "" #POPULATE

def get_latest_downloads(filter):
  files_path = os.path.join(download_directory, filter)
  files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
  return files

urls = ["foo.com", "bar.com"] #POPULATE
domains = "+".join(urls)
  
free_ssl = webdriver.Chrome()
free_ssl.set_window_position(0,0)
free_ssl.get("https://www.sslforfree.com/create?domains=" + domains)
time.sleep(10)
#select manual ftp
elems = free_ssl.find_elements(By.XPATH,'//*[@id="content_create_validation_methods"]/div[1]/a[2]')
elems[0].click()
#click manually verify
elems = free_ssl.find_elements(By.XPATH,'//*[@id="content_create_validation_methods"]/div[2]/div[2]/form/button')
elems[0].click()

#download files
for x in range(1,len(urls)+1):
  elems = free_ssl.find_elements(By.XPATH,'//*[@id="content_create_manual_output"]/ol/li[1]/ol/li[%d]/a' % x)
  elems[0].click()
  time.sleep(5)

#get paths of downloaded files
files = get_latest_downloads('*')

godaddy = webdriver.Chrome()
godaddy.get("http://yoursite.com/cpanel") #POPULATE
time.sleep(5)
elems = godaddy.find_elements(By.XPATH,'//*[@id="user"]')
elems[0].send_keys("") #POPULATE
elems = godaddy.find_elements(By.XPATH,'//*[@id="pass"]')
elems[0].send_keys("") #POPULATE
elems = godaddy.find_elements(By.XPATH,'//*[@id="login_submit"]')
elems[0].click()
time.sleep(20)
elems = godaddy.find_elements(By.XPATH,'//*[@id="item_file_manager"]')
elems[0].click()
time.sleep(2)
#may remember last value - check if unchecked?
elems = godaddy.find_elements(By.XPATH,'//*[@id="optionselect_showhidden"]')
elems[0].click()
elems = godaddy.find_elements(By.XPATH,'//*[@id="dirselect_webroot"]')
elems[0].click()
elems = godaddy.find_elements(By.XPATH,'//*[@id="optionselect_go"]')
elems[0].click()
time.sleep(5)
#move to file manager window
godaddy.switch_to_window(godaddy.window_handles[1])

elems = godaddy.find_elements(By.XPATH,'//*[@id="location"]')
elems[0].send_keys("/.well-known/acme-challenge")
elems = godaddy.find_elements(By.XPATH,'//*[@id="btnGo"]')
elems[0].click()
time.sleep(2)
elems = godaddy.find_elements(By.XPATH,'//*[@id="action-upload"]/a')
elems[0].click()

#upload files
godaddy.switch_to_window(godaddy.window_handles[2])
import autoit

for x in range(0,len(urls)):
  elems = godaddy.find_elements(By.XPATH,'//*[@id="file%d"]' % x)
  elems[0].click()
  time.sleep(2)
  autoit.win_active("Open")
  autoit.control_send("Open","Edit1",files[x])
  autoit.control_send("Open","Edit1","{ENTER}")
  time.sleep(5)


elems = godaddy.find_elements(By.XPATH,'//*[@id="backTo"]')
elems[0].click()
godaddy.switch_to_window(godaddy.window_handles[1])
godaddy.close()

#back to ssl for free to generate
elems = free_ssl.find_elements(By.XPATH,'//*[@id="content_create_manual_output"]/form/button')
elems[0].click()
time.sleep(30)
#now to download all those
elems = free_ssl.find_elements(By.XPATH,'//*[@id="certificate_download"]')
elems[0].click()
time.sleep(5)

#extract our download
files = get_latest_downloads('*.zip')
import zipfile
zip_ref = zipfile.ZipFile(files[0], 'r')
zip_ref.extractall(download_directory)
zip_ref.close()

#back to cpanel to install the files
godaddy.switch_to_window(godaddy.window_handles[0])

elems = godaddy.find_elements(By.XPATH,'//*[@id="item_ssl_tls"]')
elems[0].click()
elems = godaddy.find_elements(By.XPATH,'//*[@id="lnkCRT"]')
elems[0].click()

files = get_latest_downloads('certificate.crt')
with open(files[0], 'r') as myfile:
    data=myfile.read()

elems = godaddy.find_elements(By.XPATH, '//*[@id="crt"]')
elems[0].send_keys(data)
time.sleep(30)
elems = godaddy.find_elements(By.XPATH,'//*[@id="save-certificate"]')
elems[0].click()

elems = godaddy.find_elements(By.XPATH,'//*[@id="lnkReturn"]')
elems[0].click()
elems = godaddy.find_elements(By.XPATH,'//*[@id="lnkReturn"]')
elems[0].click()
#manage/install ssl
elems = godaddy.find_elements(By.XPATH,'//*[@id="lnkInstall"]')
elems[0].click()
elems = godaddy.find_elements(By.XPATH,'//*[@id="ssldomain"]')
elems[0].send_keys(Keys.DOWN)
elems = godaddy.find_elements(By.XPATH,'//*[@id="fetch-domain"]')
elems[0].click()
time.sleep(15)

files = get_latest_downloads('certificate.crt')
with open(files[0], 'r') as myfile:
    data=myfile.read()


elems = godaddy.find_elements(By.XPATH,'//*[@id="sslcrt"]')
elems[0].clear()
time.sleep(2)
elems[0].send_keys(data)
time.sleep(15)

elems = godaddy.find_elements(By.XPATH,'//*[@id="fetch-cert"]')
elems[0].click() #click populate from cert
time.sleep(5)

files = get_latest_downloads('private.key')
with open(files[0], 'r') as myfile:
    data=myfile.read()


elems = godaddy.find_elements(By.XPATH,'//*[@id="sslkey"]')
elems[0].clear()
time.sleep(2)
elems[0].send_keys(data)
time.sleep(15)

elems = godaddy.find_elements(By.XPATH,'//*[@id="btnInstall"]')
elems[0].click()
time.sleep(15)
elems = godaddy.find_elements(By.XPATH,'//*[starts-with(@id,"yui-gen")]/div[3]/span/button')
elems[0].click()

godaddy.close()
free_ssl.close()
