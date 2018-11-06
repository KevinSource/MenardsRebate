#! python3

import os
import sys
import fdfgen
import logging
import inspect
from typing import Union

# ********************************************************************************************************
# * Set up logging
# * To turn on logging, set root_logger.disabled = False
# * To turn off logging, set root_logger.disabled = True
# ********************************************************************************************************
root_logger = logging.getLogger()
root_logger.disabled = True # Set to false to see debugging info
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

if root_logger.disabled == False:
    file_name = inspect.stack()[0][3]  # This is slow, so only run it when logging
    called_from = lambda n=1: sys._getframe(n + 1).f_code.co_name
    logging.debug('Start of ' + file_name + ' function' + " Called from: " + called_from.__module__)

def pdf_fill(email,input_pdf_file_name):

    # ********************************************************************************************************
    # * This figures out where the script is stored
    # ********************************************************************************************************
    script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
    logging.debug('Script Directory:' + script_path)

    # ********************************************************************************************************
    # * Read in the pdf field names and values
    # ********************************************************************************************************
    input_fields_and_values_file = os.path.join(script_path, email) + '.txt'

    with open(input_fields_and_values_file) as f:
        all_fields = [tuple(i.strip().split(',')) for i in f]

    # ********************************************************************************************************
    # * Build the fully qualified file names
    # ********************************************************************************************************
    fdf_file_name = os.path.join(script_path, "file_fdf.fdf")
    base_output_f_name = os.path.split(input_pdf_file_name)[1]  # Extract the file name with extension
    base_output_f_name = os.path.splitext(base_output_f_name)   # Split the file name and extension
    output_f_name = base_output_f_name[0] + r'_output.pdf'      # Build the output file name with extension
#    output_file_name = os.path.join(script_path, output_f_name) # Build the fully qualified file name
    output_file_name = os.path.join(os.path.dirname(input_pdf_file_name), output_f_name) # Build the fully qualified file name

    # ********************************************************************************************************
    # * Create FDF file with the fields read from the file earlier
    # ********************************************************************************************************
    fdf_data = fdfgen.forge_fdf("", all_fields, [], [], [])
    fdf_file = open(fdf_file_name, "wb")
    fdf_file.write(fdf_data)
    fdf_file.close()

    # ********************************************************************************************************
    # * Run pdftk system command to populate the pdf file.
    # * The file "file_fdf.fdf" is pushed in to "input_pdf.pdf" thats generated as a new "output_pdf.pdf" file.
    # ********************************************************************************************************
    input_pdf_file_name1 = '"' + input_pdf_file_name + '"'
    output_file_name1 = '"' + output_file_name + '"'
    pdftk_cmd = "pdftk " + input_pdf_file_name1 + \
                " fill_form " + fdf_file_name + \
                " output " + output_file_name1 + " flatten"
    logging.debug('pdftk command:' + pdftk_cmd)
    os.system(pdftk_cmd)
    # ********************************************************************************************************
    # * Remove the fdf file
    # ********************************************************************************************************
    os.remove(fdf_file_name)
    return output_file_name

if __name__ == '__main__':
    f_out = pdf_fill(r"kdoglio@gmail.com",r"C:\Users\BeastAdmin\Downloads\4468.pdf")