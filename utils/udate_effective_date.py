# -*- coding: utf-8 -*-
# This script updates Effective Date in all files
import os, re

# This function does not work well. It doubles End Of Lines in the files.
def update_effective_date(ef_date):
    directory_path = 'G:\Můj disk\Private\Python Projects\CZ_SUA\Source_Files'
    directory = os.listdir(directory_path)
    os.chdir(directory_path)
    for file in directory:
        if file.endswith(".txt"):
            with open(file, 'r') as open_file:
                read_file = open_file.read()
                # txt.replace("\r", "")
                # print(read_file)
            # filedata = re.sub(r'EFFECTIVE \d{2}\w{3}\d{2}')
            # date = 'EFFECTIVE ' + ef_date
            # read_file = regex.sub(date, read_file.decode('ASCII'))
            # write_file = open(file, 'w')
            # write_file.write(read_file)



# update_effective_date('19MAY22')
