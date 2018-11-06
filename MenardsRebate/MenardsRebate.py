#! python3
# ********************************************************************************************************
# * Input through command line: None
# *
# * It will prompt the user for some input
# * It will populate the rebate form(s) found in the directory stored in file: MenardsPDFInPath.txt
# * It will open the rebate form
# *
# ********************************************************************************************************

from pdfFill import pdf_fill
import glob
import GetDataFromUser
from GetMenardsSettings import GetUrlsAndPaths
from GetDownloadPath import get_download_path
import RetrySkip
import NoPDFFiles
import os
import logging, sys
from typing import Union
from selenium import webdriver
import findfqpath
from subprocess import Popen,PIPE
from fake_useragent import UserAgent
import requests
from tkinter import messagebox
import inspect
logging.getLogger("urllib3").setLevel(logging.WARNING)

root_logger = logging.getLogger()
root_logger.disabled = True # Set to false to see debugging info
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

logging.debug('Start of Menards Rebate Program')
if root_logger.disabled == False:
    file_name = inspect.stack()[0][3]  # This is slow, so only run it when logging
    called_from = lambda n=1: sys._getframe(n + 1).f_code.co_name
    logging.debug('Start of ' + file_name + ' function' + " Called from: " + called_from.__module__)

options = webdriver.ChromeOptions()
options.binary_location = findfqpath.find_fq_path(find_file='opera.exe', num_days_valid=1)

#rebateList = [4468, 4478, 4488]

#********************************************************************************************************
#* Get the url for the Menards Rebate Form - Leaving this, maybe someday it can all be driven from here
#* Menards uses incapsula, so which protects against automation
#********************************************************************************************************
currWorkingDirPath = os.getcwd()
logging.debug('Current Working Directory:' + currWorkingDirPath)

IniPath: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
IniFile = IniPath + r'\MenardsSettings.ini'
logging.debug('Ini Path and File:' + IniFile)

ConfigData, WriteDefaultValues, IniFile = GetUrlsAndPaths()

RebateHeaderUrl = ConfigData['Header']
logging.debug('RebateUrl:' + RebateHeaderUrl)
RebatePDFUrl= ConfigData['Rebates']
logging.debug('RebatePDFUrl:' + RebatePDFUrl)

RebatePdfInPath = get_download_path()
RebatePdfPath = os.path.join(RebatePdfInPath,'Menards')
if not os.path.exists(RebatePdfPath):
    try:
        os.mkdir(RebatePdfPath)
    except:
        logging.debug('mkdir failed')
        messagebox.showerror("Error", "Unable to create 'Menards' folder under 'Download' path. Program terminating. "
                                      "No action taken.")
        sys.exit()
logging.debug('Rebate Pdf Path:' + RebatePdfPath)

# ********************************************************************************************************
# * Download the rebate form page - Maybe someday
# * User-Agent dict key it tells the website "hey i am not a robot I
# * am a person and i'm using this version of browser
# ********************************************************************************************************

user_input_data = []
user_input_data = GetDataFromUser.getUserInput()
if len(user_input_data) == 0:
    sys.exit()

rebate_users = []
rebateList = []
for i in range(len(user_input_data)):
    if user_input_data[i][0] == 'R#':
        rebateList.append(user_input_data[i][1])
    else:
        rebate_users.append(user_input_data[i][1])

# eventually you may need to update the value on the User-Agent dict key it tells the website "hey i am not a robot i
# am a person and i'm using this version of firefox
ua = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3'
ua = UserAgent(fallback='opera').opera
header = {'User-Agent': ua,
          'Referer': RebateHeaderUrl}

# * Clear out any pdf file in the target directory
files = glob.glob(RebatePdfPath + "\\*.pdf")
for f in files:
    try:
        os.remove(f)
    except OSError:
        pass

# get the rebates and save them to the writePath directory
for i in rebateList:
    logging.debug('Opening page %s...' % RebatePDFUrl + str(i) + '.pdf')
    pdf_url_try = RebatePDFUrl + str(i) + '.pdf'
    try:
        r = requests.get(pdf_url_try, headers=header)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        err = str(e)
        messagebox.showerror("Web Error", " URL: " + pdf_url_try + err + "\n\n" +
                                "Try the URL in a browser, the URL may be down.")
        sys.exit(1000)
    output_rebate_file = os.path.join(RebatePdfPath,str(i) + '.pdf')
    try:
        os.remove(output_rebate_file)
    except OSError:
        pass
#    with open(RebatePdfPath + '\\Rebate' + str(i) + '_' + today + '.pdf', 'wb') as f:
    with open(output_rebate_file, 'wb') as f:
        f.write(r.content)

PdfFileSpec = RebatePdfPath + r'\*.pdf'
RebatePdfFiles = glob.glob(PdfFileSpec)
if len(RebatePdfFiles) == 0:
    NoPDFFiles.nopdffiles(PdfFileSpec)
    sys.exit()

AdobefqPath = findfqpath.find_fq_path('AcroRd32.exe', 1)
for pdf_in_cnt in range(len(RebatePdfFiles)):
    for i in range(len(rebate_users)):
        RebatePdfFileIn = RebatePdfFiles[pdf_in_cnt]
        pdfFileOut = pdf_fill(user_input_data[i][1],RebatePdfFileIn)
        pdf_path_nm, pdf_file_nm = os.path.split(pdfFileOut)
        pdf_file_root_nm, pdf_file_ext_nm = os.path.splitext(pdf_file_nm)
        new_pdf_file_out = os.path.join(pdf_path_nm,pdf_file_root_nm + str(i)+pdf_file_ext_nm)
        rename_choice = "Retry"
        while rename_choice == "Retry":
            try:
                os.replace(pdfFileOut,new_pdf_file_out)  # Better than os.rename.
                break
            except PermissionError:
                rename_choice = RetrySkip.retryorskip(new_pdf_file_out)
        if rename_choice == "Retry":
            proc = Popen([AdobefqPath, new_pdf_file_out])  #os.startfile waits for the started program to quit
            logging.debug('Rebate File Out:' + new_pdf_file_out)
        else:
            logging.debug('Rebate File Out not renamed to: ' + new_pdf_file_out)

#os.startfile(pdfFileOut, "print")
#os.startfile(pdfFileOut, "open")

logging.debug('Done.')
