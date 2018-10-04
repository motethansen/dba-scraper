import bs4
import urllib3
from bs4 import BeautifulSoup as soup
import csv
# import for write image to file
import os
import io

#import random
#import datetime
# import for mongodb
#import pymongo

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

class dba_scraper:
    def __init__(self, output_csvfilename = "product_file.csv"):
        self.product_entries = []  # appended list of products
        self.response = ""
        self.csvfilename = output_csvfilename
        self.entries = [] # list of entries per row
        # Connect to server
        #self.mongoclient = pymongo.MongoClient('localhost', 27017)
        # Select the database
        #self.importdb = self.mongoclient.bookshelf

    def page_url(self, url_link):
        self.my_url = url_link
        # opening the connection to read the page
        self.http = urllib3.PoolManager()
        self.response = self.http.request('GET', self.my_url)

    def set_numof_pages(self, pagestoScrape):
        self.numofpages = int(pagestoScrape)

    csv_columns = ['imageurl','title','description','category','price','adurl']

    def write_cvs(self):
        try:
            with io.open(self.csvfilename,mode='w', encoding='UTF-8') as csvfile:
                writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(self.csv_columns)
                for data in self.product_entries:
                    writer.writerow(data)
            csvfile.close()
        except IOError as e:
            strerror = e.args
            print("I/O error({0}): {1}".format(errno,strerror))
        return

    def scrape_page(self):
        product = Product()

        # html parsing
        page_soup = soup(self.response.data, "html.parser")
        # grab each book entry
        containers = page_soup.findAll("tr", {"class": "dbaListing"})
        for container in containers:

            # get the ad URL
            product.adURL = container.a.get('href')

            # get the imageURL
            #imagedata = container.findAll("td", {"class": "thumbnailContainer"})
            product.imageURL = container.find('div',{"class":"thumbnail"}).attrs['data-original']
            # get the title text
            details = container.find("td", {"class": "mainContent"})
            title = details.find("div",{"class": "expandable-box"})
            titledata = title.find('a')
            product.title = titledata.text

            # get the price tag
            tds = container.findAll("td")
            product.price = tds[len(tds)-1].text

            product.print_product()   
            self.entries.append(product.imageURL)
            self.entries.append(product.title)
            self.entries.append(product.description)
            self.entries.append(product.category)
            self.entries.append(product.price)
            self.entries.append(product.adURL)
            self.product_entries.append(self.entries)
            self.entries = []

dbascrape = dba_scraper("productlist.csv")
dbascrape.set_numof_pages(31) #31
for page_count in range (1,dbascrape.numofpages):
    url_sting = "https://www.dba.dk/brugerens-annoncer/brugerid-5683282/side-" + str(page_count)
    print (url_sting)
    dbascrape.page_url(url_sting)
    dbascrape.scrape_page()

dbascrape.write_cvs()