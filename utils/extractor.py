import re


def extract_coordinates(text, output_format='degrees_minutes_seconds'):
    # Regular expression patterns for different coordinate formats
    patterns = [
        r"(\d+\.\d+),\s*(-?\d+\.\d+)",                                              # Decimal degrees format: 12.345, -67.890
        r"(\d+°\s*\d+\.\d+\'\s*[NS]),\s*(\d+°\s*\d+\.\d+\'\s*[EW])",                # Degrees, minutes format: 12° 34.567' N, 67° 89.012' W
        r"(\d+°\s*\d+\s*\d+\.\d+\"\s*[NS]),\s*(\d+°\s*\d+\s*\d+\.\d+\"\s*[EW])",    # Degrees, minutes, seconds format: 12° 34' 56.789" N, 67° 89' 12.345" W
        r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)",                                         # Decimal degrees format without whitespace: 12.345,-67.890
        r"\b(\d{6},\d{2}[NS]\d{7},\d{2}[EW])\b"                                     # 501347,71N0132453,65E (PODBORANY) - PSN 501251,65N0131549,68E (PODBORANSKY ROHOZEC)
    ]

    coordinates = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.UNICODE)
        for match in matches:
            lat, lon = match
            # Remove non-numeric characters from latitude and longitude
            lat = re.sub(r"[^\d.-]", "", lat)
            lon = re.sub(r"[^\d.-]", "", lon)
            lat, lon = float(lat), float(lon)

            if output_format == 'decimal':
                coordinates.append((lat, lon))
            elif output_format == 'degrees':
                coordinates.append((convert_to_degrees(lat), convert_to_degrees(lon)))
            elif output_format == 'degrees_minutes':
                coordinates.append((convert_to_degrees_minutes(lat), convert_to_degrees_minutes(lon)))
            elif output_format == 'degrees_minutes_seconds':
                coordinates.append((convert_to_degrees_minutes_seconds(lat), convert_to_degrees_minutes_seconds(lon)))

    return coordinates


def convert_to_degrees(coord):
    degrees = int(coord)
    minutes = (coord - degrees) * 60
    return degrees + minutes / 100


def convert_to_degrees_minutes(coord):
    degrees = int(coord)
    minutes = (coord - degrees) * 60
    return f"{degrees}° {minutes:.3f}'"


def convert_to_degrees_minutes_seconds(coord):
    degrees = int(coord)
    minutes = int((coord - degrees) * 60)
    seconds = ((coord - degrees) * 3600) % 60
    return f"{degrees}° {minutes}' {seconds:.3f}\""

text = "The coordinates are 12.345, -67.890, and also 45° 6' 7.89\" N, 123° 45' 67.890\" W."
# text = "The coordinates are 49.7689256N, 17.0833339E."
# text = "The coordinates are 12.345, -67.890"
# text = "The coordinates are 12° 34.567' N, 67° 89.012' W"
coordinates = extract_coordinates(text, 'decimal')
print(coordinates)