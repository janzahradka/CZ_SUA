import os
import pytest
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.airspace import Airspace

# === Cesty k testovacím souborům ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_STRINGS_DIR = os.path.join(BASE_DIR, '../test_strings/plain_text')

# === Plain Text soubory a očekávané výsledky ===
PLAIN_TEXT_FILES = [
    ("Lion 1", {
        "name": "NTM-LION 1",
        "airspace_class": "R",
        "category": "NOTAM",
        "upper_limit": "FL305",
        "lower_limit": "5000 FT AMSL",
        "draw_commands": [
            {"type": "polygon_point", "polygon_point_coordinate": (50.725272, 15.504781)},
            {"type": "polygon_point", "polygon_point_coordinate": (50.539275, 16.040983)},
            {"type": "polygon_point", "polygon_point_coordinate": (50.531622, 16.148778)},
        ]
    }),
    ("Lion 3", {
        "name": "NTM-LION 3",
        "airspace_class": "R",
        "category": "NOTAM",
        "upper_limit": "FL245",
        "lower_limit": "1000 FT AGL",
        "draw_commands": [
            {"type": "polygon_point", "polygon_point_coordinate": (49.641125, 14.300975)},
            {"type": "polygon_point", "polygon_point_coordinate": (49.394744, 14.611833)},
            {"type": "polygon_point", "polygon_point_coordinate": (49.165038, 14.896331)},
        ]
    }),
    ("LKP2 Temelin - kruh", {
        "name": "LKP2 TEMELÍN",
        "airspace_class": "P",
        "category": "Prohibited Area",
        "upper_limit": "5000 FT AMSL",
        "lower_limit": "GND",
        "draw_commands": [
            {"type": "circle", "circle_center_coordinate": (49.179091, 14.375492), "circle_radius": "1.1", "radius_unit": "NM"}
        ]
    }),
    ("LKP4 vlasim - polygon", {
        "name": "LKP4 VLAŠIM",
        "airspace_class": "P",
        "category": "Prohibited Area",
        "upper_limit": "5000 FT AMSL",
        "lower_limit": "GND",
        "draw_commands": [
            {"type": "polygon_point", "polygon_point_coordinate": (49.706608, 14.8991)},
            {"type": "polygon_point", "polygon_point_coordinate": (49.681472, 14.965933)},
            {"type": "polygon_point", "polygon_point_coordinate": (49.661317, 14.931878)},
        ]
    }),
    ("TRA62 Nymburk", {
        "name": "LKTRA62 NYMBURK",
        "airspace_class": "R",
        "category": "Temporary Reserved Area",
        "upper_limit": "FL245",
        "lower_limit": "3000 FT AMSL",
        "draw_commands": [
            {"type": "polygon_point", "polygon_point_coordinate": (50.476389, 15.169722)},
            {"type": "polygon_point", "polygon_point_coordinate": (50.385, 15.387778)},
            {"type": "polygon_point", "polygon_point_coordinate": (50.185833, 15.382222)},
            {"type": "arc",
             "arc_center_coordinate": (50.095833, 14.265556),
             "arc_direction": "-",
             "arc_start_point_coordinate": (50.185556, 14.9775),
             "arc_end_point_coordinate": (50.235833, 14.958056)
            }
        ]
    })
]

# === Helper funkce pro načtení souboru ===
def load_test_file(filename):
    file_path = os.path.join(TEST_STRINGS_DIR, f"{filename}.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# === Test pro třídu Extractor ===
@pytest.mark.parametrize("filename, expected_values", PLAIN_TEXT_FILES)
def test_extractor(filename, expected_values):
    """ Test funkčnosti Extractor s použitím testovacích souborů """
    input_text = load_test_file(filename)
    extractor = Extractor(input_text)

    # Provedeme extrakci
    airspace = extractor.to_airspace()

    # === Ověříme, že jsou naplněny očekávané atributy ===
    for key, value in expected_values.items():
        assert getattr(airspace, key) == value, f"Chyba v {key} pro {filename}"
