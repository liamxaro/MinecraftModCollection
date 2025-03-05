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

from src.MinecraftModScraping import Bundle

b1 = Bundle()
masterFile = ['/Users/admin/AroTekCodingSpace/Python-Workspace/MinecraftModCollectionProject/data/output/raw/detail/https:||www.curseforge.com--14-2-2025/https:||www.curseforge.com|minecraft|mc-mods|a-block-of-charcoal|files|all?page=1&pageSize=50-DATA13-2-2025.html']
print(f"Reading in file: {os.path.basename(masterFile[0])}") #perform slice because masterFile is a list, we want the file
with open(masterFile[0], 'r', encoding='utf-8') as file:
    content = file.read()
soup = BeautifulSoup(content, 'lxml')
print(f"File: {os.path.basename(masterFile[0])} loaded.")

cards = soup.find_all('div', class_='files-table')
print(f"Tables found: {len(cards)}")
#print(f"Last card extracted: {cards[-1]}")'
print(b1.filesColumns)

progressBar = tqdm.tqdm(cards, desc=f"Building DataFrame: ", colour='#7B64C2')
dfs = []         
for card in progressBar:
#headerRow = card.find('div', class_='header-row')
#columns = [item['title'] for item in headerRow.find_all('div')]
    data=[]
    rows=card.find_all('div', class_='file-row')
    #print(f"card: {card.find('a', class_="file-row-details")['href']} has len of rows: {len(rows)}")
    tqdm.tqdm.write(f"\rCard: {card.find('a', class_='file-row-details')['href']} has len of rows: {len(rows)}")


    for index, row in enumerate(rows):
        L = [elem.text.strip() for elem in row.find_all('span', class_=False)] + [elem.text.strip() for elem in row.find_all('div', class_='tooltip tooltip-small')]
        L = list(set(L))


        rowData = {
            b1.filesColumns[b1.filesColumns.index('Type')]: row.find('span', class_='channel-tag release').text.strip() if row.find('span', class_='channel-tag release') 
                                                        else row.find('span', class_='channel-tag alpha').text.strip() if row.find('span', class_='channel-tag alpha') 
                                                        else row.find('span', class_='channel-tag beta').text.strip() if row.find('span', class_='channel-tag beta') 
                                                        else 'No data recorded on website'
                                                        ,
            b1.filesColumns[b1.filesColumns.index('Name')]: row.find('span', class_='name')['title'].strip() if row.find('span', class_='name') else 'No data recorded on website',
            b1.filesColumns[b1.filesColumns.index('Uploaded')]: next((elem for elem in L if b1.is_valid_date_format(b1.dateFormats, elem)), 'No data recorded on website'),
            b1.filesColumns[b1.filesColumns.index('Size')]: next((elem for elem in L if re.search(r'\d+(\.\d+)?\s?(KB|MB|GB)', elem)), 'No data recorded on website'),
            b1.filesColumns[b1.filesColumns.index('Game Ver.')]: ', '.join(sorted(set(re.findall(r'(?<!\S)\d+\.\d+(?:\.\d+)*(?!\S)', ' '.join([elem for elem in L if not re.search(r'[a-zA-Z]', elem)]))))) or 'No data recorded on website',
            b1.filesColumns[b1.filesColumns.index('Mod Loaders')]: ', '.join(sorted(set(elem.strip() for elem in L if not re.search(r'\d', elem) and not re.fullmatch(r'release|alpha|beta', elem, re.IGNORECASE)))) or 'No data recorded on website',
            b1.filesColumns[b1.filesColumns.index('Downloads')]: next((int(elem.replace(',', '')) for elem in L if elem.replace(',', '').isdigit()), 'No data recorded on website'),
            b1.filesColumns[b1.filesColumns.index('link_extension')]: card.find('a', class_='file-row-details')['href'].split('/files')[0].strip().lower(),
            b1.filesColumns[b1.filesColumns.index('date_scraped_detail')]: os.path.splitext(masterFile[0].split('DATA')[-1])[0],
            b1.filesColumns[b1.filesColumns.index('download_link')] : "https://www.curseforge.com" + str(card.find('a', class_='file-row-details')['href'].strip().lower())
        }

        
        data.append(rowData)
    
df = pd.DataFrame(data, columns=b1.filesColumns)
df = df.drop_duplicates(keep='first')
dfs.append(df)
finalDF = pd.concat(dfs, ignore_index=True)
finalDF[b1.filesColumns[b1.filesColumns.index('selected')]] = ''

finalDF['Mod Loaders'] = finalDF['Mod Loaders'].apply(
    lambda x: x if x == "No data recorded on website" else 
              ', '.join(sorted(set(i.strip() for i in re.split(r',| ', x) if i.strip())))
)

print(finalDF[['Name', 'Mod Loaders']])

#infer a mod loader if they left it out when uploading the file
# Filter only rows where Mod Loaders is not "No data recorded on website"
filterDF = finalDF[finalDF['Mod Loaders'] != 'No data recorded on website']

# Compute replacements on the filtered dataset
replacement_map = filterDF.groupby('link_extension')['Mod Loaders'].apply(
    lambda x: x.iloc[0] if x.nunique() == 1 and ',' not in x.iloc[0] else 'No data recorded on website'
)

# Map the computed replacements back to finalDF
finalDF['Mod Loaders'] = finalDF['link_extension'].map(replacement_map).fillna(finalDF['Mod Loaders'])

# Replace "No data recorded on website" with corresponding mod loader values
finalDF['Mod Loaders'] = finalDF['Mod Loaders'].apply(
    lambda x: x if x != 'No data recorded on website' else 'No data recorded on website'
)


print(finalDF.info())
print(finalDF.columns)
print(finalDF[['Name', 'Mod Loaders']])

    