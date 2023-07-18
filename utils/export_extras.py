import os
import shutil

def export(version, label, filenames, path):
    with open(f'{path}/{label}{version}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)


label = 'SUA_PMCR23'
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
    'extra files/MTMA Caslav for competitions.txt',
    'LKTRA.txt',
    'LKTSA all seasons.txt',
    'surrounding_AS.txt',
    'NOTAMS.txt',
    'extra files/CZ-FL90 ceil.txt',
    'extra files/Engine Test Area.txt'
]
version = '-v1'
export_path = f'../Export/{label}{version}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(version, label, file_set, export_path)