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
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import datetime
import time
import tqdm
import xlsxwriter
import lxml
import openpyxl
import numpy as np

from src.MinecraftModScraping import Bundle

b1 = Bundle()
b1.mode = 'general'

df = pd.read_excel("/Users/admin/AroTekCodingSpace/Python-Workspace/MinecraftModCollectionProject/data/output/final/output.xlsx", sheet_name='detail')
# print(df.head())
# print(df.info())

#print(df['mod_loaders'].unique().tolist())
validLoaders = df[df['mod_loaders'] != 'No, data, on, recorded, website']
singleLoaderMap = validLoaders.groupby('c_link_extension')['mod_loaders'].nunique() == 1

# Get the actual mod loader values for those groups
singleLoaderValues = validLoaders.groupby('c_link_extension')['mod_loaders'].first()

# Update the original DataFrame
df['mod_loaders'] = df.apply(
    lambda row: singleLoaderValues[row['c_link_extension']]
    if row['c_link_extension'] in singleLoaderValues.index 
    and row['mod_loaders'] == 'No, data, on, recorded, website'
    else row['mod_loaders'],
    axis=1
)

print(df.head(20))
