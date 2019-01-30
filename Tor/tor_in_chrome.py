# #Tor browser must be open before running this script

# import time
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# from selenium import webdriver
# from bs4 import BeautifulSoup
# import csv
# import sys

# username = "odrs"
# password = "odrs"

    
# binary = r"C:\Users\JMILLER.AD\Desktop\Tor Browser\Browser\firefox.exe"
# firefox_binary = FirefoxBinary(binary)
# driver = webdriver.Firefox(firefox_binary=binary)
# driver.get("http://waeixxcraed4gw7q.onion/signin")


from selenium import webdriver
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# binary = FirefoxBinary(r"C:\Users\JMILLER.AD\Desktop\Tor Browser\Browser\firefox.exe")
# driver = webdriver.Firefox(firefox_binary=binary)
#driver.get("http://2pjwzzms2yqlrkhp.onion/?ai=1675")

chrome_path = r"C:\Users\JMILLER\AppData\Local\Programs\Python\Python35-32\chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9150')
driver = webdriver.Chrome(chrome_path,chrome_options=chrome_options)
driver.get("http://google.com")