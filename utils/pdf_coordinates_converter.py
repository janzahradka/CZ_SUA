coordinates = """50 29 19,4 N 013 27 49,3 E"""


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


