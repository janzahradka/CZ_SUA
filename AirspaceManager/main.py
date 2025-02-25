from extractor.extractor import Extractor
from extractor.extractor_openair import ExtractorOpenAir
from airspace import Airspace

input_openair_text: str = ""
input_plain_text: str = ""

file_path_openair = []
file_path_openair.append('./test_strings/OpenAir/LKTSA7C Jince - polygon.txt')
file_path_openair.append('./test_strings/OpenAir/TRA62 Nymburk - oblouk.txt')
file_path_openair.append('./test_strings/OpenAir/DROPZONE Breclav - kruh.txt')
for file in file_path_openair:
    with open(file, 'r', encoding='utf-8') as file:
        input_openair_text = file.read()
    openair_extractor = ExtractorOpenAir(input_openair_text)
    airspace = Airspace.from_extractor(openair_extractor)
    print(airspace)

file_path_plain = './test_strings/plain_text/Lion 1.txt'
file_path_plain = './test_strings/plain_text/Lion 3.txt'
file_path_plain = './test_strings/plain_text/LKP4 vlasim - polygon.txt'
file_path_plain = './test_strings/plain_text/LKP2 Temelin - kruh.txt'
file_path_plain = './test_strings/plain_text/TRA62 Nymburk.txt'


# print("Název:", openair_extractor.extract_name())
# print("Třída:", openair_extractor.extract_class())
# print("FRQ:", openair_extractor.extract_frequency())
# print("Název stanoviště:", openair_extractor.extract_station_name())
# print("Upper limit:", openair_extractor.extract_upper_limit())
# print("Lower limit:", openair_extractor.extract_lower_limit())
# draw_commands = openair_extractor.extract_draw_commands()
# for command in draw_commands:
#     print(command)

# text_extractor = TextExtractor(input_openair_text)
# print("Souřadnice:", openair_extractor.extract_points())
