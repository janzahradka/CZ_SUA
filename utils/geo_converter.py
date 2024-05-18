# main module for geo converting utils
# the part of this code was created using ChatGPT4
import re

def parse_various_formats(coord_str):
    # This function parse various input text formats of the coordinates and converts it to decimal format
    # Define possible patterns
    patterns = [
            # N41°16'36" E017°51'56"
        r'(?P<lat_hem1>[NS])?(?P<lat_deg>\d{1,2})°\s?(?P<lat_min>\d{1,2})\'\s?(?P<lat_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lat_hem2>[NS])?\s?(?P<lon_hem1>[EW])?(?P<lon_deg>\d{1,3})°\s?(?P<lon_min>\d{1,2})\'\s?(?P<lon_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lon_hem2>[EW])?',

            # 49° 48' 51" N, 15° 12' 06" E
        r'(?P<lat_hem1>[NS])?(?P<lat_deg>\d{1,2})°\s?(?P<lat_min>\d{1,2})\'\s?(?P<lat_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lat_hem2>[NS])?,\s?(?P<lon_hem1>[EW])?(?P<lon_deg>\d{1,3})°\s?(?P<lon_min>\d{1,2})\'\s?(?P<lon_sec>\d{1,2}(?:,\d{1,2})?)"\s?(?P<lon_hem2>[EW])?',

            # 43 02 40,66 N 014 09 25,97 E
        r'(?P<lat_deg>\d{2})\s?(?P<lat_min>\d{2})\s?(?P<lat_sec>\d{2}(?:,\d{1,2})?)\s?(?P<lat_hem>[NS])?\s?(?P<lon_deg>\d{3})\s?(?P<lon_min>\d{2})\s?(?P<lon_sec>\d{2}(?:,\d{1,2})?)\s?(?P<lon_hem>[EW])',

            # 49.7689256N, 17.0833339E
        r'(?P<lat>\d{1,2}\.\d+)(?P<lat_hem>[NS]),\s?(?P<lon>\d{1,3}\.\d+)(?P<lon_hem>[EW])'
    ]
    for pattern in patterns:
        match = re.search(pattern, coord_str)
        if match:
            details = match.groupdict()

            # Resolve the hemisphere position (beginning or end)
            lat_hem = details.get('lat_hem1') or details.get('lat_hem2') or details.get('lat_hem')
            lon_hem = details.get('lon_hem1') or details.get('lon_hem2') or details.get('lon_hem')

            if 'lat' in details:
                # Convert direct decimal values
                lat_decimal = float(details['lat'])
                if lat_hem == 'S':
                    lat_decimal = -lat_decimal

                lon_decimal = float(details['lon'])
                if lon_hem == 'W':
                    lon_decimal = -lon_decimal

            else:
                # Replace comma with dot for decimal parsing
                lat_sec = details['lat_sec'].replace(',', '.')
                lon_sec = details['lon_sec'].replace(',', '.')

                # Calculate decimal lat and lon based on the extracted details
                lat_decimal = float(details['lat_deg']) + float(details['lat_min'])/60 + float(lat_sec)/3600
                if lat_hem == 'S':
                    lat_decimal = -lat_decimal

                lon_decimal = float(details['lon_deg']) + float(details['lon_min'])/60 + float(lon_sec)/3600
                if lon_hem == 'W':
                    lon_decimal = -lon_decimal

            return lat_decimal, lon_decimal

    raise ValueError("Invalid format or format not recognized")

def convert_all_coordinates(text):

    formatted_coords = []
    patterns = [
        r'\d{1,2}\.\d+[NS],\s?\d{1,3}\.\d+[EW]', # 40.7689256N, 17.0833339E
        r"""(?:[NS])?\d{1,2}°\s*\d{1,2}'\s*\d{1,2}"\s?\s*(?:[EW])?\d{1,3}°\s*\d{1,2}'\s*\d{1,2}"?""", # N41°16'36" E017°51'56"
        r"""\d{1,2}°\s*\d{1,2}'\s*\d{1,2}"\s?(?:[NS])?,\s*\d{1,3}°\s*\d{1,2}'\s*\d{1,2}"\s(?:[EW])?""", # 49° 48' 51" N, 15° 12' 06" E
        r'\d{2}\s?\d{2}\s?\d{2}(?:,\d{1,2})?\s?[NS]\s?\d{3}\s?\d{2}\s?\d{2}(?:,\d{1,2})?\s?[EW]' # both 420246,96N0164248,91E # 43 02 40,66 N 014 09 25,97 E
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            lat_decimal, lon_decimal = parse_various_formats(match)
            formatted_coords.append(coords_to_dms_format(lat_decimal, lon_decimal))
    if formatted_coords == []:
        raise ValueError("""No coordinates found. Check your input please.
        
Examples of supported formats:
        40.7689256N, 17.0833339E
        N41°16'36" E017°51'56"
        49° 48' 51" N, 15° 12' 06" E
        420246,96N0164248,91E
        43 02 40,66 N 014 09 25,97 E
        """)
    else:
        return formatted_coords


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


def coords_to_dms_format(lat_decimal, lon_decimal):
    lat_dms = decimal_to_dms(lat_decimal)
    lon_dms = decimal_to_dms(lon_decimal, is_longitude=True)
    return f"{lat_dms} {lon_dms}"


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
    text = """49 41 39,86 N 015 27 35,89 E -  49 39 28,00 N 015 32 41,35 E -  49 37 26,38 N 015 27 39,64 E -  49 31 03,99 N 015 27 12,46 E -  49 21 58,21 N 015 16 35,64 E -  49 14 10,97 N 014 55 19,35 E -  49 09 57,74 N 014 53 46,79 E -  49 13 46,28 N 014 49 03,76 E -  49 15 51,03 N 014 49 48,92 E -  49 24 45,44 N 015 14 27,75 E -  49 32 15,15 N 015 22 13,16 E -  49 39 33,98 N 015 22 44,00 E -  49 41 39,86 N 015 27 35,89 E"""
    # text = "nic tu není"
    # Paste whole text with coordinates here

    converted_text = convert_all_coordinates(text)
    # print(converted_text)

    for c in converted_text:
        print("DP " + c)
        # print("V X=" + c)

