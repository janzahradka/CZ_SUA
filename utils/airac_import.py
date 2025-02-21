import re
import unicodedata
from geo_utils import contains_coordinate_with_index, extract_coordinate_to_dms, extract_radius_and_unit, normalize_radius
from openair_utils import get_ac_code, get_ay_code, extract_verticals, extract_frequencies, extract_airspace_name

# Funkce pro konverzi názvu na formát bez diakritiky
def remove_diacritics(text):
    normalized = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in normalized if not unicodedata.combining(c)])


# Hlavní funkce pro analýzu a konverzi na OpenAir formát z AIRAC PDF
def convert_airac_to_openair(input_text:str):
    input_text = input_text.upper() # převede na UPPER

    # nalezení vertikálních limitů
    try:
        high_limit, low_limit = extract_verticals(input_text)
    except Exception:
        high_limit, low_limit = None, None

    # nalezení frekvencí
    freqs = extract_frequencies(input_text)
    if len(freqs) > 0:
        frequency = freqs[0] # ke zpracování se použije pouze první nalezená FRQ
    else:
        frequency = None
    
    lines = [line.strip() for line in input_text.splitlines() if line.strip()]
    if not lines:
        return ""

    openair_output = []
    temporary_buffer = []
    buffer_line_index = 0

    # Kontrola zda první řádek obsahuje kód a název prostoru
    first_line = lines[0]
    code, name = extract_airspace_name(first_line)
    if code and name:
        if frequency:
            name = f"{name} {frequency}"
        openair_output.append(f"AC {get_ac_code(code)}")
        openair_output.append(f"AY {get_ay_code(code)}")
        openair_output.append(f"AN {code} {name}")

    if frequency:
        openair_output.append(f"AF {frequency}")
        openair_output.append(f"* AG UNDEFINED")

    if high_limit and low_limit:
        openair_output.append(f"AH {high_limit}")
        openair_output.append(f"AL {low_limit}")

    # Zpracování řádků
    for line_index, line in enumerate(lines):
        coordinate_found, position = contains_coordinate_with_index(line)
        buffer_line_index += 1
        if position != 0:
            # Pokud řádek NEZAČÍNÁ souřadnicí, přidej do temporary_buffer
            temporary_buffer.append(line)
        else:
            # Pokud řádek ZAČÍNÁ souřadnicí
            # Přidáme i tento řádek do temporary_buffer
            extracted_coordinate = extract_coordinate_to_dms(line)
            if buffer_line_index > 1:
    
                # Spojíme všechny řádky v temporary_buffer do jednoho bloku
                combined_text = " ".join(temporary_buffer)
    
                # Detekce kružnice nebo oblouku
                if re.search(r"\b(KRUH|CIRCLE|RADIUS)", combined_text, re.IGNORECASE):
                    radius, unit = extract_radius_and_unit(combined_text)
                    center_dms = extract_coordinate_to_dms(combined_text)
                    if re.search(r"\b(ARC|OBLOUK|ARCU|ARC OF|OBLOUKU|OBLOUKEM|CWA)", combined_text, re.IGNORECASE):
                        direction = "+"
                        arc = True
                    elif re.search(r"\b(PROTI SMĚRU|ANTI-CLOCKWISE|ANTICLOCKWISE|COUNTERCLOCKWISE|CCA)", combined_text, re.IGNORECASE):
                        direction = "-"
                        arc = True
                    else:
                        arc = False
                    if arc: # detekován oblouk
                        # první koordinát oblouku:
                        preceding_row_with_coordinate = lines[line_index - buffer_line_index] # první koordinát oblouku předchází aktuálnímu bloku, avšak může být součástí předchozího oblouku
                        arc_start_coordinate = extract_coordinate_to_dms(preceding_row_with_coordinate) # extrakce středu oblouku z bloku textu
                        if openair_output and openair_output[-1].startswith("DP"):
                            openair_output.pop()  # odstranění polygonu, který je ve skutečnosti prvním koordinátem oblouku
                        arc_end_coordinate = extracted_coordinate  # druhý koordinát oblouku je koordinát následující po bloku textu
                        openair_output.append(f"V X= {center_dms} *ARP () {radius} {unit}")
                        openair_output.append(f"V D={direction}")
                        openair_output.append(f"DB {arc_start_coordinate}, {arc_end_coordinate}")
                    else: #neidentifikován oblouk, pouze kruh
                        openair_output.append(f"V X= {center_dms}")
                        openair_output.append(f"DC {normalize_radius(radius, unit)} *{unit}")
                else: # není ani kruh ani oblouk
                    # Polygon
                    openair_output.append(f"DP {extracted_coordinate}")
            else: # víceřádkový řetězec obsahující pouze Polygon, nikoliv kruh nebo oblouk
                # Polygon
                openair_output.append(f"DP {extracted_coordinate}")

            # Vyčistíme temporary_buffer
            temporary_buffer = []
            buffer_line_index = 0

    # Výstup do konzole
    output = "\n".join(openair_output)
    print(output)


# Testovací vstupní text
# input_text = """LKTRA62 NYMBURK
# 502835.45N 0151011.21E -
# 502305.85N 0152316.12E -
# 501108.78N 0152255.61E -
# 501108.54N 0150324.04E -
# 501107.99N 0145839.41E
# odtud kruhový oblouk proti směru
# hodinových ručiček o poloměru /
# thence anti-clockwise by the arc of
# a circle radius 28 NM
# se středem v poloze / centred at
# 500544.80N 0141555.81E -
# 501409.32N 0145728.83E -
# 502833.75N 0150003.79E -
# 502835.45N 0151011.21E
# FL245 / 3000 FT AMSL"""
#
# input_text = """
# MTMA II KBELY
# 501433.28N 0145219.90E -
# 501409.32N 0145728.83E -
# CWA o poloměru / with radius 28 NM
# se středem v / centred at
# DME OKL (500544.80N 0141555.81E) -
# 501107.99N 0145839.41E -
# CWA o poloměru / with radius 28 NM
# se středem v / centred at
# DME OKL (500544.80N 0141555.81E) -
# 495503.59N 0145603.54E -
# CWA o poloměru / with radius 28 NM
# se středem v / centred at
# DME OKL (500544.80N 0141555.81E) -
# 495109.96N 0145257.92E -
# 495259.83N 0144915.52E -
# 495847.84N 0143727.62E -
# 500905.08N 0144943.92E -
# 501433.28N 0145219.90E
# 4500 ft AMSL / 2500 ft AMSL
# """
#
# control_text = """
# AC D
# AN MTMA II KBELY 124.68
# AH 4500 MSL
# AL 2500 MSL
# DP 50:14:33 N 014:52:20 E
# V X=50:05:45 N 014:15:56 E *OKL
# V D=+
# DB 50:14:09 N 014:57:29 E, 50:11:08 N 014:58:39 E
# V X=50:05:45 N 014:15:56 E *OKL
# V D=+
# DB 50:11:08 N 014:58:39 E, 49:55:04 N 014:56:04 E
# V X=50:05:45 N 014:15:56 E *OKL
# V D=+
# DB 49:55:04 N 014:56:04 E, 49:51:10 N 014:52:58 E
# DP 49:53:00 N 014:49:16 E
# DP 49:58:48 N 014:37:28 E
# DP 50:09:05 N 014:49:44 E
# DP 50:14:33 N 014:52:20 E
# """
#
#
# input_text = """
# TMA VII BRNO
# 491529.80N 0170002.50E -
# 491842.08N 0171534.45E -
# 492729.85N 0172900.64E -
# 492349.98N 0173529.94E -
# 492217.81N 0174702.26E -
# 491442.19N 0173521.58E -
# 491514.85N 0172945.86E -
# 491528.30N 0170351.62E -
# 491529.80N 0170002.50E
# FL95 / FL75
# """


input_text = """
TMA II BRNO
491528.30N 0170351.62E -
491514.85N 0172945.86E -
491442.19N 0173521.58E -
490705.08N 0171626.75E -
485615.73N 0171411.81E -
485103.05N 0165559.46E -
485542.66N 0164810.07E -
CCA o poloměru / with radius 14 NM
se středem v / centred at
DME BNO (490900.23N 0164133.29E) -
485752.54N 0165426.67E -
485731.51N 0165828.67E -
CCA o poloměru / with radius 16 NM
se středem v / centred at
DME BNO (490900.23N 0164133.29E) -
491528.30N 0170351.62E
FL95 / 3500 ft AMSL
Třída vzdušného prostoru / Class of airspace: D
PRAHA ACC
PRAHA RADAR
H24
EN, CZ
127.350 MHz
124.050 MHz* * RESERVE
"""


if __name__ == "__main__":
    # Spuštění konverze a výstupu do konzole
    convert_airac_to_openair(input_text)
