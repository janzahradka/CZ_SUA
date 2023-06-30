import os
import shutil

def export(version, label, filenames, path):
    with open(f'{path}/{label}{version}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)


label = 'PPV2023'
file_set = [
    'FileInfo/copyright.txt',
    'FileInfo/effective_date.txt',
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'extra files/PPV LKTMA.txt',
    'LKTRA.txt',
    'LKRMZ.txt',
    'LKTSA.txt',
    'surrounding_AS.txt',
    'extra files/Engine Test Area.txt',
    'NOTAMS.txt'
]
version = '-v1'
export_path = f'../Export/{label}{version}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(version, label, file_set, export_path)