import os
import pytest
from AirspaceManager.extractor.extractor import Extractor
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace_formatter import AirspaceFormatter
from AirspaceManager.evaluator import Evaluator

# === Cesty k testovacím souborům ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAIR_DIR = os.path.join(BASE_DIR, '../test_strings/openair')
PLAIN_TEXT_DIR = os.path.join(BASE_DIR, '../test_strings/plain_text')

def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def load_all_files_from_directory(directory):
    file_contents = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            file_contents.append((filename, load_file(file_path)))
    return file_contents

# Vytvoříme fixture, která pro každý testový soubor vrátí dvojici airspace_from_file a airspace_from_output
@pytest.fixture(params=[
    (OPENAIR_DIR, file_tuple) for file_tuple in load_all_files_from_directory(OPENAIR_DIR)
] + [
    (PLAIN_TEXT_DIR, file_tuple) for file_tuple in load_all_files_from_directory(PLAIN_TEXT_DIR)
])
def airspace_pair(request):
    directory, (filename, content) = request.param
    # Načtení airspace ze souboru
    extractor = ExtractorOpenAir(content) if directory == OPENAIR_DIR else Extractor(content)
    airspace_from_file = extractor.to_airspace()
    # Převod na OpenAir formát a opětovné načtení jako Airspace
    formatter = AirspaceFormatter(airspace_from_file)
    openair_output = formatter.to_openair()
    extractor_output = ExtractorOpenAir(openair_output)
    airspace_from_output = extractor_output.to_airspace()
    return airspace_from_file, airspace_from_output, filename

# Nyní upravíme testy, aby používaly jediný fixture, který nám dodá potřebné hodnoty.
def test_name(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    assert airspace_from_file.name == airspace_from_output.name, (
        f"Chyba v 'name' ({filename}): {airspace_from_file.name} != {airspace_from_output.name}"
    )

def test_airspace_class(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    assert airspace_from_file.airspace_class == airspace_from_output.airspace_class, (
        f"Chyba v 'airspace_class' ({filename}): {airspace_from_file.airspace_class} != {airspace_from_output.airspace_class}"
    )

def test_category(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    assert airspace_from_file.category == airspace_from_output.category, (
        f"Chyba v 'category' ({filename}): {airspace_from_file.category} != {airspace_from_output.category}"
    )

def test_frequencies(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    assert airspace_from_file.frequencies == airspace_from_output.frequencies, (
        f"Chyba v 'frequencies' ({filename}): {airspace_from_file.frequencies} != {airspace_from_output.frequencies}"
    )

def test_upper_limit(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    assert airspace_from_file.upper_limit == airspace_from_output.upper_limit, (
        f"Chyba v 'upper_limit' ({filename}): {airspace_from_file.upper_limit} != {airspace_from_output.upper_limit}"
    )

def test_lower_limit(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    assert airspace_from_file.lower_limit == airspace_from_output.lower_limit, (
        f"Chyba v 'lower_limit' ({filename}): {airspace_from_file.lower_limit} != {airspace_from_output.lower_limit}"
    )

def test_draw_commands(airspace_pair):
    airspace_from_file, airspace_from_output, filename = airspace_pair
    tolerance = 20  # tolerance v metrech pro porovnání koordinátů
    cmds_file = airspace_from_file.draw_commands
    cmds_output = airspace_from_output.draw_commands

    # Ověření, že oba seznamy mají stejnou délku
    assert len(cmds_file) == len(cmds_output), (
        f"Počet draw_commands se liší u {filename}: {len(cmds_file)} != {len(cmds_output)}"
    )

    import math
    for idx, (cmd1, cmd2) in enumerate(zip(cmds_file, cmds_output)):
        # Porovnání typu příkazu
        assert cmd1.get("type") == cmd2.get("type"), (
            f"Chyba v typu draw command u příkazu {idx} ({filename}): "
            f"{cmd1.get('type')} != {cmd2.get('type')}"
        )
        # Pro všechny klíče z obou příkazů
        for key in set(cmd1.keys()).union(set(cmd2.keys())):
            val1 = cmd1.get(key)
            val2 = cmd2.get(key)
            if "coordinate" in key and val1 is not None and val2 is not None:
                # Porovnáme koordináty s tolerancí
                is_within_tolerance, distance = Evaluator.compare_coordinates(val1, val2, tolerance=tolerance)
                assert is_within_tolerance, (
                    f"Chyba v {key} u příkazu {idx} ({filename}): {val1} != {val2}, "
                    f"vzdálenost = {distance:.3f} m (tolerance {tolerance} m)"
                )
            else:
                # Pokud je to možné, pokusíme se obě hodnoty převést na float a porovnat číselně
                try:
                    f_val1 = float(val1)
                    f_val2 = float(val2)
                    assert math.isclose(f_val1, f_val2, rel_tol=1e-6), (
                        f"Chyba v {key} u příkazu {idx} ({filename}): {val1} != {val2}"
                    )
                except (ValueError, TypeError):
                    # Pokud převod selže, porovnáme hodnoty přímo
                    assert val1 == val2, (
                        f"Chyba v {key} u příkazu {idx} ({filename}): {val1} != {val2}"
                    )
