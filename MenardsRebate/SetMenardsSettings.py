#! python3
# ********************************************************************************************************
# * Pops up a dialog to get rebate user information
# ********************************************************************************************************
import inspect
import logging
import os
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from typing import Union

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
# * This is the main window for changing rebate user information
# ********************************************************************************************************
class SettingsDialog(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        global SelVar
        global data_flds
        global data_labels
        global ent_frame
        global entry_fld_row_start
        global entry_fld_col_start
        global listbox_choices
        global g_row, g_col
        global data_flds_changed
        global label_flds_changed
        global user_selected_index

        data_flds_changed = False
        label_flds_changed = False

        # ********************************************************************************************************
        # * Give this window the focus
        # ********************************************************************************************************
        parent.iconify()
        parent.update()
        parent.deiconify()

        # ********************************************************************************************************
        # * Bind the enter key to the OK button
        # * Bind the escape key to the Cancel button
        # ********************************************************************************************************
        parent.bind('<Return>', self.return_ok)
        parent.bind('<Escape>', self.return_cancel)


        g_row = 0
        g_col = 0
        lb_frame = Frame(parent, height=300, width=300, bd=1, relief=SUNKEN)
        lb_frame.grid(row=g_row,column=g_col, sticky=W, padx=5, pady=15)

        # ********************************************************************************************************
        # * Pull the name out of the name, dsn tuple and put them in a list
        # ********************************************************************************************************
        listbox_choices = []
        for i in user_data_list:
            listbox_choices.append(i[0])

        # ********************************************************************************************************
        # * Load the list of rebate user names in the combobox
        # ********************************************************************************************************
        g_row += 1
        user_selected_index = 0
        SelVar = StringVar()
        self.cfg_list = ttk.Combobox(lb_frame, textvariable=SelVar)
        self.cfg_list.bind("<<ComboboxSelected>>", self.Combobox_SelectEvent)
        self.cfg_list['values'] = listbox_choices
        self.cfg_list.current(0)
        user_selected_index = 0
        self.cfg_list.grid(row=g_row, column=g_col)

        # ********************************************************************************************************
        # * Put a frame around the combobox
        # ********************************************************************************************************
        Label(lb_frame, text="Choose a configuration").grid(row=g_row, column=g_col)
        g_row += 1
        self.cfg_list.grid(row=g_row, column=g_col)
        SelVar.set(user_data_list[0][0])

        # ********************************************************************************************************
        # * Paint an "Add" button on the dialog
        # ********************************************************************************************************
        Button(parent, text='New Configuration', command=self.add_configuration_dialog).grid(row=g_row-2, column=1, sticky=W + E, pady=4, padx=10)

        # ********************************************************************************************************
        # * Paint an "Delete" button on the dialog
        # ********************************************************************************************************
        Button(parent, text='Delete', command=self.delete_configuration_dialog).grid(row=g_row, column=1, sticky=W + E, pady=0, padx=10)

        ent_frame = Frame(parent, height=200, width=300, bd=1, relief=SUNKEN)
        ent_frame.grid(row=g_row, column=g_col, sticky=W, padx=5)

        # ********************************************************************************************************
        # * Insert the data entry fields
        # ********************************************************************************************************
        self.usr_data = tk.Entry(ent_frame)
        i = 0
        entry_fld_row_start = g_row
        entry_fld_col_start = g_col
        g_col = 1
        g_row += 1
        data_labels = []
        data_flds = []
        self.load_entry_flds(rebate_user_data[i],entry_fld_row_start,entry_fld_col_start)

        # ********************************************************************************************************
        # * Put a separator line. Not sure this actually does anything.
        # ********************************************************************************************************
        g_row += 1
        rowspan = 4
        separator1 = ttk.Separator(self)
        separator1.grid(row=g_row, column=g_col, padx=5, pady=5, columnspan=4, rowspan=rowspan, sticky="EW")

        # ********************************************************************************************************
        # * Paint an "Delete" button on the dialog
        # ********************************************************************************************************
        g_row += 2
        self.ok_button = Button(parent, text='OK', command=self.return_ok)
        self.ok_button.grid(row=g_row, column=0, sticky=W + E, pady=4, padx=100)
        self.return_button = Button(parent, text='Cancel', command=self.return_cancel)
        self.return_button.grid(row=g_row, column=1, sticky=W + E, pady=4, padx=20)

        if len(rebate_user_data) == 1:
            if listbox_choices[0] == "NoData":
                self.add_configuration_dialog()

    # ********************************************************************************************************
    # * This initiates the add configuration dialog for a configuration
    # ********************************************************************************************************
    def add_configuration_dialog(self):

        Child = tk.Toplevel()
        Child.title("Add Config")
        entries_before_add = len(listbox_choices)
        re_load_combobox = False
        if listbox_choices[0] == "NoData":
            re_load_combobox = True
        new_dialog = add_config_class(Child)
        new_dialog.wait_window(new_dialog)  # Step 1 of 2 to make the popup application modal (2: get_name.grab_set())
        logging.debug('Statement after wait_window: Success!')

        entries_after_add = len(listbox_choices)
        if entries_after_add > entries_before_add or re_load_combobox is True:
            self.cfg_list['values'] = listbox_choices
            SelVar.set(new_name)
            user_selected_index = listbox_choices.index(new_name)
            self.cfg_list.current(user_selected_index)


    # ********************************************************************************************************
    # * This handles the deletion of a configuration
    # ********************************************************************************************************
    def delete_configuration_dialog(self):
        global listbox_choices
        global cfg_list
        global user_selected_index

        delete_it = messagebox.askokcancel("Delete Confirmation",
                                "Press OK to delete: " + listbox_choices[user_selected_index])
        if delete_it == True:
            logging.debug('delete_configuration_dialog: Button Click')
            email_index = self.get_email_index()
            email = rebate_user_data[user_selected_index][email_index][1]  # Need to delete the file
            # ********************************************************************************************************
            # * Delete the original user data
            # ********************************************************************************************************
            script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
            rebate_data_fields_and_values_file = os.path.join(script_path, email) + '.txt'
            logging.debug('Original Output File Name: ' + rebate_data_fields_and_values_file)
            try:
                os.remove(rebate_data_fields_and_values_file)
            except OSError:
                pass

            del listbox_choices[user_selected_index]
            del user_data_list[user_selected_index]

            self.cfg_list['values'] = listbox_choices

            SelVar.set(user_data_list[0][0])
            user_selected_index = 0
            self.cfg_list.current(0)
            self.load_entry_flds(rebate_user_data[user_selected_index], entry_fld_row_start, entry_fld_col_start)

            checkbox_write_rc = self.write_checkbox_choices(user_data_list)

    # ********************************************************************************************************
    # * Writes the file that contains teh checkbox information
    # ********************************************************************************************************
    def write_checkbox_choices(self,Checkbox_Choices):
        CheckboxPath: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
        CheckboxPath = CheckboxPath + r'\MenardsCheckBoxOptions.txt'
        logging.debug('Checkbox Path and File:' + CheckboxPath)

        f = open(CheckboxPath, "w")
        for t in Checkbox_Choices:
            output_line = ','.join(str(x) for x in t)
            f.write(output_line + '\n')
        f.close()

        return 0

    # ********************************************************************************************************
    # * Destroy the dialog. Call the routine to update the data.
    # ********************************************************************************************************
    def return_ok(self,event=None):
        # ********************************************************************************************************
        # * Need event=None because clicking the button does not send a parm, but return key does
        # ********************************************************************************************************
        logging.debug('return_ok: Button Click')

        self.write_data_if_needed('return_ok')
        self.master.destroy()

    # ********************************************************************************************************
    # * Write the configuration data if anything changed
    # ********************************************************************************************************
    def write_data_if_needed(self, called_from):
        global user_data_list

        logging.debug('write_data_if_needed: ' + called_from)

        Chg_log = ''
        if label_flds_changed is True:
            for i in range(len(rebate_user_data[user_selected_index])):
                if rebate_user_data[user_selected_index][i][0] == data_labels[i].get():
                    pass
                else:
                    Chg_log = Chg_log + 'Before: ' + rebate_user_data[user_selected_index][i][0] + ' After: ' + data_labels[
                        i].get() + '//n'
                    logging.debug('Change Log: ' + Chg_log)

        if data_flds_changed is True:
            for i in range(len(rebate_user_data[user_selected_index])):
                if rebate_user_data[user_selected_index][i][1] == data_flds[i].get():
                    pass
                else:
                    Chg_log = Chg_log + 'Before: ' + rebate_user_data[user_selected_index][i][1] + ' After: ' + data_flds[
                        i].get() + '//n'
                    logging.debug('Change Log: ' + Chg_log)

        if (data_flds_changed is True) or (label_flds_changed is True):
            email_index = self.get_email_index()

            if email_index == -1:
                return

            old_email = rebate_user_data[user_selected_index][email_index][
                1]  # Need to delete the file incase the email changed
            # ********************************************************************************************************
            # * Put the user data in the original array
            # ********************************************************************************************************
            logging.debug('rebate_user_data before: %s', list(rebate_user_data))
            for i in range(len(rebate_user_data[user_selected_index])):
                rebate_user_data[user_selected_index][i] = (data_labels[i].get(), data_flds[i].get())

            logging.debug('rebate_user_data after: %s', list(rebate_user_data))

            # ********************************************************************************************************
            # * Delete the original user data
            # ********************************************************************************************************
            email = old_email
            script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
            rebate_data_fields_and_values_file = os.path.join(script_path, email) + '.txt'
            logging.debug('Original Output File Name: ' + rebate_data_fields_and_values_file)
            try:
                os.remove(rebate_data_fields_and_values_file)
            except OSError:
                pass

            # ********************************************************************************************************
            # * Write the new data for this user
            # ********************************************************************************************************
            email = data_flds[email_index].get()
            script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
            rebate_data_fields_and_values_file = os.path.join(script_path, email) + '.txt'
            logging.debug('Output File Name: ' + rebate_data_fields_and_values_file)

            with open(rebate_data_fields_and_values_file, 'w') as f:
                for tuple in rebate_user_data[user_selected_index]:
                    f.write('%s,%s\n' % tuple)

            current_name = user_data_list[user_selected_index][0]
            del user_data_list[user_selected_index]
            t = (current_name, email)
            if len(user_data_list) == 0:
                user_data_list = []
            elif user_data_list[0][0] == "NoData":
                user_data_list = []
            user_data_list.append(t)



            checkbox_write_rc = self.write_checkbox_choices(user_data_list)


    # ********************************************************************************************************
    # * Find the email address in the currently selected user configuration data
    # ********************************************************************************************************
    def get_email_index(self):
        email_index = -1
        for i in range(len(rebate_user_data[user_selected_index])):
            if data_labels[i].get().upper() == ('EMAIL'):
                email_index = i
                logging.debug('Email index: ' + str(i))
                break

        if email_index == -1:
            logging.debug('Failed to find "Email" label.')
            messagebox.showerror("Error",
                                 'One of the label fields must be "Email". ')
        return email_index

    # ********************************************************************************************************
    # * Done. Leave
    # ********************************************************************************************************
    def return_cancel(self, event=None):
        # ********************************************************************************************************
        # * Need event=None because clicking the button does not send a parm, but escape key does
        # ********************************************************************************************************

        logging.debug('return_cancel: Button Click')
        self.master.destroy()

    # ********************************************************************************************************
    # * Something was clicked in the combobox. Figure out what to do
    # ********************************************************************************************************
    def Combobox_SelectEvent(self,click):
        global user_selected_index
        self.write_data_if_needed('Combobox_SelectEvent')
        user_selected = SelVar.get()
        logging.debug('Combobox_SelectEvent: User Selected: ' + user_selected)
        if user_selected  == '':
            pass
        else:
            user_selected_index = listbox_choices.index(user_selected)
            self.load_entry_flds(rebate_user_data[user_selected_index],entry_fld_row_start,entry_fld_col_start)

    # ********************************************************************************************************
    # * This triggers if anything changes in the data fields. It sets a flag and updates the OK button text
    # ********************************************************************************************************
    def EntryFld_KeyPressEvent(self,event):
        global data_flds_changed
        global ok_button
        logging.debug('EntryFld_KeyPressEvent: Entry Field Changed')
        data_flds_changed = True
        self.ok_button["text"] = "Update"

    # ********************************************************************************************************
    # * This triggers if anything changes in the label fields. It sets a flag and updates the OK button text
    # ********************************************************************************************************
    def LabelFld_KeyPressEvent(self,event):
        global label_flds_changed
        logging.debug('EntryFld_KeyPressEvent: Label Field Changed')
        label_flds_changed = True
        self.ok_button["text"] = "Update"

    # ********************************************************************************************************
    # * This loads the dta and label fields from the selected user data
    # ********************************************************************************************************
    def load_entry_flds(self,rebate_user_data,entry_fld_row_start,entry_fld_col_start):
        g_row = entry_fld_row_start
        g_col = entry_fld_col_start
        pady = 2
        fld = -1

        fld += 1
        for i in range(len(rebate_user_data)):
            if len(data_labels) == len(rebate_user_data):
                data_labels[fld].delete(0,END)
                data_labels[fld].insert(i, rebate_user_data[i][0])
                data_labels[fld].grid(row=g_row, column=g_col, sticky=W, padx=5, pady=pady)

                data_flds[fld].delete(0, END)
                data_flds[fld].insert(i, rebate_user_data[i][1])
                data_flds[fld].grid(row=g_row, column=g_col + 1, sticky=W, padx=5, pady=pady)
            else :
                data_labels.append(Entry(ent_frame))
                v_name = "data_flds" + str(fld)
                data_flds.append(Entry(ent_frame))
                data_labels[fld].insert(i, rebate_user_data[i][0])
                data_labels[fld].grid(row=g_row, column=g_col, sticky=W, padx=5, pady=pady)
                data_labels[fld].bind("<Key>", self.LabelFld_KeyPressEvent)  #  shorthand for <ButtonPress-1>
                data_labels[fld].config(state='disabled')  # or data_labels[fld]['state'] = 'disabled'

                data_flds[fld].bind("<Key>", self.EntryFld_KeyPressEvent)  #  shorthand for <ButtonPress-1>
                data_flds[fld].insert(i, rebate_user_data[i][1])
                data_flds[fld].grid(row=g_row, column=g_col + 1, sticky=W, padx=5, pady=pady)

            g_row += 1
            fld += 1
            logging.debug('Length of data_labels: ' + str(len(data_labels)))
            logging.debug('Length of rebate_user_data: ' + str(len(rebate_user_data)))


# ********************************************************************************************************
# * Reads all the configuration files and loads them into a list
# ********************************************************************************************************
def read_user_info():
    global user_data_list
    global rebate_user_data
    global default_user_data
    global CheckboxPath
    global rebate_data_fields_and_values_file

    # ********************************************************************************************************
    # * This figures out where the script is stored
    # ********************************************************************************************************
    script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
    logging.debug('Script Directory:' + script_path)

    CheckboxPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    CheckboxPath = CheckboxPath + r'\MenardsCheckBoxOptions.txt'
    logging.debug('Checkbox Path and File:' + CheckboxPath)

    if os.path.exists(CheckboxPath):
        with open(CheckboxPath) as f:
            user_data_list = [tuple(i.strip().split(',')) for i in f]
    else:
        user_data_list = [("NoData","NoData")]

        # ********************************************************************************************************
    # * Read in the pdf field names and values
    # * rebate_user_data[x]: list of tuples for the data
    # * rebate_user_data[x][y]: tuple in the list
    # * rebate_user_data[x][y][z]: field name or value in the tuple
    # ********************************************************************************************************
    rebate_user_data = []
    default_user_data = [("First Name", "FN"), ("last Name", "LN"), ("Address", "street addr"),
                         ("City", "some city"), ("State", "ST"), ("Zipcode", "12345"), ("Email", "email@xyz.com")]
    for i in range(len(user_data_list)):
        email = user_data_list[i][1]
        rebate_data_fields_and_values_file = os.path.join(script_path, email) + '.txt'

        try:
            with open(rebate_data_fields_and_values_file) as f:
                all_fields = [tuple(j.strip().split(',')) for j in f]
        except:
            all_fields = default_user_data

        rebate_user_data.append(all_fields)
        logging.debug(
            'rebate_user_data[' + str(i) + '][0][0]: ' + rebate_user_data[i][0][0] + ' rebate_user_data[' + str(
                i) + '][0][1]: ' + rebate_user_data[i][0][1])
        logging.debug(
            'rebate_user_data[' + str(i) + '][1][0]: ' + rebate_user_data[i][1][0] + ' rebate_user_data[' + str(
                i) + '][1][1]: ' + rebate_user_data[i][1][1])


# ********************************************************************************************************
# * This is the class for the add configuration dialog
# ********************************************************************************************************
class add_config_class(tk.Frame):
#    def add_config/uration(self, parent):
    def __init__(self,parent):
        tk.Frame.__init__(self, parent)
        logging.debug('add_configuration: Button Click')
        from tkinter.ttk import Style

        # ********************************************************************************************************
        # * Set up the dialog window
        # ********************************************************************************************************
        global get_name
        global name_in

        get_name = parent

        # ********************************************************************************************************
        # * Make the child window appplication modal
        # ********************************************************************************************************
        get_name.grab_set()  # Step 2 of 2 to make the popup application modal (1:root.wait_window(new_dialog.top))

        # ********************************************************************************************************
        # * Give this window the focus
        # ********************************************************************************************************
        get_name.iconify()
        get_name.update()
        get_name.deiconify()

        # ********************************************************************************************************
        # * Bind the enter key to the OK button
        # * Bind the escape key to the Cancel button
        # ********************************************************************************************************
        get_name.bind('<Return>', self.get_name_ok)
        get_name.bind('<Escape>', self.get_name_cancel)


        get_name.wm_title("Add Configuration")
        get_name.style = Style()
        get_name.style.theme_use("default")

        # ********************************************************************************************************
        # * Put the label and entry field in a frame
        # ********************************************************************************************************
        frame = Frame(get_name, relief=RAISED, borderwidth=2)
        frame.pack(fill=BOTH, expand=True)
        lbl = tk.Label(frame, text="Configuration Name")
        lbl.pack(side="top", fill="both", expand=True, padx=100, pady=10)

        name_in = (Entry(frame))
        name_in.pack(side="top", fill="both", expand=True, padx=50, pady=10)

        # ********************************************************************************************************
        # * Put the OK and Cancel buttons in a frame in a frame
        # ********************************************************************************************************
        button_frame = Frame(get_name, borderwidth=2)
        button_frame.pack(fill=BOTH, expand=True, pady=5)
        ok_button = Button(button_frame, text='   OK   ', command=self.get_name_ok)
        cancel_button = Button(button_frame, text='Cancel', command=self.get_name_cancel)
        ok_button.pack(side=LEFT, fill=Y, padx=15,)
        cancel_button.pack( side=RIGHT, fill=BOTH, expand=True, padx=90)
        name_in.focus()


    def get_name_ok(self,event=None):
        # ********************************************************************************************************
        # * Need event=None because clicking the button does not send a parm, but return key does
        # ********************************************************************************************************

        global new_name
        global cfg_list
        global listbox_choices
        global user_data_list
        logging.debug('get_name_ok: Button Click')

        new_name = name_in.get().strip()
        if len(new_name) < 4:
            messagebox.showerror(title="New Configuration", message="Name must be at least 4 characters")
        elif new_name in listbox_choices:
            messagebox.showerror(title="New Configuration", message=new_name + " is a duplicate name. Choose another name.")
        else:
            CheckboxPath: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
            CheckboxPath = CheckboxPath + r'\MenardsCheckBoxOptions.txt'
            logging.debug('Checkbox Path and File:' + CheckboxPath)

            if os.path.exists(CheckboxPath):
                with open(CheckboxPath) as f:
                    Checkbox_Choices = [tuple(i.strip().split(',')) for i in f]
            else:
                Checkbox_Choices = []
#            Checkbox_Choices.append(new_name, "default@default.net")
            t = (new_name, "default@default.net")
            Checkbox_Choices.append(t)
            if user_data_list[0][0] == "NoData":
                user_data_list = []
            user_data_list.append(t)

            f = open(CheckboxPath, "w")
            for t in Checkbox_Choices:
                output_line = ','.join(str(x) for x in t)
                f.write(output_line + '\n')
            f.close()

            listbox_choices = []
            #        for choice in Checkbox_Choices:
            for choice in Checkbox_Choices:
                listbox_choices.append(choice[0])
            rebate_user_data.append(default_user_data)
            get_name.destroy()

    def get_name_cancel(self,event=None):
        # ********************************************************************************************************
        # * Need event=None because clicking the button does not send a parm, but escape key does
        # ********************************************************************************************************

        logging.debug('get_name_cancel: Button Click')
        get_name.destroy()

def UpdateSettings():
    if root_logger.disabled == False:
        logging.debug("About to  instantiate dialog box for: " + file_name)

    read_user_info()

    settings_root = tk.Tk()
    s_diag = SettingsDialog(settings_root)
    settings_root.title("Rebate Configuration Settings")
    settings_root.wait_window(settings_root)

    #Settings_root.mainloop()


# ********************************************************************************************************
# * test stuff
# ********************************************************************************************************

if __name__ == "__main__":
    if root_logger.disabled == False:
        logging.debug("About to  instantiate dialog box for: " + file_name)

    read_user_info()

    Settings_root = tk.Tk()
    s_diag = SettingsDialog(Settings_root)
    Settings_root.title("Rebate Configuration Settings")
  #  s_diag.pack(fill="both", expand=True)
    Settings_root.mainloop()
