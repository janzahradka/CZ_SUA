import folium
import webbrowser
from map_utils import calculate_arc_points  # Původní funkce z map_utils.py


class Renderer:
    """ Třída Renderer pro vykreslení vzdušných prostorů na mapě pomocí Folium """

    def __init__(self, airspaces):
        self.airspaces = airspaces  # Seznam Airspace objektů

    def render_map(self):
        """ Vytvoří mapu a vykreslí všechny prostory """
        # === Vytvoření mapy s výchozím středem v ČR ===
        map_object = folium.Map(location=[50.0, 15.0], zoom_start=6)
        all_coordinates = []

        # === Vykreslení všech prostorů ===
        for airspace in self.airspaces:
            draw_commands = airspace.draw_commands
            polygon_points = []

            for command in draw_commands:
                if command["type"] == "polygon_point":
                    # === Polygon Point ===
                    lat_lon = command["polygon_point_coordinate"].split(" ")
                    lat = float(lat_lon[0].replace(":", "."))
                    lon = float(lat_lon[2].replace(":", "."))
                    polygon_points.append((lat, lon))
                    all_coordinates.append((lat, lon))

                elif command["type"] == "circle":
                    # === Circle ===
                    self.render_circle(map_object, command)

                elif command["type"] == "arc":
                    # === Arc ===
                    self.render_arc(map_object, command, polygon_points, all_coordinates)

            # === Vykreslení polygonu ===
            if polygon_points:
                polygon_points.append(polygon_points[0])  # Uzavření polygonu
                polygon = folium.Polygon(
                    locations=polygon_points,
                    color='green',
                    fill=True,
                    fill_color='lightgreen'
                ).add_to(map_object)
                # Popup s metainformacemi
                popup_content = self.build_popup_content(airspace)
                folium.Popup(popup_content, max_width=300, show=False).add_to(polygon)

        # === Nastavení zoomu na všechny prostory ===
        if all_coordinates:
            lats = [coord[0] for coord in all_coordinates]
            lons = [coord[1] for coord in all_coordinates]
            north = max(lats)
            south = min(lats)
            east = max(lons)
            west = min(lons)
            map_object.fit_bounds([(south, west), (north, east)])

        # === Uložení a zobrazení mapy ===
        map_object.save("airspace_map.html")
        webbrowser.open("airspace_map.html")

    def render_circle(self, map_object, command):
        """ Vykreslí kružnici """
        center_coordinate = command["circle_center_coordinate"].split(" ")
        lat = float(center_coordinate[0].replace(":", "."))
        lon = float(center_coordinate[2].replace(":", "."))
        radius_nm = float(command["circle_radius"])
        radius_m = radius_nm * 1852  # Převod NM na metry

        folium.Circle(
            location=(lat, lon),
            radius=radius_m,
            color='blue',
            fill=True,
            fill_color='lightblue'
        ).add_to(map_object)

    def render_arc(self, map_object, command, polygon_points, all_coordinates):
        """ Vykreslí oblouk jako část kružnice """
        center = command["arc_center_coordinate"].split(" ")
        center = (float(center[0].replace(":", ".")), float(center[2].replace(":", ".")))
        start = command["arc_start_point_coordinate"].split(" ")
        start_coords = (float(start[0].replace(":", ".")), float(start[2].replace(":", ".")))
        end = command["arc_end_point_coordinate"].split(" ")
        end_coords = (float(end[0].replace(":", ".")), float(end[2].replace(":", ".")))
        direction = command["arc_direction"]

        arc_points = calculate_arc_points(center, start_coords, end_coords, direction)

        # Přidáme body oblouku do polygonu
        if polygon_points:
            polygon_points.append(polygon_points[-1])  # Spojení s předchozím bodem
        polygon_points.extend(arc_points)
        polygon_points.append(end_coords)

        all_coordinates.extend(arc_points)

    def build_popup_content(self, airspace):
        """ Sestaví obsah popupu s metainformacemi """
        content = ""
        if airspace.name:
            content += f"Název: <b>{airspace.name}</b><br>"
        if airspace.airspace_class:
            content += f"Třída: <b>{airspace.airspace_class}</b><br>"
        if airspace.category:
            content += f"Kategorie: <b>{airspace.category}</b><br>"
        if airspace.frequency:
            content += f"Frekvence: <b>{airspace.frequency}</b><br>"
        if airspace.station_name:
            content += f"Stanoviště: <b>{airspace.station_name}</b><br>"
        if airspace.upper_limit:
            content += f"Horní hranice: <b>{airspace.format_limit(airspace.upper_limit)}</b><br>"
        if airspace.lower_limit:
            content += f"Spodní hranice: <b>{airspace.format_limit(airspace.lower_limit)}</b><br>"
        return content
