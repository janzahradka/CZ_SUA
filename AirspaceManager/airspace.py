from AirspaceManager.extractor.convertor import Convertor

class Airspace:
    """ Třída Airspace reprezentuje jeden vzdušný prostor """

    def __init__(self, name=None, airspace_class=None, category=None,
                 frequency=None, station_name=None,
                 upper_limit=None, lower_limit=None, draw_commands=None):
        self.name = name
        self.airspace_class = airspace_class
        self.category = category
        self.frequency = frequency
        self.station_name = station_name
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.draw_commands = draw_commands if draw_commands is not None else []


    def to_dict(self):
        """ Převede objekt na slovník (např. pro předání do Renderer) """
        return {
            "name": self.name,
            "airspace_class": self.airspace_class,
            "category": self.category,
            "frequency": self.frequency,
            "station_name": self.station_name,
            "upper_limit": self.upper_limit,
            "lower_limit": self.lower_limit,
            "draw_commands": self.draw_commands,
        }

    def format_draw_commands(self):
        """ Formátovaný výpis draw_commands pro čitelnější ladění ve formátu CSDMS """
        output = "Příkazy kreslení:\n"
        for command in self.draw_commands:
            for key, value in command.items():
                if key != "type":
                    # === Převod na CSDMS formát pokud jde o souřadnice ===
                    if isinstance(value, tuple) and len(value) == 2:
                        lat, lon = value
                        csdms_lat = Convertor.decimal_to_csdms(lat, is_longitude=False)
                        csdms_lon = Convertor.decimal_to_csdms(lon, is_longitude=True)
                        output += f"      {key}: {csdms_lat} {csdms_lon}\n"
                    else:
                        output += f"      {key}: {value}\n"
        return output

    def format_limit(self, limit):
        """ Formátovaný výpis limitu jako 'value unit' nebo 'unitvalue' pro FL """
        if limit and "value" in limit and "unit" in limit:
            # === Flight Levels (FL) ===
            if limit["unit"] == "FL":
                return f"{limit['unit']} {limit['value']}"  # Např. FL240, FL95
            # === Ostatní jednotky ===
            return f"{limit['value']} {limit['unit']}"  # Např. 4000 MSL, 1000 ft AGL
        return f"Neznámý formát limitu: {limit}"

    def __str__(self):
        """ Textová reprezentace pro ladění a testování """
        return (
            f"\n=== Airspace ===\n"
            f" airspace_class (AC): {self.airspace_class}\n"
            f" name (AN): {self.name}\n"
            f" category (AY): {self.category}\n"
            f" frequency (AF): {self.frequency}\n"
            f" station_name (AG): {self.station_name}\n"
            f" upper_limit (AH): {self.format_limit(self.upper_limit)}\n"
            f" lower_limit (AL): {self.format_limit(self.lower_limit)}\n"
            f" draw_commands (): {self.draw_commands}\n"
            f"{self.format_draw_commands()}"
        )
