import re

# SeeYou format
# coor = """N50°16'36" E017°51'56"""
# longitude = f"{coor[1:3]}:{coor[4:6]}:{coor[7:9]} N"
# latitude = f"{coor[12:15]}:{coor[16:18]}:{coor[19:21]} E"


# Hřiven format
# coor = "492732,96N0164248,91E"
# polygon = ["493616,00N0162051,00E ",
#            "493604,00N0163214,00E",
#            "493443,00N0164320,00E ",
#            "493352,00N0165438,00E ",
#            "492603,00N0165358,00E ",
#            "492817,00N0164307,00E ",
#            "492803,00N0163200,00E ",
#            "493137,00N0162352,00E ",
#            "493616,00N0162051,00E "]


def extract_coordinates(text):
    # Regular expression pattern for the geocoordinates format
    pattern = r"\b(\d{6},\d{2}[NS]\d{7},\d{2}[EW])\b"

    coordinates = re.findall(pattern, text)
    return coordinates

text = "PSN 501347,71N0132453,65E (PODBORANY) - PSN 501251,65N0131549,68E (PODBORANSKY ROHOZEC) - PSN 501640,00N0131406,00E (KADANSKY ROHOZEC) - PSN 501835,00N0131345,00E (KOJETIN) - PSN 502104,00N0131347,00E (2KM SW UHOSTANY) - PSN 502132,18N0130847,14E (8KM SW KADAN) - PSN 502228,57N0131627,46E (KADAN) - PSN 502324,39N0132556,53E (2KM SE BREZNO) - PSN 501526,40N0132611,07E (3KM E VYSOKE TREBUSICE) - PSN 501347,71N0132453,65E (PODBORANY). "
coordinates = extract_coordinates(text)
print(coordinates)


polygon = coordinates


# CIRCLE
# command = "V X="
#
# LINE
command = "DP "


for coor in polygon:
    longitude = f"{coor[0:2]}:{coor[2:4]}:{coor[4:6]} N"
    lat = coor.rsplit("N")[1]
    latitude = f"{lat[0:3]}:{lat[3:5]}:{lat[5:7]} E"
    print(command, longitude, latitude)
