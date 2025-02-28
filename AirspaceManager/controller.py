# controller.py
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace_formatter import AirspaceFormatter
from AirspaceManager.evaluator import Evaluator
from AirspaceManager.airspace import Airspace
from AirspaceManager.evaluator import Evaluator


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
