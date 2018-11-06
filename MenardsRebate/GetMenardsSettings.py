#! python3
# ********************************************************************************************************
# * Reads the config (.ini) file for the URLs needed
# ********************************************************************************************************

def GetUrlsAndPaths():

    import configparser
    import logging
    import inspect
    import sys
    import os

    global IniFile
    global ConfigData

    # ********************************************************************************************************
    # * Set up logging
    # * To turn on logging, set root_logger.disabled = False
    # * To turn off logging, set root_logger.disabled = True
    # ********************************************************************************************************
    root_logger = logging.getLogger()
    root_logger.disabled = True  # Set to false to see debugging info
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

    if root_logger.disabled == True:
        file_name = inspect.stack()[0][3] # This is slow, so only run it when logging
        called_from = lambda n=1: sys._getframe(n + 1).f_code.co_name
        logging.debug('Start of ' + file_name + ' function' + " Called from: " + called_from.__module__)

    # ********************************************************************************************************
    # * Set up the path to the .ini file
    # ********************************************************************************************************
    WriteDefaultValues = False
    IniPath: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
    IniFile = IniPath + r'\MenardsSettings.ini'

    # ********************************************************************************************************
    # * Set up default values in case the file is not thre or corrupt
    # ********************************************************************************************************
    default_hdrURL = r'https://www.menards.com/main/rebates.html'
    default_rebateURL = r'https://www.menards.com/main/assets/rebates/'

    # ********************************************************************************************************
    # * If the .ini file is there, read it.
    # ********************************************************************************************************
    if os.path.exists(IniFile):
        config = configparser.ConfigParser()
        config.sections()
        config.read(IniFile)
        # ********************************************************************************************************
        # * If the URLs section was in the .ini file extract the values and store them in a dictionary.
        # ********************************************************************************************************
        if 'URLs' in config.sections():
            PgmSettings = {'Header': config['URLs']['Header']}
            PgmSettings['Rebates'] = config['URLs']['Rebates']
        else:
            # ********************************************************************************************************
            # * If the URLs section wasn't found, use the defaults
            # ********************************************************************************************************
            PgmSettings = {'Header': default_hdrURL}
            PgmSettings['Rebates'] = default_rebateURL
            WriteDefaultValues = True
    else:
        # ********************************************************************************************************
        # * If the .ini file wasn't found, use the defaults
        # ********************************************************************************************************
        PgmSettings = {'Header': default_hdrURL}
        PgmSettings['Rebates'] = default_rebateURL
        WriteDefaultValues = True

    logging.debug('RebateHeaderUrl:' + PgmSettings['Header'])
    logging.debug('RebatePDFUrl:' + PgmSettings['Header'])

    return PgmSettings, WriteDefaultValues, IniFile


# ********************************************************************************************************
# * Testing code
# ********************************************************************************************************
if __name__ == '__main__':

    import os
    import sys
    from typing import Union

    RebateHeaderUrl = ''
    RebatePDFUrl = ''
    data={}
    IniPath: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
    IniFile = IniPath + r'\MenardsSettings.ini'
    data = GetUrlsAndPaths(IniFile)
