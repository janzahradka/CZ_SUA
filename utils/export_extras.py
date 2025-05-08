import os
import shutil

def export(version, label, filenames, path):
    # Zajisti výstupní soubor s kódováním UTF-8
    with open(f'{path}/{label}{version}.txt', 'w', encoding='utf-8') as outfile:
        for fname in filenames:
            with open("../Source_Files/" + fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)



# label = 'WWGC2025'
# file_set = [
#     'DROPZONES.txt',
#     'LKCTR.txt',
#     'LKD.txt',
#     'LKP.txt',
#     'LKPGZ.txt',
#     'LKR.txt',
#     # 'LKR-NP.txt',
#     'LKRMZ.txt',
#     'LKTMA.txt',
#     'extra files/AZ cup LKTMA.txt',
#     'extra files/AZ cup LKTRAGA.txt',
#     'LKTRA.txt',
#     'LKTSA all seasons.txt',
#     # 'LKTSA summer OFF.txt',
#     'surrounding_AS.txt',
#     'NOTAMS.txt',
#     'extra files/competition_area.txt',
#     'extra files/Engine Test Area LKZB.txt'
#     ]
#
# version = '-v1'


label = 'PMCR2025'
file_set = [
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    # 'LKR-NP.txt',
    'LKRMZ.txt',
    'LKTMA.txt',
    'extra files/LKTMA MTMA CASLAV PPV.txt',
    'LKTRA.txt',
    'LKTSA all seasons.txt',
    'LKTSA summer OFF.txt',
    'surrounding_AS.txt',
    'NOTAMS.txt',
    'models.txt',
    # 'extra files/competition_area.txt',
    'extra files/Engine Test Area LKHB.txt'
    ]

version = '-v3'
export_path = f'../Export/{label}{version}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(version, label, file_set, export_path)