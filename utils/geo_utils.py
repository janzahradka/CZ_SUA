# Module for handeling coordinates

import re

GEOGRAPHICAL_PATTERNS  = [
    # 49.7689256N, 17.0833339E - Decimální formát
    r'(?P<lat>[0-8]\d\.\d{1,7})(?P<lat_hem>[NS]),\s?(?P<lon>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)\.\d{1,7})(?P<lon_hem>[EW])',
    #
    # 500552.95N 0142437.57E - Kompaktní DMS formát
    r'(?P<lat_dms>([0-8][0-9]|\d)[0-5]\d[0-5]\d\.\d{1,2})(?P<lat_hem>[NS])\s(?P<lon_dms>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)[0-5]\d[0-5]\d\.\d{1,2})(?P<lon_hem>[EW])',
    #
    # N41°16'36" E017°51'56" - DMS formát s ° ' "
    r'(?P<lat_hem>[NS])(?P<lat_deg>([0-8][0-9]|\d))°\s?(?P<lat_min>[0-5]\d)\'\s?(?P<lat_sec>[0-5]\d(?:,\d{1,2})?)",?\s?(?P<lon_hem>[EW])(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))°\s?(?P<lon_min>[0-5]\d)\'\s?(?P<lon_sec>[0-5]\d(?:,\d{1,2})?)"',
    #
    # 49° 48' 51" N, 15° 12' 06" E - DMS s čárkou
    r'(?P<lat_deg>([0-8][0-9]|\d))°\s?(?P<lat_min>[0-5]\d)\'\s?(?P<lat_sec>[0-5]\d)"\s?(?P<lat_hem>[NS]),?\s?(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))°\s?(?P<lon_min>[0-5]\d)\'\s?(?P<lon_sec>[0-5]\d(?:,\d{1,2})?)"\s?(?P<lon_hem>[EW])',

    # 43 02 40,66 N 014 09 25,97 E - DMS s čárkami
    r'(?P<lat_deg>([0-8][0-9]|\d))\s?(?P<lat_min>[0-5]\d)\s?(?P<lat_sec>[0-5]\d(?:,\d{1,2})?)\s?(?P<lat_hem>[NS])\s?(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))\s?(?P<lon_min>[0-5]\d)\s?(?P<lon_sec>[0-5]\d(?:,\d{1,2})?)\s?(?P<lon_hem>[EW])',

    # 49:48:51 N 15:12:06 E - Časový formát
    r'(?P<lat_deg>([0-8][0-9]|\d)):(?P<lat_min>[0-5]\d):(?P<lat_sec>[0-5]\d)\s?(?P<lat_hem>[NS])\s+(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)):(?P<lon_min>[0-5]\d):(?P<lon_sec>[0-5]\d)\s?(?P<lon_hem>[EW])'
]


"""
Tato konstanta definuje seznam regulárních výrazů pro zpracování geografických souřadnic ve
více formátech. Každý regulární výraz pokrývá jednu z těchto forem:

1. N41°16'36" E017°51'56"
2. 49° 48' 51" N, 15° 12' 06" E
3. 43 02 40,66 N 014 09 25,97 E
4. 49.7689256N, 17.0833339E
5. 500552.95N 0142437.57E
"""


def dms_compact_to_decimal(dms, hemisphere, is_longitude=False):
    """
    Converts DDDMMSS.SS format to decimal degrees.
    """
    # Rozdělení na stupně, minuty a sekundy
    degrees = int(dms[:3 if is_longitude else 2])  # 3 číslice pro délku, 2 pro šířku
    minutes = int(dms[3 if is_longitude else 2:5 if is_longitude else 4])
    seconds = float(dms[5 if is_longitude else 4:])

    # Převod na desetinný formát
    decimal = degrees + minutes / 60 + seconds / 3600

    # Přidáme správné znaménko podle polokoule
    if hemisphere in ['S', 'W']:
        decimal *= -1
    return decimal


def extract_geo_coordinate(coord_str) -> tuple[float, float] | None:
    """
    Extracts coordinates from given text using GEOGRAPHICAL_PATTERNS for different coordinate formats and converts them to decimal format.
    If no coordinate is found -> returns None
    """

    # Iterate over patterns and try to match each one
    for pattern in GEOGRAPHICAL_PATTERNS:
        match = re.search(pattern, coord_str)
        if match:
            details = match.groupdict()

            # Resolve the hemisphere position (beginning or end)
            lat_hem = details.get('lat_hem1') or details.get('lat_hem2') or details.get('lat_hem')
            lon_hem = details.get('lon_hem1') or details.get('lon_hem2') or details.get('lon_hem')

            if 'lat' in details:
                # Decimální formát
                lat_decimal = float(details['lat'])
                if lat_hem == 'S':
                    lat_decimal = -lat_decimal

                lon_decimal = float(details['lon'])
                if lon_hem == 'W':
                    lon_decimal = -lon_decimal

            elif 'lat_dms' in details:
                # Nový formát DDDMMSS.SS
                lat_decimal = dms_compact_to_decimal(details['lat_dms'], lat_hem)
                lon_decimal = dms_compact_to_decimal(details['lon_dms'], lon_hem, is_longitude=True)


            else:
                # Replace comma with dot for decimal parsing
                lat_sec = details['lat_sec'].replace(',', '.')
                lon_sec = details['lon_sec'].replace(',', '.')

                # Calculate decimal lat and lon based on the extracted details
                lat_decimal = float(details['lat_deg']) + float(details['lat_min']) / 60 + float(lat_sec) / 3600
                if lat_hem == 'S':
                    lat_decimal = -lat_decimal

                lon_decimal = float(details['lon_deg']) + float(details['lon_min']) / 60 + float(lon_sec) / 3600
                if lon_hem == 'W':
                    lon_decimal = -lon_decimal

            return lat_decimal, lon_decimal

    # If no patterns match
    return None


def decimal_to_dms(decimal_degree, is_longitude=False) -> str:
    """ Convert decimal degrees to degrees, minutes, and seconds (DMS) format."""
    if is_longitude:
        if decimal_degree < 0:
            hemisphere = 'W'
            decimal_degree = -decimal_degree
        else:
            hemisphere = 'E'
    else:
        if decimal_degree < 0:
            hemisphere = 'S'
            decimal_degree = -decimal_degree
        else:
            hemisphere = 'N'

    # Convert to DMS (Degrees, Minutes, Seconds)
    degrees = int(decimal_degree)
    minutes_decimal = (decimal_degree - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = round((minutes_decimal - minutes) * 60)  # Zaokrouhlíme sekundy na celé číslo

    # Správné zaokrouhlení a přenos zbytků
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1

    # Formátování s pevnou strukturou (bez desetinné tečky)
    return f"{degrees:02}:{minutes:02}:{seconds:02} {hemisphere}"




def coords_to_dms_format(lat_decimal: float, lon_decimal: float) -> str:
    """
    Convert geographic coordinates from decimal degrees to degrees, minutes, and seconds (DMS) format.

    This function processes latitude and longitude in decimal degrees and converts them to their corresponding
    DMS format representation. The resulting format is returned as a single formatted string, useful for
    geographic and spatial representation contexts.
    input example: 50.055295, 14.243757
    Returns example output: '50:05:45 N 014:15:56 E'
    """
    lat_dms = decimal_to_dms(lat_decimal)
    lon_dms = decimal_to_dms(lon_decimal, is_longitude=True)
    return f"{lat_dms} {lon_dms}"


def extract_coordinate_to_dms(coordinate: str) -> str:
    """
    Converts coordinate string in any of GEOGRAPHIC_PATTERNS to DMS format such as:
        input example:
                50:05:53 N 014:24:38 E
                49° 48' 51" N, 15° 12' 06" E
                43 02 40,66 N 014 09 25,97 E
                49.7689256N, 17.0833339E
                500552.95N 0142437.57E
        output example: '41:16:36 N 017:51:56 E'
    Returns an empty string if no coordinate is found.
    """
    # Zavoláme funkci na extrakci souřadnic
    coordinates = extract_geo_coordinate(coordinate)

    # Zkontrolujeme, zda byly souřadnice nalezeny
    if coordinates:
        # Pokud ano, převedeme na DMS formát
        return coords_to_dms_format(*coordinates)
    else:
        # Pokud nebyly nalezeny, vrátíme prázdný řetězec nebo jiný výstup podle potřeby
        return ""


def contains_coordinate_with_index(coord_str) -> tuple[bool, int]:
    """
    Determines whether a given string contains geographical coordinates and their position in the string.
    :rtype: tuple[bool, int] - Returns a tuple where the first element is whether a coordinate is found (True/False),
            and the second element is the starting index of the coordinate in the string (-1 if not found).
    """
    for pattern in GEOGRAPHICAL_PATTERNS:
        match = re.search(pattern, coord_str)
        if match:  # Pokud byl nalezen shoda
            return True, match.start()  # Vrací True a počáteční index shody
    return False, -1  # Pokud není souřadnice nalezena


def extract_radius_and_unit(text):
    """
    Prohledá řetězec a extrahuje informaci o poloměru a jednotkách.

    :param text: Vstupní řetězec (např. "3 NM", "28 KM", "3.5 NM").
    :return: Tuple ve formátu (radius, unit) nebo (None, None) pokud nic nenajde.
    """
    # Regulární výraz pro číslo (celé nebo desetinné) následované jednotkou (NM nebo KM)
    match = re.search(r'(\d+\.?\d*)\s*(NM|KM)', text, re.IGNORECASE)

    if match:
        # Extrahujeme číslo (radius) a jednotku (unit)
        radius = float(match.group(1))  # Změníme číslo na float
        unit = match.group(2).upper()  # Jednotku převedeme na velká písmena, např. NM nebo KM
        return radius, unit
    else:
        # Pokud žádný radius neexistuje, vrátíme None
        return None, None


def normalize_radius(radius, unit):
    """
    Normalizuje poloměr podle zadané jednotky.
    V případě "KM" převede na námořní míle (NM).

    :param radius: Číselná hodnota poloměru.
    :param unit: Jednotka poloměru ("NM" nebo "KM").
    :return: Normalizovaný poloměr v NM.
    """
    # Kontrola jednotky a případná konverze na NM
    if unit == "NM":
        return round(radius, 3)
        # Beze změny
    elif unit == "KM":
        # Převod z kilometrů na námořní míle
        return round(radius * 0.539957, 3)
    else:
        # Pokud je jednotka neznámá
        raise ValueError(f"Neznámá jednotka: {unit}")


def get_lines_by_coordinates(text: str) -> list[str]:
    """
    Rozdělí text na základě geografických shod, ale pouze podle začátku shod.
    Shody jsou deduplikovány a překrývající shody způsobí výjimku.
    """

    # Odstraníme zalomení řádků a vytvoříme jednolitý řetězec
    single_line_text = text.replace("\n", " ")

    # Seznam pro uložení indexů všech shod (jen jejich začátek)
    match_indices = []

    # Iterace přes všechny vzory v GEOGRAPHICAL_PATTERNS
    for pattern in GEOGRAPHICAL_PATTERNS:
        for match in re.finditer(pattern, single_line_text):
            # Uložíme start index shody
            match_indices.append(match.start())

    # Deduplication: odstranění duplicitních indexů
    match_indices = sorted(set(match_indices))

    # Kontrola překryvů (jen pro případ, že by existovaly duplicity, i když by neměly)
    for i in range(len(match_indices) - 1):
        start_current = match_indices[i]
        start_next = match_indices[i + 1]
        # Pokud dvě shody začínají příliš blízko (například další shoda by začínala uvnitř předchozí části)
        if start_current >= start_next:
            raise ValueError(
                f"Překryv nalezen mezi shodami na pozicích {start_current} a {start_next}."
            )

    # Rozdělení textu na části podle počátečních indexů shod
    split_lines = []
    last_index = 0

    for start in match_indices:
        # Text před shodou přidáme jako součást seznamu
        before_match = single_line_text[last_index:start].strip()
        if before_match:
            split_lines.append(before_match)
        #poslední prvek
        if start == max(match_indices):
            split_lines.append(single_line_text[start:].strip())

        # Posuneme `last_index` na začátek další části
        last_index = start

    return split_lines
# if __name__ == "__main__":
#

#     text = """
#        N41°16'36" E017°51'56"
#        S41°16'36" W017°51'56"
#        49° 48' 51" N, 15° 12' 06" E
#        49° 48' 51" S, 15° 12' 06" W
#        43 02 40,66 N 014 09 25,97 E
#        43 02 40,66 S 014 09 25,97 W
#        49.7689256N, 17.0833339E
#        49.7689256S, 17.0833339W
#        500552.95N 0142437.57E
#        500552.95S 0142437.57W
#        495259.83N 0144915.52E
#        495959.83N 0145959.99E
#     """
#
#     for line in text.splitlines():
#         if line.strip():
#             print(extract_coordinate_to_dms(line))
#
# examples = [
#     "3 NM",
#     "3.5 NM",
#     "28 NM",
#     "3 KM",
#     "3.5 KM",
#     "28 KM",
#     "text bez informací"
# ]
#
# for example in examples:
#     radius, unit = extract_radius_and_unit(example)
#     print(f"Vstup: '{example}' -> radius: {radius}, unit: {unit}")
#
# for example in  examples:
#     radius, unit = extract_radius_and_unit(example)
#     if radius is not None and unit is not None:
#         normalized = normalize_radius(radius, unit)
#         print(f"Vstup: radius = {radius}, unit = {unit} -> Normalizovaný radius: {normalized} NM")

