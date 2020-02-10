import certifi
import requests
from bs4 import BeautifulSoup as soup
import csv
# import for write image to file
import os
import io
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#options = webdriver.ChromeOptions()
#options.add_argument('--ignore-certificate-errors')
#options.add_argument('--incognito')
#options.add_argument('--headless')
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1024x1400")

# download Chrome Webdriver  
# https://sites.google.com/a/chromium.org/chromedriver/download
# put driver executable file in the script directory
#chrome_driver = os.path.join(os.getcwd(), "chromedriver")

#driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
#driver = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)
driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
wait = WebDriverWait(driver, 100)
imgdriver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
waitimg = WebDriverWait(imgdriver, 100)

encoding = 'utf8'
productList=[]

class Product:
    def __init__(self, imageURL="", title="", author="", description="", category="", price="", adURL=""):
        # type: (object, object, object, object, object, object, object) -> object
        self.imageURL = imageURL
        self.title = title
        self.author = author
        self.description = description
        self.category = category
        self.price = price
        self.adURL = adURL

    def print_product(self):
        print("img : ", str(self.imageURL))
        print("Title : ", str(self.title))
        print("Author: ", str(self.author))
        print("Description : ", str(self.description))
        print("Category : ", str(self.category))
        print("Price : ", str(self.price))
        print("Ad URL : ", str(self.adURL))


class DBA_scraper:
    def __init__(self, output_csvfilename="product_file.csv", productObj=0):
        self.product_entries = []  # appended list of products
        self.csvfilename = output_csvfilename
        self.dba_addurls = []  # list of urls from pages
        #link to the product instance
        self.product = productObj
        # Connect to server
        self.mongoclient = pymongo.MongoClient('localhost', 27017)
        # Select the database
        self.importdb = self.mongoclient.dbabase

    def page_url(self, url_link):
        driver.get(url_link)

    def close_page(self):
        driver.close()

    def document_initialised(self, driver):
        return driver.execute_script("return initialised")
        
    def check_exists_by_xpath(self, xpathstring):
        returnValue= False
        if len(driver.find_elements_by_xpath(xpathstring))>0:
            # Element is present
            returnValue = True
        else:
            # Element is not present
            returnValue = False
        return returnValue
    
    def check_exists_imgurl_by_xpath(self, xpathstring):
        returnValue= False
        if len(imgdriver.find_elements_by_xpath(xpathstring))>0:
            # Element is present
            returnValue = True
        else:
            # Element is not present
            returnValue = False
        return returnValue

    def getImgUrl(self, urlString):
        imgdriver.get(urlString)
        imgUrl= None
        waitimg.until(EC.presence_of_element_located((By.ID, 'pictureBrowser')))
        if self.check_exists_imgurl_by_xpath('//*[@id="pictureBrowser"]/div/div'):
            element = imgdriver.find_element_by_class_name('mainImage')
            attributeString = element.find_element_by_tag_name('div').value_of_css_property('background-image')
            imgUrl = self.parse_style_attribute(attributeString)
        return imgUrl

    def parse_style_attribute(self, style_string):
        s_string = (style_string.split('url("')[1]).split('")')[0]
        return s_string
    
    def scrape_product(self, prod):
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sidebar-layout')))
        
        if self.check_exists_by_xpath("//*[@id='content']/div[2]/article/div[4]/table/tbody/tr[1]/td[2]"):
            title = driver.find_element_by_xpath("//*[@id='content']/div[2]/article/div[4]/table/tbody/tr[1]/td[2]")
            prod.title = title.text
        if self.check_exists_by_xpath("//*[@id='content']/div[1]/div[1]/div/div[2]/span[1]"):
            price = driver.find_element_by_xpath("//*[@id='content']/div[1]/div[1]/div/div[2]/span[1]")
            prod.price = price.text
        if self.check_exists_by_xpath("//*[@id='content']/div[2]/article/div[1]/a[1]"):
            imgURL = driver.find_element_by_xpath("//*[@id='content']/div[2]/article/div[1]/a[1]")
            imgUrlString = imgURL.get_attribute('href')
            prod.imageURL = self.getImgUrl(imgUrlString)
        if self.check_exists_by_xpath("//*[@id='content']/div[2]/article/div[2]/p[1]"):
            descr = driver.find_element_by_xpath("//*[@id='content']/div[2]/article/div[2]/p[1]")
            prod.description = descr.text
        if self.check_exists_by_xpath("//*[@id='content']/div[2]/article/div[2]/p[2]"):
            status = driver.find_element_by_xpath("//*[@id='content']/div[2]/article/div[2]/p[2]")
            prod.description = prod.description + " " + status.text 
        if self.check_exists_by_xpath("//*[@id='content']/div[2]/article/div[4]/table/tbody/tr[1]/td[5]"):
            kategori = driver.find_element_by_xpath("//*[@id='content']/div[2]/article/div[4]/table/tbody/tr[1]/td[5]")
            prod.category = kategori.text
        if self.check_exists_by_xpath("//*[@id='content']/div[2]/article/div[4]/table/tbody/tr[2]/td[2]"):
            author = driver.find_element_by_xpath("//*[@id='content']/div[2]/article/div[4]/table/tbody/tr[2]/td[2]")
            prod.author = author.text
        else:
            prod.author = ""

        prod.adURL = driver.current_url

        self.product_entries.append(prod)
        productList.append(prod)
    
    # This function is extracting the list or addURLS from all the pages this advertiser has on the dba website.
    def scrape_page (self):
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'listings__gallery__item')))
        # get each URL 
        a_list = driver.find_elements_by_class_name("listings__gallery__item")
        print("Count#: ",len(a_list))
        for elm in a_list:
            # Get the url string
            url_string = elm.get_attribute('href')
            # add url string to the class list of URLs
            self.dba_addurls.append(url_string)
    
        

    def set_numof_pages(self, pagestoScrape):
        self.numofpages = int(pagestoScrape)

    def write_cvs(self):
        try:
            with open(self.csvfilename, 'w', newline='') as csvfile:
                fields = ['imageurl', 'title', 'author', 'description', 'category', 'price', 'adurl']
                # creating a csv dict writer object 
                writer = csv.writer(csvfile) 
                writer.writerow(fields)
                # writing data rows 
                for plist in productList:
                    writelist = [ plist.imageURL ,
                        plist.title ,
                        plist.author,
                        plist.description ,
                        plist.category ,
                        plist.price ,
                        plist.adURL ]

                    writer.writerow(writelist)
            csvfile.close()
        except IOError as e:
            strerror = e.args
            print("I/O error({0}): {1}".format(errno, strerror))
        return

    def push_to_db(self):
            for data in self.product_entries:
                self.list_index = len(data)

                self.productdata = dict(
                    imageURL=data[0],
                    title=data[1],
                    description=data[2],
                    category=data[3],
                    price=data[4],
                    adURL=data[5])
                self.importdb.productimports.insert(self.productdata)


product = Product()
dbascrape = DBA_scraper("productlist.csv", product)
dbascrape.set_numof_pages(73)  # 70
for page_count in range(1, dbascrape.numofpages):
    url_sting = "https://www.dba.dk/saelger/privat/dba/5683282/?page=" + \
                str(page_count)
    print(url_sting)
    dbascrape.page_url(url_sting)
    # the scrape_page function takes all the URLs on the page and add to a list variable
    dbascrape.scrape_page()

print("total urls collected :", len(dbascrape.dba_addurls))
url_cnt = 0
for entry_item in dbascrape.dba_addurls:
    url_cnt=url_cnt+1
    print(url_cnt, ") URL: ", entry_item)
    dbascrape.page_url(entry_item)
    prod = Product()
    dbascrape.scrape_product(prod)
    print("Products: ", len(productList))

driver.quit()
imgdriver.quit()
#dbascrape.push_to_db()
dbascrape.write_cvs()
