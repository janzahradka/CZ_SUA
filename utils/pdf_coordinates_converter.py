# coordinates = """50 20 56,37 N 014 02 25,78 E
# 50 17 10,23 N 013 55 18,27 E
# 50 18 39,85 N 013 52 10,09 E
# 50 23 31,25 N 014 01 40,62 E
# """

coordinates = """48 57 46,42N 014 15 34,47E
48 57 46,85N 014 21 21,49E
48 56 47,00N 014 25 39,00E
48 57 46,96N 014 29 56,45E
48 57 46,65N 014 38 47,40E
48 55 46,74N 014 38 47,18E
48 55 46,85N 014 35 42,13E
48 51 27,77N 014 30 50,55E
48 51 27,67N 014 20 26,51E
48 55 46,52N 014 15 35,77E
"""



def round_number(text):
    number = round(float(text.replace(",", ".")), 0)
    rounded = str(int(number))
    if len(rounded) < 2:
        rounded = "0" + rounded
    return rounded

for line in coordinates.splitlines():
    l = line.split(" ")
    latitude = l[0] + ":" + l[1] + ":" + round_number(l[2][:-1]) + " N"
    longitude = l[3] + ":" + l[4] + ":" + round_number(l[5][:-1]) + " E"
    print(f"DP {latitude} {longitude}")


