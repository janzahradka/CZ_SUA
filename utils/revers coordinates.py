file = "tmp.txt"
for line in reversed(list(open(file))):
    print(line.rstrip())
