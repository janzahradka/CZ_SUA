import os
import glob
import pytest
import math
from AirspaceManager.extractor.extractor_openair import ExtractorOpenAir
from AirspaceManager.airspace_formatter import AirspaceFormatter
from AirspaceManager.evaluator import Evaluator


def load_all_airspace_blocks():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Path to the directory containing txt files
    dir_path = os.path.join(BASE_DIR, '../test_strings/roundtrip_test')
    txt_files = glob.glob(os.path.join(dir_path, '*.txt'))
    all_valid_blocks = []
    for file_path in txt_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Split the file into lines and remove comments (take only text before the first "*")
        all_lines = content.splitlines()
        preproc_lines = [line.split('*')[0].strip() for line in all_lines]

        # Create blocks – blocks are separated by two (or more) empty lines.
        blocks = []
        current_block = []
        empty_count = 0
        for l in preproc_lines:
            if l == "":
                empty_count += 1
            else:
                if empty_count >= 2 and current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                empty_count = 0
                current_block.append(l)
        if current_block:
            blocks.append("\n".join(current_block))

        # Filter: only blocks that start with "AC" and do not contain lines starting with "SP " or "SB "
        for idx, block in enumerate(blocks):
            lines_block = block.splitlines()
            if lines_block and lines_block[0].startswith("AC") and not any(
                    line.startswith("SP ") or line.startswith("SB ") for line in lines_block):
                # Attempt to extract the airspace name from the "AN " tag
                name = None
                for line in lines_block:
                    if line.startswith("AN "):
                        name = line.split("AN ", 1)[1].strip()
                        break
                if not name:
                    name = "Bez názvu"
                file_name = os.path.basename(file_path)
                param_id = f"{file_name} - {name}"
                all_valid_blocks.append(pytest.param((file_name, idx, block), id=param_id))
    return all_valid_blocks


@pytest.fixture(params=load_all_airspace_blocks())
def airspace_data(request):
    """
    Fixture returns a dictionary with:
      - file_name: name of the file,
      - index: index of the block within the file,
      - block: original text of the block,
      - from_file: Airspace object parsed from the original text,
      - from_output: Airspace object obtained from the round-trip conversion.
    """
    file_name, idx, block = request.param
    extractor = ExtractorOpenAir(block)
    airspace_from_file = extractor.to_airspace()
    formatter = AirspaceFormatter(airspace_from_file)
    openair_output = formatter.to_openair()
    extractor_output = ExtractorOpenAir(openair_output)
    airspace_from_output = extractor_output.to_airspace()
    return {
        "file_name": file_name,
        "index": idx,
        "block": block,
        "from_file": airspace_from_file,
        "from_output": airspace_from_output
    }


def test_name(airspace_data):
    idx = airspace_data["index"]
    file_name = airspace_data["file_name"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    name_info = af.name or "Nedefinován"
    assert af.name == ao.name, f"{file_name} - Blok {idx} ({name_info}): name mismatch: {af.name} vs {ao.name}"


def test_airspace_class(airspace_data):
    idx = airspace_data["index"]
    file_name = airspace_data["file_name"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    name_info = af.name or "Nedefinován"
    assert af.airspace_class == ao.airspace_class, f"{file_name} - Blok {idx} ({name_info}): airspace_class mismatch: {af.airspace_class} vs {ao.airspace_class}"


def test_category(airspace_data):
    idx = airspace_data["index"]
    file_name = airspace_data["file_name"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    name_info = af.name or "Nedefinován"
    assert af.category == ao.category, f"{file_name} - Blok {idx} ({name_info}): category mismatch: {af.category} vs {ao.category}"


def test_frequencies(airspace_data):
    idx = airspace_data["index"]
    file_name = airspace_data["file_name"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    name_info = af.name or "Nedefinován"
    assert af.frequencies == ao.frequencies, f"{file_name} - Blok {idx} ({name_info}): frequencies mismatch: {af.frequencies} vs {ao.frequencies}"


def test_upper_limit(airspace_data):
    idx = airspace_data["index"]
    file_name = airspace_data["file_name"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    name_info = af.name or "Nedefinován"
    assert af.upper_limit == ao.upper_limit, f"{file_name} - Blok {idx} ({name_info}): upper_limit mismatch: {af.upper_limit} vs {ao.upper_limit}"


def test_lower_limit(airspace_data):
    idx = airspace_data["index"]
    file_name = airspace_data["file_name"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    name_info = af.name or "Nedefinován"
    assert af.lower_limit == ao.lower_limit, f"{file_name} - Blok {idx} ({name_info}): lower_limit mismatch: {af.lower_limit} vs {ao.lower_limit}"


def test_draw_commands(airspace_data):
    file_name = airspace_data["file_name"]
    idx = airspace_data["index"]
    af = airspace_data["from_file"]
    ao = airspace_data["from_output"]
    tolerance = 20  # tolerance v metrech pro porovnání souřadnic
    cmds_file = af.draw_commands
    cmds_output = ao.draw_commands

    # Ověření, že oba seznamy mají stejnou délku
    assert len(cmds_file) == len(cmds_output), (
        f"{file_name} - Blok {idx}: Počet draw_commands se liší: {len(cmds_file)} != {len(cmds_output)}"
    )

    for cmd_idx, (cmd1, cmd2) in enumerate(zip(cmds_file, cmds_output)):
        # Porovnání typu příkazu
        assert cmd1.get("type") == cmd2.get("type"), (
            f"{file_name} - Blok {idx} ({af.name or 'Nedefinován'}): "
            f"Chyba v typu draw command u příkazu {cmd_idx}: {cmd1.get('type')} != {cmd2.get('type')}"
        )
        # Porovnání všech klíčů v příkazu
        for key in set(cmd1.keys()).union(set(cmd2.keys())):
            val1 = cmd1.get(key)
            val2 = cmd2.get(key)
            if "coordinate" in key and val1 is not None and val2 is not None:
                # Porovnání koordinátů s tolerancí
                is_within_tolerance, distance = Evaluator.compare_coordinates(val1, val2, tolerance=tolerance)
                assert is_within_tolerance, (
                    f"{file_name} - Blok {idx} ({af.name or 'Nedefinován'}): "
                    f"Chyba v {key} u příkazu {cmd_idx}: {val1} != {val2}, vzdálenost = {distance:.3f} m (tolerance {tolerance} m)"
                )
            else:
                try:
                    f_val1 = float(val1)
                    f_val2 = float(val2)
                    assert math.isclose(f_val1, f_val2, rel_tol=1e-6), (
                        f"{file_name} - Blok {idx} ({af.name or 'Nedefinován'}): "
                        f"Chyba v {key} u příkazu {cmd_idx}: {val1} != {val2}"
                    )
                except (ValueError, TypeError):
                    assert val1 == val2, (
                        f"{file_name} - Blok {idx} ({af.name or 'Nedefinován'}): "
                        f"Chyba v {key} u příkazu {cmd_idx}: {val1} != {val2}"
                    )
