import os
import pytest
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace import Airspace
from AirspaceManager.extractor.convertor import Convertor

convertor = Convertor()

# === Cesty k testovacím souborům ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_STRINGS_DIR = os.path.join(BASE_DIR, '../test_strings')

# === OpenAir soubory a očekávané výsledky ===
OPENAIR_FILES = [
    ("DROPZONE Breclav - kruh", "OpenAir", {
        "airspace_class": "Q",
        "name": "DROPZONE Breclav 119.655",
        "category": "Para Jumping Area",
        "frequencies": ['119.655'],
        "station_name": "Breclav RADIO",
        "upper_limit": {"value": 95, "unit": "FL"},
        "lower_limit": {"value": 0, "unit": "AGL"},
        "draw_commands": [{
            'type': 'circle',
            'circle_center_coordinate': convertor.extract_coodinate_from_text('48:47:27 N 016:53:33 E'),
            'circle_radius': '2', 'radius_unit': 'NM'}]
    }),
    ("LKTSA7C Jince - polygon", "OpenAir", {
        "airspace_class": "R",
        "name": "LKTSA7C JINCE 126.10",
        "frequencies": ['126.100'],
        "station_name": "PRAHA INFORMATION",
        "draw_commands": [{'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('49:49:42 N 013:56:17 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('49:48:32 N 013:57:50 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('49:45:44 N 013:51:00 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('49:47:44 N 013:52:00 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('49:49:42 N 013:56:17 E')}]
    }),
    ("TRA62 Nymburk - oblouk", "OpenAir", {
        "airspace_class": "R",
        "name": "LKTRA62 NYMBURK",
        "draw_commands": [{'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('50:28:35 N 15:10:11 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('50:23:06 N 15:23:16 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('50:11:09 N 15:22:56 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('50:11:09 N 15:03:24 E')},
                          {'type': 'arc', 'arc_center_coordinate': convertor.extract_coodinate_from_text('50:05:45 N 14:15:56 E'), 'arc_direction': '-',
                           'arc_start_point_coordinate': convertor.extract_coodinate_from_text('50:11:08 N 14:58:39 E'),
                           'arc_end_point_coordinate': convertor.extract_coodinate_from_text('50:14:09 N 14:57:29 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('50:28:34 N 15:00:04 E')},
                          {'type': 'polygon_point', 'polygon_point_coordinate': convertor.extract_coodinate_from_text('50:28:35 N 15:10:11 E')}]
    })
]


# === Helper funkce pro načtení souboru ===
def load_test_file(folder, filename):
    file_path = os.path.join(TEST_STRINGS_DIR, folder, f"{filename}.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


@pytest.mark.parametrize("filename, folder, expected_values", OPENAIR_FILES)
def test_to_airspace_filled_attributes(filename, folder, expected_values):
    """ Test funkčnosti to_airspace() pro naplnění pouze neprázdných parametrů """
    input_text = load_test_file(folder, filename)
    extractor_openair = ExtractorOpenAir(input_text)

    # === Nyní get_airspace_data voláme uvnitř to_airspace ===
    airspace = extractor_openair.to_airspace()
    print(airspace)

    # === Ověříme, že jsou naplněny očekávané atributy ===
    for key, value in expected_values.items():
        assert getattr(airspace, key) == value

    # # === Ověříme, že ostatní atributy jsou None nebo prázdné seznamy ===
    # for attr in vars(airspace):
    #     if attr not in expected_values:
    #         attr_value = getattr(airspace, attr)
    #         assert attr_value is None or attr_value == []  # Prázdné seznamy nebo None
