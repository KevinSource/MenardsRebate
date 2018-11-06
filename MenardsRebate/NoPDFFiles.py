#! python3
# ********************************************************************************************************
# * reporting there were no PDF files to process
# ********************************************************************************************************

import logging
from tkinter import *


def return_ok():
    global button_choice
    button_choice = "OK"
    master.destroy()
    return button_choice



def nopdffiles(PdfFileSpec):
    # ********************************************************************************************************
    # * Set up logging
    # * To turn on logging, set root_logger.disabled = False
    # * To turn off logging, set root_logger.disabled = True
    # ********************************************************************************************************
    root_logger = logging.getLogger()
    root_logger.disabled = True  # Set to false to see debugging info
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

    logging.debug('Start of NoPDFFiles.py function')

    global button_choice
    global master

    master = Tk()
    master.winfo_toplevel().title("No Files")

    Label(master, text="There were no pdf files found in: " + PdfFileSpec + '\n' +
                       "Make sure you downloaded to the correct folder.",bg="red", fg="white", font='bold').grid(row=0, sticky=W, padx=10)

    i = 1
    Button(master, text='OK', command=return_ok).grid(row=i, sticky=W+E, pady=4, padx=180)
    master.mainloop()
    return button_choice

# data = retryorskip('test.ext')
# logging.debug("Return value from retryorskip: " + data)