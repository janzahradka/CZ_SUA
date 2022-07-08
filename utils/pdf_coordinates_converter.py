coordinates = """50 20 56,37 N 014 02 25,78 E
50 17 10,23 N 013 55 18,27 E
50 18 39,85 N 013 52 10,09 E
50 23 31,25 N 014 01 40,62 E
"""



def round_number(text):
    number = round(float(text.replace(",", ".")), 0)
    rounded = str(int(number))
    if len(rounded) < 2:
        rounded = "0" + rounded
    return rounded

for line in coordinates.splitlines():
    l = line.split(" ")
    latitude = l[0] + ":" + l[1] + ":" + round_number(l[2]) + " " + l[3]
    longitude = l[4] + ":" + l[5] + ":" + round_number(l[6]) + " " + l[7]
    print(f"DP {latitude} {longitude}")


