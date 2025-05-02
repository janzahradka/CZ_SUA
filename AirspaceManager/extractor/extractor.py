import re
from typing import Optional

from pycparser.c_ast import Return

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
    {"name_template": "LKTSA", "AC_tag": "R", "AY_tag": "Temporary segregated airspace"},
    {"name_template": "LKTRA", "AC_tag": "R", "AY_tag": "Temporary reserved airspace"},
    {"name_template": "MCTR", "AC_tag": "D", "AY_tag": "Military Control Zone"},
    {"name_template": "MTMA", "AC_tag": "D", "AY_tag": "Military Terminal Zone"},
    {"name_template": "NTM", "AC_tag": "R", "AY_tag": "NOTAM"},
    {"name_template": "PGZ", "AC_tag": "GS", "AY_tag": "Paragliding Zone"},
    {"name_template": "TMA", "AC_tag": "D", "AY_tag": "Terminal Manoeuvring Area"},
    {"name_template": "TRA GA", "AC_tag": "GS", "AY_tag": "GSEC"},
    {"name_template": "MODELS", "AC_tag": "Q", "AY_tag": "Dangerous Area"}
]

class Extractor:
    """ Extractor pro vytěžování dat z méně strukturovaného textu """

    def __init__(self, input_text):
        cleaned_text = self.remove_diacritics(input_text)
        self.text = cleaned_text
        self.lines_by_coordinates = self.get_lines_by_coordinates(cleaned_text)
        self.name: Optional[str] = self.extract_name()
        self.airspace_class: Optional[str] = self.extract_airspace_class()
        self.category: Optional[str] = self.extract_category()
        self.frequencies: Optional[list] = self.extract_frequencies()
        upper, lower = self.extract_verticals()
        self.upper_limit: Optional[dict] = upper
        self.lower_limit: Optional[dict] = lower
        self.draw_commands: Optional[list[dict]] = self.extract_draw_commands()


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
        """
        Extrahuje název prostoru z prvního řádku.
        Pokud řádek začíná shodou s template, vrátí celý řádek (max. 50 znaků).
        """
        first_line = self.text.splitlines()[0].strip()  # První řádek bez mezer na začátku a konci

        for item in AIRSPACE_TYPE_MAP:
            template = item["name_template"]

            # === Nový regulární výraz ===
            # - `^` začátek řádku
            # - `re.IGNORECASE` pro ignorování velikosti písmen
            match = re.match(rf"^{template}", first_line, re.IGNORECASE)

            if match:
                # === self.name bude celý řádek (max. 50 znaků) ===
                self.name = first_line[:50].strip()  # Max. 50 znaků a oříznutí mezer na konci
                break
        else:
            self.name = None  # Pokud není shoda, nastaví na None

        return self.name

    def extract_airspace_class(self):
        """ Rozpoznání třídy prostoru podle mapování """
        for item in AIRSPACE_TYPE_MAP:
            if self.name and self.name.startswith(item["name_template"]):
                self.airspace_class = item["AC_tag"]
                return self.airspace_class

    def extract_category(self):
        """ Rozpoznání kategorie prostoru podle mapování """
        for item in AIRSPACE_TYPE_MAP:
            if self.name and self.name.startswith(item["name_template"]):
                self.category = item["AY_tag"]
                return self.category

    def extract_verticals(self):
        """
        Extracts upper and lower vertical limits from text and returns them as dicts.
        Expected output: upper_limit, lower_limit
            upper_limit: {"value": int, "unit": str}
            lower_limit: {"value": int, "unit": str}
        expected input such as:
            FL125,  1000 ft AGL
            FL125  FL95
            1000 ft AGL  GND
            FL95 / GND
            FL95 / FL65
            FL95 / 2500 ft AMSL
            FL95 / 5000 ft AMSL
            FL245 / FL95

        converts:
            GND -> {"value": 0, "unit": "AGL"}
            1000 ft AGL -> {"value": 1000, "unit": "AGL"}
            2000 FT AMSL -> {"value": 2000, "unit": "MSL"}
            FL95 -> {"value": 95, "unit": "FT"}
            FL245 -> {"value": 245, "unit": "FT"}

        """
        # Regulární výraz pro extrakci vertikálních limitů
        pattern = re.compile(r"""
            \b(?:FL)\s?(?P<fl>\d{2,3})\b |                              # Flight Level (např. FL95, FL 95)
            \b(?P<feet>\d{1,4})\s?(?:ft)?\s?(?P<unit>AGL|AMSL|MSL)\b |  # Feet s jednotkou
            \b(?P<gnd>GND)\b                                             # GND
        """, re.IGNORECASE | re.VERBOSE)

        # Najdi všechny shody
        matches = pattern.findall(self.text)
        if len(matches) != 2:
            return None, None

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
        """ Extrakce frekvencí v rozsahu 118.000 - 136.975 bez změny pořadí """
        pattern = r'\b(1[1-3][0-9]\.\d{1,3})\b'
        matches = re.findall(pattern, self.text)

        frequencies = []
        for match in matches:
            freq = float(match)
            if 118.000 <= freq <= 136.975:
                # === Převedeme na tři desetinná místa ===
                formatted_freq = f"{freq:.3f}"
                frequencies.append(formatted_freq)

        # === Deduplication bez změny pořadí ===
        deduplicated_frequencies = list(dict.fromkeys(frequencies))

        return deduplicated_frequencies if deduplicated_frequencies else None

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
            radius_value = float(match.group(1))  # Změníme číslo na float
            unit = match.group(2).upper()  # Jednotku převedeme na velká písmena, např. NM nebo KM
            if unit == "KM":
                return round(radius_value * 0.539957, 3)  # TODO: přesunout do Convertoru
            elif unit == "NM":
                pass
            else:
                # Pokud je jednotka neznámá
                raise ValueError(f"Neznámá jednotka: {unit}")
            return radius_value, unit
        else:
            # Pokud žádný radius neexistuje, vrátíme None
            return None, None

    
    def extract_draw_commands(self):
        """ Rozpoznání tvarů: kruhy, polygony, oblouky """
        self.draw_commands = []
        lines = self.lines_by_coordinates

        # === Přidáno ošetření na None ===
        if lines is None:
            print("Chyba: lines_by_coordinates je None.")
            return  # Přeskočí zpracování, pokud lines není naplněno

        skipping_lines = 0
        current_direction = "+"
        for line_index, line in enumerate(lines):
            if skipping_lines == 0:
                extracted_coordinate = Convertor.extract_coodinate_from_text(line)
                if re.search(r"\b(KRUH|CIRCLE|RADIUS)", line, re.IGNORECASE):
                    radius_value, unit = self.extract_radius_and_unit(line)
                    search_arc = re.search(r"\b(ARC|OBLOUK|ARCU|ARC OF|OBLOUKU|OBLOUKEM|CWA)", line, re.IGNORECASE)
                    search_anti_arc = re.search(r"\b(PROTI SMĚRU|ANTI-CLOCKWISE|ANTICLOCKWISE|COUNTERCLOCKWISE|CCA)",
                                                line,
                                                re.IGNORECASE)
                    if search_arc or search_anti_arc:
                        arc = True
                        if search_anti_arc:
                            current_direction = "-"
                        else:
                            current_direction = "+"
                    else:
                        arc = False
                    if arc:  # detekován oblouk
                        arc_start_coordinate = extracted_coordinate  # start oblouku je na prvním řádku
                        current_center = Convertor.extract_coodinate_from_text(
                            lines[line_index + 1])  # střed oblouku je na následujícím řádku
                        arc_end_coordinate = Convertor.extract_coodinate_from_text(
                            lines[line_index + 2])  # konec oblouku je na následujícím řádku
                        skipping_lines = 2  # přeskočí následující dva řádky ze zpracování
                        self.draw_commands.append({
                            "type": "arc",
                            "arc_center_coordinate": current_center,
                            "arc_direction": current_direction,
                            "arc_start_point_coordinate": arc_start_coordinate,
                            "arc_end_point_coordinate": arc_end_coordinate
                        })
                    else:  # neidentifikován oblouk, pouze kruh
                        current_center = Convertor.extract_coodinate_from_text(
                            lines[line_index + 1])  # střed kruhu je na následujícím řádku
                        self.draw_commands.append({
                            "type": "circle",
                            "circle_center_coordinate": current_center,
                            "circle_radius": radius_value,
                            "radius_unit": unit
                        })
                        skipping_lines = 1  # přeskočí řádek se středem kruhu
                else:  # není ani kruh ani oblouk
                    # Polygon
                    if extracted_coordinate:
                        self.draw_commands.append({
                            "type": "polygon_point",
                            "polygon_point_coordinate": extracted_coordinate
                        })
            else:
                skipping_lines -= 1
        return self.draw_commands

    def to_airspace(self):
        """ Naplní a vrátí objekt Airspace s daty z Extractoru """
        return Airspace(
            name=self.name,
            airspace_class=self.airspace_class,
            category=self.category,
            frequencies=self.frequencies,
            upper_limit=self.upper_limit,
            lower_limit=self.lower_limit,
            draw_commands=self.draw_commands
        )