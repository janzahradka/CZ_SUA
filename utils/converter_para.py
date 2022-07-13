from unidecode import unidecode

in_text = """Erpužice RADIO
123,490

ARP: 49° 48' 10" N, 13° 02' 17" E
"""

i = 0
output = "\n\n"
for line in in_text.splitlines():
    if i == 0:
        output += "AC Q\n"
        output += "AN PARA " + unidecode(line) + "\n"
    elif i == 1:
        output += "AF " + line.replace(",", ".") + "\n"
    elif i == 3:
        output += "AH FL 95\n"
        output += "AL 0 AGL\n"
        output += f"V X={line[5:7]}:{line[9:11]}:{line[13:15]} N 0{line[20:22]}:{line[24:26]}:{line[28:30]} E\n"
        output += "DC 2 *NM\n"
    i += 1

# output = f"{in_text[5:7]}:{in_text[9:11]}:{in_text[13:15]} N 0{in_text[20:22]}:{in_text[24:26]}:{in_text[28:30]} E"
print(output)
