import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import pyperclip
from airac_import import convert_airac_to_openair
import folium
import webbrowser
from geo_utils import extract_geo_coordinate
from map_utils import calculate_arc_points
from tkinter import ttk, scrolledtext
import tkinter as tk
from tkinter import messagebox

"""
pro lepší zážitek doporučuju nainstalovat font Roboto a JetBrains Mono
Roboto: https://fonts.google.com/specimen/Roboto
JetBrains Mono: https://fonts.google.com/specimen/JetBrains+Mono, https://www.jetbrains.com/lp/mono/
"""

class AirspaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airspace Converter")
        self.root.geometry("1600x800")

        # Ovládací lišta s Unicode ikonami
        self.create_toolbar()

        # rozložení s taby
        self.create_tabs()

    def create_toolbar(self):
        """ Vytvoří ovládací lištu s Unicode ikonami na tlačítkách """
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Přidání pružné mezery vlevo
        tk.Label(toolbar, text="").pack(side=tk.LEFT, expand=True)

        # Vycentrovaná tlačítka s větším fontem
        paste_btn = tk.Button(toolbar, text="📋 Vložit z clipboardu", font=("Roboto", 12), command=self.paste_from_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)

        process_btn = tk.Button(toolbar, text="▶️ Spustit zpracování", font=("Roboto", 12), command=self.process_text)
        process_btn.pack(side=tk.LEFT, padx=2, pady=2)

        copy_btn = tk.Button(toolbar, text="📄 Kopírovat výstup", font=("Roboto", 12), command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)

        map_btn = tk.Button(toolbar, text="🗺️ Zobrazit na mapě", font=("Roboto", 12), command=self.show_map)
        map_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Přidání pružné mezery vpravo od vycentrovaných tlačítek
        tk.Label(toolbar, text="").pack(side=tk.LEFT, expand=True)

        # Tlačítko Reset na pravém okraji
        reset_btn = tk.Button(toolbar, text="🔄 Reset", font=("Roboto", 12), command=self.reset_fields)
        reset_btn.pack(side=tk.RIGHT, padx=2, pady=2)


    # def create_text_fields(self):
    #     """ Vytvoří textová pole s popisky pro vstup a výstup """
    #
    #     # Detekce dostupnosti fontu JetBrains Mono
    #     try:
    #         import tkinter.font as tkFont
    #         available_fonts = tkFont.families()
    #         if "JetBrains Mono" in available_fonts:
    #             font_to_use = ("JetBrains Mono", 12)
    #         else:
    #             font_to_use = ("Courier New", 12)  # Defaultní monospace
    #     except Exception:
    #         font_to_use = ("Courier New", 12)  # Fallback na Courier New
    #
    #     # Rámec pro vstupní pole a popisek
    #     input_frame = tk.Frame(self.root)
    #     input_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    #
    #     # Popisek pro vstup
    #     input_label = tk.Label(input_frame, text="Vstup", font=("Arial", 12, "bold"))
    #     input_label.pack(anchor="w")  # Zarovnáno vlevo
    #
    #     # Vstupní pole (80 znaků na šířku) s JetBrains Mono nebo Courier New
    #     self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=80, height=30)
    #     self.input_text.config(font=font_to_use)
    #     self.input_text.pack(fill=tk.BOTH, expand=True)
    #
    #     # Rámec pro výstupní pole a popisek
    #     output_frame = tk.Frame(self.root)
    #     output_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    #
    #     # Popisek pro výstup
    #     output_label = tk.Label(output_frame, text="Výstup", font=("Arial", 12, "bold"))
    #     output_label.pack(anchor="w")  # Zarovnáno vlevo
    #
    #     # Výstupní pole (80 znaků na šířku) s JetBrains Mono nebo Courier New
    #     self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=30)
    #     self.output_text.config(font=font_to_use)
    #     self.output_text.pack(fill=tk.BOTH, expand=True)



    def paste_from_clipboard(self):
        """ Vloží text z clipboardu do vstupního pole """
        try:
            clipboard_content = pyperclip.paste()
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, clipboard_content)
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při vkládání z clipboardu: {e}")

    def process_text(self):
        """ Spustí zpracování vstupního textu """
        input_text = self.input_text.get(1.0, tk.END).strip()
        if input_text:
            self.output_text.delete(1.0, tk.END)
            try:
                # Zpracování vstupu
                output = convert_airac_to_openair(input_text)
                self.output_text.insert(tk.END, output)

                # === AUTOMATICKÉ PŘEPNUTÍ NA VÝSTUP ===
                self.output_notebook.select(self.output_tab)

            except Exception as e:
                self.output_text.insert(tk.END, f"Chyba při zpracování: {e}")
        else:
            messagebox.showwarning("Upozornění", "Vstupní pole je prázdné.")

    def copy_to_clipboard(self):
        """ Zkopíruje výstup do clipboardu bez pop-up okna """
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            pyperclip.copy(output_text)
        else:
            messagebox.showwarning("Upozornění", "Výstupní pole je prázdné.")

    def reset_fields(self):
        """ Resetuje vstupní a výstupní pole """
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

    def build_popup_content(self, space_name, space_class, category, frequency, station_name, upper_limit, lower_limit):
        """ Sestaví HTML obsah pro popup okno na základě vyplněných tagů """
        popup_content = ""

        # Pomocná funkce pro převod ft na m
        def convert_to_meters(feet):
            return round(float(feet) * 0.3048)

        # Převod jednotek pro horní hranici
        if upper_limit:
            if "MSL" in upper_limit or "AMSL" in upper_limit:
                # Pokud je MSL, převedeme ft na m
                value = ''.join(filter(str.isdigit, upper_limit))
                if value:
                    meters = convert_to_meters(value)
                    upper_limit = f"{value} ft / {meters} m AMSL"
            elif "AGL" in upper_limit:
                # Pokud je AGL, převedeme ft na m
                value = ''.join(filter(str.isdigit, upper_limit))
                if value:
                    meters = convert_to_meters(value)
                    upper_limit = f"{value} ft / {meters} m AGL"

        # Převod jednotek pro spodní hranici
        if lower_limit:
            if "MSL" in lower_limit or "AMSL" in lower_limit:
                # Pokud je MSL, převedeme ft na m
                value = ''.join(filter(str.isdigit, lower_limit))
                if value:
                    meters = convert_to_meters(value)
                    lower_limit = f"{value} ft / {meters} m AMSL"
            elif "AGL" in lower_limit:
                # Pokud je AGL, převedeme ft na m
                value = ''.join(filter(str.isdigit, lower_limit))
                if value:
                    meters = convert_to_meters(value)
                    lower_limit = f"{value} ft / {meters} m AGL"

        # Sestavení obsahu podle požadovaného pořadí
        if space_name:
            popup_content += f"Název: <b>{space_name}</b><br>"
        if space_class:
            popup_content += f"Třída: <b>{space_class}</b><br>"
        if category:
            popup_content += f"Kategorie: <b>{category}</b><br>"
        if frequency:
            popup_content += f"FRQ: <b>{frequency}</b><br>"
        if station_name:
            popup_content += f"Název stanoviště: <b>{station_name}</b><br>"
        if upper_limit:
            popup_content += f"Horní hranice: <b>{upper_limit}</b><br>"
        if lower_limit:
            popup_content += f"Spodní hranice: <b>{lower_limit}</b><br>"

        # Pokud nejsou vyplněné žádné informace
        if not popup_content:
            popup_content = "Prostor nemá definované podrobnosti"

        return popup_content

    def show_on_map(self, output_text):
        """ Vykreslí obrazce na interaktivní mapě pomocí Folium a zazoomuje na prostor """
        # Vytvoříme mapu s výchozím středem v ČR
        map_object = folium.Map(location=[50.0, 15.0], zoom_start=6)

        # Přidáme vlastní CSS pro offset popupu
        custom_css = """
        <style>
            .leaflet-popup-content-wrapper {
                transform: translate(0px, -150px) !important;
            }
            .leaflet-popup-tip {
                display: none !important;
            }
        </style>
        """
        folium.Element(custom_css).add_to(map_object)

        # Rozdělíme text na řádky a projdeme je
        lines = output_text.splitlines()

        # Proměnné pro uložení bodů polygonu, středu a poloměru
        polygon_points = []
        center = None
        radius = None
        all_coordinates = []  # Seznam všech souřadnic pro výpočet bounding boxu

        # Metainformace
        space_name = None
        space_class = None
        category = None
        frequency = None
        station_name = None
        upper_limit = None
        lower_limit = None
        direction = "+"  # Výchozí směr pro oblouk: ve směru hodinových ručiček

        for line in lines:
            if line.startswith("AN"):
                # Název prostoru
                space_name = line.split("AN ")[1]

            elif line.startswith("AC"):
                # Třída prostoru
                space_class = line.split("AC ")[1]

            elif line.startswith("AY"):
                # Kategorie prostoru
                category = line.split("AY ")[1]

            elif line.startswith("AF"):
                # Frekvence
                frequency = line.split("AF ")[1]

            elif line.startswith("AG"):
                # Název stanoviště
                station_name = line.split("AG ")[1]

            elif line.startswith("AH"):
                # Horní vertikální hranice
                upper_limit = line.split("AH ")[1]

            elif line.startswith("AL"):
                # Spodní vertikální hranice
                lower_limit = line.split("AL ")[1]

            elif line.startswith("V D="):
                # Směr oblouku
                direction = line.split("V D=")[1].strip()

            elif line.startswith("DP"):
                # Polygonový bod
                coordinate_str = line.split("DP ")[1]
                coords = extract_geo_coordinate(coordinate_str)
                if coords:
                    lat, lon = coords
                    polygon_points.append((lat, lon))
                    all_coordinates.append((lat, lon))

            elif line.startswith("V X="):
                # Střed kruhu nebo oblouku
                center_str = line.split("V X=")[1].strip()
                center = extract_geo_coordinate(center_str)
                if center:
                    all_coordinates.append(center)

            elif line.startswith("DC"):
                # Kruh
                radius_nm = float(line.split()[1])  # Poloměr v námořních mílích
                radius = radius_nm * 1852  # Převod NM na metry
                if center and radius:
                    circle = folium.Circle(
                        location=center,
                        radius=radius,
                        color='blue',
                        fill=True,
                        fill_color='lightblue'
                    ).add_to(map_object)

                    # Přidáme popup s metainformacemi po kliknutí na kruh
                    popup_content = self.build_popup_content(space_name, space_class, category, frequency, station_name,
                                                             upper_limit, lower_limit)
                    folium.Popup(popup_content, max_width=300, show=False, sticky=False).add_to(circle)

            elif line.startswith("DB"):
                # Oblouk
                points = line.split("DB ")[1].split(",")
                start_coords = extract_geo_coordinate(points[0].strip())
                end_coords = extract_geo_coordinate(points[1].strip())
                if start_coords and end_coords and center:
                    # Výpočet bodů oblouku
                    arc_points = calculate_arc_points(center, start_coords, end_coords, direction)
                    # === SPOJENÍ OBLUKU S POLYGONEM ===
                    # 1. Pokud je předchozí bod, připojíme ho k začátku oblouku
                    if polygon_points:
                        polygon_points.append(polygon_points[-1])  # Spojení s předchozím bodem
                    # 2. Připojíme všechny body oblouku
                    polygon_points.extend(arc_points)
                    # 3. Připojíme koncový bod oblouku
                    polygon_points.append(end_coords)
                    # 4. Body oblouku jsou nyní součástí polygonu
                    all_coordinates.extend(arc_points)

                    # # Přidáme popup s metainformacemi po kliknutí na oblouk
                    # popup_content = self.build_popup_content(space_name, space_class, category, frequencies, station_name,
                    #                                          upper_limit, lower_limit)
                    # folium.Popup(popup_content, max_width=300, show=False, sticky=False).add_to(arc)

        # Pokud máme polygonové body, vykreslíme je jako polygon
        if polygon_points:
            polygon = folium.Polygon(
                locations=polygon_points,
                color='green',
                fill=True,
                fill_color='lightgreen'
            ).add_to(map_object)

            # Přidáme popup s metainformacemi po kliknutí na polygon
            popup_content = self.build_popup_content(space_name, space_class, category, frequency, station_name,
                                                     upper_limit, lower_limit)
            folium.Popup(popup_content, max_width=300, show=False, sticky=False).add_to(polygon)

        # === VÝPOČET ROZŠÍŘENÉHO BOUNDING BOXU ===
        if all_coordinates:
            lats = [coord[0] for coord in all_coordinates]
            lons = [coord[1] for coord in all_coordinates]
            north = max(lats)
            south = min(lats)
            east = max(lons)
            west = min(lons)

            # Vypočítáme střed bounding boxu
            center_lat = (north + south) / 2
            center_lon = (east + west) / 2

            # Zvětšíme bounding box na dvojnásobek
            height = north - south
            width = east - west
            new_north = center_lat + height
            new_south = center_lat - height
            new_east = center_lon + width
            new_west = center_lon - width

            # Nastavíme mapu tak, aby byla přizpůsobena všem souřadnicím
            map_object.fit_bounds([(new_south, new_west), (new_north, new_east)])

        # Uložíme mapu jako HTML a otevřeme ji v prohlížeči
        map_object.save("airspace_map.html")
        webbrowser.open("airspace_map.html")

    def show_map(self):
        """ Zobrazí výstup na interaktivní mapě """
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            self.show_on_map(output_text)
        else:
            messagebox.showwarning("Upozornění", "Výstupní pole je prázdné.")

    def show_map_multi(self):
        """ Zobrazí všechny prostory z vícenásobného výstupu na jedné mapě """
        # Načteme obsah vícenásobného výstupu
        multi_output_text = self.multi_output_text.get(1.0, tk.END).strip()

        if not multi_output_text:
            # Pokud je vícenásobný výstup prázdný, zobrazíme varování
            messagebox.showwarning("Upozornění", "Vícenásobný výstup je prázdný.")
            return

        # Rozdělíme text na jednotlivé prostory podle dvou prázdných řádků
        spaces = multi_output_text.split("\n\n")

        # Spojíme všechny prostory do jednoho řetězce
        combined_spaces = "\n".join(spaces)

        # Zobrazíme všechny prostory na jedné mapě
        self.show_on_map(combined_spaces)

    def create_tabs(self):
        """ Vytvoří rozložení s taby pro vstup, výstup a vícenásobný výstup """
        # === DETEKCE FONTU JETBRAINS MONO ===
        try:
            import tkinter.font as tkFont
            available_fonts = tkFont.families()
            if "JetBrains Mono" in available_fonts:
                font_to_use = ("JetBrains Mono", 12)
            else:
                font_to_use = ("Courier New", 12)  # Fallback na monospace
        except Exception:
            font_to_use = ("Courier New", 12)

        # === LEVÝ PANEL (VSTUP) ===
        input_notebook = ttk.Notebook(self.root)
        input_notebook.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        input_tab = tk.Frame(input_notebook)
        input_notebook.add(input_tab, text="Vstup")

        # Vstupní pole s JetBrains Mono nebo Courier New
        self.input_text = scrolledtext.ScrolledText(input_tab, wrap=tk.WORD, width=80, height=30, font=font_to_use)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Ovládací lišta pro vstupní pole
        input_toolbar = tk.Frame(input_tab)
        input_toolbar.pack(fill=tk.X)

        clear_input_btn = tk.Button(input_toolbar, text="Vymazat", command=lambda: self.clear_field(self.input_text))
        clear_input_btn.pack(side=tk.RIGHT)

        # === PRAVÝ PANEL (VÝSTUP A VÍCENÁSOBNÝ VÝSTUP) ===
        self.output_notebook = ttk.Notebook(self.root)
        self.output_notebook.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # === Tab pro současné výstupní pole ===
        self.output_tab = tk.Frame(self.output_notebook)
        self.output_notebook.add(self.output_tab, text="Výstup")

        self.output_text = scrolledtext.ScrolledText(self.output_tab, wrap=tk.WORD, width=80, height=30,
                                                     font=font_to_use)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Ovládací lišta pro výstupní pole
        output_toolbar = tk.Frame(self.output_tab)
        output_toolbar.pack(fill=tk.X)

        clear_output_btn = tk.Button(output_toolbar, text="Vymazat", command=lambda: self.clear_field(self.output_text))
        clear_output_btn.pack(side=tk.RIGHT)

        move_to_multi_btn = tk.Button(output_toolbar, text="Přesunout do vícenásobného",
                                      command=self.move_to_multi_output)
        move_to_multi_btn.pack(side=tk.LEFT)

        # === Tab pro vícenásobný výstup ===
        self.multi_output_tab = tk.Frame(self.output_notebook)
        self.output_notebook.add(self.multi_output_tab, text="Vícenásobný výstup")

        self.multi_output_text = scrolledtext.ScrolledText(self.multi_output_tab, wrap=tk.WORD, width=80, height=30,
                                                           font=font_to_use)
        self.multi_output_text.pack(fill=tk.BOTH, expand=True)

        # Ovládací lišta pro vícenásobný výstup
        multi_output_toolbar = tk.Frame(self.multi_output_tab)
        multi_output_toolbar.pack(fill=tk.X)

        clear_multi_output_btn = tk.Button(multi_output_toolbar, text="Vymazat",
                                           command=lambda: self.clear_field(self.multi_output_text))
        clear_multi_output_btn.pack(side=tk.RIGHT)

        show_map_multi_btn = tk.Button(multi_output_toolbar, text="Zobrazit na mapě", command=self.show_map_multi)
        show_map_multi_btn.pack(side=tk.LEFT)

    def move_to_multi_output(self):
        """ Přesune obsah výstupního pole do vícenásobného výstupu a přepne na tento tab """
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            # Přidáme obsah do vícenásobného výstupu s oddělením dvěma prázdnými řádky
            current_text = self.multi_output_text.get(1.0, tk.END).strip()
            if current_text:
                new_text = current_text + "\n\n\n" + output_text
            else:
                new_text = output_text
            self.multi_output_text.delete(1.0, tk.END)
            self.multi_output_text.insert(tk.END, new_text)

            # === AUTOMATICKÉ PŘEPNUTÍ NA VÍCENÁSOBNÝ VÝSTUP ===
            self.output_notebook.select(self.multi_output_tab)
            self.multi_output_text.focus_set()

    def clear_field(self, field):
        """ Vymaže obsah jednoho textového pole """
        field.delete(1.0, tk.END)


# Spuštění aplikace
if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceApp(root)
    root.mainloop()

# TODO: rozšířit zobrazení mapy na více prostorů