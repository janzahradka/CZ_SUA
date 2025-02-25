import pytest
from AirspaceManager.extractor.convertor import Convertor

# === Testovací data ===
COORDINATES_TEST_CASES = [
    # === Decimální formát ===
    ("49.7689256N, 17.0833339E", (49.768926, 17.083334)),
    ("49.7689256S, 17.0833339W", (-49.768926, -17.083334)),

    # === Kompaktní DMS formát ===
    ("500552.95N 0142437.57E", (50.098042, 14.410436)),
    ("500552.95S 0142437.57W", (-50.098042, -14.410436)),

    # === Klasický DMS s ° ' " ===
    ("N41°16'36\" E017°51'56\"", (41.276667, 17.865556)),
    ("S41°16'36\" W017°51'56\"", (-41.276667, -17.865556)),

    # === DMS s čárkou ===
    ("49° 48' 51\" N, 15° 12' 06\" E", (49.814167, 15.201667)),
    ("49° 48' 51\" S, 15° 12' 06\" W", (-49.814167, -15.201667)),

    # === DMS s čárkami bez ° ' " ===
    ("43 02 40,66 N 014 09 25,97 E", (43.044628, 14.157214)),
    ("43 02 40,66 S 014 09 25,97 W", (-43.044628, -14.157214)),

    # === CSDMS (Colon-separated DMS) formát ===
    ("49:48:51 N 15:12:06 E", (49.814167, 15.201667)),
    ("49:48:51 S 15:12:06 W", (-49.814167, -15.201667))
]

# === Testovací data pouze pro CSDMS formát ===
CSDMS_TEST_CASES = [
    "49:48:51 N 15:12:06 E",
    "49:48:51 S 115:12:06 W",
    "41:16:36 N 17:51:56 E",
    "74:59:59 S 11:51:56 W",
    "50:05:52 N 14:24:37 E",
    "50:05:52 S 14:24:37 W"
]


# === Testy pro detekci a převod na decimal ===
@pytest.mark.parametrize("input_str, expected", COORDINATES_TEST_CASES)
def test_detect_and_convert(input_str, expected):
    """ Testuje správnou detekci a převod na decimal """
    result = Convertor.detect_and_convert(input_str)
    assert result[0] == pytest.approx(expected[0], abs=1e-3)
    assert result[1] == pytest.approx(expected[1], abs=1e-3)


# === Testy pro převod na CSDMS a zpět na decimal ===
@pytest.mark.parametrize("input_str, expected", COORDINATES_TEST_CASES)
def test_decimal_to_csdms_and_back(input_str, expected):
    """ Testuje obousměrnou konverzi (decimal -> CSDMS -> decimal) """
    decimal_lat, decimal_lon = expected

    # Převod na CSDMS
    csdms_lat = Convertor.decimal_to_csdms(decimal_lat, is_longitude=False)
    csdms_lon = Convertor.decimal_to_csdms(decimal_lon, is_longitude=True)

    # Převod zpět na decimal
    converted_lat, converted_lon = Convertor.detect_and_convert(f"{csdms_lat} {csdms_lon}")

    # Ověření zpětné kompatibility pomocí pytest.approx
    assert converted_lat == pytest.approx(decimal_lat, abs=1e-3), f"Chyba při zpětné konverzi LAT: {input_str}"
    assert converted_lon == pytest.approx(decimal_lon, abs=1e-3), f"Chyba při zpětné konverzi LON: {input_str}"


# === Testy pro CSDMS -> Decimal -> CSDMS ===
@pytest.mark.parametrize("input_str", CSDMS_TEST_CASES)
def test_csdms_to_decimal_and_back(input_str):
    """ Testuje obousměrnou konverzi (CSDMS -> decimal -> CSDMS) """
    # Převod na decimal
    decimal_lat, decimal_lon = Convertor.detect_and_convert(input_str)

    # Převod zpět na CSDMS
    csdms_lat = Convertor.decimal_to_csdms(decimal_lat, is_longitude=False)
    csdms_lon = Convertor.decimal_to_csdms(decimal_lon, is_longitude=True)

    # Rekonstruovaný CSDMS formát
    reconstructed_csdms = f"{csdms_lat} {csdms_lon}"

    # Ověření zpětné kompatibility (porovnání vstupního a výstupního CSDMS)
    assert reconstructed_csdms == input_str, f"Chyba při zpětné konverzi CSDMS: {input_str}"