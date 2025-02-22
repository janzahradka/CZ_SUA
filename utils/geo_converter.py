# main module for geo converting utils
# the part of this code was created using ChatGPT4
import re


# Centralizované vzory pro identifikaci i extrakci
GEOGRAPHICAL_PATTERNS = [
    {
        "pattern": r'(?P<lat_hem1>[NS])?(?P<lat_deg>\d{1,2})°\s?(?P<lat_min>\d{1,2})\'\s?(?P<lat_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lat_hem2>[NS])?\s?(?P<lon_hem1>[EW])?(?P<lon_deg>\d{1,3})°\s?(?P<lon_min>\d{1,2})\'\s?(?P<lon_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lon_hem2>[EW])?',
        "description": "Pattern for DMS with N/S/E/W",
    },
    {
        "pattern": r'(?P<lat>\d{1,2}\.\d+)(?P<lat_hem>[NS]),\s?(?P<lon>\d{1,3}\.\d+)(?P<lon_hem>[EW])',
        "description": "Pattern for Decimal Degrees with N/S/E/W suffix",
    },
    {
        "pattern": r'(?P<lat_dms>\d{6,8}\.\d+)(?P<lat_hem>[NS])\s(?P<lon_dms>\d{6,8}\.\d+)(?P<lon_hem>[EW])',
        "description": "Pattern for Compact DDDMMSS.SS format",
    },
    # Další vzory...
]

# Funkce pro identifikaci přítomnosti souřadnic v textu
def detect_coordinates(text):
    """
    Detekuje přítomnost geografických souřadnic dle centrálních patternů.
    """
    for entry in GEOGRAPHICAL_PATTERNS:
        if re.search(entry["pattern"], text):
            return True
    return False

# Funkce pro extrakci a konverzi na desetinné stupně
def parse_coordinates(text):
    """
    Extrahuje a konvertuje souřadnice z textu na desetinné stupně.
    """
    for entry in GEOGRAPHICAL_PATTERNS:
        match = re.search(entry["pattern"], text)
        if match:
            details = match.groupdict()
            return convert_details_to_decimal(details)
    raise ValueError("No valid coordinates found or unrecognized format")


# Pomocná funkce pro konverzi extrahovaných údajů
def convert_details_to_decimal(details):
    """
    Převede extrahované detaily souřadnic (např. stupně, minuty, sekundy) na desetinné formáty.
    """
    # Rozpoznání formátu a převod
    if 'lat' in details:
        # Decimal Degrees
        lat_decimal = float(details['lat'])
        lon_decimal = float(details['lon'])
        if details.get('lat_hem') == 'S':
            lat_decimal *= -1
        if details.get('lon_hem') == 'W':
            lon_decimal *= -1
    elif 'lat_dms' in details:
        # Compact formát DDDMMSS.SS
        lat_decimal = dms_compact_to_decimal(details['lat_dms'], details['lat_hem'])
        lon_decimal = dms_compact_to_decimal(details['lon_dms'], details['lon_hem'], is_longitude=True)
    else:
        # DMS (Degrees, Minutes, Seconds)
        lat_sec = float(details['lat_sec'].replace(',', '.'))
        lon_sec = float(details['lon_sec'].replace(',', '.'))
        lat_decimal = float(details['lat_deg']) + float(details['lat_min']) / 60 + lat_sec / 3600
        lon_decimal = float(details['lon_deg']) + float(details['lon_min']) / 60 + lon_sec / 3600
        if details.get('lat_hem') == 'S':
            lat_decimal *= -1
        if details.get('lon_hem') == 'W':
            lon_decimal *= -1

    return lat_decimal, lon_decimal


# Zjednodušená funkce pro hromadný převod všech souřadnic v textu
def convert_all_coordinates(text):
    """
    Najde všechny geografické souřadnice v textu a převede je do jednotného formátu DMS.
    """
    formatted_coords = []
    for entry in GEOGRAPHICAL_PATTERNS:
        matches = re.findall(entry["pattern"], text)
        for match in matches:
            # Výsledek zpravidla použijeme k extrakci a převodu
            lat_decimal, lon_decimal = parse_coordinates(match)
            formatted_coords.append(coords_to_dms_format(lat_decimal, lon_decimal))
    if not formatted_coords:
        raise ValueError("No coordinates found in the provided text.")
    return formatted_coords


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


# def parse_various_formats(coord_str):
#     """
#     Parse various input text formats of the coordinates and convert them to decimal format.
#     """
#     # Define possible patterns
#     patterns = [
#         # N41°16'36" E017°51'56"
#         r'(?P<lat_hem1>[NS])?(?P<lat_deg>\d{1,2})°\s?(?P<lat_min>\d{1,2})\'\s?(?P<lat_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lat_hem2>[NS])?\s?(?P<lon_hem1>[EW])?(?P<lon_deg>\d{1,3})°\s?(?P<lon_min>\d{1,2})\'\s?(?P<lon_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lon_hem2>[EW])?',
#
#         # 49° 48' 51" N, 15° 12' 06" E
#         r'(?P<lat_hem1>[NS])?(?P<lat_deg>\d{1,2})°\s?(?P<lat_min>\d{1,2})\'\s?(?P<lat_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lat_hem2>[NS])?,\s?(?P<lon_hem1>[EW])?(?P<lon_deg>\d{1,3})°\s?(?P<lon_min>\d{1,2})\'\s?(?P<lon_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lon_hem2>[EW])?',
#
#         # 43 02 40,66 N 014 09 25,97 E
#         r'(?P<lat_deg>\d{2})\s?(?P<lat_min>\d{2})\s?(?P<lat_sec>\d{2}(?:,\d{1,2})?)\s?(?P<lat_hem>[NS])?\s?(?P<lon_deg>\d{3})\s?(?P<lon_min>\d{2})\s?(?P<lon_sec>\d{2}(?:,\d{1,2})?)\s?(?P<lon_hem>[EW])',
#
#         # 49.7689256N, 17.0833339E
#         r'(?P<lat>\d{1,2}\.\d+)(?P<lat_hem>[NS]),\s?(?P<lon>\d{1,3}\.\d+)(?P<lon_hem>[EW])',
#
#         # 500552.95N 0142437.57E
#         r'(?P<lat_dms>\d{6,8}\.\d+)(?P<lat_hem>[NS])\s(?P<lon_dms>\d{6,8}\.\d+)(?P<lon_hem>[EW])',
#     ]
#
#     # Iterate over patterns and try to match each one
#     for pattern in patterns:
#         match = re.search(pattern, coord_str)
#         if match:
#             details = match.groupdict()
#
#             # Resolve the hemisphere position (beginning or end)
#             lat_hem = details.get('lat_hem1') or details.get('lat_hem2') or details.get('lat_hem')
#             lon_hem = details.get('lon_hem1') or details.get('lon_hem2') or details.get('lon_hem')
#
#             if 'lat' in details:
#                 # Decimální formát
#                 lat_decimal = float(details['lat'])
#                 if lat_hem == 'S':
#                     lat_decimal = -lat_decimal
#
#                 lon_decimal = float(details['lon'])
#                 if lon_hem == 'W':
#                     lon_decimal = -lon_decimal
#
#             elif 'lat_dms' in details:
#                 # Nový formát DDDMMSS.SS
#                 lat_decimal = dms_compact_to_decimal(details['lat_dms'], lat_hem)
#                 lon_decimal = dms_compact_to_decimal(details['lon_dms'], lon_hem, is_longitude=True)
#
#             else:
#                 # Replace comma with dot for decimal parsing
#                 lat_sec = details['lat_sec'].replace(',', '.')
#                 lon_sec = details['lon_sec'].replace(',', '.')
#
#                 # Calculate decimal lat and lon based on the extracted details
#                 lat_decimal = float(details['lat_deg']) + float(details['lat_min']) / 60 + float(lat_sec) / 3600
#                 if lat_hem == 'S':
#                     lat_decimal = -lat_decimal
#
#                 lon_decimal = float(details['lon_deg']) + float(details['lon_min']) / 60 + float(lon_sec) / 3600
#                 if lon_hem == 'W':
#                     lon_decimal = -lon_decimal
#
#             return lat_decimal, lon_decimal
#
#     # If no patterns match
#     raise ValueError("Invalid format or format not recognized")



# def convert_all_coordinates(text):
#     """
#     Converts various coordinate formats into a uniform DMS (Degrees, Minutes, Seconds) format: '50:28:35 N 015:10:11 E'
#
#     This function attempts to parse and format geographical coordinates provided in the input
#     text.
#
#     Examples of supported formats:
#         40.7689256N, 17.0833339E
#         40.7689256N 17.0833339E
#         N41°16'36" E017°51'56"
#         49° 48' 51" N, 15° 12' 06" E
#         500552.95N 0142437.57E
#         43 02 40,66 N 014 09 25,97 E
#
#     :param text: A string containing latitude and longitude coordinates in various formats.
#     :type text: str
#     :return: A list of formatted latitude and longitude coordinates in DMS (Degrees, Minutes,
#         Seconds) format.
#     Output example: ['50:28:35 N 015:10:11 E', '50:23:06 N 015:23:16 E', '50:11:09 N 015:22:56 E']
#     :rtype: list
#     :raises ValueError: If no valid coordinates are found in the input text, a detailed
#         error message is raised, including examples of supported formats.
#     """
#     formatted_coords = []
#     patterns = [
#         r'\d{1,2}\.\d+[NS],\s?\d{1,3}\.\d+[EW]',  # 40.7689256N, 17.0833339E
#         r"""(?:[NS])?\d{1,2}°\s*\d{1,2}'\s*\d{1,2}"\s?\s*(?:[EW])?\d{1,3}°\s*\d{1,2}'\s*\d{1,2}"?""",
#         # N41°16'36" E017°51'56"
#         r"""\d{1,2}°\s*\d{1,2}'\s*\d{1,2}"\s?(?:[NS])?,\s*\d{1,3}°\s*\d{1,2}'\s*\d{1,2}"\s(?:[EW])?""",
#         # 49° 48' 51" N, 15° 12' 06" E
#         r'\d{6,8}\.\d+[NS]\s\d{6,8}\.\d+[EW]',  # 500552.95N 0142437.57E
#     ]
#     for pattern in patterns:
#         matches = re.findall(pattern, text)
#         for match in matches:
#             lat_decimal, lon_decimal = parse_various_formats(match)
#             formatted_coords.append(coords_to_dms_format(lat_decimal, lon_decimal))
#     if formatted_coords == []:
#         raise ValueError("""No coordinates found. Check your input please.""")
#     else:
#         return formatted_coords

def decimal_to_dms(decimal_degree, is_longitude=False):
    # Determine the hemisphere (N/S or E/W) and make degree positive for calculations
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
    seconds = round((minutes_decimal - minutes) * 60)  # Round to 0 decimal places

    # Return formatted string
    if is_longitude:
        return f"{degrees:03}:{minutes:02}:{seconds:02} {hemisphere}"
    else:
        return f"{degrees:02}:{minutes:02}:{seconds:02} {hemisphere}"


def coords_to_dms_format(lat_decimal: float, lon_decimal: float) -> str:
    """
    Convert geographic coordinates from decimal degrees to degrees, minutes, and seconds (DMS) format.

    This function processes latitude and longitude in decimal degrees and converts them to their corresponding
    DMS format representation. The resulting format is returned as a single formatted string, useful for
    geographic and spatial representation contexts.

    Returns example output: '50:05:45 N 014:15:56 E'
    """
    lat_dms = decimal_to_dms(lat_decimal)
    lon_dms = decimal_to_dms(lon_decimal, is_longitude=True)
    return f"{lat_dms} {lon_dms}"


def print_label(label, width=50):
    print("")
    before_after = "-" * ((width - len(label)) // 2)
    print(f"{before_after} {label} {before_after}")


if __name__ == "__main__":
    #

    # Testing with the given text
    # text = """the first is 40.7689256N, 17.0833339E a taky nějak takhle
    # the second is  N41°16'36" E017°51'56"
    # the third 420246,96N0164248,91E asdf
    # the fourth  43 02 40,66 N 014 09 25,97 E
    # and finally ARP: 44° 48' 51" N, 15° 12' 06" E
    # """

    # text = """ARP: 40° 48' 51" N, 15° 12' 06" E ARP: 41° 48' 51" N, 15° 12' 06" E ARP: 42° 48' 51" N, 15° 12' 06" E """
    text = """LKTRA62 NYMBURK
502835.45N 0151011.21E -
502305.85N 0152316.12E -
501108.78N 0152255.61E -
501108.54N 0150324.04E -
501107.99N 0145839.41E"""
    # Paste whole text with coordinates here

    if detect_coordinates(text):
        print("Coordinates detected!")
        converted = convert_all_coordinates(text)
        # print("Converted Coordinates:", converted)
    else:
        print("No coordinates found.")

    # converted_text = convert_all_coordinates(text)
    # # print(converted_text)
    #
    #
    # print_label("POLYGON")
    # for c in converted_text:
    #     print("DP " + c)
    #
    # if len(converted_text) == 1:
    #     if "clockwise" in text.lower():
    #         if "counter" in text.lower() or "anti" in text.lower():
    #             print_label("ARC Anticlockwise")
    #             for c in converted_text:
    #                 print(f"V X= {c} * ARP () R ()NM")
    #                 print("V D=-")
    #         else:
    #             print_label("ARC Clockwise")
    #             for c in converted_text:
    #                 print(f"V X= {c} * ARP () R ()NM")
    #                 print("V D=+")
    #     else:
    #         if "circle" in text.lower():
    #             print_label("CIRCLE")
    #             for c in converted_text:
    #                 print(f"V X= {c} * ARP ()")
    #                 print("DC () * R NM")






