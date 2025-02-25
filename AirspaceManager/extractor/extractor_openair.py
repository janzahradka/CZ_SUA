from .extractor import Extractor
from AirspaceManager.airspace import Airspace
from typing import Optional
import re
import unicodedata
from AirspaceManager.extractor.convertor import Convertor




class ExtractorOpenAir(Extractor):
    """ ExtractorOpenAir pro extrakci z OpenAir formátu """

    def __init__(self, input_text):
        cleaned_text = self.remove_diacritics(input_text)
        cleaned_text = self.remove_comments(cleaned_text)
        self.text = cleaned_text
        self.lines = self.text.splitlines()
        self.name: Optional[str] = None
        self.airspace_class: Optional[str] = None
        self.category: Optional[str] = None
        self.frequency: Optional[str] = None
        self.station_name: Optional[str] = None
        self.upper_limit: Optional[dict] = None
        self.lower_limit: Optional[dict] = None
        self.draw_commands: list = []

    def get_airspace_data(self):
        self.extract_name()
        self.extract_airspace_class()
        self.extract_category()
        self.extract_frequency()
        self.extract_station_name()
        self.extract_upper_limit()
        self.extract_lower_limit()
        self.extract_draw_commands()

    def to_airspace(self):
        """ Naplní a vrátí objekt Airspace s daty z Extractoru """
        self.get_airspace_data()  # Nejprve vytěžíme data
        return Airspace(
            name=self.name,
            airspace_class=self.airspace_class,
            category=self.category,
            frequency=self.frequency,
            station_name=self.station_name,
            upper_limit=self.upper_limit,
            lower_limit=self.lower_limit,
            draw_commands=self.draw_commands
        )

    def remove_diacritics(self,text: str) -> str:
        normalized = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in normalized if not unicodedata.combining(c)])

    def remove_comments(self, text: str) -> str:
        """
        Odstraní komentáře z OpenAir textu.
        - Odstraní celé řádky začínající na '*'
        - Odstraní vše od '*' na konci řádku, pokud není na začátku
        """
        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Pokud řádek začíná na *, je to celý komentář a přeskočíme ho
            if line.startswith('*'):
                continue

            # Odstraníme komentář na konci řádku (vše od * dál), pokud není na začátku
            line = re.split(r"\s*\*.*", line)[0].strip()

            # Přidáme jen nekomentované řádky
            if line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def extract_name(self):
        """ Extrakce názvu prostoru (AN) a přiřazení k self.name """
        for line in self.lines:
            if line.startswith("AN"):
                self.name = line.split("AN ")[1].strip()
                break  # bude jen jeden AN v prostoru
        return self.name

    def extract_airspace_class(self):
        """ Extrakce třídy prostoru (AC) """
        for line in self.lines:
            if line.startswith("AC"):
                self.airspace_class = line.split("AC ")[1].strip()
                break # bude jen jeden AC v prostoru
        return self.airspace_class

    def extract_category(self):
        """ Extrakce kategorie prostoru (AY) """
        for line in self.lines:
            if line.startswith("AY"):
                self.category = line.split("AY ")[1].strip()
                break # bude jen jeden AY v prostoru
        return self.category

    def extract_frequency(self):
        """ Extrakce frekvence (AF) """
        for line in self.lines:
            if line.startswith("AF"):
                self.frequency = line.split("AF ")[1].strip()
        return self.frequency

    def extract_station_name(self):
        """ Extrakce názvu stanoviště (AG) """
        for line in self.lines:
            if line.startswith("AG"):
                self.station_name = line.split("AG ")[1].strip()
        return self.station_name

    def extract_limit(self, text):
        pattern = re.compile(r"""
            (?:FL\s*(\d+))|            # Match Flight Level (FL95, FL 95)
            (?:(\d+)\s*(AGL|MSL))|      # Match feet with units (1000 ft AGL, 2000 ft MSL)
            (GND)                      # Match GND
        """, re.IGNORECASE | re.VERBOSE)

        match = pattern.search(text)
        if match:
            fl_value, feet_value, unit, gnd = match.groups()  # Použijeme .groups()

            # Flight level
            if fl_value:
                return {
                    "value": int(fl_value),
                    "unit": "FL"
                }

            # Feet s jednotkou (AGL nebo MSL)
            elif feet_value and unit:
                return {
                    "value": int(feet_value),
                    "unit": unit.upper()
                }

            # GND (Ground Level)
            elif gnd:
                return {
                    "value": 0,
                    "unit": "GND"
                }
         # Pokud nic nesedí, vrátíme None
        return None

    def extract_upper_limit(self):
        """ Extrakce horní vertikální hranice (AH) FL 95, 1000 AGL, 1000 MSL """
        for line in self.lines:
            if line.startswith("AH"):
                upper_limit_raw = line.split("AH ")[1].strip()
                self.upper_limit = self.extract_limit(upper_limit_raw)
        return self.upper_limit

    def extract_lower_limit(self):
        """ Extrakce spodní vertikální hranice (AL) """
        for line in self.lines:
            if line.startswith("AL"):
                lower_limit_raw = line.split("AL ")[1].strip()
                self.lower_limit = self.extract_limit(lower_limit_raw)
        return self.lower_limit

    def extract_draw_commands(self):
        """ Extrakce příkazů kreslení (DP, DC, DB, V X=, V D=) """
        self.draw_commands = []
        current_center = None
        current_direction = "+"

        for line in self.lines:
            if line.startswith("DP"):
                coordinate = line.split("DP ")[1].strip()
                # === Použití Convertor.detect_and_convert() ===
                try:
                    lat, lon = Convertor.detect_and_convert(coordinate)
                    # === Uložíme jako tuple ===
                    self.draw_commands.append({
                        "type": "polygon_point",
                        "polygon_point_coordinate": (lat, lon)
                    })
                except ValueError as e:
                    print(f"Chyba při konverzi souřadnic: {coordinate}. {e}")

            elif line.startswith("V X="):
                current_center = line.split("V X=")[1].strip()
                try:
                    lat, lon = Convertor.detect_and_convert(current_center)
                    current_center = (lat, lon)  # === Uložíme jako tuple ===
                except ValueError as e:
                    print(f"Chyba při konverzi souřadnic středu: {current_center}. {e}")

            elif line.startswith("V D="):
                current_direction = line.split("V D=")[1].strip()

            elif line.startswith("DC"):
                radius = line.split("DC ")[1].strip().split(" ")[0]
                self.draw_commands.append({
                    "type": "circle",
                    "circle_center_coordinate": current_center,
                    "circle_radius": radius,
                    "radius_unit": "NM"
                })

            elif line.startswith("DB"):
                start, end = line.split("DB ")[1].split(",")
                try:
                    start_lat, start_lon = Convertor.detect_and_convert(start.strip())
                    end_lat, end_lon = Convertor.detect_and_convert(end.strip())
                    # === Uložíme jako tuple ===
                    self.draw_commands.append({
                        "type": "arc",
                        "arc_center_coordinate": current_center,
                        "arc_direction": current_direction,
                        "arc_start_point_coordinate": (start_lat, start_lon),
                        "arc_end_point_coordinate": (end_lat, end_lon)
                    })
                except ValueError as e:
                    print(f"Chyba při konverzi souřadnic oblouku: {start}, {end}. {e}")

        return self.draw_commands
