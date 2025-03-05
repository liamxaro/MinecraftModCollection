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
from MinecraftModScraping import b1

from MinecraftModProcessing import *



def main(b1: Bundle):
    """
    """
    #Scrape desired data from curseforge website
    scrape(b1)
    
    #Finalize time logic to display total execution time
        #needed to access b1.startTime
    
    endTime = time.time()
    elapsedTime = endTime - b1.startTime
    hours, remainder = divmod(elapsedTime, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Collection Process Completed In: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
    
    process(b1)
    
    
    

if __name__ == '__main__':
    main(b1)