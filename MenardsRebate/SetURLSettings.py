#! python3
# ********************************************************************************************************
# * Pops up a dialog to get URL information
# ********************************************************************************************************
import configparser
import inspect
import logging
import sys
import tkinter as tk
from tkinter import *

from GetMenardsSettings import GetUrlsAndPaths

global URLdata_flds
URLdata_flds_changed = False

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

# ********************************************************************************************************
# * This is the main window for changing URL links
# ********************************************************************************************************
class URLSettingsDialog(tk.Frame):

    def __init__(self, parent):
        global URLdata_flds
        global URLDialog
        global ConfigData
        global IniFile
        global WriteDefaultValues
        WriteDefaultValues = False

        # ********************************************************************************************************
        # * Give this window the focus
        # ********************************************************************************************************
        parent.iconify()
        parent.update()
        parent.deiconify()
        URLDialog = parent

        # ********************************************************************************************************
        # * Bind the enter key to the OK button
        # * Bind the escape key to the Cancel button
        # ********************************************************************************************************
        parent.bind('<Return>', self.URLreturn_ok)
        parent.bind('<Escape>', self.URLreturn_cancel)

        g_row = 0
        g_col = 0
        ent_frame = Frame(URLDialog, height=200, width=500, bd=1) # relief=SUNKEN)
        ent_frame.grid(row=g_row, column=g_col, sticky=W, padx=50)

        # ********************************************************************************************************
        # * Insert the data entry fields
        # ********************************************************************************************************
        self.URL_data = tk.Entry(ent_frame)
        i = 0
        entry_fld_row_start = g_row
        entry_fld_col_start = g_col
        g_col = 1
        g_row += 1
        URLdata_flds = []
        data_labels = []

        # ********************************************************************************************************
        # * Get the URL links from the .ini file
        # ********************************************************************************************************
        ConfigData, WriteDefaultValues, IniFile = GetUrlsAndPaths()
        RebateHeaderUrl = ConfigData['Header']
        RebatePDFUrl = ConfigData['Rebates']

        pady = 5
        fld = 0
        w=(Label(ent_frame,text='Header URL'))
        w.grid(row=g_row, column=g_col, sticky=W, padx=5, pady=pady)
        URLdata_flds.append(Entry(ent_frame, width=80))
        g_row += 1
        URLdata_flds[fld].bind("<Key>", self.EntryFld_KeyPressEvent)  # shorthand for <ButtonPress-1>
        URLdata_flds[fld].insert(fld,RebateHeaderUrl)
        URLdata_flds[fld].grid(row=g_row, column=g_col , sticky=W, padx=5, pady=pady)
        g_row += 1

        fld = 1
        w1=(Label(ent_frame,text='PDF URL'))
        w1.grid(row=g_row, column=g_col, sticky=W, padx=5, pady=pady)
        URLdata_flds.append(Entry(ent_frame, width=80))
        g_row += 1
        URLdata_flds[fld].bind("<Key>", self.EntryFld_KeyPressEvent)  # shorthand for <ButtonPress-1>
        URLdata_flds[fld].insert(fld, RebatePDFUrl)
        URLdata_flds[fld].grid(row=g_row, column=g_col , sticky=W, padx=5, pady=pady)
        g_row += 1

        g_col = 0
        ButtonFrame = Frame(URLDialog, height=30, width=500, bd=1) # relief=SUNKEN)
        ButtonFrame.grid(row=g_row, column=g_col, sticky=W, padx=50)

        i = g_row + 2
        self.ok_button = Button(ButtonFrame, text='OK',width=10, command=self.URLreturn_ok)
        self.ok_button.grid(row=i, column=1, sticky=E, pady=4, padx=20)
        Button(ButtonFrame, text='Cancel',width=10, command=self.URLreturn_cancel).grid(row=i, column=3, sticky=W + E, pady=4, padx=15)

    # ********************************************************************************************************
    # * Destroy the dialog. Call the routine to update the data.
    # ********************************************************************************************************
    @staticmethod
    def URLreturn_ok(event=None):
        # ********************************************************************************************************
        # * Need event=None because clicking the button does not send a parm, but return key does
        # ********************************************************************************************************
        global ConfigData
        global IniFile

        logging.debug('URLreturn_ok: Button Click')

        URLwrite_data_if_needed('URLreturn_ok', ConfigData, URLdata_flds)
        URLDialog.destroy()

    def URLreturn_cancel(self, event=None):
        # ********************************************************************************************************
        # * Need event=None because clicking the button does not send a parm, but escape key does
        # ********************************************************************************************************
        logging.debug('URLreturn_cancel: Button Click')

        URLDialog.destroy()

    # ********************************************************************************************************
    # * This triggers if anything changes in the data fields. It sets a flag and updates the OK button text
    # ********************************************************************************************************
    def EntryFld_KeyPressEvent(self,event):
        global URLdata_flds_changed
        global ok_button
        logging.debug('EntryFld_KeyPressEvent: Entry Field Changed')
        URLdata_flds_changed = True
        self.ok_button["text"] = "Update"

# ********************************************************************************************************
# * Write the configuration data if anything changed
# ********************************************************************************************************
def URLwrite_data_if_needed(called_from, ConfigData, URLdata_flds):
    global WriteDefaultValues
    global IniFile

    logging.debug('write_data_if_needed: ' + called_from)

    Chg_log = ''
    if URLdata_flds_changed is True:
        config = configparser.ConfigParser()
        config.sections()
        config.read(IniFile)

        i = 0
        for key in ConfigData:
            if ConfigData[key] == URLdata_flds[i].get():
                pass
            else:
                Chg_log = Chg_log + 'Before: ' + key + '=' + ConfigData[key] + ' After: ' + URLdata_flds[i].get() + '//n'
                logging.debug('Change Log: ' + Chg_log)
                config.set('URLs',key,URLdata_flds[i].get())
            i += 1

    if WriteDefaultValues is True:# Writing our configuration file
        config = configparser.ConfigParser()
        config.add_section('URLs')
        i = 0
        for key in ConfigData:
            Chg_log = Chg_log + 'Before: ' + key + '=' + "No Value" + ' After: ' + URLdata_flds[i].get() + '//n'
            logging.debug('Change Log: ' + Chg_log)
            config.set('URLs',key,URLdata_flds[i].get())
            i += 1


    if URLdata_flds_changed is True or WriteDefaultValues is True:# Writing our configuration file
        with open(IniFile, 'w') as configfile:
            config.write(configfile)

def URLUpdateSettings():
    if root_logger.disabled == False:
        logging.debug("About to  instantiate dialog box for: SetURLSettings")

    URLSettings_root = tk.Tk()
    URLs_diag = URLSettingsDialog(URLSettings_root)
    URLSettings_root.title("URL Link Settings")
    URLSettings_root.mainloop()


if __name__ == '__main__':

    if root_logger.disabled == False:
        logging.debug("About to  instantiate dialog box for: SetURLSettings")

    URLSettings_root = tk.Tk()
    dialog = URLSettingsDialog(URLSettings_root)
    URLs_diag = dialog
    URLSettings_root.title("URL Link Settings")
    URLSettings_root.mainloop()
