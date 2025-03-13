from AirspaceManager.extractor.convertor import Convertor
import re

class AirspaceFormatter:
    COMMON_RADIO_STATIONS = {
        '126.100' : 'Praha Information (W)',
        '136.175' : 'Praha Information (E)',
        '119.375' : 'Ostrava Radar'
    }

    def __init__(self, airspace):
        self.airspace = airspace

    def to_openair(self) -> str:
        """ Převádí Airspace objekt do OpenAir formátu """
        lines = []

        if self.airspace.airspace_class:
            lines.append(f"AC {self.airspace.airspace_class}")

        if self.airspace.name:
            frequency_pattern = r'\b(1[1-3][0-9]\.\d{1,3})\b'
            cleaned_name = re.sub(frequency_pattern, '', self.airspace.name).strip()
            if self.airspace.frequencies:
                for frequency in self.airspace.frequencies:
                    self.airspace.name += f" {frequency}"
            lines.append(f"AN {self.airspace.name}")

        if self.airspace.category:
            lines.append(f"AY {self.airspace.category}")

        if self.airspace.frequencies:
            lines.append(f"AF {self.airspace.frequencies[0]}") # Do AF tagu pouze první frekvence

        if self.airspace.station_name:
            lines.append(f"AG {self.airspace.station_name}")
        else:
            # pokud je první frekvence v COMMON_RADIO_STATION, pak naplní station name
            if self.airspace.frequencies:
                if self.airspace.frequencies[0] in self.COMMON_RADIO_STATIONS:
                    self.airspace.station_name = self.COMMON_RADIO_STATIONS[self.airspace.frequencies[0]]
                    lines.append(f"AG {self.airspace.station_name}")

        if self.airspace.lower_limit and self.airspace.upper_limit:
            lines.append(f"AL {self._format_vertical_limit(self.airspace.lower_limit)}")
            lines.append(f"AH {self._format_vertical_limit(self.airspace.upper_limit)}")

        # Přidání tvarů (polygony, kruhy, oblouky)
        for command in self.airspace.draw_commands:
            if command['type'] == 'polygon_point':
                # === Převod na CSDMS pomocí get_csdms_from_decimal() ===
                csdms = Convertor.get_csdms_from_decimal(command['polygon_point_coordinate'])
                lines.append(f"DP {csdms}")

            elif command['type'] == 'circle':
                # === Převod na CSDMS pomocí get_csdms_from_decimal() ===
                csdms = Convertor.get_csdms_from_decimal(command['circle_center_coordinate'])
                lines.append(f"V X={csdms}")
                lines.append(f"DC {command['circle_radius']} *{command['radius_unit']}")

            elif command['type'] == 'arc':
                # === Převod na CSDMS pomocí get_csdms_from_decimal() ===
                center_csdms = Convertor.get_csdms_from_decimal(command['arc_center_coordinate'])
                start_csdms = Convertor.get_csdms_from_decimal(command['arc_start_point_coordinate'])
                end_csdms = Convertor.get_csdms_from_decimal(command['arc_end_point_coordinate'])
                lines.append(f"V X={center_csdms}")
                lines.append(f"V D={command['arc_direction']}")
                lines.append(f"DB {start_csdms}, {end_csdms}")

        return "\n".join(lines)

    def _format_vertical_limit(self, limit: dict) -> str:
        """ Formátuje vertikální limit pro OpenAir """
        if limit['unit'] == "FL":
            return f"FL{limit['value']}"
        else:
            return f"{limit['value']} {limit['unit']}"
