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

encoding = 'utf8'


class Product:
    def __init__(self, imageURL="", title="", description="", category="", price="", adURL=""):
        # type: (object, object, object, object, object, object, object) -> object
        self.imageURL = imageURL
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.adURL = adURL

    def print_product(self):
        print("img : ", str(self.imageURL))
        print("Title : ", str(self.title))
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

    def scrape_product(self):
        # get the imageURL
        # imagedata = container.findAll("td", {"class": "thumbnailContainer"})
        product.imageURL = container.find(
            'div', {"class": "thumbnail"}).attrs['data-original']
        # get the title text
        details = container.find("td", {"class": "mainContent"})
        title = details.find("div", {"class": "expandable-box"})
        titledata = title.find('a')
        product.title = titledata.text

        # get the price tag
        tds = container.findAll("td")
        product.price = tds[len(tds) - 1].text

    def scrape_page (self):
        # html parsing
        #productlist = driver.find_elements_by_class_name("listings__gallery__item")
        # grab each product entry
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'listings__gallery__item')))
        a_list = driver.find_elements_by_class_name("listings__gallery__item")
        print("Count#: ",len(a_list))
        for elm in a_list:
            url_string = elm.get_attribute('href')
            self.dba_addurls.append(url_string)
        #page_source = driver.page_source
        #sp = soup(page_source, 'html.parser')
        #print(sp.prettify())
        #for item in productlist:
            # get the ad URL
            #self.product.adURL = container.a.get('href')
        #    print("url: %s", item)
            #self.product_entries.append(product)
            #product.print_product()

    def set_numof_pages(self, pagestoScrape):
        self.numofpages = int(pagestoScrape)

    csv_columns = ['imageurl', 'title',
                   'description', 'category', 'price', 'adurl']

    def write_cvs(self):
        try:
            with io.open(self.csvfilename, mode='w', encoding='UTF-8') as csvfile:
                writer = csv.writer(csvfile, dialect='excel',
                                    quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(self.csv_columns)
                for data in self.product_entries:
                    writer.writerow(data)
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
dbascrape.set_numof_pages(3)  # 70
for page_count in range(1, dbascrape.numofpages):
    url_sting = "https://www.dba.dk/saelger/privat/dba/5683282/?page=" + \
                str(page_count)
    print(url_sting)
    dbascrape.page_url(url_sting)
    dbascrape.scrape_page()


print("total urls collected :", len(dbascrape.dba_addurls))
url_cnt = 0
for entry_item in dbascrape.dba_addurls:
    url_cnt=url_cnt+1
    print(url_cnt, ") URL: ", entry_item)
    

#dbascrape.push_to_db()
#dbascrape.write_cvs()
