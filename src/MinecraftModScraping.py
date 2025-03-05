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
        




#Instantiate collection of variables outside of the scrape()
#   so we can import it into other files
b1 = Bundle()
def scrape(b1: Bundle) -> None:
    
    

    #gather input on whether to scrape data or continue with data already there. If its your first time you need to scrape
    while True:
        ans = str(input("Would you like to scrape more data to aggregate (Y/N): ").lower())

        if ans in ['yes', 'y', 'yeah', 'yup', 'no', 'n', 'nah', 'nope']:
            break

        else:
            print("Invalid response. Please enter (Y or Yes) or (N or No).")

    #Determine which browser you would like python to use
    if ans in ['yes', 'y', 'yeah', 'yup']:
        while True:
            driverAns = str(input(f"Type the browser you would like to use as it appears here\n{list(b1.driverOptions.keys())}: ").lower())

            if driverAns in list(b1.driverOptions.keys()):
                break

            else:
                print(f"Invalid response. Please enter a value consistent with [{list(b1.driverOptions.keys())}")

        
        #attempt to use the browser chosen by user
        try:
            driver = b1.driverOptions[driverAns]()
            b1.chosenDriver = driver
        except:

            print('That browser is not properly configured for automation on your system.  Properly configure it or restart the program and try another browser.')
            return
        
        print("""DISCLAIMER: There are two modes to choose from [general, detail].  Running in general mode is quicker and only scrapes
                preview level data.  It does not provide a complete insight on the mods availabe and only gives you a rough estimate of 
                what to expect. The data is taken only from the preview cards.  Running in detail mode scrapes the extended table from the 
                files tab while inside the selected mod page.""")
        while True:
            modeAns = str(input(f"Type the mode you would like to use to scrape the data [general, detail]: ").lower())
            if modeAns in ['general', 'detail']:
                b1.mode = modeAns
                break
            else:
                print('Invalid response. Please enter an answer consistent with these two modes [general, detail]')
        
        while True:
            resumeAns = str(input("Type 'True' or 'False' if you are resuming an unfinished run: ").strip().lower())
            if resumeAns in ['true', 'false']:
                if resumeAns == 'true':
                    b1.resumeUnfinishedRun = True
                else:
                    b1.resumeUnfinishedRun = False
                break
            else:
                print('Invalid response. Please enter an answer consistent with these two modes [True, False].')

        
        if b1.resumeUnfinishedRun == True and b1.mode == 'detail':
            b1.logFile = f'log-{b1.todaysDate.date()}-{b1.mode}-{b1.resumeUnfinishedRun}.txt'
            with open(os.path.join(b1.currentDirectory, b1.parentDataDirectory, b1.logsDirectory,b1.logFile), 'w') as file:
                file.write('')
            
            #grab the newest mod folder scraped
            newestCurseforgeDirectory = os.path.join(b1.currentDirectory,
                                                     b1.parentDataDirectory,
                                                     b1.outputDataDirectory,
                                                     b1.rawDataDirectory,
                                                     b1.mode,
                                                     get_newest_curseforge_directory(b1))
            #grab the newest file created
            newestFile = get_newest_file(newestCurseforgeDirectory)
            newestMods = get_newest_mod_grouping(newestCurseforgeDirectory, newestFile)
            print(newestMods[0])
            searchForMod = newestMods[0].split('mc-mods')[1].split('files')[0].strip('|')
            
            #delete the newest mod scraped and its subsequent files for rescraping
            for index, mod in enumerate(newestMods):
                
                os.remove(os.path.join(newestCurseforgeDirectory, mod))
                if os.path.exists(os.path.join(newestCurseforgeDirectory, mod)):
                    print(f"Stopping Process. Deletion error with {mod}")
                    return
                else: 
                    print(f"Mod file(s) successfully deleted: {mod}")
                    searchForMod = mod.split('mc-mods')[1].split('files')[0].strip('|')
              
            #begin searching for mod
            maxWebpages = get_max_webpages(b1)
            minWebPages = None
            progressBar = tqdm.tqdm(range(1, maxWebpages + 1), colour='#7B64C2', desc=f"Searching for {searchForMod}: ")    
            for i in progressBar:
                b1.previewUrl = f"https://www.curseforge.com/minecraft/search?page={i}&pageSize={b1.previewPageSize}&sortBy={b1.previewSortType}&class=mc-mods"

                #retrieve the data from the webpage
                soup = get_website_data(b1)
                cards = soup.find_all('div', class_='project-card')
                
                #iterate through each mod card
                for index, card in enumerate(cards):

                    cardLabel = card.find('a', class_='overlay-link')
                    cardLink = cardLabel.get('href')
                    mod = cardLink.split('/')[-1]
                    
                    #once we find the mod, save the page number and mod card number
                    if mod.strip().lower() == searchForMod.strip().lower():
                        minWebPages = i
                        cardIndex = index
                        # Make the progress bar look complete
                        progressBar.n = progressBar.total  # Set the current progress to total
                        progressBar.last_print_n = progressBar.total  # Prevent flickering or delays
                        progressBar.update(0)  # Force a refresh of the display
                        break
                
                #Trick to break the outter loop so we aren't brute force searching anymore
                if minWebPages is not None:
                    break
                
            #Resume the exact page  
            b1.previewUrl = f"https://www.curseforge.com/minecraft/search?page={minWebPages}&pageSize={b1.previewPageSize}&sortBy={b1.previewSortType}&class=mc-mods"

            #retrieve the data from the webpage
            soup = get_website_data(b1)
            cards = soup.find_all('div', class_='project-card')
            
            #filter cards
            for index, card in enumerate(cards):
                link = card.find('a', href=True)
                modId = link['href'].split('mc-mods/')[-1].strip().lower()
                
                if searchForMod == modId:
                    select = index
            #subset cards       
            cards = cards[select:]
            
            for index, card in tqdm.tqdm(enumerate(cards, start=cardIndex), total=len(cards), desc=f"Resume Run at: {card}", colour='#7B64C2'):
                cardLabel = card.find('a', class_='overlay-link')
                cardLink = cardLabel.get('href')
                
                b1.selectedUrl = f'https://www.curseforge.com' + cardLink + f'/files/all?page=1&pageSize={b1.filesPageSize}' #b1 1 is used in this url
                
                #grab the maximum amount of pages dedicated to the files table
                maxFilepages = get_max_filepages(b1)
                
                if not maxFilepages:
                    
                    with open(b1.logFile, 'a', encoding='utf-8') as file:
                        file.write(str(card) + '/n')
                
                    continue
                
                #grab the table containing all availabe files for the mod
                filesTable = get_files_table(b1)

                # print(f"{index} URL Being Used: {b1.selectedUrl}")
                # print(filesTable)
                newlyCreatedFile = create_cached_data(filesTable, b1)
                write_cached_data(filesTable, newlyCreatedFile)


                if maxFilepages > 1:
                    #iterate through each file page dedicated to the mod
                    for i in range(2, maxFilepages + 1): # we adjust our loop to 2 to max() + 1
                        b1.selectedUrl = f'https://www.curseforge.com' + cardLink + f'/files/all?page={i}&pageSize={b1.filesPageSize}'
                        #div class you're looking for is called files-table
                        #print(f"URL Being Used: {b1.selectedUrl}")
                        filesTable = get_files_table(b1)

                        newlyCreatedFile = create_cached_data(filesTable, b1)
                        write_cached_data(filesTable, newlyCreatedFile)
                        #print(filesTable)
            
            progressBar = tqdm.tqdm(range(minWebPages + 1, maxWebpages + 1), colour='#7B64C2')
            #iterate through all the webpages
            for i in progressBar:
                b1.previewUrl = f"https://www.curseforge.com/minecraft/search?page={i}&pageSize={b1.previewPageSize}&sortBy={b1.previewSortType}&class=mc-mods"
                                
                #retrieve the mod cards from each webpage
                soup = get_website_data(b1)
                cards = soup.find_all('div', class_='project-card')
                
                #iterate through each mod card
                for index, card in enumerate(cards):

                    cardLabel = card.find('a', class_='overlay-link')
                    cardLink = cardLabel.get('href')
                    progressBar.set_description(f"Processing {cardLink.split('/')[-1]}")
                    b1.selectedUrl = f'https://www.curseforge.com' + cardLink + f'/files/all?page=1&pageSize={b1.filesPageSize}' #b1 1 is used in this url
                    
                    #grab the maximum amount of pages dedicated to the files table
                    maxFilepages = get_max_filepages(b1)
                    
                    #grab the table containing all availabe files for the mod
                    filesTable = get_files_table(b1)

                    # print(f"{index} URL Being Used: {b1.selectedUrl}")
                    # print(filesTable)
                    newlyCreatedFile = create_cached_data(filesTable, b1)
                    write_cached_data(filesTable, newlyCreatedFile)


                    if maxFilepages > 1:
                        #iterate through each file page dedicated to the mod
                        for i in range(2, maxFilepages + 1): # we adjust our loop to 2 to max() + 1
                            b1.selectedUrl = f'https://www.curseforge.com' + cardLink + f'/files/all?page={i}&pageSize={b1.filesPageSize}'
                            #div class you're looking for is called files-table
                            #print(f"URL Being Used: {b1.selectedUrl}")
                            filesTable = get_files_table(b1)

                            newlyCreatedFile = create_cached_data(filesTable, b1)
                            write_cached_data(filesTable, newlyCreatedFile)
                            #print(filesTable)
                
                

        
        elif b1.mode == 'general' and b1.resumeUnfinishedRun == False:
            #create log
            b1.logFile = f'log-{b1.todaysDate.date}-{b1.mode}-{b1.resumeUnfinishedRun}.txt'
            with open(os.path.join(b1.currentDirectory, b1.parentDataDirectory, b1.logsDirectory,b1.logFile), 'w') as file:
                file.write('')
                
            #grab the max amount of webpages that exist on the website that we will scrape
            maxWebpages = get_max_webpages(b1)

            progressBar = tqdm.tqdm(range(1, maxWebpages + 1), colour='#7B64C2')
            #iterate through all the webpages
            for i in progressBar:
                b1.previewUrl = f"https://www.curseforge.com/minecraft/search?page={i}&pageSize={b1.previewPageSize}&sortBy={b1.previewSortType}&class=mc-mods"

                #retrieve the data from the webpage
                soup = get_website_data(b1)
                
                #create repository structure, handling all parent directories, subdirectories, and files
                newlyCreatedFile = create_cached_data(soup, b1)

                #each webpage gets recorded as its own html file in directory 'CachedData'
                write_cached_data(soup, newlyCreatedFile)

            #close browser used
            b1.chosenDriver.quit()
        
        elif b1.mode == 'detail' and b1.resumeUnfinishedRun == False:
            #create log
            b1.logFile = f'log-{b1.todaysDate.date()}-{b1.mode}-{b1.resumeUnfinishedRun}.txt'
            with open(os.path.join(b1.currentDirectory, b1.parentDataDirectory, b1.logsDirectory,b1.logFile), 'w') as file:
                file.write('')
            
            #get max number of webpages on the website   
            maxWebpages = get_max_webpages(b1)

            progressBar = tqdm.tqdm(range(1, maxWebpages + 1), colour='#7B64C2')
            #iterate through all the webpages
            for i in progressBar:
                b1.previewUrl = f"https://www.curseforge.com/minecraft/search?page={i}&pageSize={b1.previewPageSize}&sortBy={b1.previewSortType}&class=mc-mods"
                                
                #retrieve the mod cards from each webpage
                soup = get_website_data(b1)
                cards = soup.find_all('div', class_='project-card')
                
                #iterate through each mod card
                for index, card in enumerate(cards):

                    cardLabel = card.find('a', class_='overlay-link')
                    cardLink = cardLabel.get('href')
                    progressBar.set_description(f"Processing {cardLink.split('/')[-1]}")
                    b1.selectedUrl = f'https://www.curseforge.com' + cardLink + f'/files/all?page=1&pageSize={b1.filesPageSize}' #b1 1 is used in this url
                    
                    #grab the maximum amount of pages dedicated to the files table
                    maxFilepages = get_max_filepages(b1)
                    
                    if not maxFilepages:
                    
                        with open(b1.logFile, 'a', encoding='utf-8') as file:
                            file.write(str(card) + '/n')
                    
                        continue
                    
                    #grab the table containing all availabe files for the mod
                    filesTable = get_files_table(b1)

                    # print(f"{index} URL Being Used: {b1.selectedUrl}")
                    # print(filesTable)
                    newlyCreatedFile = create_cached_data(filesTable, b1)
                    write_cached_data(filesTable, newlyCreatedFile)


                    if maxFilepages > 1:
                        #iterate through each file page dedicated to the mod
                        for i in range(2, maxFilepages + 1): # we adjust our loop to 2 to max() + 1
                            b1.selectedUrl = f'https://www.curseforge.com' + cardLink + f'/files/all?page={i}&pageSize={b1.filesPageSize}'
                            #div class you're looking for is called files-table
                            #print(f"URL Being Used: {b1.selectedUrl}")
                            filesTable = get_files_table(b1)

                            newlyCreatedFile = create_cached_data(filesTable, b1)
                            write_cached_data(filesTable, newlyCreatedFile)
                            #print(filesTable)
                            
            #close browser used
            b1.chosenDriver.quit()



                    
        
    


def create_cached_data(websiteData: BeautifulSoup, b1: Bundle) -> str:
    """
    description:
            The purpose of this function is to handle the parent directory, subdirectory and file creation.
            The function will check if the parent (data) directory exists, if not it will create it. Then 
            it will ask if the subdirectory that will contain all scraped html files exists, if not it will create it. Lastly,
            it will ask if the file containing the website data just scraped was created, if not it will create it.

    parameters:

            websiteData (BeautifulSoup): webiste data just scraped from the webpage
            b1(Bundle):
                url (str): website url used to get the websiteData in the parameter above
                currentDirectory (str): absolute path to the current directory where this current code file exists
    
    returns:
            filePath (str): absolute path to the file that was just created
    """
    todaysDate = b1.todaysDate

    #set up cached data folder system 
    parentFolderPath = os.path.join(b1.currentDirectory, b1.parentDataDirectory, b1.outputDataDirectory, b1.rawDataDirectory)

    #Establish name of folder based off website we are scraping
    #Example: takes data from curseforge.com and names it like
    #           https:||www.curseforge.com--dd-mm-yyy
    tld = extract_tld(b1)
    websiteFolderName = b1.previewUrl.replace('/', '|')
    websiteFolderName = websiteFolderName[0:(b1.previewUrl.index(tld) + len(tld))] #this trick grabs the index of the tld in the url
    websiteFolderPath = os.path.join(parentFolderPath, b1.mode, websiteFolderName)
    websiteFolderPath = websiteFolderPath + '--' + str(todaysDate.day) + '-' + str(todaysDate.month) + '-' + str(todaysDate.year)

    #Establish naming system for each file that will be placed inside websiteFolderPath
    #Example: takes webpage https:||www.curseforge.com|minecraft|search?page=1&pageSize=50&sortType=1&class=mc-mods-DATA24-12-2024.html
    # adds -DATA-dd-mm-yyyy at the end of the file
    if b1.mode == 'general':
        fileName = b1.previewUrl.replace('/', '|') + '-DATA' + str(todaysDate.day) + '-' + str(todaysDate.month) + '-' + str(todaysDate.year) + '.html'
        filePath = os.path.join(websiteFolderPath, fileName)
    elif b1.mode == 'detail':
        fileName = b1.selectedUrl.replace('/', '|') + '-DATA' + str(todaysDate.day) + '-' + str(todaysDate.month) + '-' + str(todaysDate.year) + '.html'
        filePath = os.path.join(websiteFolderPath, fileName)


    #
    #Create CachedData repository
    #

    if not os.path.exists((parentFolderPath)):

        os.mkdir(parentFolderPath, exist_ok=True)

    if not os.path.exists(os.path.join(parentFolderPath, b1.mode)):

        os.mkdir(os.path.join(parentFolderPath, b1.mode))

    if not os.path.exists(os.path.join(parentFolderPath, websiteFolderPath)):

        os.mkdir(os.path.join(parentFolderPath, websiteFolderPath))

    if not os.path.exists(filePath):

        with open(filePath, 'w') as file:
            file.write('')
        
    
    return filePath

def write_cached_data(websiteData: BeautifulSoup, newlyCreatedFile: str):
    """
    description:
            This function is responsibe for writing the scraped website data into the newly
            created html file

    parameters:

        websiteData (BeautifulSoup): Data from the webpage we want to write to the file

        newlyCreatedFile (str): the absolute path to the file where we will write the data

    return: 

        None
    """

    if websiteData is None:
        print("No data was captured. Thus the file will be empty")
    else:
        with open(newlyCreatedFile, 'w', encoding='utf-8') as file:
            file.write(websiteData.prettify())
        file.close()

def get_website_data(b1: Bundle) -> BeautifulSoup:
    try:
        b1.chosenDriver.get(b1.previewUrl)
        time.sleep(b1.recommendedDelayInSeconds)
        wait = WebDriverWait(b1.chosenDriver, 10)
        waitForIt = wait.until(EC.presence_of_element_located((By.CLASS_NAME, b1.previewPageClassSelector)))

        # Get the HTML content of the 'results-container' element
        webpage = waitForIt.get_attribute('outerHTML')

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(webpage, features="html.parser")

        return soup
    except Exception as e:
        print(f"An exception occurred: {e}")
    
def extract_tld(b1:Bundle) -> str:
    # Use tldextract to extract the domain components
    extracted_info = tldextract.extract(b1.previewUrl)

    # Construct and return the top-level domain with the leading dot
    tld = f".{extracted_info.suffix}"
    return tld

def get_max_webpages(b1: Bundle) -> int:
    """
    description:
        The purpose of this function is get the highest number of pages from the 
        general section of the website.  This is important because if the 
        modding website ever adds more pages, we won't have to manually adjust the loop
        to go through those pages. it will automatically loop from 1 to the max amount of webpages.

        The max number is determined by setting the page filter to 50 mods per page and finding
        the max number. it generallly looks like 1, 2, 3, 4, ... , 200.

        Needed for general mode

    parameters:
        b1 (Bundle)
            previewUrl (string): string location of the website we want to get the number from
            chosenDriver (webdriver): this is the driver that is responsible for handling the browser
            maxPageNumberClassSelector (str): this contains the class selector that holds the max number of pages

    returns:
        maxWebpages (int): whole number that represents the most amount of pages
                            in the website that contains minecraft mods
    """

    try:

        b1.chosenDriver.get(b1.previewUrl)
        time.sleep(b1.recommendedDelayInSeconds)
        wait = WebDriverWait(b1.chosenDriver, 10)
        #wait until the page numbers we want generate in the website
        waitForIt = wait.until(EC.presence_of_element_located((By.CLASS_NAME, b1.maxPageNumberClassSelector)))

        # Get the HTML content of the 'results-container' element
        webpage = waitForIt.get_attribute('outerHTML')

    except Exception as e:
        print(f"An exception occurred: {e}")

    #parse the webpage as html
    soup = BeautifulSoup(webpage, 'html.parser')

    #find all the buttons because the numbers are href links
    buttons = soup.find_all('button')

    #Extract the numbers as integers out of the html tags of the webpage
    cleanedButtons = []
    
    for index, element in enumerate(buttons):
        
        try: 
            cleanedButtons.append(int(buttons[index].text.strip()))
        
        except:

            continue
        
    return max(cleanedButtons)

def get_max_filepages(b1: Bundle) -> int:
    """
    description:
        The purpose of this function is get the highest number of pages from the 
        individual mod files section of the website.  This is important because if the 
        modding website ever adds more pages, we won't have to manually adjust the loop
        to go through those pages. it will automatically loop from 1 to the max amount of file
        pages.

        The max number is determined by setting the page filter to 50 mods per page and finding
        the max number. it generallly looks like 1, 2, 3 ,4... 10.

        Needed for detail mode

    parameters:
        b1 (Bundle)
            selectedUrl (string): string location of the website we want to get the number from
            chosenDriver (webdriver): this is the driver that is responsible for handling the browser
            maxPageNumberClassSelector (str): this contains the class selector that holds the max number of pages

    returns:
        maxWebpages (int): whole number that represents the most amount of pages
                            in the website that contains minecraft mods
    """

    try:

        b1.chosenDriver.get(b1.selectedUrl)
        time.sleep(b1.recommendedDelayInSeconds)
        
        
    except Exception as e:
        print(f"An exception occurred getting the url: {e}")
        #wait until the page numbers we want generate in the website
    
    seconds = 0
    buttons = []
    attempt = 0
    while attempt <= b1.maxAttempts and not buttons:
        
        
        try:
            time.sleep(seconds)
            wait = WebDriverWait(b1.chosenDriver, 10)
            waitForIt = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.page-numbers button")))

            # Once all buttons are present, extract their text
            buttons = b1.chosenDriver.find_elements(By.CSS_SELECTOR, "ul.page-numbers button")
            seconds = min(seconds + 2, 10)
            attempt = attempt + 1
            if buttons:
                #print(f"buttons: {buttons}")
                break
            


        except Exception as e:
            print(f"Retrying at attempt number {attempt}.\n An exception occurred: {str(e)}")
            seconds = min(seconds + 2, 10)
            attempt = attempt + 1


    #Extract the numbers as integers out of the html tags of the webpage
    cleanedButtons = []
    
    for index, element in enumerate(buttons):
        
        try: 
            cleanedButtons.append(int(buttons[index].text.strip()))
        
        except:

            continue
    
    # Final check before returning
    if not cleanedButtons:
        return None
        
        
    return max(cleanedButtons)

def get_files_table(b1: Bundle) -> BeautifulSoup:
    """
    """
    try:
        b1.chosenDriver.get(b1.selectedUrl)
        wait = WebDriverWait(b1.chosenDriver, 10)
        waitForIt = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'files-table')))
        
        # Wait for all file-row-details elements inside the file-row to be present
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'file-row-details')))

        # Get the HTML content of the 'results-container' element
        webpage = waitForIt.get_attribute('outerHTML')

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(webpage, features="html.parser")

        return soup
    except Exception as e:
        print(f"An exception occurred: {e}")

def get_newest_file(folder: str) -> str:
    """
    """
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    
    if not files:
        
        return None
    
     # Find the file with the most recent creation time
    newestFile = max(files, key=lambda f: os.path.getctime(os.path.join(folder, f)))
    
    return newestFile
    
def get_newest_curseforge_directory(b1: Bundle) -> str:
    """
    """
    # List all folders in the newest directory
    
    folders = [f for f in os.listdir(os.path.join(b1.currentDirectory, b1.parentDataDirectory, b1.outputDataDirectory, b1.rawDataDirectory, b1.mode)) 
                if os.path.isdir(os.path.join(b1.currentDirectory, b1.parentDataDirectory, b1.outputDataDirectory, b1.rawDataDirectory, b1.mode, f))]

    if not folders:
        return None  # Return None if there are no folders
    
    # Function to extract the date from the folder name
    def extract_date(folderName):
        try:
            # Extract date part after '--' and convert it to a datetime object
            dateStr = folderName.split('--')[1]  # Take the part after '--'
            return datetime.datetime.strptime(dateStr, '%d-%m-%Y')  # Convert to datetime object
        except (IndexError, ValueError):
            return None  # Return None if the folder name format is not correct

    # Find the folder with the latest date
    newestFolder = max(folders, key=lambda f: extract_date(f) if extract_date(f) else datetime.datetime.min)
    
    return newestFolder
    
def get_newest_mod_grouping(newestFolder: str, newestFile: str) -> list[str]:
    """
    """
    files = [f for f in os.listdir(newestFolder) if os.path.isfile(os.path.join(newestFolder, f))]
    mod = newestFile.split('mc-mods')[1].split('files')[0]
    
    # List comprehension to find files that contain the desired pattern
    matchingFiles = [
        f for f in files
        if 'mc-mods' in f and 'files' in f and mod in f.split('mc-mods')[1].split('files')[0]
    ]
    
    return matchingFiles
    
    
if __name__ == '__main__':
    scrape(b1)
