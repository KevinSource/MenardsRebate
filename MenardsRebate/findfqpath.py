#! python3
# Finds the current the most current version of a file
# Once it's found, it will be stored in a shelf file
# Future calls pull from the shelf file first and search if the file is older than requested

import os
import sys
import glob
import shelve
import logging
from pathlib import Path
from shelve import DbfilenameShelf
from typing import Union
import datetime
from datetime import timedelta
import ctypes.wintypes

# ********************************************************************************************************
# * Set up logging
# * To turn on logging, set root_logger.disabled = False
# * To turn off logging, set root_logger.disabled = True
# ********************************************************************************************************
root_logger = logging.getLogger()
root_logger.disabled = True
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# ********************************************************************************************************
# *
# * find_fq_path: will return a full qualified path or None
# * find_file: Name of the file to find (ie. opera.exe)
# * num_days_valid: Trigger a new search if the data in the shelf file is older than this number of days
# *                  0 will always trigger a new search
# *
# ********************************************************************************************************


def find_fq_path(find_file, num_days_valid, scope="Shared"):
    # ********************************************************************************************************
    # *
    # * This figures out where the shelf file is and gets the data if it's there
    # *
    # ********************************************************************************************************


    if scope.upper() == "LOCAL":
        script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
        logging.debug('Script Directory:' + script_path)
        pathkey = find_file + 'fqpath'
        path_update_date_key = find_file + 'DateUpdated'
        shelf_nm = script_path + r'\FileShlf'
        logging.debug('Shelf File Name: %s', shelf_nm)
        find_file_path_shelf: DbfilenameShelf = shelve.open(shelf_nm)
    else:
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        return_value = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        shelf_path = buf.value
        logging.debug('Shared Directory:' + shelf_path)

        pathkey = find_file + 'fqpath'
        path_update_date_key = find_file + 'DateUpdated'
        shelf_nm = shelf_path + r'\FileShlf'
        logging.debug('Shelf File Name: %s',  shelf_nm)
        find_file_path_shelf: DbfilenameShelf = shelve.open(shelf_nm)

    # ********************************************************************************************************
    # * Get the fully qualified path of the file and the date it was stored (if it's there)
    # ********************************************************************************************************
    if pathkey in find_file_path_shelf:
        curr_find_file_path = find_file_path_shelf[pathkey]
        curr_path_last_update_dt = find_file_path_shelf[path_update_date_key]

        #  ********************************************************************************************************
        #  * See if the file still exists and see if it is recent enough to use, if so, return the
        #  * fully qualified path and quit
        #  ********************************************************************************************************
        test_file = Path(curr_find_file_path)
        if test_file.is_file() and datetime.datetime.now() < \
                curr_path_last_update_dt + timedelta(days=num_days_valid):
            logging.debug('Find File Name Location: %s', curr_find_file_path)
            find_file_path_shelf.close()
            return curr_find_file_path
        else:
            # * If not, set up the search path one directory level up from where it was found before
            logging.debug('Entering Search for file: %s', curr_find_file_path)
            path_parts1 = os.path.split(curr_find_file_path)
            path_parts2 = os.path.split(path_parts1[0])
            drive, rest = os.path.splitdrive(path_parts1[0])
            search_from_path = path_parts2[0]


    # ********************************************************************************************************
    # * Initialize the search variables
    # * The Program Files path, then the root path will be used if the shelf file is empty (first time)
    # ********************************************************************************************************
    search_from_path = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"))

    drive, rest = os.path.splitdrive(search_from_path)

    # ********************************************************************************************************
    # * Set the wildcard node in the path and append the file name
    # ********************************************************************************************************
    search_path = os.path.join(search_from_path+'*', '**')
    search_path = os.path.join(search_path, find_file)

    # ********************************************************************************************************
    # * This loop will search through directories progressively upwards as needed
    # ********************************************************************************************************
    root_search = os.path.join(drive + os.sep, '**')  # Used to know when to give up
    root_search = os.path.join(root_search, find_file)
    logging.debug('Root search is %s: ', root_search)
    nodes_to_check = True
    while nodes_to_check:
        logging.debug('About to search for file %s in: %s', find_file, search_path)
        found_file_list = glob.glob(search_path, recursive=True)
        logging.debug('Matches found for file %s is %d', find_file, len(found_file_list))
        # Found it
        if len(found_file_list) > 0:
            nodes_to_check = False
        # Searched as far as can be done, gotta quit
        if search_path == root_search:
            nodes_to_check = False
        # Didn't find it. Take a node off of the path (go up a level) for the next try
        if len(found_file_list) == 0:
            search_from_path, rest = os.path.split(search_from_path)
            search_path = os.path.join(search_from_path, '**')
            search_path = os.path.join(search_path, find_file)

    # * Initialize the date variable
    most_recent_date = datetime.datetime(year=1900, month=1, day=1, hour=00, minute=00, second=0, microsecond=1)
    # ********************************************************************************************************
    # * Find the most recent version of the file
    # ********************************************************************************************************
    i = 0
    for files in found_file_list:
        if datetime.datetime.fromtimestamp(os.path.getmtime(files)) > most_recent_date:
            most_recent_date = datetime.datetime.fromtimestamp(os.path.getmtime(files))
            most_recent_file = i
            i += 1

    # ********************************************************************************************************
    # * Write the info to the shelf file and return the fully qualified file and path
    # ********************************************************************************************************
    if len(found_file_list) > 0:
        curr_find_file_path = found_file_list[most_recent_file]
        find_file_path_shelf[pathkey] = curr_find_file_path
        find_file_path_shelf[path_update_date_key] = datetime.datetime.now()
        find_file_path_shelf.close()
        return curr_find_file_path
    else:
        # * Couldn't find it, return None
        return None


# opera_file_path = find_fq_path(find_file='opera.exe', num_days_valid=1,scope="Shared")
# logging.debug('Path for requested file: %s', opera_file_path)