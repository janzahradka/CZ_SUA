import os
import shutil

label_cz_all = 'CZ_SUA_'
cz_all = [
    'FileInfo/all_info.txt',
    'FileInfo/effective_date.txt',
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKRMZ.txt',
    'LKTMA.txt',
    'LKTMA above FL95.txt',
    'LKTRA.txt',
    'LKTRA above FL95.txt',
    'LKTRAGA.txt',
    'LKTSA.txt',
    'LKTSA above FL95.txt',
    'NOTAMS.txt'
]

label_cz_low = 'CZ_low_'
cz_low = [
    'FileInfo/low_info.txt',
    'FileInfo/effective_date.txt',
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'extra files/Engine Test Area.txt',
    # 'LKRMZ.txt',
    'LKTMA.txt',
    'LKTRA.txt',
    'LKTRAGA.txt',
    'LKTSA.txt',
    'surrounding_AS.txt',
    'NOTAMS.txt'
]
#
# label_cz_low_ce = 'CZ_low_plus_CE_'
# cz_low_ce = [
#     'DROPZONES.txt',
#     'LKCTR.txt',
#     'LKD.txt',
#     'LKP.txt',
#     'LKPGZ.txt',
#     'LKRMZ.txt',
#     'LKR.txt',
#     'LKR-NP.txt',
#     'LKTMA.txt',
#     'LKTRA.txt',
#     'LKTRAGA.txt',
#     'LKTSA.txt',
#     'NOTAMS.txt',
#     'surrounding_AS.txt'
# ]


def export(effective, label, filenames, path):
    with open(f'{path}/{label}{effective}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)

if __name__ == "__main__":
    effective_date = '23-06-27'
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


    export_path = f'../Export/PMRG2023/'
    # export_path = f'../Export/CZ_SUA_{effective_date}/'

    if os.path.exists(export_path):
        shutil.rmtree(export_path)
    os.mkdir(export_path)
    # export(effective_date, label_cz_all, cz_all, export_path)
    export(effective_date, label_cz_low, cz_low, export_path)
    # export(effective_date, label_cz_low_ce, cz_low_ce, export_path)
    shutil.copy('../Source_Files/FileInfo/ReadMe.md', export_path)
