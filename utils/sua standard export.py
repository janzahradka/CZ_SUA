import os
import re
import shutil
import chardet
from datetime import datetime

from export_workflow import generate_html_maps, prompt_yes_no, publish_standard_release



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
def get_effective_date(file_path):
    try:
        # Otevřít soubor a přečíst obsah
        with open(file_path, 'r') as file:
            content = file.read()

        # Použít regulární výraz k nalezení datového úseku
        match = re.search(r'\*\*\*\*\*\*\*\* EFFECTIVE (\d{2}[A-Z]{3}\d{2}) \*\*\*\*\*\*\*\*', content)

        if not match:
            raise ValueError("Effective date not found in the file.")

        # Extrahovat nalezené datum
        date_str = match.group(1)

        # Parsovat datum
        effective_date = datetime.strptime(date_str, "%d%b%y")
        return effective_date.strftime("%y-%m-%d")

    except Exception as e:
        return f"Error reading effective date: {e}"

                    
                    
if __name__ == "__main__":
    # effective_date = '25-04-01' # YY-MM-DD
    effective_date = get_effective_date('../Source_Files/FileInfo/effective_date.txt')  # YY-MM-DD
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

    if prompt_yes_no("Publikovat novy standardni release do docs/public?", default=False):
        publish_standard_release(export_path)
        print("Publikace dokoncena.")

