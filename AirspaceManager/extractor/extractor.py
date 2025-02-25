import re

class Extractor:
    """ Extractor pro méně strukturovaný text """

    def __init__(self, input_text):
        """ Inicializace a rozdělení vstupního textu na řádky """
        self.input_text = input_text
        self.lines = input_text.splitlines()

    def extract(self):
        """ Základní metoda pro extrakci dat """
        print("Extracting from less structured text...")
        return {
            "name": "Example Name",
            "category": "Example Category"
        }


# class Extractor:
#     """ Nadřazená třída Extractor pro rozpoznání typu vstupu a vytvoření Airspace """
#
#     def __init__(self, input_text):
#         self.input_text = input_text
#         self.lines = input_text.splitlines()
#         self.lines_by_coords = self.get_lines_by_coords(input_text)
#         self.airspace_name = self.get_airspace_name(self.lines)
#
#     def get_extractor(self):
#         """ Rozpozná typ vstupu a vytvoří odpovídající extraktor """
#         # === Rozpoznání OpenAir formátu ===
#
#         if any(re.match(r"^\s*(AN|AC|AY|DC|AF|AG|DP|AH|AL)\b", line) for line in self.lines):
#             return ExtractorOpenAir(self.input_text)
#
#         # === Jinak použijeme Plain extraktor ===
#         return ExtractorPlain(self.input_text)
#
#     def to_airspace(self):
#         """ Naplní a předá kompletní objekt Airspace """
#         extractor = self.get_extractor()
#         return extractor.to_airspace()
#
#     def get_lines_by_coords(self,text):
#         """
#         Rozdělí text na řádky dle koordinátů. Každý řádek vyjma prvního začíná koordinátem.
#         """
#
#         # Odstraníme zalomení řádků a vytvoříme jednolitý řetězec
#         single_line_text = text.replace("\n", " ")
#
#         # Seznam pro uložení indexů všech shod (jen jejich začátek)
#         match_indices = []
#
#         # Iterace přes všechny vzory v COORIDNATES_PATTERNS
#         for pattern in COORIDNATES_PATTERNS:
#             for match in re.finditer(pattern, single_line_text):
#                 # Uložíme start index shody
#                 match_indices.append(match.start())
#
#         # Deduplication: odstranění duplicitních indexů
#         match_indices = sorted(set(match_indices))
#
#         # Kontrola překryvů (jen pro případ, že by existovaly duplicity, i když by neměly)
#         for i in range(len(match_indices) - 1):
#             start_current = match_indices[i]
#             start_next = match_indices[i + 1]
#             # Pokud dvě shody začínají příliš blízko (například další shoda by začínala uvnitř předchozí části)
#             if start_current >= start_next:
#                 raise ValueError(
#                     f"Překryv nalezen mezi shodami na pozicích {start_current} a {start_next}."
#                 )
#
#         # Rozdělení textu na části podle počátečních indexů shod
#         split_lines = []
#         last_index = 0
#
#         for start in match_indices:
#             # Text před shodou přidáme jako součást seznamu
#             before_match = single_line_text[last_index:start].strip()
#             if before_match:
#                 split_lines.append(before_match)
#             # poslední prvek
#             if start == max(match_indices):
#                 split_lines.append(single_line_text[start:].strip())
#
#             # Posuneme `last_index` na začátek další části
#             last_index = start
#
#         return split_lines
#
#     def get_airspace_name(self, text):
#         airspace_name = ""
#         return airspace_name

