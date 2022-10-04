import os
import shutil

label_cz_all = 'CZ_all_'
cz_all = [
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKTMA.txt',
    'LKTMA above FL95.txt',
    'LKTRA.txt',
    'LKTRA above FL95.txt',
    'LKTRAGA.txt',
    'LKTSA.txt',
    'LKTSA above FL95.txt'
]

label_cz_low = 'CZ_low_'
cz_low = [
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKTMA.txt',
    'LKTRA.txt',
    'LKTRAGA.txt',
    'LKTSA.txt'
]

label_cz_low_ce = 'CZ_low_plus_CE_'
cz_low_ce = [
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKTMA.txt',
    'LKTRA.txt',
    'LKTRAGA.txt',
    'LKTSA.txt',
    'surrounding_AS.txt'
]


def export(effective, label, filenames, path):
    with open(f'{path}/{label}{effective}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)


effective_date = '22-10-06'
export_path = f'../Export/CZ_SUA_{effective_date}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(effective_date, label_cz_all, cz_all, export_path)
export(effective_date, label_cz_low, cz_low, export_path)
export(effective_date, label_cz_low_ce, cz_low_ce, export_path)
shutil.copy('../ReadMe.md', export_path)
