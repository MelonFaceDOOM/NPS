'''
log in 
open scrape_progress
begin looping through to_scrape list
with each loop:
    scrape data
    save data
    update "to_scrape" and "scraped"
    save into scrape_progress
    
todo:
fix the pickle file so URLs are actually visited in the correct order
change mirrors if current one fails to load after x retries
text self with captcha image to allow beating captcha while away from pc
add routine for getting pass ddos check
'''

#Tor browser must be open before running this script
#may need to run "chcp 65001" in cmd before running this python file to allow certain characters to be printed

import time
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import csv
import sys
import pickle
import re

def main():

    out_file = "dm_scrape.csv"

    username = "odrs"
    password = "odrs"

    chrome_path = r"C:\Users\JMILLER\AppData\Local\Programs\Python\Python35-32\chromedriver.exe"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9150')
    chrome_options.add_experimental_option('useAutomationExtension',False)
    driver = webdriver.Chrome(chrome_path,chrome_options=chrome_options)
    
    dm_mirror = "http://bkjcpa2klkkmowwq.onion/"

    '''
    jd6yhuwcivehvdt4.onion
    t3e6ly3uoif4zcw2.onion
    7ep7acrkunzdcw3l.onion
    vilpaqbrnvizecjo.onion
    igyifrhnvxq33sy5.onion
    6qlocfg6zq2kyacl.onion
    x3x2dwb7jasax6tq.onion
    bkjcpa2klkkmowwq.onion
    xytjqcfendzeby22.onion
    nhib6cwhfsoyiugv.onion
    k3pd243s57fttnpa.onion
    '''
    
    driver.get(dm_mirror)

    first_loop = True
    while True:
        captcha = input("enter captcha:\n")
        html_source = driver.page_source
        
        if first_loop == True:
            username_name, password_name, captcha_name = get_dream_form_names(html_source)
        else:
            username_name, password_name, captcha_name = get_dream_form_names(html_source,username_in_field="odrs")
        
        driver.find_element_by_name(username_name).clear() # username field will still have previous entry if captcha failed
        driver.find_element_by_name(username_name).send_keys(username)
        driver.find_element_by_name(password_name).send_keys(password)
        driver.find_element_by_name(captcha_name).send_keys(captcha)
        driver.find_element_by_xpath("//input[@value='Login']").click()
        
        try:
            driver.find_element_by_xpath("//div[contains(@class, 'error') and text()='Captcha was incorrectly entered']") #look for captcha fail message
            first_loop = False
            pass #captcha failed and error was found; restart loop
        except:
            break #captcha did not fail. Quit loop
    
    with open("scrape_progress", "rb") as sp:
        to_scrape = pickle.load(sp)
        try:
            scraped = pickle.load(sp)
        except:
            scraped = []
    
    #drug category URLs have follow the format of "/?category=119"
    #pages follow the format: "//?page=77&category=126"
    counter = 0
    scraped_drug_info = []
    scraped_urls = []
    
    urls_to_visit = to_scrape #to_scrape will be modified with each loop, so a 2nd list is created to loop through
    
    for url_ext in urls_to_visit:
        counter = counter + 1 #count how many loops have passed through
        
        retry_counter = 0
        while True: 
            #quit after 5 attempts to load page
            if retry_counter >= 5:
                print("Page not loading -- reached max 5 retries")
                sys.exit()
            
            driver.get("{domain}{url_ext}".format(domain=dm_mirror,url_ext=url_ext))
            try:
                driver.find_element_by_xpath("//div[@class = 'headNavitems']") #test to see if page loaded properly
                break
            except:
                retry_counter = retry_counter + 1
                time.sleep(5)
        
        #skip to next page if no drugs are present on this one
        if drug_info_boxes_present(driver):
            pass #run through rest of for loop
        else:
            continue
        
        #drug_cat1 will only be 'selected' if there is no subcategory.
        try:
            drug_cat1 = driver.find_element_by_xpath("//div[@class = 'category  selected  depth1']/a").text
            drug_cat2 = "N/A"
        except:
            drug_cat1 = driver.find_element_by_xpath("//div[@class = 'category  depth1']/a").text
            drug_cat2 = driver.find_element_by_xpath("//div[@class = 'category  selected  depth2']/a").text
            
        #get cat# and page# for record-keeping purposes
        cat,page = get_cat_and_page(url_ext)
        
        ###scrape drug info on this page###
        for drug_info_box in driver.find_elements_by_css_selector("div[class^='shopItem']"):
            Title = drug_info_box.find_element_by_css_selector("a[class^='productThumbImage_']").text
            Price = drug_info_box.find_element_by_css_selector("div[class='bottom oPrice']").text
            Vendor = drug_info_box.find_element_by_css_selector("div[class='oVendor']").text
            Ships = drug_info_box.find_element_by_css_selector("span[class='osBod']").text

            scraped_drug_info.append([Title,Price,Vendor,Ships,drug_cat1,drug_cat2,cat,page]) # if these are changed, update header list in create_file()
            scraped_urls.append(url_ext)
            
        #save only ever 5 loops
        if counter >= 5:
            ###write to csv###
            create_file(out_file)
            with open(out_file, 'a', encoding='utf-8', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                for row in scraped_drug_info:
                    csv_writer.writerow(row)
                
            ###move url from to_scrape to scraped###
            to_scrape = [x for x in to_scrape if x not in scraped_urls]
            scraped = [x for x in scraped if x not in scraped_urls]
            #[to_scrape.remove(u) for u in scraped_urls]
            #[scraped.append(u) for u in scraped_urls]
            
            with open("scrape_progress", "wb") as sp:
                pickle.dump(to_scrape,sp)
                pickle.dump(scraped,sp)
            
            counter = 0
            scraped_drug_info = []
            scraped_urls = []

def get_dream_form_names(url,username_in_field=""):
    #username_in_field is "" by default. If captcha fails, the site will empty all fields but leave the username field as it was previously filled.
    soup = BeautifulSoup(url, "lxml")
    login = soup.find('div',{'class':'formInputs'})
    login = login.findAll('input')
    for l in login:
        try:
            if l['value'] == username_in_field:
                if l['type'] == "text":
                    username_name = l['name']
            if l['value'] == "":
                if l['type'] == "password":
                    password_name = l['name']
        except:
            pass
    captcha_name = soup.find('input',{'title':'Captcha, case sensitive'})['name']
    return username_name, password_name, captcha_name
      
def get_cat_and_page(url):
    reg_pattern = "page=([0-9]+)"
    page = re.search(reg_pattern,url).groups(1)[0]
    
    reg_pattern = "category=([0-9]+)"
    category = re.search(reg_pattern,url).groups(1)[0]

    return category, page
          
def create_file(out_file):
    #if csv file doesn't exist, create and put headers
    #if it exists, check if the header row is correct. if not, raise error and end program
    
    headers = ['Title','Prices','Vendor','Ships','drug_cat1','drug_cat2','cat','page']
    
    if os.path.isfile(out_file):
        #check if the header row is correct. if not, raise error and end program
        with open(out_file, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile)
            try:
                row1 = next(reader)
            except:
                row1 = []
        
        if row1 == headers:
            pass
        else:
            print("headers in {} do not match with the headers in this script".format(out_file))
            sys.exit()
    else:
        #create file and write header row
        with open(out_file, 'w', encoding='utf-8', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(headers)
            

def drug_info_boxes_present(driver):
    #if any drug_info_boxes are present, return True
    try:
        driver.find_element_by_xpath("//div[contains(@class, 'shopItem')]")
        return True
    except:
        return False
        
def click_and_wait(link):
#this shouldn't be necessary and causes significant slows. however, it was made as a workaround to the builtin click() function not waiting for pages to load correctly.
#update -- after testing with chrome instead of firefox, the issue is no longer present, so this function is no longer used.
    start_page = driver.page_source
    link.click()
    while True:
        new_page = driver.page_source
        if start_page == new_page:
            print("waiting for new page")
            time.sleep(0.5)
        else:
            #time.sleep(0.5)
            break
if __name__ == "__main__":
    main()