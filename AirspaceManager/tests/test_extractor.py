import os
import pytest

from AirspaceManager.extractor.convertor import Convertor
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.airspace import Airspace

# === Cesty k testovacím souborům ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_STRINGS_DIR = os.path.join(BASE_DIR, '../test_strings/plain_text')
VERTICALS_FILE = os.path.join(BASE_DIR, '../test_strings/verticals.txt')

# === Plain Text soubory a očekávané výsledky ===
PLAIN_TEXT_FILES = [
    ("Lion 1", {
        "name": "NTM-LION 1",
        "airspace_class": "R",
        "category": "NOTAM",
        "frequencies": ['126.100'],
        "upper_limit": "FL 305",
        "lower_limit": "5000 MSL",
        "draw_commands": [{'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 43 34,98 N 015 30 17,21 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 32 21,39 N 016 02 27,74 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 31 53,84 N 016 08 55,60 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 26 31,16 N 016 05 45,97 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 21 32,07 N 016 10 18,06 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 09 53,81 N 016 27 11,77 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 02 17,53 N 016 41 50,84 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 03 04.96 N 016 43 45.04 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 59 00,00 N 017 16 00,00 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 46 35,89 N 017 32 27,73 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 45 47,94 N 017 40 53,77 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 42 16,93 N 017 43 20,75 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 38 58,84 N 017 38 17,85 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 34 13,89 N 017 37 40,77 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 33 22.90 N 017 32 39.77 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 33 25.05 N 017 31 51.04 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 34 40.89 N 017 28 59.77 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 35 58,88 N 017 23 50,72 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 27 32,96 N 016 42 48,91 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 25 30,09 N 016 33 03,64 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 30 44.56 N 016 06 40.45 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 36 32,85 N 015 39 25,61 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 50 05,68 N 015 07 54,92 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 00 16,76 N 015 11 41,67 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 11 08,50 N 015 09 20,30 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 11 07,99 N 014 58 39,41 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 14 09,32 N 014 57 28,83 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 28 33,75 N 015 00 03,79 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 28 35,45 N 015 10 11,21 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 33 59,66 N 015 02 57,23 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 36 32,01 N 015 05 42,92 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('50 43 34,98 N 015 30 17,21 E')}]
    }),
    ("Lion 3", {
        "name": "NTM-LION 3",
        "airspace_class": "R",
        "category": "NOTAM",
        "upper_limit": "FL 245",
        "lower_limit": "1000 AGL",
        "draw_commands": [{'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 38 28.05 N 014 18 03.71 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 23 41.08 N 014 36 42.60 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 09 57.74 N 014 53 46.79 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('48 51 04.30 N 014 44 33.21 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('48 48 32.66 N 014 16 16.87 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('48 54 59.73 N 014 07 56.81 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('48 54 41.66 N 013 53 33.78 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 03 12.62 N 013 33 40.47 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 19 56.98 N 013 53 56.70 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('49 38 28.05 N 014 18 03.71 E')}]
    }),
    ("LKP2 Temelin - kruh", {
        "name": "LKP2 TEMELIN",
        "airspace_class": "P",
        "category": "Prohibited Area",
        "upper_limit": "5000 MSL",
        "lower_limit": "0 AGL",
        "draw_commands": [{'type': 'circle', 'circle_center_coordinate': Convertor.extract_coodinate_from_text('491048.73N 0142231.77E'), 'circle_radius': 1.1,
                           'radius_unit': 'NM'}]
    }),
    ("LKP4 vlasim - polygon", {
        "name": "LKP4 VLASIM",
        "airspace_class": "P",
        "category": "Prohibited Area",
        "upper_limit": "5000 MSL",
        "lower_limit": "0 AGL",
        "draw_commands": [{'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('494223.79N 0145356.76E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('494053.30N 0145757.76E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('493940.74N 0145554.76E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('494223.79N 0145356.76E')}]
    }),
    ("TRA62 Nymburk", {
        "name": "LKTRA62 NYMBURK",
        "airspace_class": "R",
        "category": "Temporary Reserved Area",
        "upper_limit": "FL 245",
        "lower_limit": "3000 MSL",
        "draw_commands": [{'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('502835.45N 0151011.21E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('502305.85N 0152316.12E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('501108.78N 0152255.61E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('501108.54N 0150324.04E')},
                          {'type': 'arc', 'arc_center_coordinate': Convertor.extract_coodinate_from_text('500544.80N 0141555.81E'), 'arc_direction': '-',
                           'arc_start_point_coordinate': Convertor.extract_coodinate_from_text('501107.99N 0145839.41E'),
                           'arc_end_point_coordinate': Convertor.extract_coodinate_from_text('501409.32N 0145728.83E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('502833.75N 0150003.79E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': Convertor.extract_coodinate_from_text('502835.45N 0151011.21E')}]
    }),
    ("TMA II Brno - polygon", {
        "name": "TMA II BRNO",
        "airspace_class": "D",
        "category": "Terminal Manoeuvring Area",
        "upper_limit": "FL 95",
        "lower_limit": "3500 MSL",
        "draw_commands": [
            {"type": "polygon_point",
             "polygon_point_coordinate": Convertor.extract_coodinate_from_text("491528.30N 0170351.62E")},
            {"type": "polygon_point",
             "polygon_point_coordinate": Convertor.extract_coodinate_from_text("491514.85N 0172945.86E")},
            {"type": "polygon_point",
             "polygon_point_coordinate": Convertor.extract_coodinate_from_text("491442.19N 0173521.58E")},
            {"type": "polygon_point",
             "polygon_point_coordinate": Convertor.extract_coodinate_from_text("490705.08N 0171626.75E")},
            {"type": "polygon_point",
             "polygon_point_coordinate": Convertor.extract_coodinate_from_text("485615.73N 0171411.81E")},
            {"type": "polygon_point",
             "polygon_point_coordinate": Convertor.extract_coodinate_from_text("485103.05N 0165559.46E")},
            {"type": "arc",
             "arc_center_coordinate": Convertor.extract_coodinate_from_text("490900.23N 0164133.29E"),
             "arc_direction": "-",
             "arc_start_point_coordinate": Convertor.extract_coodinate_from_text("485542.66N 0164810.07E"),
             "arc_end_point_coordinate": Convertor.extract_coodinate_from_text("485752.54N 0165426.67E")
             },
            {"type": "arc",
             "arc_center_coordinate": Convertor.extract_coodinate_from_text("490900.23N 0164133.29E"),
             "arc_direction": "-",
             "arc_start_point_coordinate": Convertor.extract_coodinate_from_text("485731.51N 0165828.67E"),
             "arc_end_point_coordinate": Convertor.extract_coodinate_from_text("491528.30N 0170351.62E")
             },
        ]
    })
]


# === Helper funkce pro načtení souboru ===
def load_test_file(filename):
    file_path = os.path.join(TEST_STRINGS_DIR, f"{filename}.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# === Test pro třídu Extractor ===
# === Aktualizace hlavního testu ===
@pytest.mark.parametrize("filename, expected_values", PLAIN_TEXT_FILES)
def test_extractor(filename, expected_values):
    """ Test funkčnosti Extractor s použitím testovacích souborů """
    input_text = load_test_file(filename)
    extractor = Extractor(input_text)

    # Provedeme extrakci
    airspace = extractor.to_airspace()
    print(airspace)

    # === Přeformátování vertical limits ===
    # Pokud je klíč upper_limit nebo lower_limit, přeformátuje na očekávaný řetězec
    for key, value in expected_values.items():
        actual_value = getattr(airspace, key)

        # === Formátování pro upper_limit a lower_limit ===
        if key in ["upper_limit", "lower_limit"]:
            actual_value = format_vertical_limit(actual_value)

        # === Ověření výsledku ===
        assert actual_value == value, f"Chyba v {key} pro {filename}"


# === Helper funkce pro načtení verticals.txt ===
def load_verticals_file():
    """ Načte testovací soubor s vertikálními limity """
    with open(VERTICALS_FILE, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # === Rozdělení podle '|' a odstranění bílých znaků ===
    data = []
    for line in lines:
        line = line.strip()
        # === Ignorování komentářů ===
        if line.startswith("#") or not line:
            continue
        parts = line.split('|')
        if len(parts) == 3:  # Musí být přesně tři části na řádek
            input_text = parts[0].strip()
            expected_upper = parts[1].strip()
            expected_lower = parts[2].strip()
            data.append((input_text, expected_upper, expected_lower))
    return data


# === Jednoduchý formátovací blok ===
def format_vertical_limit(limit):
    """
    Převede výstup extract_verticals() na řetězec pro porovnání v testu.
    Formát:
        - FL 305
        - 5000 MSL
        - 0 AGL
    """
    if limit is None:
        return None  # Ošetření pokud je limit None

    # === Jednoduché formátování podle jednotky ===
    if limit['unit'] == "FL":
        return f"{limit['unit']} {limit['value']}"
    else:
        return f"{limit['value']} {limit['unit']}"


# === Test pro Extractor.extract_verticals() ===
@pytest.mark.parametrize("input_text, expected_upper, expected_lower", load_verticals_file())
def test_extract_verticals(input_text, expected_upper, expected_lower):
    """ Test funkčnosti Extractor.extract_verticals() s různými vertikálními limity """
    if expected_lower == "None":
        expected_lower = None
    if expected_upper == "None":
        expected_upper = None

    extractor = Extractor(input_text)

    # === Očekávání výjimky u nevalidních vstupů ===
    # === Validní vstupy ===
    extractor.extract_verticals()

    # === Formátování výstupu pro porovnání ===
    upper_limit = format_vertical_limit(extractor.upper_limit)
    lower_limit = format_vertical_limit(extractor.lower_limit)

    # === Ověření výsledku ===
    assert upper_limit == expected_upper, f"Chyba v upper_limit pro '{input_text}'"
    assert lower_limit == expected_lower, f"Chyba v lower_limit pro '{input_text}'"
