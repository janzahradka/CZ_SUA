import re

# Kompletní mapování typů prostorů
AIRSPACE_TYPE_MAP = [
    {"name_template": "LKP",
     "AC_tag": "P",
     "AY_tag": "Prohibited Area"
     },
    {"name_template": "LKD",
     "AC_tag": "Q",
     "AY_tag": "Dangerous Area"
     },
    {"name_template": "LKR",
     "AC_tag": "R",
     "AY_tag": "Restricted Area"
     },
    {"name_template": "LKTSA",
     "AC_tag": "R",
     "AY_tag": "Temporary Segregated Area"
     },
    {"name_template": "LKTRA",
     "AC_tag": "R",
     "AY_tag": "Temporary Reserved Area"
     },
    {"name_template": "LKCTR",
     "AC_tag": "D",
     "AY_tag": "Control Zone"
     },
    {"name_template": "MCTR",
     "AC_tag": "D",
     "AY_tag": "Military Control Zone"
     },
    {"name_template": "LKTMA",
     "AC_tag": "D",
     "AY_tag": "Terminal Manoeuvring Area"
     },
    {"name_template": "TMA",
     "AC_tag": "D",
     "AY_tag": "Terminal Manoeuvring Area"
     },
    {"name_template": "MTMA",
     "AC_tag": "D",
     "AY_tag": "Military Terminal Zone"
     },
    {"name_template": "LKPGZ",
     "AC_tag": "GS",
     "AY_tag": "Paragliding Zone"
     },
    {"name_template": "LKRMZ",
     "AC_tag": "E",
     "AY_tag": "RMZ"
     },
    {"name_template": "DROPZONE",
     "AC_tag": "Q",
     "AY_tag": "Dropzone"
     },
    {"name_template": "TRA GA",
     "AC_tag": "GS",
     "AY_tag": "GSEC"}
]


def extract_airspace_name(text: str, max_words: int = 5):
    """
    Extrahuje kód prostoru a název prostoru na základě mapování v AIRSPACE_TYPE_MAP.

    Pravidla:
    - Pokud text začíná některým z name_template z AIRSPACE_TYPE_MAP, je to rozpoznáno jako kód prostoru.
    - Pokud jsou za kódem přilepené číslice (např. LKR1), jsou součástí kódu.
    - Název prostoru je maximálně prvních 5 slov za kódem.
    - Pokud není rozpoznán kód prostoru, vrátí (None, None)

    Parametry:
    - text (str): Vstupní text
    - max_words (int): Maximální počet slov v názvu prostoru (výchozí: 5)

    Návratové hodnoty:
    - tuple (code, name) - Kód prostoru a název prostoru
    """
    text = text.strip().upper()  # Normalizace textu
    for airspace in AIRSPACE_TYPE_MAP:
        template = airspace["name_template"]
        # Kontrola, zda text začíná šablonou (s volitelnými číslicemi na konci)
        match = re.match(rf"({template}\d*)\b", text)
        if match:
            code = match.group(1)
            name = text[len(code):].strip()
            # Rozdělení názvu na slova a použití maximálně prvních max_words
            name_words = name.split()
            name = " ".join(name_words[:max_words])
            return code, name

    # Pokud není rozpoznán kód prostoru, vrátí (None, None)
    return None, None


def get_ay_code(space_name:str):
    """
    Funkce vrací čitelný typ prostoru na základě názvu.

    Parametry:
        space_name (str): Název prostoru (např. 'LKP1 PRAZSKY HRAD')

    Návratová hodnota:
        str: Čitelný typ prostoru (např. 'Prohibited Area', 'Dangerous Area')
    """
    # Procházení mapování a hledání shody na začátku názvu
    for airspace in AIRSPACE_TYPE_MAP:
        if space_name.upper().startswith(airspace["name_template"]):
            return airspace["AY_tag"]

    # Pokud není nalezeno, vrátí 'Unknown'
    return "Unknown"


def get_ac_code(space_name):
    """
    Funkce vrací kód typu prostoru na základě názvu.

    Parametry:
        space_name (str): Název prostoru (např. 'LKP1 PRAZSKY HRAD')

    Návratová hodnota:
        str: Kód typu prostoru (např. 'P', 'Q', 'R')
    """
    # Procházení mapování a hledání shody na začátku názvu
    for airspace in AIRSPACE_TYPE_MAP:
        if space_name.upper().startswith(airspace["name_template"]):
            return airspace["AC_tag"]

    # Pokud není nalezeno, vrátí 'Unknown'
    return "Unknown"

#
# # Testovací příklady
# print(get_ay_code("LKP1 PRAZSKY HRAD"))  # Očekávaný výstup: "Prohibited Area"
# print(get_ay_code("LKD10 DOLNI DUNAJOVICE"))  # Očekávaný výstup: "Dangerous Area"
# print(get_ay_code("LKTRA62 NYMBURK"))  # Očekávaný výstup: "Temporary Reserved Area"
# print(get_ay_code("DROPZONE Breclav"))  # Očekávaný výstup: "Dropzone"
# print(get_ay_code("MCTR CASLAV"))  # Očekávaný výstup: "Military Control Zone"
# print(get_ay_code("TRA GA CHOTEBOR"))  # Očekávaný výstup: "GSEC"
#
# print(get_ac_code("LKP1 PRAZSKY HRAD"))  # Očekávaný výstup: "P"
# print(get_ac_code("LKD10 DOLNI DUNAJOVICE"))  # Očekávaný výstup: "Q"
# print(get_ac_code("LKTRA62 NYMBURK"))  # Očekávaný výstup: "R"
# print(get_ac_code("DROPZONE Breclav"))  # Očekávaný výstup: "Q"
# print(get_ac_code("MCTR CASLAV"))  # Očekávaný výstup: "D"
# print(get_ac_code("TRA GA CHOTEBOR"))  # Očekávaný výstup: "GS"


def extract_verticals(text: str) -> tuple[str, str]:
    """
    Extracts high and low vertical limits from text and returns them as formatted strings.
    Expected output:
        high_limit: str - Upper limit with unit (e.g., "FL 125", "5000 MSL")
        low_limit: str - Lower limit with unit (e.g., "1000 AGL", "0 AGL")
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
    matches = pattern.findall(text)
    if len(matches) != 2:
        raise ValueError("Expected exactly two vertical limits in the text")

    # Konverze shod na číselné hodnoty a jednotky
    limits = []
    for match in matches:
        fl, value, unit, gnd = match

        # Flight level
        if fl:
            limit = f"FL {int(fl)}"
            unit = "FL"

        # Feet s jednotkou
        elif value and unit:
            limit = f"{int(value)} {unit.upper()}"
            unit = unit.upper()
            # Převod AMSL na MSL
            if unit == "AMSL":
                unit = "MSL"
                limit = limit.replace("AMSL", "MSL")

        # GND
        elif gnd:
            limit = "0 AGL"
            unit = "AGL"

        # Přidáme limit do seznamu
        limits.append((limit, unit))

    # Rozhodnutí, který limit je high a který low
    def compare_limits(lim1, lim2):
        # Přidáno AMSL jako alias pro MSL
        order = {"AGL": 1, "MSL": 2, "FL": 3}
        # Pokud jsou jednotky různé, porovnáme podle pořadí
        if lim1[1] != lim2[1]:
            return lim1 if order[lim1[1]] > order[lim2[1]] else lim2
        # Pokud jsou jednotky stejné, porovnáme číselnou hodnotu
        else:
            return lim1 if int(re.search(r'\d+', lim1[0]).group()) > int(re.search(r'\d+', lim2[0]).group()) else lim2

    # Určení high a low limitu
    high, low = (limits[0], limits[1]) if compare_limits(limits[0], limits[1]) == limits[0] else (limits[1], limits[0])

    # Výstup ve formátu řetězců
    high_limit = high[0]
    low_limit = low[0]

    return high_limit, low_limit


def extract_frequencies(text: str) -> list[str]:
    """
    Extracts valid frequencies from a given text within
    the acceptable range of 118.000 to 136.975.

    :param text: The input text containing potential frequency values.
    :type text: str

    :return: A list of valid frequency strings formatted to three decimal places.
    :rtype: list[str]
    """
    # Regulární výraz pro zachycení potenciálních frekvencí
    pattern = r'\b(1[1-3][0-9]\.\d{1,3})\b'
    matches = re.findall(pattern, text)

    # Převod na float a filtrování podle rozsahu
    frequencies = []
    for match in matches:
        freq = float(match)
        if 118.000 <= freq <= 136.975:
            frequencies.append(f"{freq:.3f}")

    return frequencies


if __name__ == "__main__":
    vertical_tags = """
    FL125 / 1000 ft AGL
    FL125 / FL95
    1000 ft AGL / GND
    FL95 / GND
    FL95 / FL65
    FL95 / 2500 ft AMSL
    FL95 / 5000 ft AMSL
    4500 ft AMSL / 2500 ft AMSL
    """

    for line in vertical_tags.splitlines():
        if line.strip():
            high_limit,  low_limit = extract_verticals(line)
            print(f"{line} -> AH {high_limit}, AL {low_limit}")