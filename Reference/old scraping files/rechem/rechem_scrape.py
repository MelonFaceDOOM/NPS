# import time
# from bs4 import BeautifulSoup

import csv
import sys
import re
from selenium import webdriver

def main():
    chrome_path = r"C:\Users\JMILLER\AppData\Local\Programs\Python\Python35-32\chromedriver.exe"
    driver = webdriver.Chrome(chrome_path)
    driver.get("https://www.rechem.ca/index.php?route=product/category")
    
    rechem_drugs = [] # will fill with a dict for each drug on the website
    
    parent_cat_links = []
    for list_item in driver.find_elements_by_xpath("//a[contains(@class, 'list-group-item')]"): #all list_items on this page are the main drug categories
        parent_cat_links.append(list_item.get_attribute("href"))
        
    for parent_cat in parent_cat_links:
        driver.get(parent_cat)
        
        list_item_links = []
        for list_item in driver.find_elements_by_xpath("//a[contains(@class, 'list-group-item')]"): #list_items on this page will be both main- and sub-categories
            list_item_links.append(list_item.get_attribute("href"))
        child_cat_links = prune_list(parent_cat,list_item_links)
        
        #first see if there are some drugs listed on the parent_cat page:
        drugs_in_page = driver.find_elements_by_xpath("//div[contains(@class, 'product-layout product-grid col-lg-4 col-md-4 col-sm-6 col-xs-12')]")
        drugs_in_page_extracted = extract_drug_info(drugs_in_page)
        
        rechem_drugs.extend(drugs_in_page_extracted)
        
        for child_cat in child_cat_links:
            driver.get(child_cat)
            
            drugs_in_page = driver.find_elements_by_xpath("//div[contains(@class, 'product-layout product-grid col-lg-4 col-md-4 col-sm-6 col-xs-12')]")
            drugs_in_page_extracted = extract_drug_info(drugs_in_page)
        
            rechem_drugs.extend(drugs_in_page_extracted)
            
    keys = rechem_drugs[0].keys()
    with open("rechem_scrape.csv", 'w', encoding='utf-8') as csvfile:
        dict_writer = csv.DictWriter(csvfile,keys,lineterminator = '\n')
        dict_writer.writeheader()
        dict_writer.writerows(rechem_drugs)
    
    
    
def extract_drug_info(drugs_in_page):
    
    if len(drugs_in_page) == 0:
        return []
    
    extracted_drug_info = [] # will fill with a dict for each drug in page
    
    cat1 = drugs_in_page[0].find_element_by_xpath("//ul[@class='breadcrumb']/li[2]/a").text
    try: #all pages will have cat1, but not all will have a cat2, so try and except is used
        cat2 = drugs_in_page[0].find_element_by_xpath("//ul[@class='breadcrumb']/li[3]/a").text
    except:
        cat2 = "N/A"
        
    for drug_info_box in drugs_in_page:
        drug = {}
        drug['title'] = drug_info_box.find_element_by_xpath(".//div[@class='prod-title']/h4/a").text
        drug['price'] = drug_info_box.find_element_by_xpath(".//p[@class='price']").text
        drug['main_category'] = cat1
        drug['sub_category'] = cat2
        extracted_drug_info.append(drug)
        
    return extracted_drug_info
        


def prune_list(parent_cat_link, list_item_links):
    #check if links are a sub-category of parent_cat_link; if yes keep, otherwise discard
    #example links:
        #parent_cat_link = https://www.rechem.ca/index.php?route=product/category&path=62
        #sub-link: https://www.rechem.ca/index.php?route=product/category&path=62_125
        #next parent cateogry: https://www.rechem.ca/index.php?route=product/category&path=63

    child_cat_links = [] #build with all appropriate links and return

    reg_pattern = "path=([0-9]+)"
    parent_cat_number = re.search(reg_pattern,parent_cat_link).groups(1)[0]

    for link in list_item_links:
        link_number = re.search(reg_pattern,link).groups(1)[0]
        if parent_cat_number == link_number:
            child_cat_links.append(link)
    return child_cat_links
     
if __name__ == "__main__":
    main()