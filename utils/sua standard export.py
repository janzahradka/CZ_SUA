from AirspaceManager.renderer import Renderer
from AirspaceManager.controller import airspace_from_openair, split_openair_blocks
import os
import shutil
import chardet



label_cz_all = 'CZ_all_'
cz_all = [
     'FileInfo/info_cz_all.txt',
     'FileInfo/effective_date.txt',
     'FileInfo/copyright.txt',
     'DROPZONES.txt',
     'LKCTR.txt',
     'LKD.txt',
     'LKP.txt',
     'LKPGZ.txt',
     'LKR.txt',
     'LKR-NP.txt',
     'LKRMZ.txt',
     'LKTMA.txt',
     'LKTMA MTMA Caslav.txt',
     'LKTMA above FL95.txt',
     'LKTRA.txt',
     'LKTRA above FL95.txt',
     'LKTRAGA.txt',
     'LKTSA all seasons.txt',
     'LKTSA summer OFF.txt',
     'LKTSA above FL95.txt',
     # 'extra files/CZ-FL95 ceil.txt',
     'NOTAMS.txt'
 ]

label_cz_low = 'CZ_low_'
cz_low = [
     'FileInfo/info_CZ_low.txt',
     'FileInfo/effective_date.txt',
     'FileInfo/copyright.txt',
     'DROPZONES.txt',
     'LKCTR.txt',
     'LKD.txt',
     'LKP.txt',
     'LKPGZ.txt',
     'LKR.txt',
     'LKR-NP.txt',
     'LKRMZ.txt',
     'LKTMA.txt',
     'LKTMA MTMA Caslav.txt',
     'LKTRA.txt',
     'LKTRAGA.txt',
     'LKTSA all seasons.txt',
     'LKTSA summer OFF.txt',
     # 'extra files/CZ-FL95 ceil.txt',
     'NOTAMS.txt'
 ]
 #
label_cz_low_ce = 'CZ_low_plus_CE_'
cz_low_ce = [
    'FileInfo/info_low_plus_CE.txt',
    'FileInfo/effective_date.txt',
    'FileInfo/copyright.txt',
    'DROPZONES.txt',
    'LKCTR.txt',
    'LKD.txt',
    'LKP.txt',
    'LKPGZ.txt',
    'LKR.txt',
    'LKR-NP.txt',
    'LKRMZ.txt',
    'LKTMA.txt',
    'LKTMA MTMA Caslav.txt',
    'LKTRA.txt',
    'LKTRAGA.txt',
    'LKTSA all seasons.txt',
    'LKTSA summer OFF.txt',
    'NOTAMS.txt' ,
    # 'extra files/CZ-FL95 ceil.txt',
    'surrounding_AS.txt'
 ]

label_cz_all_xcsoar = 'CZ_all_xcsoar_'
cz_all_xcsoar = [
     'FileInfo/info_cz_all.txt',
     'FileInfo/effective_date.txt',
     'FileInfo/copyright.txt',
     'DROPZONES.txt',
     'LKCTR.txt',
     'LKD.txt',
     'LKP.txt',
     'LKPGZ.txt',
     'LKR.txt',
     'LKR-NP.txt',
     'LKRMZ.txt',
     'LKTMA.txt',
     'LKTMA MTMA Caslav.txt',
     'LKTMA above FL95.txt',
     'LKTRA.txt',
     'LKTRA above FL95.txt',
     'LKTRAGA.txt',
     'LKTSA all seasons.txt',
     'LKTSA summer OFF.txt',
     'LKTSA above FL95.txt',
     # 'extra files/CZ-FL95 ceil.txt',
     'NOTAMS.txt'
 ]


def export(effective, label, filenames, path):
    """
    Vytvoří exportní soubor kombinací všech vstupních souborů.
    """
    export_file_path = f'{path}/{label}{effective}.txt'
    with open(export_file_path, 'w', encoding='utf-8') as outfile:
        for fname in filenames:
            file_path = "../Source_Files/" + fname
            # Detekce kódování
            with open(file_path, 'rb') as raw_file:
                raw_data = raw_file.read()
                detected = chardet.detect(raw_data)
                encoding = detected.get("encoding", "utf-8")  # Použijeme detekované kódování nebo UTF-8
            try:
                with open(file_path, encoding=encoding) as infile:
                    for line in infile:
                        outfile.write(line)
            except Exception as e:
                print(f"Error reading file '{file_path}' with encoding '{encoding}': {e}")
    return export_file_path  # Vrací cestu k výslednému exportnímu souboru


def generate_html_maps(export_files, export_path):
    """
    Vytvoří HTML mapy pro každý exportní soubor a uloží je do exportního adresáře.

    :param export_files: Seznam cest k exportním souborům.
    :param export_path: Cesta do exportní složky.
    """
    print("Generating HTML maps for exported files...")

    # Adresář pro ukládání HTML map
    html_dir = os.path.join(export_path, "html")
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)  # Pokud složka neexistuje, vytvoříme ji

    for export_file in export_files:
        try:
            with open(export_file, 'r', encoding='utf-8') as f:
                airspace_data = f.read()

            # Zpracování bloků do Airspace objektů
            airspaces = []
            blocks = split_openair_blocks(airspace_data)
            for block in blocks:
                block = block.strip()
                if block:
                    try:
                        airspace_obj = airspace_from_openair(block)
                        airspaces.append(airspace_obj)
                    except Exception as e:
                        print(f"Skipping invalid block: {e}")

            if not airspaces:
                print(f"No valid airspaces found in {export_file}, map skipped.")
                continue

            # Název HTML souboru
            map_title = os.path.splitext(os.path.basename(export_file))[0]  # Název souboru bez přípony
            map_filename = f"{map_title}.html"

            # Generování mapy pomocí Renderer
            renderer = Renderer(airspaces)
            renderer.render_map(title=map_title, filename=map_filename, output_dir=html_dir)

            print(f"Map '{map_filename}' generated successfully.")
        except Exception as e:
            print(f"Error generating map for {export_file}: {e}")



if __name__ == "__main__":
    effective_date = '25-04-01' # YY-MM-DD
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

    export_path = f'../Export/CZ_SUA_{effective_date}/'

    if os.path.exists(export_path):
        shutil.rmtree(export_path)
    os.mkdir(export_path)

    # Uložíme všechny exportované soubory do seznamu, abychom mohli generovat mapy
    export_files = []

    # Provádíme export jednotlivých skupin souborů
    export_files.append(export(effective_date, label_cz_all, cz_all, export_path))
    export_files.append(export(effective_date, label_cz_low, cz_low, export_path))
    export_files.append(export(effective_date, label_cz_low_ce, cz_low_ce, export_path))
    # export_files.append(export(effective_date, label_cz_all_xcsoar, cz_all_xcsoar, export_path))

    # Kopírujeme ReadMe.md do exportní složky
    shutil.copy('../Source_Files/FileInfo/ReadMe.md', export_path)

    # Generování HTML map pro všechny exportní soubory
    generate_html_maps(export_files, export_path)

