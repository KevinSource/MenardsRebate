#! python3
# ********************************************************************************************************
# * Pops up a dialog to get information
# ********************************************************************************************************

import logging
import inspect
from tkinter import messagebox


def return_retry():
    button_choice = "Retry"
    return button_choice

def return_skip():
    button_choice = "Skip"
    return button_choice

def retryorskip(target_file_nm):
    # ********************************************************************************************************
    # * Set up logging
    # * To turn on logging, set root_logger.disabled = False
    # * To turn off logging, set root_logger.disabled = True
    # ********************************************************************************************************
    root_logger = logging.getLogger()
    root_logger.disabled = True  # Set to false to see debugging info
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

    if root_logger.disabled == False:
        file_name = inspect.stack()[0][3]  # This is slow, so only run it when logging
        called_from = lambda n=1: sys._getframe(n + 1).f_code.co_name
        logging.debug('Start of ' + file_name + ' function' + " Called from: " + called_from.__module__)

    TF = ( messagebox.askretrycancel("Rename Error", "Need to rename " + target_file_nm + '\n' +
                       "File my be in use. Retry?"))
    if TF:
        return return_retry()
    else:
        return return_skip()

# ********************************************************************************************************
# * test stuff
# ********************************************************************************************************

if __name__ == "__main__":
    data = retryorskip('test.ext')
    logging.debug("Return value from retryorskip: " + data)