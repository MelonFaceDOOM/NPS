#Tor browser must be open before running this script
'''
1) go through drug categories on Dream Market
2) map contents (i.e. sub-category URLs, number of pages in each category
3) erase the current contents of the "scrape_progress" file
4) save a list of URLs to be scraped in "scrape_progress"
'''
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import pickle
import time

def main():
    username = "odrs"
    password = "odrs"
    
    ####################################
    ### OPEN BROWSER TO DREAM MARKET ###
    ####################################
    
    chrome_path = r"C:\Users\JMILLER\AppData\Local\Programs\Python\Python35-32\chromedriver.exe"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9150')
    chrome_options.add_experimental_option('useAutomationExtension',False)
    driver = webdriver.Chrome(chrome_path,chrome_options=chrome_options)
    
    dm_mirror = "http://k3pd243s57fttnpa.onion"
    
    ################################################################################################################################################
        
    ##############
    ### LOG IN ###
    ##############
    
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

    ################################################################################################################################################
    
    #######################
    ### MAP SITE LAYOUT ###
    #######################
    
    driver.get("{}/?category=104".format(dm_mirror))
    
    #"{domain}/?page={page}&category={category}".format(domain=domain,page=page,category=category)

    #create a list of all URLs to be scraped
    to_scrape = []

    drug_cats = driver.find_elements_by_xpath("//div[@class='category  depth1']/a")
    cat_urls = []
    for drug_cat in drug_cats:
        cat_urls.append(drug_cat.get_attribute("href"))

    for url in cat_urls:
        driver.get(url)

        sub_cat_urls = []
        for element in driver.find_elements_by_xpath("//div[contains(@class, 'category  depth2')]/a"):
            sub_cat_urls.append(element.get_attribute("href"))
            
        if len(sub_cat_urls) == 0:
            num_pages = count_pages(driver)
            to_scrape.extend(gen_url_list(num_pages,url))
            
        else:
            for sub_cat_url in sub_cat_urls:
                driver.get(sub_cat_url)
                num_pages = count_pages(driver)
                to_scrape.extend(gen_url_list(num_pages,sub_cat_url))
        
        time.sleep(5) # attempt to avoid ddos protection
        
        
    with open("scrape_progress", "wb") as sp:
        pickle.dump(to_scrape,sp)
    
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
        
        
def count_pages(driver):
    try:
        pageNav = driver.find_element_by_xpath("//ul[@class='pageNav']")
        pages = pageNav.find_elements_by_tag_name("li")
        page_count = int(pages[-2].text) #the last page will be the 2nd last li element
    except: # there will be no pageNav if there is only 1 page in this category
        page_count = 1
        
    return page_count
        
def gen_url_list(num_pages,url):
    reg_pattern = "category=([0-9]+)"
    category = re.search(reg_pattern,url).groups(1)[0]
    urls =[]
    [urls.append("/?page={page}&category={category}".format(page=page,category=category))
     for page in range(1,num_pages+1)
    ]
    
    return urls
            
if __name__ == "__main__":
    main()