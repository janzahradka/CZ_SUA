import os
import shutil

def export(version, label, filenames, path):
    with open(f'{path}/{label}{version}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)


label = 'PMRG24'
file_set = [
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
    'NOTAMS.txt',
    'surrounding_AS.txt'
]

version = '-v3'
export_path = f'../Export/{label}{version}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(version, label, file_set, export_path)