# import sys
from aerofiles.openair.reader import Reader as OpenAirReader

with open('../Export/CZ_SUA_24-08-07/CZ_all_24-08-07.txt') as fp:
    reader = OpenAirReader(fp);
    for record, error in reader:
        if error:
            raise error  # or handle it otherwise
