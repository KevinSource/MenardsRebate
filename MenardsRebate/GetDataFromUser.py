#! python3
# ********************************************************************************************************
# * Pops up a dialog to get information
# ********************************************************************************************************

import os
import inspect
import logging
from typing import Union
from tkinter import *
from SetMenardsSettings import *
from SetURLSettings import *
from tkinter import messagebox


def return_ok(event=None):
    # ********************************************************************************************************
    # * Need event=None because clicking the button does not send a parm, but return key does
    # ********************************************************************************************************
    global user_entered_data
    user_entered_data = []
    for i in range(len(Checkbox_Choices)):
        if CheckBoxResult[i].get() > 0:
            user_entered_data.append((CheckBoxResult[i].get(),Checkbox_Choices[i][1]))
    for i in range(len(rebate)):
        if rebate[i].get().strip() > '':
            user_entered_data.append(("R#", rebate[i].get()))
    master.destroy()
    return user_entered_data

def return_cancel(event=None):
    # ********************************************************************************************************
    # * Need event=None because clicking the button does not send a parm, but escape key does
    # ********************************************************************************************************

    global user_entered_data
    user_entered_data = []
    master.destroy()
    return user_entered_data

def NumValidation(S):
    if S in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        return True
    master.bell() # .bell() plays that ding sound telling you there was invalid input
    return False


# noinspection PyProtectedMember
def getUserInput():
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

    global Checkbox_Choices
    global master
    global CheckBoxResult
    global rebate
    master = Tk()
    master.winfo_toplevel().title("Rebate Selection")

    # ********************************************************************************************************
    # * Bind the enter key to the OK button
    # * Bind the escape key to the Cancel button
    # ********************************************************************************************************
    master.bind('<Return>', return_ok)
    master.bind('<Escape>', return_cancel)

    vcmd = (master.register(NumValidation), '%S')


    CheckboxPath: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
    CheckboxPath = CheckboxPath + r'\MenardsCheckBoxOptions.txt'
    logging.debug('Checkbox Path and File:' + CheckboxPath)

#    with open(CheckboxPath) as f:
#        Checkbox_Choices = [tuple(i.strip().split(',')) for i in f]
    if os.path.exists(CheckboxPath):
        with open(CheckboxPath) as f:
            Checkbox_Choices = [tuple(i.strip().split(',')) for i in f]
    else:
        Checkbox_Choices = [("NoData","NoData")]

    row_y = 0
    row_y += 1

    master.winfo_toplevel().title("Rebate Selection")
    # create a toplevel menu
    menubar = Menu(master)
    Settingsbar = Menu(menubar, tearoff=0)
    Settingsbar.add_command(label="User Configuration Settings", command=menards_rebate_settings)
    Settingsbar.add_command(label="URL Settings", command=menards_URL_settings)
    menubar.add_cascade(label="Settings", menu=Settingsbar)
    master.config(menu=menubar)
    if Checkbox_Choices[0][0] == "NoData":
        i = row_y + 2
        messagebox.showinfo("Establish Rebate User Information", "There is no rebate user information. Rebate User Information " +
            "for multiple users may be set up. Each unique set of user data is given a 'configuration name'. Click 'Settings' on the dialog to get started.")
    else:
        row_y += 1; col_x = 0
        Label(master, text="Enter Rebate Numbers").grid(row=row_y, column=1, columnspan=4)

        row_y += 1; col_x = 0
        rebate = []
        for i in range(6):
            if i%2 == 0:
                row_y += 1
                col_x = i%2
            else:
                col_x = 2
            Label(master, text=str(i+1)).grid(row=row_y,column=col_x,sticky=E)
            rebate.append(Entry(master, validate='key', vcmd=vcmd)); rebate[i].grid(row=row_y, column=col_x+1, sticky=W, padx=5)


        CheckBoxResult = []
        for i in range(row_y,len(Checkbox_Choices)+row_y):
            CheckBoxResult.append(IntVar())
            Checkbutton(master, text=Checkbox_Choices[i-row_y][0], variable=CheckBoxResult[i-row_y]).grid(row=i+1, column=1, sticky=W, padx=10)
        i += 2

    Button(master, text='OK', command=return_ok).grid(row=i, column=1, sticky=W+E, pady=4, padx=20)
    # i += 1
    Button(master, text='Cancel', command=return_cancel).grid(row=i, column=3, sticky=W+E, pady=4, padx=20)

    # ********************************************************************************************************
    # * Give this window the focus
    # ********************************************************************************************************
    master.iconify()
    master.update()
    master.deiconify()
    if Checkbox_Choices[0][0] == "NoData":
        pass
    else:
        rebate[0].focus()

    master.mainloop()
    return user_entered_data

def menards_rebate_settings():

    logging.debug("About to  instantiate dialog box for Menards Settings: " )

#    master.withdraw()
    master.destroy()
    UpdateSettings()
    getUserInput()

def menards_URL_settings():

    logging.debug("About to  instantiate dialog box for Menards Settings: " )

#    master.withdraw()
    master.destroy()
    URLUpdateSettings()
    getUserInput()


#    master.deiconify()

if __name__ == '__main__':
    data = getUserInput()