import folium
import webbrowser
import numpy as np
from extractor.convertor import Convertor
from folium import MacroElement
from jinja2 import Template
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
import os

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
    """Renderer pro vykreslení vzdušných prostorů do mapy pomocí Folia."""

    def __init__(self, airspaces):
        self.airspaces = airspaces  # List of Airspace objektů

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

    @staticmethod
    def compute_polygon_area(polygon_points):
        if len(polygon_points) < 4:
            return 0
        coords = [(lon, lat) for (lat, lon) in polygon_points]
        poly = Polygon(coords)
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
        poly_m = transform(transformer.transform, poly)
        return poly_m.area / 1e6 # km²

    def get_rendering_polygons(self, airspace):
        """
        Pro daný airspace projde drawing_commands a vrátí kompletní pole polygon_points.
        Převádí typy příkazů: "polygon_point", "circle" i "arc" na jednotný polygon.
        """
        polygon_points = []
        circle_polygon = None
        arc_points = []
        for command in airspace.draw_commands:
            if command["type"] == "circle":
                coord = self.get_coordinate(command["circle_center_coordinate"])
                if coord:
                    lat = coord["lat"]
                    lon = coord["lon"]
                    radius_nm = float(command["circle_radius"])
                    radius_m = radius_nm * 1852
                    polygon_points = self.approximate_circle_polygon((lat, lon), radius_m, num_points=50)
                    continue
            elif command["type"] == "polygon_point":
                coord = self.get_coordinate(command["polygon_point_coordinate"])
                if coord:
                    polygon_points.append((coord["lat"], coord["lon"]))
            elif command["type"] == "arc":
                center = self.get_coordinate(command["arc_center_coordinate"])
                start = self.get_coordinate(command["arc_start_point_coordinate"])
                end = self.get_coordinate(command["arc_end_point_coordinate"])
                if center and start and end:
                    center_coords = (center["lat"], center["lon"])
                    start_coords = (start["lat"], start["lon"])
                    end_coords = (end["lat"], end["lon"])
                    direction = command["arc_direction"]
                    arc_segment = self.calculate_arc_points(center_coords, start_coords, end_coords, direction)
                    polygon_points.extend(arc_segment)

        if polygon_points:
            if polygon_points[0] != polygon_points[-1]:
                polygon_points.append(polygon_points[0])
            return polygon_points
        else:
            return []

    def process_airspace(self, airspace):
        """
        Zpracuje daný airspace – získá polygon, spočítá plochu a sestaví obsah popupu.
        """
        polygon_points = self.get_rendering_polygons(airspace)
        if polygon_points and len(polygon_points) >= 4:
            area = Renderer.compute_polygon_area(polygon_points)
        else:
            area = 0
        popup_content = self.build_popup_content(airspace, area=area)
        airspace_class = getattr(airspace, "airspace_class", "")
        default_color = get_color(airspace_class)
        return {
            "airspace": airspace,
            "polygon_points": polygon_points,
            "area": area,
            "popup": popup_content,
            "airspace_class": airspace_class,
            "default_color": default_color
        }

    def render_map(self, title=None, filename=None):
        # Výchozí hodnota pro titulek
        if not title or title.strip() == "":
            title = "Untitled Map"

        # Generování bezpečného názvu souboru
        sanitized_title = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in title).strip().replace(" ", "_")
        filename = filename or f"{sanitized_title}.html"

        map_object = folium.Map(location=[50.0, 15.0], zoom_start=8)

        # CSS styly
        inline_css = """
        <style>
                 .custom-popup {
                     background-color: white;
                     border: 1px solid gray;
                     padding: 10px;
                     font-size: 14px;
                     border-radius: 5px;
                     box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                     max-height: 200px;
                     max-width: 300px;
                     overflow-y: auto;
                 }
                
                 .leaflet-popup {
                     bottom: 30px !important;
                 }
                
                  #titleBox {
                      position: fixed;
                      top: 10px;                 /* Umístění nahoře */
                      right: 10px;               /* Umístění vpravo */
                      width: 300px;              /* Šířka panelu */
                      padding: 10px;             /* Vnitřní odsazení */
                      background-color: white;   /* Barva pozadí */
                      border: 1px solid gray;    /* Barva a styl okraje */
                      z-index: 1000;             /* Zajištění viditelnosti nad ostatními prvky */
                      font-size: 18px;           /* Velikost písma */
                      border-radius: 10px;       /* Zaoblené rohy */
                      box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.5); /* Přidání stínu */
                  }
                
                  #infoBox {
                      position: fixed;
                      top: 70px;                 /* Umístění nahoře */
                      right: 10px;               /* Umístění vpravo */
                      width: 300px;              /* Šířka panelu */
                      padding: 10px;             /* Vnitřní odsazení */
                      background-color: white;   /* Barva pozadí */
                      border: 1px solid gray;    /* Barva a styl okraje */
                      z-index: 1000;             /* Zajištění viditelnosti nad ostatními prvky */
                      font-size: 14px;           /* Velikost písma */
                      border-radius: 10px;       /* Zaoblené rohy */
                      box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.5); /* Přidání stínu */
                  }     
                             

        </style>
        """

        # Přidání CSS stylů do HTML šablony
        map_object.get_root().html.add_child(folium.Element(inline_css))

        # JavaScript pro přepsání `bottom` hodnoty
        custom_js = """
           <script>
               document.addEventListener("DOMContentLoaded", function() {
                   window.map.on("popupopen", function (e) {
                       var popup = e.popup._container;
                       if (popup) {
                           popup.style.bottom = "30px";
                       }
                   });
               });
           </script>
           """
        map_object.get_root().html.add_child(folium.Element(custom_js))

        # HTML nadpis
        title_html = f"""
            <div id="titleBox">
               <strong>{title}</strong>
            </div>
            """
        map_object.get_root().html.add_child(folium.Element(title_html))

        info_html = """
        <div id="infoBox">
          <b>Airspace Details</b><br>
          Hover over an airspace...
        </div>
        """
        map_object.get_root().html.add_child(folium.Element(info_html))
        processed_airspaces = []
        all_coordinates = []
        # Zpracování každého vzdušného prostoru najednou
        for airspace in self.airspaces:
            processed = self.process_airspace(airspace)
            processed_airspaces.append(processed)
            if processed["polygon_points"]:
                all_coordinates.extend(processed["polygon_points"])
        # Seřazení podle plochy (od největší)
        processed_airspaces.sort(key=lambda x: x["area"], reverse=True)
        print("Computed order of airspaces (Order, Area, Airspace):")
        for idx, proc in enumerate(processed_airspaces, start=1):
            print(f"{idx}. Area: {proc['area']:.2f} km²\n{proc['airspace']}\n")
        # Vykreslení každého prostoru do mapy
        for proc in processed_airspaces:
            polygon_points = proc["polygon_points"]
            if polygon_points and len(polygon_points) >= 3:
                # Převod souřadnic (lat, lon) na formát GeoJSON ([lon, lat])
                geo_coords = [[lon, lat] for (lat, lon) in polygon_points]
                polygon_geojson = {
                    "type": "Feature",
                    "properties": {
                        "popup": proc["popup"],
                        "airspace_class": proc["airspace_class"],
                        "defaultColor": proc["default_color"]
                    },
                    "geometry": {"type": "Polygon", "coordinates": [geo_coords]}
                }
                popup = folium.GeoJsonPopup(
                    fields=["popup"],
                    labels=False,
                    popup_options={
                        "maxWidth": "300",  # maximální šířka pop-upu
                        "className": "custom-popup"
                    }
                )
                geojson = folium.GeoJson(
                    polygon_geojson,
                    style_function=polygon_style_function,
                    highlight_function=constant_highlight,
                    popup=popup,
                )
                geojson.add_child(HoverScript())
                geojson.add_to(map_object)
        # Nastavení zorného pole mapy podle souřadnic
        if all_coordinates:
            lats = [coord[0] for coord in all_coordinates]
            lons = [coord[1] for coord in all_coordinates]
            north = max(lats)
            south = min(lats)
            east = max(lons)
            west = min(lons)
            map_object.fit_bounds([(south, west), (north, east)])
        map_object.save(filename)
        webbrowser.open(f"file://{os.path.realpath(filename)}")

    def build_popup_content(self, airspace, area):
        content = ""
        if airspace.name:
            content += f"Name: <b>{airspace.name}</b><br>"
        if airspace.airspace_class:
            content += f"Class: <b>{airspace.airspace_class}</b><br>"
        if airspace.category:
            content += f"Category: <b>{airspace.category}</b><br>"
        if airspace.frequencies:
            content += f"Frequencies: <b>{ ' '.join(frequency for frequency in airspace.frequencies)}</b><br>"
        if airspace.station_name:
            content += f"Station: <b>{airspace.station_name}</b><br>"
        if airspace.upper_limit:
            content += f"Upper Limit: <b>{airspace.format_limit(airspace.upper_limit)}</b><br>"
        if airspace.lower_limit:
            content += f"Lower Limit: <b>{airspace.format_limit(airspace.lower_limit)}</b><br>"
        if area is not None:
            content += f"Area: <b>{area:.2f} km²</b><br>"
        return content
