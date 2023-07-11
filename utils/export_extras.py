import os
import shutil

def export(version, label, filenames, path):
    with open(f'{path}/{label}{version}.txt', 'w') as outfile:
        for fname in filenames:
            with open("../Source_Files/"+fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)


label = 'SUA_CGP2023'
file_set = [
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKTMA.txt',
    'LKTRA.txt',
    'extra files/MTMA Caslav for competitions.txt',
    'LKTSA.txt',
    'surrounding_AS.txt',
    'extra files/AZCUPNOTAMS2023.txt'
    # 'extra files/AZ cup Engine Test Area.txt'
]
version = '-v1'
export_path = f'../Export/{label}{version}/'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export(version, label, file_set, export_path)