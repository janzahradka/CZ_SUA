import pytest
from AirspaceManager.extractor.convertor import Convertor

# === Testovací data ===
COORDINATES_TEST_CASES = [
    # === Decimální formát ===
    ("49.7689256N, 17.0833339E", (49.768926, 17.083334)),
    ("49.7689256S, 17.0833339W", (-49.768926, -17.083334)),

    # === Kompaktní DMS formát ===
    ("500552.95N 0142437.57E", (50.097486, 14.410436)),
    ("500552.95S 0142437.57W", (-50.097486, -14.410436)),

    # === Klasický DMS s ° ' " ===
    ("N41°16'36\" E017°51'56\"", (41.276667, 17.865556)),
    ("S41°16'36\" W017°51'56\"", (-41.276667, -17.865556)),

    # === DMS s čárkou ===
    ("49° 48' 51\" N, 15° 12' 06\" E", (49.814167, 15.201667)),
    ("49° 48' 51\" S, 15° 12' 06\" W", (-49.814167, -15.201667)),

    # === DMS s čárkami bez ° ' " ===
    ("43 02 40,66 N 014 09 25,97 E", (43.044628, 14.157214)),
    ("43 02 40,66 S 014 09 25,97 W", (-43.044628, -14.157214)),

    # === Časový formát ===
    ("49:48:51 N 15:12:06 E", (49.814167, 15.201667)),
    ("49:48:51 S 15:12:06 W", (-49.814167, -15.201667))
]


# === Testy pro detekci a převod na decimal ===
@pytest.mark.parametrize("input_str, expected", COORDINATES_TEST_CASES)
def test_detect_and_convert(input_str, expected):
    """ Testuje správnou detekci a převod na decimal """
    result = Convertor.detect_and_convert(input_str)
    assert result == expected, f"Chyba při konverzi: {input_str}"


# === Testy pro převod na DMS a zpět na decimal ===
@pytest.mark.parametrize("input_str, expected", COORDINATES_TEST_CASES)
def test_decimal_to_dms_and_back(input_str, expected):
    """ Testuje obousměrnou konverzi (decimal -> DMS -> decimal) """
    decimal_lat, decimal_lon = expected

    # Převod na DMS
    dms_lat = Convertor.decimal_to_dms(decimal_lat, is_lat=True)
    dms_lon = Convertor.decimal_to_dms(decimal_lon, is_lat=False)

    # Převod zpět na decimal
    converted_lat, converted_lon = Convertor.detect_and_convert(f"{dms_lat} {dms_lon}")

    # Ověření zpětné kompatibility
    assert round(converted_lat, 6) == round(decimal_lat, 6), f"Chyba při zpětné konverzi LAT: {input_str}"
    assert round(converted_lon, 6) == round(decimal_lon, 6), f"Chyba při zpětné konverzi LON: {input_str}"
