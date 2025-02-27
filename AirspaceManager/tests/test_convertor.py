import pytest
from AirspaceManager.extractor.convertor import Convertor

# === Testovací data ===
COORDINATES_TEST_CASES = [
    # === Decimální formát ===
    ("49.7689256N, 17.0833339E", {"lat": 49.768926, "lon": 17.083334}),
    ("49.7689256S, 17.0833339W", {"lat": -49.768926, "lon": -17.083334}),

    # === Kompaktní DMS formát ===
    ("500552.95N 0142437.57E", {"lat": 50.098042, "lon": 14.410436}),
    ("500552.95S 0142437.57W", {"lat": -50.098042, "lon": -14.410436}),

    # === Klasický DMS s ° ' " ===
    ("N41°16'36\" E017°51'56\"", {"lat": 41.276667, "lon": 17.865556}),
    ("S41°16'36\" W017°51'56\"", {"lat": -41.276667, "lon": -17.865556}),

    # === DMS s čárkou ===
    ("49° 48' 51\" N, 15° 12' 06\" E", {"lat": 49.814167, "lon": 15.201667}),
    ("49° 48' 51\" S, 15° 12' 06\" W", {"lat": -49.814167, "lon": -15.201667}),

    # === DMS s čárkami bez ° ' " ===
    ("43 02 40,66 N 014 09 25,97 E", {"lat": 43.044628, "lon": 14.157214}),
    ("43 02 40,66 S 014 09 25,97 W", {"lat": -43.044628, "lon": -14.157214}),

    # === CSDMS (Colon-separated DMS) formát ===
    ("49:48:51 N 15:12:06 E", {"lat": 49.814167, "lon": 15.201667}),
    ("49:48:51 S 15:12:06 W", {"lat": -49.814167, "lon": -15.201667}),

    # === Nepodporovaný formát (Očekává se None) ===
    ("Neplatný formát bez souřadnic", None)
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
def test_extract_coodinate_from_text(input_str, expected):
    """ Testuje správnou detekci a převod na decimal """
    result = Convertor.extract_coodinate_from_text(input_str)
    if expected == "None":
        expected = None

    # Pokud se očekává None
    if expected is None:
        assert result is None, f"Očekává se None pro '{input_str}', ale bylo: {result}"
    else:
        # Očekáváme slovník s klíči 'lat' a 'lon'
        assert isinstance(result, dict), f"Očekávám dict, ale dostal jsem {type(result)}"
        assert "lat" in result and "lon" in result, "Chybí klíče 'lat' a 'lon' v návratové hodnotě"
        # Porovnání hodnoty 'lat' a 'lon' pomocí pytest.approx
        assert result["lat"] == pytest.approx(expected["lat"], abs=1e-3), f"Chyba v LAT: {input_str}"
        assert result["lon"] == pytest.approx(expected["lon"], abs=1e-3), f"Chyba v LON: {input_str}"


# === Testy pro převod na CSDMS a zpět na decimal ===
@pytest.mark.parametrize("input_str, expected", COORDINATES_TEST_CASES)
def test_decimal_to_csdms_and_back(input_str, expected):
    """ Testuje obousměrnou konverzi (decimal -> CSDMS -> decimal) """
    decimal_1 = Convertor.extract_coodinate_from_text(input_str)
    csdms_1 = Convertor.get_csdms_from_decimal(decimal_1)
    result = Convertor.extract_coodinate_from_text(csdms_1)

    if expected == "None":
        expected = None

    # Pokud se očekává None
    if expected is None:
        assert result is None, f"Očekává se None pro '{input_str}', ale bylo: {result}"
    else:
            # Ověření zpětné kompatibility pomocí pytest.approx
        assert expected["lat"] == pytest.approx(result["lat"], abs=1e-3), f"Chyba při zpětné konverzi LAT: {input_str}"
        assert expected["lon"] == pytest.approx(result["lon"], abs=1e-3), f"Chyba při zpětné konverzi LON: {input_str}"


# === Testy pro CSDMS -> Decimal -> CSDMS ===
@pytest.mark.parametrize("input_str", CSDMS_TEST_CASES)
def test_csdms_to_decimal_and_back(input_str):
    """ Testuje obousměrnou konverzi (CSDMS -> decimal -> CSDMS) """
    # Převod na decimal (výstup je nyní dict)
    decimal = Convertor.extract_coodinate_from_text(input_str)
    result = Convertor.get_csdms_from_decimal(decimal)

    # Ověření zpětné kompatibility (porovnání vstupního a výstupního CSDMS)
    assert input_str == result, f"Chyba při zpětné konverzi CSDMS: {input_str}"
