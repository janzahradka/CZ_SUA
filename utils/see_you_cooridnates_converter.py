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

polygon = ["493225,00N0130953,00E "]

command = "V X="
for coor in polygon:
    longitude = f"{coor[0:2]}:{coor[2:4]}:{coor[4:6]} N"
    lat = coor.rsplit("N")[1]
    latitude = f"{lat[0:3]}:{lat[3:5]}:{lat[5:7]} E"
    print(command, longitude, latitude)
