import os
import shutil

label_cz_all = 'CZ_all_'
cz_all = [
     'FileInfo/info_cz_all.txt',
     'FileInfo/effective_date.txt',
     'FileInfo/copyright.txt',
     'DROPZONES.txt',
     'LKCTR.txt',
     'LKD.txt',
     'LKP.txt',
     'LKPGZ.txt',
     'LKR.txt',
     'LKR-NP.txt',
     'LKRMZ.txt',
     'LKTMA.txt',
     'MTMA Caslav.txt',
     'LKTMA above FL95.txt',
     'LKTRA.txt',
     'LKTRA above FL95.txt',
     'LKTRAGA.txt',
     'LKTSA all seasons.txt',
     'LKTSA summer OFF.txt',
     'LKTSA above FL95.txt',
     # 'extra files/CZ-FL95 ceil.txt',
     'NOTAMS.txt'
 ]

label_cz_low = 'CZ_low_'
cz_low = [
     'FileInfo/info_CZ_low.txt',
     'FileInfo/effective_date.txt',
     'FileInfo/copyright.txt',
     'DROPZONES.txt',
     'LKCTR.txt',
     'LKD.txt',
     'LKP.txt',
     'LKPGZ.txt',
     'LKR.txt',
     'LKR-NP.txt',
     'LKRMZ.txt',
     'LKTMA.txt',
     'MTMA Caslav.txt',
     'LKTRA.txt',
     'LKTRAGA.txt',
     'LKTSA all seasons.txt',
     'LKTSA summer OFF.txt',
     # 'extra files/CZ-FL95 ceil.txt',
     'NOTAMS.txt'
 ]
 #
label_cz_low_ce = 'CZ_low_plus_CE_'
cz_low_ce = [
    'FileInfo/info_low_plus_CE.txt',
    'FileInfo/effective_date.txt',
    'FileInfo/copyright.txt',
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKRMZ.txt',
    'LKTMA.txt',
    'MTMA Caslav.txt',
    'LKTRA.txt',
    'LKTRAGA.txt',
    'LKTSA all seasons.txt',
    'LKTSA summer OFF.txt',
    'NOTAMS.txt' ,
    'extra files/CZ-FL95 ceil.txt',
    'surrounding_AS.txt'
 ]

label_cz_all_xcsoar = 'CZ_all_xcsoar_'
cz_all_xcsoar = [
     'FileInfo/info_cz_all.txt',
     'FileInfo/effective_date.txt',
     'FileInfo/copyright.txt',
     'DROPZONES.txt',
     'LKCTR.txt',
     'LKD.txt',
     'LKP.txt',
     'LKPGZ.txt',
     'LKR.txt',
     'LKR-NP.txt',
     'LKRMZ.txt',
     'LKTMA.txt',
     'MTMA Caslav.txt',
     'LKTMA above FL95.txt',
     'LKTRA.txt',
     'LKTRA above FL95.txt',
     'LKTRAGA.txt',
     'LKTSA all seasons.txt',
     'LKTSA summer OFF.txt',
     'LKTSA above FL95.txt',
     'extra files/CZ-FL95 ceil.txt',
     'NOTAMS.txt'
 ]



def export(effective, label, filenames, path):
    with open(f'{path}/{label}{effective}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)

if __name__ == "__main__":
    effective_date = '24-08-07' # YY-MM-DD
    confirmed = False
    while not confirmed:
        answer = input(f'Effective date "{effective_date}" correct? [Y/N] ').lower()
        if answer == "y":
            confirmed = True
        elif answer == "n":
            effective_date = input("type version date [YY-MM-DD] ")
        else:
            print("Wrong value - proces terminated by user. Nothing happend.")
            quit()


    export_path = f'../Export/CZ_SUA_{effective_date}/'

    if os.path.exists(export_path):
        shutil.rmtree(export_path)
    os.mkdir(export_path)
    export(effective_date, label_cz_all, cz_all, export_path)
    export(effective_date, label_cz_low, cz_low, export_path)
    export(effective_date, label_cz_low_ce, cz_low_ce, export_path)
    export(effective_date, label_cz_all_xcsoar, cz_all_xcsoar, export_path)
    shutil.copy('../Source_Files/FileInfo/ReadMe.md', export_path)
