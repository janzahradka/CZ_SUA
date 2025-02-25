import re

class Convertor:
    """ Třída pro konverzi geografických souřadnic mezi formáty """

    # Přesunuté a doplněné COORDINATES_PATTERNS
    COORDINATES_PATTERNS = [
        # 49.7689256N, 17.0833339E - Decimální formát
        re.compile(r'(?P<lat>[0-8]\d\.\d{1,7})(?P<lat_hem>[NS]),\s?(?P<lon>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)\.\d{1,7})(?P<lon_hem>[EW])'),

        # 500552.95N 0142437.57E - Kompaktní DMS formát
        re.compile(r'(?P<lat_dms>([0-8][0-9]|\d)[0-5]\d[0-5]\d\.\d{1,2})(?P<lat_hem>[NS])\s(?P<lon_dms>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)[0-5]\d[0-5]\d\.\d{1,2})(?P<lon_hem>[EW])'),

        # N41°16'36" E017°51'56" - DMS formát s ° ' "
        re.compile(r'(?P<lat_hem>[NS])(?P<lat_deg>([0-8][0-9]|\d))°\s?(?P<lat_min>[0-5]\d)\'\s?(?P<lat_sec>[0-5]\d(?:,\d{1,2})?)",?\s?(?P<lon_hem>[EW])(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))°\s?(?P<lon_min>[0-5]\d)\'\s?(?P<lon_sec>[0-5]\d(?:,\d{1,2})?)"'),

        # 49° 48' 51" N, 15° 12' 06" E - DMS s čárkou
        re.compile(r'(?P<lat_deg>([0-8][0-9]|\d))°\s?(?P<lat_min>[0-5]\d)\'\s?(?P<lat_sec>[0-5]\d)"\s?(?P<lat_hem>[NS]),?\s?(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))°\s?(?P<lon_min>[0-5]\d)\'\s?(?P<lon_sec>[0-5]\d(?:,\d{1,2})?)"\s?(?P<lon_hem>[EW])'),

        # 43 02 40,66 N 014 09 25,97 E - DMS s čárkami
        re.compile(r'(?P<lat_deg>([0-8][0-9]|\d))\s?(?P<lat_min>[0-5]\d)\s?(?P<lat_sec>[0-5]\d(?:,\d{1,2})?)\s?(?P<lat_hem>[NS])\s?(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))\s?(?P<lon_min>[0-5]\d)\s?(?P<lon_sec>[0-5]\d(?:,\d{1,2})?)\s?(?P<lon_hem>[EW])'),

        # 49:48:51 N 15:12:06 E - Časový formát
        re.compile(r'(?P<lat_deg>([0-8][0-9]|\d)):(?P<lat_min>[0-5]\d):(?P<lat_sec>[0-5]\d)\s?(?P<lat_hem>[NS])\s+(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)):(?P<lon_min>[0-5]\d):(?P<lon_sec>[0-5]\d)\s?(?P<lon_hem>[EW])')
    ]

    @staticmethod
    def dms_to_decimal(deg, min_, sec, hem) -> float:
        """
        Převádí hodnoty DMS na desetinný formát.
        """
        decimal = float(deg) + float(min_) / 60 + float(sec) / 3600
        if hem in ['S', 'W']:
            decimal *= -1
        return round(decimal, 6)

    @classmethod
    def detect_and_convert(cls, coordinate_str: str) -> tuple:
        """
        Detekuje formát souřadnic pomocí COORDINATES_PATTERNS a převede na decimal.
        """
        for pattern in cls.COORDINATES_PATTERNS:
            match = pattern.search(coordinate_str)
            if match:
                if 'lat' in match.groupdict() and 'lon' in match.groupdict():
                    # Decimální formát
                    lat = float(match.group('lat'))
                    if match.group('lat_hem') in ['S']:
                        lat *= -1
                    lon = float(match.group('lon'))
                    if match.group('lon_hem') in ['W']:
                        lon *= -1
                    return lat, lon

                elif 'lat_dms' in match.groupdict() and 'lon_dms' in match.groupdict():
                    # Kompaktní DMS formát
                    lat = cls.dms_to_decimal(match.group('lat_dms')[:2], match.group('lat_dms')[2:4], match.group('lat_dms')[4:], match.group('lat_hem'))
                    lon = cls.dms_to_decimal(match.group('lon_dms')[:3], match.group('lon_dms')[3:5], match.group('lon_dms')[5:], match.group('lon_hem'))
                    return lat, lon

                elif 'lat_deg' in match.groupdict() and 'lon_deg' in match.groupdict():
                    # Klasický DMS formát
                    lat = cls.dms_to_decimal(match.group('lat_deg'), match.group('lat_min'), match.group('lat_sec'), match.group('lat_hem'))
                    lon = cls.dms_to_decimal(match.group('lon_deg'), match.group('lon_min'), match.group('lon_sec'), match.group('lon_hem'))
                    return lat, lon

        raise ValueError(f"Neznámý formát souřadnic: {coordinate_str}")
