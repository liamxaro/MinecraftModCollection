import requests
import tldextract
import re
import webbrowser
import os
from bs4 import BeautifulSoup
import chardet

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import datetime
import time
import tqdm
import openpyxl
from openpyxl import load_workbook
import lxml
import numpy as np

from MinecraftModScraping import *
from MinecraftModScraping import b1


def collect(b1: Bundle):
    """
    """
    
    df = pd.read_excel(os.path.join(os.getcwd(),
                                    b1.parentDataDirectory,
                                    b1.outputDataDirectory,
                                    b1.finalDataDirectory,
                                    'output.xlsx'),
                       sheet_name='detail')
    
    headers = {
    "Accept": "application/x-clarity-gzip",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "1976",  # You can exclude this if it changes dynamically
    "Cookie": "MUID=3370C1A3E99066B30960D4C8E88967CD",  # Add more cookies if needed
    "Host": "s.clarity.ms",
    "Origin": "https://www.curseforge.com",
    "Referer": "https://www.curseforge.com/",
    "Sec-CH-UA": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"macOS"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    }
    
    df['c_selected'] = df['c_selected'].str.strip().str.lower()
    if df['c_selected'].nunique() > 1:
        print("other symbols were marked on rows. terminating process")
    filtered = df[df['c_selected'] == 'x']
    
    filtered['c_download_link'] = filtered['c_download_link'].str.replace('files', 'download')
    links = filtered['c_download_link'].tolist()
    
    print(f"Beginning Mod Collection. {len(links)} mods to download")
    for idx, link in enumerate(links):
        
        url = 'https://www.curseforge.com' + link
        
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(os.path.join(os.getcwd(), b1.parentDataDirectory, b1.outputDataDirectory, 'selection', df.loc[df['c_link_extension'] == link, 'name'].iloc[0]), 'wb') as jarFile:
                jarFile.write(response.content)
    
 


collect(b1)  
    