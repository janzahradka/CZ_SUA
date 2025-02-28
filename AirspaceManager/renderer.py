import folium
import webbrowser
import numpy as np
from extractor.convertor import Convertor

class Renderer:
    """Renderer for drawing airspaces on a map using Folium"""

    def __init__(self, airspaces):
        self.airspaces = airspaces  # List of Airspace objects

    def get_coordinate(self, coord_input):
        """
        If coord_input is a dict, return it.
        If it is a string, parse it using Convertor.extract_coodinate_from_text.
        Otherwise, return None.
        """
        if isinstance(coord_input, dict):
            return coord_input
        elif isinstance(coord_input, str):
            return Convertor.extract_coodinate_from_text(coord_input)
        else:
            return None

    def calculate_arc_points(self, center, start, end, direction="+", num_points=100):
        """
        Calculates arc points between start and end around center.
        direction: '+' for clockwise, '-' for counterclockwise.
        num_points: number of points on the arc.
        """
        def to_rad(deg):
            return deg * np.pi / 180

        def to_deg(rad):
            return rad * 180 / np.pi

        center_lat, center_lon = to_rad(center[0]), to_rad(center[1])
        start_lat, start_lon = to_rad(start[0]), to_rad(start[1])
        end_lat, end_lon = to_rad(end[0]), to_rad(end[1])

        radius = np.arccos(
            np.sin(center_lat) * np.sin(start_lat) +
            np.cos(center_lat) * np.cos(start_lat) * np.cos(start_lon - center_lon)
        )

        start_angle = np.arctan2(np.sin(start_lon - center_lon) * np.cos(start_lat),
                                 np.cos(center_lat) * np.sin(start_lat) -
                                 np.sin(center_lat) * np.cos(start_lat) * np.cos(start_lon - center_lon))
        end_angle = np.arctan2(np.sin(end_lon - center_lon) * np.cos(end_lat),
                               np.cos(center_lat) * np.sin(end_lat) -
                               np.sin(center_lat) * np.cos(end_lat) * np.cos(end_lon - center_lon))

        if direction == "-":
            if end_angle > start_angle:
                end_angle -= 2 * np.pi
        else:
            if end_angle < start_angle:
                end_angle += 2 * np.pi

        angles = np.linspace(start_angle, end_angle, num_points)
        arc_points = []
        for angle in angles:
            lat = np.arcsin(np.sin(center_lat) * np.cos(radius) +
                            np.cos(center_lat) * np.sin(radius) * np.cos(angle))
            lon = center_lon + np.arctan2(np.sin(angle) * np.sin(radius) * np.cos(center_lat),
                                          np.cos(radius) - np.sin(center_lat) * np.sin(lat))
            arc_points.append((to_deg(lat), to_deg(lon)))
        return arc_points

    def render_map(self):
        """Creates a map and draws all airspaces."""
        # Nastavujeme výchozí zoom na 8
        map_object = folium.Map(location=[50.0, 15.0], zoom_start=8)
        all_coordinates = []

        for airspace in self.airspaces:
            draw_commands = airspace.draw_commands
            polygon_points = []

            for command in draw_commands:
                if command["type"] == "polygon_point":
                    coord = self.get_coordinate(command["polygon_point_coordinate"])
                    if coord is None:
                        continue
                    lat = coord["lat"]
                    lon = coord["lon"]
                    polygon_points.append((lat, lon))
                    all_coordinates.append((lat, lon))

                elif command["type"] == "circle":
                    self.render_circle(map_object, command, all_coordinates)

                elif command["type"] == "arc":
                    self.render_arc(map_object, command, polygon_points, all_coordinates)

            if polygon_points:
                polygon_points.append(polygon_points[0])  # Close the polygon
                polygon = folium.Polygon(
                    locations=polygon_points,
                    color='green',
                    fill=True,
                    fill_color='lightgreen'
                ).add_to(map_object)
                popup_content = self.build_popup_content(airspace)
                folium.Popup(popup_content, max_width=300, show=False).add_to(polygon)

        if all_coordinates:
            lats = [coord[0] for coord in all_coordinates]
            lons = [coord[1] for coord in all_coordinates]
            north = max(lats)
            south = min(lats)
            east = max(lons)
            west = min(lons)

            # Přidáme marži až 5násobek velikosti prostoru
            margin_factor = 1.0
            lat_margin = (north - south) * margin_factor
            lon_margin = (east - west) * margin_factor

            north += lat_margin
            south -= lat_margin
            east += lon_margin
            west -= lon_margin

            map_object.fit_bounds([(south, west), (north, east)])

        map_object.save("airspace_map.html")
        webbrowser.open("airspace_map.html")

    def render_circle(self, map_object, command, all_coordinates):
        """Renders a circle and adds its bounding box to all_coordinates."""
        coord = self.get_coordinate(command["circle_center_coordinate"])
        if coord is None:
            return
        lat = coord["lat"]
        lon = coord["lon"]
        radius_nm = float(command["circle_radius"])
        radius_m = radius_nm * 1852  # Convert NM to meters

        folium.Circle(
            location=(lat, lon),
            radius=radius_m,
            color='blue',
            fill=True,
            fill_color='lightblue'
        ).add_to(map_object)

        # Přibližný výpočet bounding boxu kruhu
        dlat = radius_m / 111000  # přibližně 111 km na stupeň zeměpisné šířky
        dlon = radius_m / (111000 * np.cos(np.radians(lat)))  # korekce pro zeměpisnou délku
        # Přidáme čtyři rohy bounding boxu
        all_coordinates.append((lat - dlat, lon - dlon))
        all_coordinates.append((lat - dlat, lon + dlon))
        all_coordinates.append((lat + dlat, lon - dlon))
        all_coordinates.append((lat + dlat, lon + dlon))

    def render_arc(self, map_object, command, polygon_points, all_coordinates):
        """Renders an arc as part of a circle."""
        center = self.get_coordinate(command["arc_center_coordinate"])
        start = self.get_coordinate(command["arc_start_point_coordinate"])
        end = self.get_coordinate(command["arc_end_point_coordinate"])
        if center is None or start is None or end is None:
            return
        center_coords = (center["lat"], center["lon"])
        start_coords = (start["lat"], start["lon"])
        end_coords = (end["lat"], end["lon"])
        direction = command["arc_direction"]

        arc_points = self.calculate_arc_points(center_coords, start_coords, end_coords, direction)

        if polygon_points:
            polygon_points.append(polygon_points[-1])  # Connect to previous point
        polygon_points.extend(arc_points)
        polygon_points.append(end_coords)

        all_coordinates.extend(arc_points)

    def build_popup_content(self, airspace):
        """Builds popup content with airspace details."""
        content = ""
        if airspace.name:
            content += f"Name: <b>{airspace.name}</b><br>"
        if airspace.airspace_class:
            content += f"Class: <b>{airspace.airspace_class}</b><br>"
        if airspace.category:
            content += f"Category: <b>{airspace.category}</b><br>"
        if airspace.frequencies:
            content += f"Frequencies: <b>{airspace.frequencies}</b><br>"
        if airspace.station_name:
            content += f"Station: <b>{airspace.station_name}</b><br>"
        if airspace.upper_limit:
            content += f"Upper Limit: <b>{airspace.format_limit(airspace.upper_limit)}</b><br>"
        if airspace.lower_limit:
            content += f"Lower Limit: <b>{airspace.format_limit(airspace.lower_limit)}</b><br>"
        return content
