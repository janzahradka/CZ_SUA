# controller.py
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace_formatter import AirspaceFormatter
import re


def process_plain_text(input_text: str) -> str:
    """
    Processes input text using Extractor, then creates an Airspace object and
    formats it with AirspaceFormatter.
    """
    extractor = Extractor(input_text)
    airspace_obj = extractor.to_airspace()
    formatter = AirspaceFormatter(airspace_obj)
    return formatter.to_openair()

def process_openair_text(input_text: str) -> str:
    """
    Processes input text using ExtractorOpenAir, then creates an Airspace object and
    formats it with AirspaceFormatter.
    """
    extractor = ExtractorOpenAir(input_text)
    airspace_obj = extractor.to_airspace()
    formatter = AirspaceFormatter(airspace_obj)
    return formatter.to_openair()

def airspace_from_openair(openair_text: str):
    """
    Converts OpenAir formatted text into an Airspace object.
    This function is used by the renderer.
    """
    extractor = ExtractorOpenAir(openair_text)
    airspace_obj = extractor.to_airspace()
    return airspace_obj


def split_openair_blocks(text):
    """
    Rozdělí text na bloky oddělené jedním nebo více prázdnými řádky
    a vrátí pouze ty bloky, kde je tag na začátku řádku následovaný mezerou.

    :param text: Vstupní text obsahující vzdušné prostory.
    :return: List bloků (každý blok obsahuje text jednoho vzdušného prostoru).
    """
    # Klíčové tagy dle OpenAir formátu
    openair_tags = ["AC", "AY", "AN", "AL", "AH", "DP", "V D=", "DB"]

    # Rozdělení textu na základě dvou nebo více po sobě jdoucích prázdných řádků
    blocks = re.split(r"(?:\r?\n){2,}", text.strip())

    # Funkce zkontroluje, jestli blok obsahuje tag na začátku řádku následovaný mezerou
    def is_valid_block(block):
        for line in block.splitlines():
            for tag in openair_tags:
                if re.match(rf"^{tag} ", line):  # Tag musí být na začátku řádku a za ním mezera
                    return True
        return False

    # Filtrace bloků dle výše uvedené validace
    valid_blocks = [block for block in blocks if is_valid_block(block)]

    return valid_blocks

