import os
import shutil

from export_workflow import generate_html_maps, prompt_yes_no, publish_directory_to_docs


def export(version, label, filenames, path):
    # Zajisti výstupní soubor s kódováním UTF-8
    export_file_path = f'{path}/{label}{version}.txt'
    with open(export_file_path, 'w', encoding='utf-8') as outfile:
        for fname in filenames:
            with open("../Source_Files/" + fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)
    return export_file_path


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

#
# label = 'PPV2025'
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
#     'extra files/LKTMA MTMA CASLAV PPV.txt',
#     'LKTRA.txt',
#     'LKTSA all seasons.txt',
#     # 'LKTSA summer OFF.txt',
#     'surrounding_AS.txt',
#     'NOTAMS.txt',
#     'models.txt',
#     # 'extra files/competition_area.txt',
#     'extra files/Engine Test Area LKHB.txt'
#     ]

# label = 'PMRG2025'
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
#     'LKTMA MTMA Caslav.txt',
#     # 'extra files/LKTMA MTMA CASLAV PPV.txt',
#     'LKTRA.txt',
#     'LKTSA all seasons.txt',
#     # 'LKTSA summer OFF.txt',
#     'surrounding_AS.txt',
#     'NOTAMS.txt',
#     'models.txt',
#     # 'extra files/competition_area.txt',
#     'extra files/Engine Test Area LKHB.txt'
#     ]

label = 'AZcup2026'
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
    'extra files/AZ cup LKTMA.txt',
    # 'extra files/AZ cup LKTRAGA.txt',
    'LKTRA.txt',
    'LKTSA all seasons.txt',
    'LKTSA summer OFF.txt',
    'surrounding_AS.txt',
    'NOTAMS.txt',
    'extra files/competition_area.txt',
    'extra files/Engine Test Area LKZB.txt'
]

version = '-v1'
export_path = f'../Export/{label}{version}/'

# Cílová podsložka v docs/public. Příklady:
# "Competitions/AZ cup", "Competitions/PMRG", "Specials/2025 SAR MEET"
docs_relative_dir = 'Competitions/AZ cup'

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export_file = export(version, label, file_set, export_path)
generate_html_maps([export_file], export_path)

publish_target = f"{docs_relative_dir}/{label}{version}"
if prompt_yes_no(f"Publikovat export do docs/public/{publish_target}?", default=False):
    publish_directory_to_docs(export_path, docs_relative_dir)
    print(f"Publikace dokoncena: docs/public/{publish_target}")
