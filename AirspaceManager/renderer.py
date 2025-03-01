import folium
import webbrowser
import numpy as np
from extractor.convertor import Convertor
from folium import MacroElement
from jinja2 import Template
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj

def get_color(airspace_class):
    if airspace_class:
        airspace_class = airspace_class.strip().upper()
    mapping = {
        "C": "purple",
        "D": "crimson",
        "R": "orange",
        "Q": "brown",
        "E": "green",
        "GS": "white",
        "P": "red"
    }
    return mapping.get(airspace_class, "blue")


def polygon_style_function(feature):
    # Použijeme předdefinovanou barvu z vlastností
    color = feature["properties"].get("defaultColor", "blue")
    return {
        'fillColor': color,
        'color': color,
        'fillOpacity': 0.4,
        'weight': 2
    }

def constant_highlight(feature):
    return {
        'fillColor': 'yellow',
        'color': 'yellow',
        'fillOpacity': 0.7,
        'weight': 3
    }

class HoverScript(MacroElement):
    _template = Template(u"""
        {% macro script(this, kwargs) %}
        function onEachFeature(feature, layer) {
            layer.on('mouseover', function(e) {
                document.getElementById('infoBox').innerHTML = feature.properties.popup;
                layer.setStyle({
                    fillColor: 'yellow',
                    color: 'yellow',
                    fillOpacity: 0.7,
                    weight: 3
                });
            });
            layer.on('mouseout', function(e) {
                document.getElementById('infoBox').innerHTML = "Hover over an airspace...";
                layer.setStyle({
                    fillColor: feature.properties.defaultColor,
                    color: feature.properties.defaultColor,
                    fillOpacity: 0.4,
                    weight: 2
                });
            });
        }
        {{this._parent.get_name()}}.eachLayer(function(layer) {
            if(layer.feature){
                onEachFeature(layer.feature, layer);
            }
        });
        {% endmacro %}
    """)

class Renderer:
    """Renderer for drawing airspaces on a map using Folium"""

    def __init__(self, airspaces):
        self.airspaces = airspaces  # List of Airspace objects

    def get_coordinate(self, coord_input):
        if isinstance(coord_input, dict):
            return coord_input
        elif isinstance(coord_input, str):
            return Convertor.extract_coodinate_from_text(coord_input)
        else:
            return None

    def calculate_arc_points(self, center, start, end, direction="+", num_points=100):
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

    @staticmethod
    def compute_polygon_area(polygon_points):
        if len(polygon_points) < 4:
            return 0
        coords = [(lon, lat) for (lat, lon) in polygon_points]
        poly = Polygon(coords)
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        poly_m = transform(transformer.transform, poly)
        return poly_m.area

    def approximate_circle_polygon(self, center, radius_m, num_points=50):
        lat, lon = center
        points = []
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            dlat = (radius_m / 111320) * np.cos(angle)
            dlon = (radius_m / (111320 * np.cos(np.radians(lat)))) * np.sin(angle)
            points.append((lat + dlat, lon + dlon))
        points.append(points[0])
        return points

    def render_map(self):
        map_object = folium.Map(location=[50.0, 15.0], zoom_start=8)
        info_html = """
        <div id="infoBox" style="position: fixed; top: 10px; right: 10px; width: 300px;
             padding: 10px; background-color: white; border: 1px solid gray;
             z-index: 1000; font-size: 14px;">
          <b>Airspace Details</b><br>
          Hover over an airspace...
        </div>
        """
        map_object.get_root().html.add_child(folium.Element(info_html))
        all_coordinates = []
        airspaces_with_area = []
        for airspace in self.airspaces:
            polygon_points = []
            found_circle = False
            circle_area = 0
            for command in airspace.draw_commands:
                if command["type"] == "polygon_point":
                    coord = self.get_coordinate(command["polygon_point_coordinate"])
                    if coord:
                        polygon_points.append((coord["lat"], coord["lon"]))
                elif command["type"] == "circle":
                    found_circle = True
                    radius_nm = float(command["circle_radius"])
                    radius_m = radius_nm * 1852
                    circle_area = np.pi * (radius_m ** 2)
            if polygon_points:
                if polygon_points[0] != polygon_points[-1]:
                    polygon_points.append(polygon_points[0])
                area = Renderer.compute_polygon_area(polygon_points)
            elif found_circle:
                area = circle_area
            else:
                area = 0
            airspaces_with_area.append((airspace, area))
        airspaces_with_area.sort(key=lambda x: x[1], reverse=True)
        print("Computed order of airspaces (Order, Area, Airspace):")
        for idx, (airspace, area) in enumerate(airspaces_with_area, start=1):
            print(f"{idx}. Area: {area:.2f}\n{airspace}\n")
        for airspace, area in airspaces_with_area:
            popup_content = self.build_popup_content(airspace)
            airspace_class = airspace.airspace_class if hasattr(airspace, "airspace_class") else ""
            default_color = get_color(airspace_class)
            draw_commands = airspace.draw_commands
            polygon_points = []
            has_polygon = False
            for command in draw_commands:
                if command["type"] == "polygon_point":
                    coord = self.get_coordinate(command["polygon_point_coordinate"])
                    if coord is None:
                        continue
                    lat = coord["lat"]
                    lon = coord["lon"]
                    polygon_points.append((lat, lon))
                    all_coordinates.append((lat, lon))
                    has_polygon = True
                elif command["type"] == "circle":
                    self.render_circle(map_object, command, all_coordinates, popup_content, airspace_class)
                elif command["type"] == "arc":
                    self.render_arc(map_object, command, polygon_points, all_coordinates)
            if has_polygon:
                polygon_points.append(polygon_points[0])
                geo_coords = [[lon, lat] for (lat, lon) in polygon_points]
                polygon_geojson = {
                    "type": "Feature",
                    "properties": {
                        "popup": popup_content,
                        "airspace_class": airspace_class,
                        "defaultColor": default_color
                    },
                    "geometry": {"type": "Polygon", "coordinates": [geo_coords]}
                }
                popup = folium.GeoJsonPopup(fields=["popup"], labels=False)
                geojson = folium.GeoJson(
                    polygon_geojson,
                    style_function=polygon_style_function,
                    highlight_function=constant_highlight,
                    popup=popup,
                )
                geojson.add_child(HoverScript())
                geojson.add_to(map_object)
        if all_coordinates:
            lats = [coord[0] for coord in all_coordinates]
            lons = [coord[1] for coord in all_coordinates]
            north = max(lats)
            south = min(lats)
            east = max(lons)
            west = min(lons)
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

    def render_circle(self, map_object, command, all_coordinates, popup_content=None, airspace_class=""):
        coord = self.get_coordinate(command["circle_center_coordinate"])
        if coord is None:
            return
        lat = coord["lat"]
        lon = coord["lon"]
        radius_nm = float(command["circle_radius"])
        radius_m = radius_nm * 1852
        circle_points = self.approximate_circle_polygon((lat, lon), radius_m, num_points=50)
        for pt in circle_points:
            all_coordinates.append(pt)
        geo_coords = [[pt[1], pt[0]] for pt in circle_points]
        polygon_geojson = {
            "type": "Feature",
            "properties": {
                "popup": popup_content if popup_content else "",
                "airspace_class": airspace_class,
                "defaultColor": get_color(airspace_class)
            },
            "geometry": {"type": "Polygon", "coordinates": [geo_coords]}
        }
        popup = folium.GeoJsonPopup(fields=["popup"], labels=False)
        geojson = folium.GeoJson(
            polygon_geojson,
            style_function=polygon_style_function,
            highlight_function=constant_highlight,
            popup=popup,
        )
        geojson.add_child(HoverScript())
        geojson.add_to(map_object)

    def render_arc(self, map_object, command, polygon_points, all_coordinates):
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
            polygon_points.append(polygon_points[-1])
        polygon_points.extend(arc_points)
        polygon_points.append(end_coords)
        all_coordinates.extend(arc_points)

    def build_popup_content(self, airspace):
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
