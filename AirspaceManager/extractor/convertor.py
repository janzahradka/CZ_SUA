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
        re.compile(r'(?P<lat_deg>([0-8][0-9]|\d))\s?(?P<lat_min>[0-5]\d)\s?(?P<lat_sec>[0-5]\d(?:[,\.]\d{1,2})?)\s?(?P<lat_hem>[NS])\s?(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d))\s?(?P<lon_min>[0-5]\d)\s?(?P<lon_sec>[0-5]\d(?:[,\.]\d{1,2})?)\s?(?P<lon_hem>[EW])'),

        # 49:48:51 N 15:12:06 E - Časový formát
        re.compile(r'(?P<lat_deg>([0-8][0-9]|\d)):(?P<lat_min>[0-6]\d):(?P<lat_sec>[0-6]\d)\s?(?P<lat_hem>[NS])\s+(?P<lon_deg>(1[0-7][0-9]|0[0-8][0-9]|[0-9][0-9]|\d)):(?P<lon_min>[0-6]\d):(?P<lon_sec>[0-6]\d)\s?(?P<lon_hem>[EW])')
    ]

    @staticmethod
    def dms_to_decimal(deg, min_, sec, hem) -> float:
        """
        Převádí hodnoty DMS na desetinný formát.
        """
        # Nahrazení čárky tečkou pro všechny části DMS
        deg = deg.replace(',', '.')
        min_ = min_.replace(',', '.')
        sec = sec.replace(',', '.')

        decimal = float(deg) + float(min_) / 60 + float(sec) / 3600
        if hem in ['S', 'W']:
            decimal *= -1
        return round(decimal, 6)

    @staticmethod
    def get_csdms_component(decimal_degree, is_longitude=False) -> str:
        """ Convert decimal degrees to degrees, minutes, and seconds (Colon-separated DMS) format."""
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

    @classmethod
    def get_csdms_from_decimal(cls, coordinate: dict) -> str | None:
        """
        Převádí celý koordinát na CSDMS formát.
        Očekává slovník s klíči 'lat' a 'lon'.

        Např.:
        {
            "lat": 49.15283,
            "lon": 17.035162
        }
        """
        if coordinate is None or "lat" not in coordinate or "lon" not in coordinate:
            return None
        else:
            lat_csdms = cls.get_csdms_component(coordinate["lat"], is_longitude=False)
            lon_csdms = cls.get_csdms_component(coordinate["lon"], is_longitude=True)

            csdms_coordinate = f'{lat_csdms} {lon_csdms}'
            return csdms_coordinate

    @staticmethod
    def decimal_to_dict(coordinate_tuple: tuple) -> dict:
        """
        Převádí tuple (lat, lon) na dict s klíči 'lat' a 'lon'.

        Např.:
        (49.15283, 17.035162) -> {
            "lat": 49.15283,
            "lon": 17.035162
        }
        """
        if not isinstance(coordinate_tuple, tuple) or len(coordinate_tuple) != 2:
            raise ValueError("Očekávám tuple s dvěma prvky: (lat, lon)")

        lat, lon = coordinate_tuple
        return {
            "lat": lat,
            "lon": lon
        }

    @classmethod
    def extract_coodinate_from_text(cls, coordinate_str: str) -> dict | None:
        """
        Detekuje formát souřadnic pomocí COORDINATES_PATTERNS a převede na decimal.
        Vrací dict:
        {
            "lat": <latitude>,
            "lon": <longitude>
        }
        """
        if coordinate_str:
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
                        # Použití decimal_to_dict()
                        return cls.decimal_to_dict((lat, lon))

                    elif 'lat_dms' in match.groupdict() and 'lon_dms' in match.groupdict():
                        # Kompaktní DMS formát
                        lat = cls.dms_to_decimal(match.group('lat_dms')[:2], match.group('lat_dms')[2:4],
                                                 match.group('lat_dms')[4:], match.group('lat_hem'))
                        lon = cls.dms_to_decimal(match.group('lon_dms')[:3], match.group('lon_dms')[3:5],
                                                 match.group('lon_dms')[5:], match.group('lon_hem'))
                        # Použití decimal_to_dict()
                        return cls.decimal_to_dict((lat, lon))

                    elif 'lat_deg' in match.groupdict() and 'lon_deg' in match.groupdict():
                        # Klasický DMS formát
                        lat = cls.dms_to_decimal(match.group('lat_deg'), match.group('lat_min'), match.group('lat_sec'),
                                                 match.group('lat_hem'))
                        lon = cls.dms_to_decimal(match.group('lon_deg'), match.group('lon_min'), match.group('lon_sec'),
                                                 match.group('lon_hem'))
                        # Použití decimal_to_dict()
                        return cls.decimal_to_dict((lat, lon))
                # Pokud není nalezen platný formát
            return None
        else:
            return None

