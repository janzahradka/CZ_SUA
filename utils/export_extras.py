from AirspaceManager.renderer import Renderer
from AirspaceManager.controller import airspace_from_openair, split_openair_blocks
import os
import shutil


def export(version, label, filenames, path):
    # Zajisti výstupní soubor s kódováním UTF-8
    export_file_path = f'{path}/{label}{version}.txt'
    with open(export_file_path, 'w', encoding='utf-8') as outfile:
        for fname in filenames:
            with open("../Source_Files/" + fname, encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)
    return export_file_path


def generate_html_maps(export_files, export_path):
    """
    Vytvoří HTML mapy pro exportované OpenAir soubory a uloží je do složky html.
    """
    print("Generating HTML maps for exported files...")

    html_dir = os.path.join(export_path, "html")
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)

    for export_file in export_files:
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                airspace_data = f.read()

            airspaces = []
            blocks = split_openair_blocks(airspace_data)
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                try:
                    airspace_obj = airspace_from_openair(block)
                    airspaces.append(airspace_obj)
                except Exception as e:
                    print(f"Skipping invalid block: {e}")

            if not airspaces:
                print(f"No valid airspaces found in {export_file}, map skipped.")
                continue

            map_title = os.path.splitext(os.path.basename(export_file))[0]
            map_filename = f"{map_title}.html"

            renderer = Renderer(airspaces)
            renderer.render_map(title=map_title, filename=map_filename, output_dir=html_dir)

            print(f"Map '{map_filename}' generated successfully.")
        except Exception as e:
            print(f"Error generating map for {export_file}: {e}")


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

label = 'AZCup2026'
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

if os.path.exists(export_path):
    shutil.rmtree(export_path)
os.mkdir(export_path)
export_file = export(version, label, file_set, export_path)
generate_html_maps([export_file], export_path)
