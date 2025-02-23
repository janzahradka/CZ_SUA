import re
import unicodedata
from geo_utils import contains_coordinate_with_index, extract_coordinate_to_dms, extract_radius_and_unit, normalize_radius, get_lines_by_coordinates
from openair_utils import get_ac_code, get_ay_code, extract_verticals, extract_frequencies, extract_airspace_name

# Funkce pro odstranění diakritiky
def remove_diacritics(text:str) -> str:
    """
    Odstraní diakritiku z textu
    :param text:
    :return:
    """
    normalized = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in normalized if not unicodedata.combining(c)])


# Hlavní funkce pro analýzu a konverzi na OpenAir formát z AIRAC PDF
def convert_airac_to_openair(input_text:str):
    """
    Converts an input AIRAC format text to an OpenAir formatted string by extracting and
    transforming various air traffic-related data such as coordinates, airspace characteristics,
    frequencies, and more. The function processes the input text, identifies key components,
    and outputs an OpenAir formatted result based on the extracted data.

    :param input_text: The input AIRAC format text to be converted.
    :type input_text: str
    :return: A string containing the converted OpenAir formatted text. If input text is empty
             or not applicable, it returns an empty string.
    :rtype: str
    :raises Exception: Raised during the extraction of vertical limits if an error occurs.
    """
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
        if freqs:
            name = f'{name} {" ".join(freqs)}'
        openair_output.append(f"AC {get_ac_code(code)}")
        openair_output.append(f"AY {get_ay_code(code)}")
        openair_output.append(f"AN {code} {name}")

    if frequency:
        openair_output.append(f"AF {frequency}")
        openair_output.append(f"* AG UNDEFINED")

    if high_limit and low_limit:
        openair_output.append(f"AH {high_limit}")
        openair_output.append(f"AL {low_limit}")

    lines = get_lines_by_coordinates(input_text)
    # Zpracování řádků
    skipping_lines = 0
    for line_index, line in enumerate(lines):
        if skipping_lines == 0:
            extracted_coordinate = extract_coordinate_to_dms(line)
            if re.search(r"\b(KRUH|CIRCLE|RADIUS)", line, re.IGNORECASE):
                radius, unit = extract_radius_and_unit(line)
                # center_dms = extract_coordinate_to_dms(line)
                search_arc = re.search(r"\b(ARC|OBLOUK|ARCU|ARC OF|OBLOUKU|OBLOUKEM|CWA)", line, re.IGNORECASE)
                search_anti_arc = re.search(r"\b(PROTI SMĚRU|ANTI-CLOCKWISE|ANTICLOCKWISE|COUNTERCLOCKWISE|CCA)", line,
                                   re.IGNORECASE)
                if search_arc or search_anti_arc:
                    arc = True
                    if search_anti_arc:
                        direction = "-"
                    else:
                        direction = "+"
                else:
                    arc = False
                if arc:  # detekován oblouk
                    arc_start_coordinate = extracted_coordinate # start oblouku je na prvním řádku
                    arc_centre_coordinate = extract_coordinate_to_dms(lines[line_index + 1]) # střed oblouku je na následujícím řádku
                    arc_end_coordinate = extract_coordinate_to_dms(lines[line_index + 2]) # konec oblouku je na následujícím řádku
                    skipping_lines = 2 # přeskočí následující dva řádky ze zpracování

                    openair_output.append(f"V X= {arc_centre_coordinate} *ARP () {radius} {unit}")
                    openair_output.append(f"V D={direction}")
                    openair_output.append(f"DB {arc_start_coordinate}, {arc_end_coordinate}")
                else:  # neidentifikován oblouk, pouze kruh
                    circle_centre_coordinate = extract_coordinate_to_dms(lines[line_index + 1]) # střed kruhu je na následujícím řádku
                    openair_output.append(f"V X={circle_centre_coordinate}")
                    openair_output.append(f"DC {normalize_radius(radius, unit)} *{unit}")
                    skipping_lines = 1 # přeskočí řádek se středem kruhu
            else:  # není ani kruh ani oblouk
                # Polygon
                if extracted_coordinate:
                    openair_output.append(f"DP {extracted_coordinate}")
        else:
            skipping_lines -= 1

    # Výstup do konzole
    output = "\n".join(openair_output)
    normalized_output = remove_diacritics(output)
    return normalized_output


# # Testovací vstupní text
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


# input_text = """
# TMA II BRNO
# 491528.30N 0170351.62E -
# 491514.85N 0172945.86E -
# 491442.19N 0173521.58E -
# 490705.08N 0171626.75E -
# 485615.73N 0171411.81E -
# 485103.05N 0165559.46E -
# 485542.66N 0164810.07E -
# CCA o poloměru / with radius 14 NM
# se středem v / centred at
# DME BNO (490900.23N 0164133.29E) -
# 485752.54N 0165426.67E -
# 485731.51N 0165828.67E -
# CCA o poloměru / with radius 16 NM
# se středem v / centred at
# DME BNO (490900.23N 0164133.29E) -
# 491528.30N 0170351.62E
# FL95 / 3500 ft AMSL
# Třída vzdušného prostoru / Class of airspace: D
# PRAHA ACC
# PRAHA RADAR
# H24
# EN, CZ
# 127.350 MHz
# 124.050 MHz* * RESERVE
# """

# input_text = """
# 500749.90N 0160359.89E -
# 500631.57N 0162158.95E -
# 495214.81N 0161847.72E -
# 495055.69N 0154834.46E -
# 495547.79N 0153511.65E -
# 495516.82N 0155046.70E -
# 495454.00N 0160231.00E -
# 500110.00N 0160451.00E -
# 500710.00N 0160405.00E -
# 500749.90N 0160359.89E
# """

# input_text="""
# LKP2 TEMELÍN
# Kružnice o poloměru / A circle of radius 1.1 NM
# se středem v poloze / centred at
# 491048.73N 0142231.77E
# 5000 FT AMSL / GND
# """


# input_text = """
# TMA II BRNO
# 491528.30N 0170351.62E -
# 491514.85N 0172945.86E -
# 491442.19N 0173521.58E -
# 490705.08N 0171626.75E -
# 485615.73N 0171411.81E -
# 485103.05N 0165559.46E -
# 485542.66N 0164810.07E -
# CCA o poloměru / with radius 14 NM
# se středem v / centred at
# DME BNO (490900.23N 0164133.29E) -
# 485752.54N 0165426.67E -
# 485731.51N 0165828.67E -
# CCA o poloměru / with radius 16 NM
# se středem v / centred at
# DME BNO (490900.23N 0164133.29E) -
# 491528.30N 0170351.62E
# 495959.99N 0175959.99E
# FL95 / 3500 ft AMSL
# Třída vzdušného prostoru / Class of airspace: D
# PRAHA ACC
# PRAHA RADAR
# H24
# EN, CZ
# 127.350 MHz
# 124.050 MHz*
# """

# if __name__ == "__main__":
#     # Spuštění konverze a výstupu do konzole
#     # input_text = input_text.replace("\n", " ")
#     print(convert_airac_to_openair(input_text))
