import os
import shutil

def export(version, label, filenames, path):
    with open(f'{path}/{label}{version}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)


label = 'AZCUP2023'
file_set = [
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'extra files/AZ cup LKTMA.txt',
    'LKTRA.txt',
    'extra files/AZ cup LKTRAGA.txt',
    'LKTSA.txt',
    'surrounding_AS.txt',
    'extra files/AZ cup NOTAMS.txt',
    'extra files/AZ cup Engine Test Area.txt'
]
version = '-v2'
export_path = f'../Export/{label}{version}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(version, label, file_set, export_path)