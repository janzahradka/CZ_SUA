# �prava funkce pro konverzi na OpenAir form�t s kontrolou pr�zdn�ch ��dk�
def convert_to_openair(input_text):
    lines = [line.strip() for line in input_text.splitlines() if line.strip()]
    if not lines:
        return ""

    # Prvn� ��dek obsahuje k�d prostoru a n�zev
    first_line = lines[0]
    if len(first_line.split()) < 2:
        return ""  # P�esko��me pr�zdn� nebo neplatn� ��dky

    code, name = first_line.split(maxsplit=1)
    openair_name = remove_diacritics(name).upper()

    # Rozpozn�n� typu prostoru podle prefixu
    if code.startswith("LKP"):
        airspace_class = "P"  # Prohibited Area
    elif code.startswith("LKD"):
        airspace_class = "Q"  # Dangerous Area
    elif code.startswith("LKTRA"):
        airspace_class = "R"  # Temporary Reserved Area
    else:
        airspace_class = "R"  # Defaultn� jako Reserved

    # Rozpozn�n� horn� a spodn� hranice
    lower_limit, upper_limit = None, None
    if "/" in lines[-1]:
        upper_limit, lower_limit = lines[-1].split(" / ")

    # Identifikace typu geometrie
    openair_output = []
    openair_output.append(f"AC {airspace_class}")
    openair_output.append(f"AN {code} {openair_name}")
    openair_output.append(f"AH {upper_limit}")
    openair_output.append(f"AL {lower_limit}")
    openair_output.append(f"AF * add FRQ(123.456)")
    openair_output.append(f"AG * add station call sign")

    # Zpracov�n� sou�adnic a geometrie
    coords = []
    is_circle = False
    center_point = None
    radius = None
    is_arc = False
    arc_direction = "+"

    for line in lines[1:-1]:
        if "kru�nice" in line.lower() or "circle" in line.lower():
            is_circle = True
        elif "st�edem v poloze" in line.lower() or "centred at" in line.lower():
            center_point = line.split()[-2:]
        elif "polom�ru" in line.lower() or "radius" in line.lower():
            radius = re.findall(r'\d+\.?\d*', line)[0]
        elif "oblouk" in line.lower() or "arc" in line.lower():
            is_arc = True
            if "proti sm�ru" in line.lower() or "anti-clockwise" in line.lower():
                arc_direction = "-"
        else:
            coords.append(line)

    # Pokud je kru�nice
    if is_circle and center_point and radius:
        center = ' '.join(center_point)
        lat_decimal, lon_decimal = parse_various_formats(center)
        center_dms = coords_to_dms_format(lat_decimal, lon_decimal)
        openair_output.append(f"V X= {center_dms}")
        openair_output.append(f"DC {radius} *NM")

    # Pokud je oblouk
    elif is_arc and center_point and radius:
        center = ' '.join(center_point)
        lat_decimal, lon_decimal = parse_various_formats(center)
        center_dms = coords_to_dms_format(lat_decimal, lon_decimal)
        openair_output.append(f"V X= {center_dms}")
        openair_output.append(f"V D={arc_direction}")
        openair_output.append(f"DC {radius} *NM")

    # Pokud je polygon
    else:
        for coord in coords:
            coord = coord.replace(" -", "")  # Odstran�n� poml�ky na konci
            lat_decimal, lon_decimal = parse_various_formats(coord)
            dms_format = coords_to_dms_format(lat_decimal, lon_decimal)
            openair_output.append(f"DP {dms_format}")

    return "\n".join(openair_output)

# Op�tovn� konverze v�ech vstupn�ch soubor�
input_text = """LKTRA62 NYMBURK
502835.45N 0151011.21E -
502305.85N 0152316.12E -
501108.78N 0152255.61E -
501108.54N 0150324.04E -
501107.99N 0145839.41E
odtud kruhov� oblouk proti sm�ru
hodinov�ch ru�i�ek o polom�ru /
thence anti-clockwise by the arc of
a circle radius 28 NM
se st�edem v poloze / centred at
500544.80N 0141555.81E -
501409.32N 0145728.83E -
502833.75N 0150003.79E -
502835.45N 0151011.21E
FL245 / 3000 FT AMSL"""

print(convert_to_openair(input_text))
