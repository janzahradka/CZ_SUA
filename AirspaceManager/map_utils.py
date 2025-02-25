import numpy as np

def calculate_arc_points(center, start, end, direction="+", num_points=100):
    """
    Vypočítá body oblouku mezi start a end kolem center.
    direction: '+' pro směr hodinových ručiček, '-' pro proti směru.
    num_points: počet bodů na oblouku.
    """
    # Převod na radiány
    def to_rad(deg):
        return deg * np.pi / 180

    # Převod na stupně
    def to_deg(rad):
        return rad * 180 / np.pi

    # Převod na radiány
    center_lat, center_lon = to_rad(center[0]), to_rad(center[1])
    start_lat, start_lon = to_rad(start[0]), to_rad(start[1])
    end_lat, end_lon = to_rad(end[0]), to_rad(end[1])

    # Poloměr oblouku
    radius = np.arccos(
        np.sin(center_lat) * np.sin(start_lat) +
        np.cos(center_lat) * np.cos(start_lat) * np.cos(start_lon - center_lon)
    )

    # Úhly
    start_angle = np.arctan2(np.sin(start_lon - center_lon) * np.cos(start_lat),
                             np.cos(center_lat) * np.sin(start_lat) -
                             np.sin(center_lat) * np.cos(start_lat) * np.cos(start_lon - center_lon))
    end_angle = np.arctan2(np.sin(end_lon - center_lon) * np.cos(end_lat),
                           np.cos(center_lat) * np.sin(end_lat) -
                           np.sin(center_lat) * np.cos(end_lat) * np.cos(end_lon - center_lon))

    # === OPRAVA SMĚRU ===
    # Směr oblouku
    if direction == "-":  # Proti směru hodinových ručiček
        if end_angle > start_angle:
            end_angle -= 2 * np.pi
    else:  # Ve směru hodinových ručiček
        if end_angle < start_angle:
            end_angle += 2 * np.pi

    # Vytvoření posloupnosti úhlů
    angles = np.linspace(start_angle, end_angle, num_points)

    # Výpočet bodů oblouku
    arc_points = []
    for angle in angles:
        lat = np.arcsin(np.sin(center_lat) * np.cos(radius) +
                        np.cos(center_lat) * np.sin(radius) * np.cos(angle))
        lon = center_lon + np.arctan2(np.sin(angle) * np.sin(radius) * np.cos(center_lat),
                                      np.cos(radius) - np.sin(center_lat) * np.sin(lat))
        arc_points.append((to_deg(lat), to_deg(lon)))

    return arc_points
