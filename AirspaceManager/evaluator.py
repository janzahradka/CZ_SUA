from math import radians, sin, cos, sqrt, atan2

class Evaluator:
    """ Třída pro speciální zeměpisné operace """

    @staticmethod
    def get_distance(coord1: dict, coord2: dict) -> float:
        """
        Vypočítá vzdálenost mezi dvěma geografickými souřadnicemi.
        Vstup:
            coord1: {"lat": <latitude>, "lon": <longitude>}
            coord2: {"lat": <latitude>, "lon": <longitude>}
        Výstup:
            Vzdálenost v metrech jako float
        """
        # Převod stupňů na radiány
        lat1, lon1 = radians(coord1["lat"]), radians(coord1["lon"])
        lat2, lon2 = radians(coord2["lat"]), radians(coord2["lon"])

        # Haversinova formule
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Poloměr Země v metrech
        R = 6371000
        distance = R * c

        return distance

    @staticmethod
    def compare_coordinates(coord1: dict, coord2: dict, tolerance: float = 15) -> tuple:
        """
        Porovná dvě geografické souřadnice na základě vzdálenosti.
        Vstup:
            coord1: {"lat": <latitude>, "lon": <longitude>}
            coord2: {"lat": <latitude>, "lon": <longitude>}
            tolerance: Maximální přípustná vzdálenost v metrech (defaultně 15 m)
        Výstup:
            (True/False, distance)
            - True, pokud je vzdálenost menší než tolerance
            - False, pokud je vzdálenost větší než tolerance
            - distance: Vzdálenost mezi body v metrech
        """
        distance = Evaluator.get_distance(coord1, coord2)
        is_within_tolerance = distance <= tolerance
        return is_within_tolerance, distance
