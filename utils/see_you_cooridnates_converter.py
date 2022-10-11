coor = """N50°16'36" E017°51'56"""
command = "DP"

longitude = f"{coor[1:3]}:{coor[4:6]}:{coor[7:9]} N"
latitude = f"{coor[12:15]}:{coor[16:18]}:{coor[19:21]} E"

print(command, longitude, latitude)
