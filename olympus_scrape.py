#Tor browser must be open before running this script

import time
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import sys

username = "odrs"
password = "odrs"

    
def find_link(link_title):
    try:
        link = driver.find_element_by_xpath('//*[@rel="{}"]'.format(link_title))
    except:
        link = ""
    return link

def click_and_wait(link):
    start_page = driver.page_source
    link.click()
    while True:
        new_page = driver.page_source
        if start_page == new_page:
            print("waiting for new page")
            time.sleep(2)
        else:
            time.sleep(2)
            break
    
binary = r"C:\Users\mmjac\OneDrive\Desktop\Tor browser\browser\firefox.exe"
firefox_binary = FirefoxBinary(binary)
driver = webdriver.Firefox(firefox_binary=binary)
driver.get("http://waeixxcraed4gw7q.onion/signin")


first_loop = True
while True:
    captcha = input("enter captcha:\n")
    
    driver.find_elements_by_xpath("//input[contains(@id, 'username')]").send_keys(username)
    driver.find_elements_by_xpath("//input[contains(@id, 'password')]").send_keys(password)
    driver.find_elements_by_xpath("//input[contains(@id, 'captcha')]").send_keys(captcha)
    click_and_wait(driver.find_elements_by_xpath("//button[contains(@class, 'btn btn-primary btn-block btn-lg')]"))
    
    try:
        driver.find_element_by_xpath("//div[contains(@class, 'alert alert-danger')]") #look for captcha fail message
        first_loop = False
        pass #captcha failed and error was found; restart loop
    except:
        break #captcha did not fail. Quit loop
    
click_and_wait(driver.find_element_by_xpath("//a[@href='http://waeixxcraed4gw7q.onion/listings/drugs']"))
#click_and_wait(driver.find_element_by_xpath("//a[@href='http://waeixxcraed4gw7q.onion/listings/drugs-rcs']"))

scraped_drug_info = []
page_num = 1
while True:
    for drug_info_box in driver.find_elements_by_xpath("//div[contains(@class, 'col-md-4')]"):
        Title = drug_info_box.find_element_by_xpath(".//span[contains(@class, 'bold')]").text
        Vendor = drug_info_box.find_element_by_xpath("//dl[@class='dl-horizontal olympus-product-dictionary m-t-15']/dt[. = 'Sold by:']/following-sibling::dd").text
        Ships = drug_info_box.find_element_by_xpath("//dl[@class='dl-horizontal olympus-product-dictionary m-t-15']/dt[. = 'Shipping:']/following-sibling::dd").text
        Category = drug_info_box.find_element_by_xpath("//dl[@class='dl-horizontal olympus-product-dictionary m-t-15']/dt[. = 'Category:']/following-sibling::dd").text
        Price = drug_info_box.find_element_by_xpath(".//a[contains(@class, 'btn btn-primary btn-block m-b-2')]").text
        print("Title:{}, Price:{}, Vendor:{}, Ships:{}, page_num:{}".format(Title,Price,Vendor,Ships,page_num))
        scraped_drug_info.append({'Title':Title,'Price':Price,'Vendor':Vendor,'Ships':Ships,'Category':Category,'page_num':page_num})

    next_page_link = find_link("next")
    if next_page_link != "":
        click_and_wait(next_page_link)
        page_num = page_num + 1
    else:
        break

keys = scraped_drug_info[0].keys()
with open("Olympus_scrape.csv", 'w', encoding='utf-8') as csvfile:
    dict_writer = csv.DictWriter(csvfile,keys,lineterminator = '\n')
    dict_writer.writeheader()
    dict_writer.writerows(scraped_drug_info)