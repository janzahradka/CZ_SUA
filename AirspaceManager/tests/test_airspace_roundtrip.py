import os
import pytest
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace_formatter import AirspaceFormatter
from AirspaceManager.airspace import Airspace

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

# === Funkce pro porovnání Airspace objektů ===
def compare_airspaces(airspace1: Airspace, airspace2: Airspace):
    assert airspace1.name == airspace2.name, f"Chyba v 'name': {airspace1.name} != {airspace2.name}"
    assert airspace1.airspace_class == airspace2.airspace_class, f"Chyba v 'airspace_class': {airspace1.airspace_class} != {airspace2.airspace_class}"
    assert airspace1.category == airspace2.category, f"Chyba v 'category': {airspace1.category} != {airspace2.category}"
    assert airspace1.frequencies == airspace2.frequencies, f"Chyba v 'frequencies': {airspace1.frequencies} != {airspace2.frequencies}"
    assert airspace1.station_name == airspace2.station_name, f"Chyba v 'station_name': {airspace1.station_name} != {airspace2.station_name}"
    assert airspace1.upper_limit == airspace2.upper_limit, f"Chyba v 'upper_limit': {airspace1.upper_limit} != {airspace2.upper_limit}"
    assert airspace1.lower_limit == airspace2.lower_limit, f"Chyba v 'lower_limit': {airspace1.lower_limit} != {airspace2.lower_limit}"
    assert airspace1.draw_commands == airspace2.draw_commands, f"Chyba v 'draw_commands': {airspace1.draw_commands} != {airspace2.draw_commands}"

# === Test pro OpenAir soubory ===
def test_roundtrip_openair():
    """ Testuje round-trip pro OpenAir soubory (OpenAir → Airspace → OpenAir → Airspace) """
    openair_files = load_all_files_from_directory(OPENAIR_DIR)

    for filename, content in openair_files:
        print(f"\n--- {filename} ---")

        # === Krok 1: Načti jako Airspace ===
        extractor = ExtractorOpenAir(content)
        airspace_from_file = extractor.to_airspace()
        print("-- airspace from file --")
        print(airspace_from_file)

        # === Krok 2: Převeď na OpenAir formát ===
        formatter = AirspaceFormatter(airspace_from_file)
        openair_output = formatter.to_openair()
        print("-- openair output --")
        print(openair_output)

        # === Krok 3: Načti OpenAir výstup jako Airspace ===
        extractor_output = ExtractorOpenAir(openair_output)
        airspace_from_output = extractor_output.to_airspace()
        print("-- airspace from output --")
        print(airspace_from_output)

        # === Krok 4: Porovnej oba Airspace objekty ===
        compare_airspaces(airspace_from_file, airspace_from_output)

# === Test pro Plain Text soubory ===
def test_roundtrip_plain_text():
    """ Testuje round-trip pro Plain Text soubory (Plain Text → Airspace → OpenAir → Airspace) """
    plain_text_files = load_all_files_from_directory(PLAIN_TEXT_DIR)

    for filename, content in plain_text_files:
        print(f"\n--- {filename} ---")

        # === Krok 1: Načti jako Airspace ===
        extractor = Extractor(content)
        airspace_from_file = extractor.to_airspace()

        # === Krok 2: Převeď na OpenAir formát ===
        formatter = AirspaceFormatter(airspace_from_file)
        openair_output = formatter.to_openair()

        # === Krok 3: Načti OpenAir výstup jako Airspace ===
        extractor_output = ExtractorOpenAir(openair_output)
        airspace_from_output = extractor_output.to_airspace()

        # === Krok 4: Porovnej oba Airspace objekty ===
        compare_airspaces(airspace_from_file, airspace_from_output)
