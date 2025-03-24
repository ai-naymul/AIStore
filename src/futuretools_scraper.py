import os
import sys
import requests
import hashlib
from bs4 import BeautifulSoup
import time


import scraper_utils
from scraper_root import Scraper

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService

from pymongo import MongoClient, errors
from datetime import datetime

import numpy as np
import pprint as pp

from log_config import logger

import platform
system_platform = platform.system()

class ScraperFutureTools(Scraper):
    def download_html(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")  # Ensure GUI is off
        firefox_options.add_argument("--no-sandbox")  # Bypass OS security model
        firefox_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

        if system_platform == 'Linux':
            firefox_options.binary_location = "/usr/bin/firefox"
            geckodriver_path = '/usr/bin/geckodriver'
            service = FirefoxService(executable_path=geckodriver_path)
            driver = webdriver.Firefox(service=service, options=firefox_options)
        elif system_platform == 'Darwin':  # Darwin is the system name for macOS
            driver = webdriver.Firefox(options=firefox_options)
        else:
            raise Exception("Unsupported platform: {}".format(system_platform))

        main_url = 'https://futuretools.io'
        driver.get(main_url)

        last_height = driver.execute_script("return document.body.scrollHeight")

        s_id = 1
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            print(f"{s_id}. Scrolling...")
            logger.info(f"{s_id}. Scrolling...")
            s_id += 1

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html_content = driver.page_source

        fpath = self.getUrl()
        with open(fpath, "w", encoding='utf-8') as f:
            f.write(html_content)
            f.close()
            time.sleep(1)

        driver.quit()


    def __init__(self, db_name, collection_name, dropDB=False, dropCollection=False):
        super().__init__()

        try:
            # Try connecting to localhost first
            self.client = scraper_utils.connect_to_mongodb()
        except errors.ConnectionFailure:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

        if dropDB:
            try:
                self.client.drop_database(db_name)
                logger.info(f"Dropped database {db_name}.")
            except Exception as e:
                logger.error(f"Failed to drop database {db_name}: {e}")
        if dropCollection:
            try:
                db = self.client[db_name]
                db[collection_name].drop()
                logger.info(f"Dropped collection {collection_name}.")
            except Exception as e:
                logger.error(f"Failed to drop collection {collection_name}: {e}")

        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
    def scrape_data_from_file(self):
        ft_img_base_url = "https://global-uploads.webflow.com/63994dae1033718bee6949ce/"
        fpath = self.url.split("file://")[1]
        tools = []
        try:
            with open(fpath, 'r') as f:
                soup = BeautifulSoup(f, 'html.parser')
                list_sel = 'div.tool'
                ls = soup.select(list_sel) 

                tools = []
                for i, sii in enumerate(ls):
                    print("Scraping tool {}...".format(i))
                    logger.info("Scraping tool {}...".format(i))

                    tool = {}
                    si = BeautifulSoup(str(sii), 'html.parser') 
                    # get tool_name
                    tn = si.find('a', {'class': 'tool-item-link---new'})
                    if tn is not None:
                        tool_name = tn.text
                    else:
                        continue

                        tn2 = si.find('a', {'class': 'tool-item-link'}) 
                        tn3 = si.find('a', {'class': 'tool-item-link---featured'}) 
                        if tn2 is not None:
                            tool_name = tn2.text
                        elif tn3 is not None:
                            tool_name = tn3.text
                        else:
                            print("No tool name found.")
                            logger.error("No tool name found.")

                    tu = si.find('a', {'class': 'tool-item-new-window---new'})

                    if tu is not None:
                        tool_url = tu['href']
                    else:
                        tu2 = si.find('a', {'class': 'tool-item-link'}) 
                        tu3 = si.find('a', {'class': 'tool-item-link---featured'}) 
                        if tu2 is not None:
                            tool_url = tu2['href']
                        elif tu3 is not None:
                            tool_url = tu3['href']
                        else:
                            tool_url = ""

                    if tool_url != "":
                        try:
                            ru = requests.get(tool_url)
                            if ru.status_code == 200:
                                surl = BeautifulSoup(ru.content, 'html.parser')

                                meta_refresh = surl.find('meta', attrs={'http-equiv': 'refresh'})
                                content = meta_refresh['content']
                                url = content.split(";")[1].strip().split("=")[1].split("/?")[0].split("?ref")[0]
                                tool_url = url
                            else:
                                logger.error(f'Request failed with status code {ru.status_code}.')
                        except Exception as e:
                            logger.error(f'Failed to get tool url: {e}')
                            print(f'Failed to get tool url: {e}')
                    
                    td = si.find('div', {'class': 'tool-item-description-box---new'})

                    if td is not None:
                        tool_description = td.text
                    else:
                        td2 = si.find('div', {'class': 'tool-item-description-box'}) 
                        td3 = si.find('div', {'class': 'tool-item-description-box---featured'}) 
                        if td2 is not None:
                            tool_description = td2.text
                        elif td3 is not None:
                            tool_description = td3.text
                        else:
                            tool_description = ""
                    
                    # tis = si.find('img', {'class': 'tool-item-image---new'})
                    
                    # if tis is not None:
                    #     #i_src = ft_img_base_url + tis['src'].split("/")[2]
                    #     tool_img_src = tis['src']
                    # else:
                    #     tool_img_src = ""

                    tc = si.find('div', {'class': 'text-block-53'})
                    if tc is not None:
                        tool_usecase = tc.text
                    else:
                        tool_usecase = "N/A"

                    tup = si.find('div', {'class': 'text-block-52'})

                    if tup is not None:
                        upvotes = tup.text
                    else:
                        upvotes = 0


                    tool['name'] = tool_name 
                    tool['url']  = tool_url
                    tool['use_case'] = tool_usecase
                    tool['category'] = tool_usecase
                    tool['description'] = tool_description
                    # tool['img_src'] = tool_img_src
                    tool['rank'] = {}
                    tool['rank']['upvotes'] = int(upvotes)

                    #self.getWebTrafficStat(tool)

                    tool['hash'] = self.generate_hash(tool)
                    tool['last_update_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    existing_tool = self.collection.find_one({'hash': tool['hash']})
                    if existing_tool:
                        if existing_tool != tool:
                            self.collection.update_one({'_id': existing_tool['_id']}, {'$set': tool})
                            print(f"Updated tool into MongoDB.")
                            logger.info(f"Updated tool into MongoDB.")
                    else:
                        self.collection.insert_one(tool)
                        logger.info(f"Inserted {len(tools)} items into MongoDB.")
                        print("Inserted {} items into MongoDB.".format(len(tools)))
                    
                    tools.append(tool)
                    print(tool)
                    logger.info(tool)
        except Exception as e:
            logger.error(f"Failed to scrape data from {self.url}: {e}")
            print("Failed to scrape data from {}: {}".format(self.url, e))
            return

    def scrape(self):
        if "file://" in self.url:
            self.scrape_data_from_file()
        else:
            try:
                # Get the html content
                r = requests.get(self.url)
                soup = BeautifulSoup(r.content, 'html.parser')
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to scrape data from {self.url}: {e}")