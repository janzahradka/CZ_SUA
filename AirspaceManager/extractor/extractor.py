import re
from typing import Optional
from AirspaceManager.extractor.convertor import Convertor
from AirspaceManager.airspace import Airspace
import unicodedata


AIRSPACE_TYPE_MAP = [
    {"name_template": "ATZ", "AC_tag": "E", "AY_tag": "Aerodrome Traffic Zone"},
    {"name_template": "CTR", "AC_tag": "D", "AY_tag": "Control Zone"},
    {"name_template": "DROPZONE", "AC_tag": "Q", "AY_tag": "Dropzone"},
    {"name_template": "LKD", "AC_tag": "Q", "AY_tag": "Dangerous Area"},
    {"name_template": "LKP", "AC_tag": "P", "AY_tag": "Prohibited Area"},
    {"name_template": "LKRMZ", "AC_tag": "E", "AY_tag": "Radio Mandatory zone"},
    {"name_template": "LKTMZ", "AC_tag": "E", "AY_tag": "Transponder Mandatory Zone"},
    {"name_template": "LKR", "AC_tag": "R", "AY_tag": "Restricted Area"},
    {"name_template": "LKTSA", "AC_tag": "R", "AY_tag": "Temporary Segregated Area"},
    {"name_template": "LKTRA", "AC_tag": "R", "AY_tag": "Temporary Reserved Area"},
    {"name_template": "MCTR", "AC_tag": "D", "AY_tag": "Military Control Zone"},
    {"name_template": "MTMA", "AC_tag": "D", "AY_tag": "Military Terminal Zone"},
    {"name_template": "NTM", "AC_tag": "R", "AY_tag": "NOTAM"},
    {"name_template": "PGZ", "AC_tag": "GS", "AY_tag": "Paragliding Zone"},
    {"name_template": "TMA", "AC_tag": "D", "AY_tag": "Terminal Manoeuvring Area"},
    {"name_template": "TRA GA", "AC_tag": "GS", "AY_tag": "GSEC"}
]

class Extractor:
    """ Extractor pro vytěžování dat z méně strukturovaného textu """

    def __init__(self, input_text):
        cleaned_text = self.remove_diacritics(input_text)
        self.text = cleaned_text
        self.lines_by_coordinates = self.get_lines_by_coordinates(cleaned_text)
        self.name: Optional[str] = None
        self.airspace_class: Optional[str] = None
        self.category: Optional[str] = None
        self.frequency: Optional[str] = None
        self.upper_limit: Optional[str] = None
        self.lower_limit: Optional[str] = None
        self.draw_commands: list = []

    def remove_diacritics(self, text: str) -> str:
        """ Odstraní diakritiku z textu """
        normalized = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in normalized if not unicodedata.combining(c)])

    def get_lines_by_coordinates(self, text: str) -> str:
        """
        Rozdělí text na základě geografických shod, ale pouze podle začátku shod.
        Shody jsou deduplikovány a překrývající shody způsobí výjimku.
        """

        # Odstraníme zalomení řádků a vytvoříme jednolitý řetězec
        single_line_text = text.replace("\n", " ")

        # Seznam pro uložení indexů všech shod (jen jejich začátek)
        match_indices = []

        # Iterace přes všechny vzory v COORDINATES_PATTERNS
        for pattern in Convertor.COORDINATES_PATTERNS:
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
            # poslední prvek
            if start == max(match_indices):
                split_lines.append(single_line_text[start:].strip())

            # Posuneme `last_index` na začátek další části
            last_index = start

        return split_lines

    def extract_name(self):
        """ Rozpoznání názvu a kódu prostoru """
        lines = self.text.splitlines()
        first_line = lines[0] if lines else ''
        match = re.match(r"([A-Z0-9]+) (.+)", first_line)
        if match:
            code, name = match.groups()
            self.name = f"{code} {name}"
        return self.name

    def extract_class(self):
        """ Rozpoznání třídy prostoru podle mapování """
        for airspace in AIRSPACE_TYPE_MAP:
            if self.name and self.name.startswith(airspace["name_template"]):
                self.airspace_class = airspace["AC_tag"]
                break
        return self.airspace_class

    def extract_category(self):
        """ Rozpoznání kategorie prostoru podle mapování """
        for airspace in AIRSPACE_TYPE_MAP:
            if self.name and self.name.startswith(airspace["name_template"]):
                self.category = airspace["AY_tag"]
                break
        return self.category

    def extract_verticals(self):
        """
        Extracts upper and lower vertical limits from text and returns them as formatted strings.
        Expected output:
            upper_limit: str - Upper limit with unit (e.g., "FL 125", "5000 MSL")
            lower_limit: str - Lower limit with unit (e.g., "1000 AGL", "0 AGL")
        expected input such as:
            FL125 / 1000 ft AGL
            FL125 / FL95
            1000 ft AGL / GND
            FL95 / GND
            FL95 / FL65
            FL95 / 2500 ft AMSL
            FL95 / 5000 ft AMSL
            FL245 / FL95

        converts:
            GND -> 0 AGL
            1000 ft AGL -> 1000 AGL
            2000 ft AMSL -> 2000 MSL
            FL95 -> FL 95
            FL245 -> FL 245

        """
        # Regulární výraz pro extrakci vertikálních limitů
        pattern = re.compile(r"""
            (?:FL\s*(\d+))|            # Match Flight Level (FL95, FL 95)
            (?:(\d+)\s*ft\s*(AGL|AMSL|MSL))|  # Match feet with units (1000 ft AGL, 2000 ft AMSL)
            (GND)                      # Match GND
        """, re.IGNORECASE | re.VERBOSE)

        # Najdi všechny shody
        matches = pattern.findall(self.text)
        if len(matches) != 2:
            raise ValueError("Expected exactly two vertical limits in the text")

        # Konverze shod na číselné hodnoty a jednotky
        limits = []
        limit_value, unit = None, None
        for match in matches:
            fl_value, feet_value, unit, gnd = match

            # Flight level
            if fl_value:
                limits.append({"value": int(fl_value), "unit": "FL"})

            # Feet s jednotkou
            elif feet_value and unit:
                unit = unit.upper()
                # Převod AMSL na MSL
                if unit == "AMSL":
                    unit = "MSL"
                limits.append({"value": int(feet_value), "unit": unit})

            # GND
            elif gnd:
                limit_value = 0
                unit = "AGL"
                limits.append({"value": 0, "unit": unit})

            # Rozhodnutí, který limit je upper a který lower
            lim1, lim2 = limits[0], limits[1]
            order = {"AGL": 1, "MSL": 2, "FL": 3} # FL vždy > MSL > AGL
            # Pokud jsou jednotky různé, porovnáme podle pořadí
            if lim1["unit"] != lim2["unit"]:
                self.upper_limit = lim1 if order[lim1["unit"]] > order[lim2["unit"]] else lim2
                self.lower_limit = lim1 if order[lim1["unit"]] < order[lim2["unit"]] else lim2
            # Pokud jsou jednotky stejné, porovnáme číselnou hodnotu
            else:
                self.upper_limit = lim1 if lim1["value"] > lim2["value"] else lim2
                self.lower_limit = lim1 if lim1["value"] < lim2["value"] else lim2

        return self.upper_limit, self.lower_limit

    def extract_frequencies(self):
        """ Extrakce frekvencí v rozsahu 118.000 - 136.975 """
        pattern = r'\b(1[1-3][0-9]\.\d{1,3})\b'
        matches = re.findall(pattern, self.text)

        frequencies = []
        for match in matches:
            freq = float(match)
            if 118.000 <= freq <= 136.975:
                frequencies.append(f"{freq:.3f}")

        self.frequency = frequencies[0] if frequencies else None
        return self.frequency

    def extract_radius_and_unit(self, text:str):
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

    def normalize_radius(self, radius, unit):
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
    
    def extract_draw_commands(self):
        """ Rozpoznání tvarů: kruhy, polygony, oblouky """
        self.draw_commands = []
        lines = self.input_text.splitlines()
        for line in lines:
            if "KRUH" in line or "CIRCLE" in line:
                radius_match = re.search(r"(\d+(\.\d+)?)\s*(NM|KM|M)", line)
                if radius_match:
                    radius = radius_match.group(1)
                    unit = radius_match.group(3)
                    center_line = lines[lines.index(line) + 1]
                    center_lat, center_lon = Convertor.detect_and_convert(center_line)
                    self.draw_commands.append({
                        "type": "circle",
                        "circle_center_coordinate": (center_lat, center_lon),
                        "circle_radius": radius,
                        "radius_unit": unit
                    })
        return self.draw_commands

    def get_airspace_data(self):
        """ Zavolá všechny extrakční metody """
        self.extract_name()
        self.extract_class()
        self.extract_category()
        self.extract_verticals()
        self.extract_frequencies()
        self.extract_draw_commands()

    def to_airspace(self):
        """ Naplní a vrátí objekt Airspace s daty z Extractoru """
        self.get_airspace_data()
        return Airspace(
            name=self.name,
            airspace_class=self.airspace_class,
            category=self.category,
            frequency=self.frequency,
            upper_limit=self.upper_limit,
            lower_limit=self.lower_limit,
            draw_commands=self.draw_commands
        )