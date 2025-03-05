import requests
import tldextract
import re
import webbrowser
import os
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import *
import pandas as pd
import datetime
import time
import tqdm
import openpyxl

from MinecraftModScraping import *
from MinecraftModProcessing import *

class Bundle():

    def __init__(self, startTime=time.time(), parentDataDirectory='data', currentDirectory=os.getcwd(), 
                 inputDataDirectory = 'input', outputDataDirectory = 'output', rawDataDirectory='raw',
                 finalDataDirectory = 'final', logsDirectory = 'logs',
                 previewUrl = 'https://www.curseforge.com/minecraft/search?page=1&pageSize=50&sortBy=relevancy&class=mc-mods',
                 selectedUrl = 'https://www.curseforge.com/minecraft/mc-mods/ae2-network-analyser/files/all?page=1&pageSize=50',
                 driverOptions = {'google chrome': webdriver.Chrome,
                                    'apple safari' : webdriver.Safari,
                                    'microsoft edge' : webdriver.Edge,
                                    'mozilla firefox' : webdriver.Firefox},
                recommendedDelayInSeconds = 2, maxAttempts = 5, maxPageNumberClassSelector = 'page-numbers',
                previewPageClassSelector = 'results-container', previewPageSize=50, previewSortType = 'relevancy',
                filesPageSize = 50, logFile = None, todaysDate=datetime.datetime.now()):

        #/default values
        self.startTime = startTime
        self.parentDataDirectory = parentDataDirectory
        self.currentDirectory = currentDirectory
        self.inputDataDirectory = inputDataDirectory
        self.outputDataDirectory = outputDataDirectory
        self.rawDataDirectory = rawDataDirectory
        self.finalDataDirectory = finalDataDirectory
        self.logsDirectory = logsDirectory
        self.previewUrl = previewUrl
        self.selectedUrl = selectedUrl
        self.driverOptions = driverOptions
        self.recommendedDelayInSeconds = recommendedDelayInSeconds
        self.maxAttempts = maxAttempts
        self.maxPageNumberClassSelector = maxPageNumberClassSelector
        self.previewPageClassSelector = previewPageClassSelector
        self.previewPageSize = previewPageSize
        self.previewSortType = previewSortType # acceptable values are ['relevancy', 'popularity', 'creation+date', 'latest+update', 'total+downloads']
        self.filesPageSize = filesPageSize
        self.logFile = logFile
        self.todaysDate = todaysDate
        self.resumeUnfinishedRun = None
        self.mode = None
        self.dateFormats = ["%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"]
        self.encoding = None
        self.filesColumns = ["Type", "Name", "Uploaded", "Size", "Game Ver.", "Mod Loaders", "Downloads",
                             "c_link_extension", "c_date_scraped_detail", "c_download_link", "c_selected"]
       
    def is_valid_date_format(self, dateFormats, possibleDate):
        """
        """
        for fmt in dateFormats:
            try:
                datetime.datetime.strptime(possibleDate, fmt)
                return True
            except ValueError:
                continue
        return False
        



def main(b1: Bundle):
    """
    """
    #Scrape desired data from curseforge website
    print("trying to scrape")
    scrape(b1)
    print("did we scrape?")
    
    #Finalize time logic to display total execution time
        #needed to access b1.startTime
    
    endTime = time.time()
    elapsedTime = endTime - b1.startTime
    hours, remainder = divmod(elapsedTime, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Collection Process Completed In: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
    
    process(b1)
    
    
    

if __name__ == '__main__':
    b1 = Bundle()
    main(b1)