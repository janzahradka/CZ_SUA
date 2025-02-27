import os
import pytest
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace_formatter import AirspaceFormatter

# === Cesty k testovacím souborům ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAIR_DIR = os.path.join(BASE_DIR, '../test_strings/openair')
PLAIN_TEXT_DIR = os.path.join(BASE_DIR, '../test_strings/plain_text')

# === Helper funkce pro načtení souboru ===
def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# === Načtení všech souborů ===
def load_all_files_from_directory(directory):
    file_contents = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            file_contents.append((filename, load_file(file_path)))
    return file_contents

# === Test pro výpis výstupu do konzole ===
def test_print_openair_output():
    """ Načte všechny soubory z OpenAir a plain_text a vytiskne výstup do konzole """

    # === OpenAir soubory ===
    openair_files = load_all_files_from_directory(OPENAIR_DIR)
    print("\n===== OpenAir Files =====")
    for filename, content in openair_files:
        print(f"\n--- {filename} ---")
        extractor = ExtractorOpenAir(content)
        airspace = extractor.to_airspace()
        formatter = AirspaceFormatter(airspace)
        print(formatter.to_openair())

    # === Plain Text soubory ===
    plain_text_files = load_all_files_from_directory(PLAIN_TEXT_DIR)
    print("\n===== Plain Text Files =====")
    for filename, content in plain_text_files:
        print(f"\n--- {filename} ---")
        extractor = Extractor(content)
        airspace = extractor.to_airspace()
        formatter = AirspaceFormatter(airspace)
        print(formatter.to_openair())
