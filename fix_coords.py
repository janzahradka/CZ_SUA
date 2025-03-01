import re
import sys
import os
import datetime

# Funkce pro úpravu nalezeného vzoru – zvýší číslo o 1 a nahradí "60" za "00"
def fix_coordinate(match):
    # match.group(1): předcházející číslo (minuty nebo sekundy)
    # match.group(2): oddělovač (např. ":" nebo " ")
    # match.group(3): případný další oddělovač nebo konec řetězce
    preceding = int(match.group(1))
    sep = match.group(2)
    following = match.group(3) if match.group(3) is not None else ""
    new_preceding = preceding + 1
    new_preceding_str = f"{new_preceding:02d}"
    return f"{new_preceding_str}{sep}00{following}"

# Funkce, která zpracuje jeden řádek
def process_line(line):
    # Tento regulární výraz hledá 1-2 číslice, oddělovač (":" nebo mezera), poté přesně "60"
    # a nakonec buď další oddělovač nebo konec řetězce.
    pattern = re.compile(r'(\d{1,2})([:\s])60((?:[:\s]|$))')
    return pattern.sub(fix_coordinate, line)

# Funkce pro zpracování jednoho souboru; vrací logovací zprávy jako seznam řádků
def process_file(filepath, log_lines):
    try:
        with open(filepath, encoding="utf-8") as f:
            original_lines = f.readlines()
    except Exception as e:
        log_lines.append(f"[{datetime.datetime.now()}] ERROR: Cannot read file {filepath}: {e}\n")
        return

    # Získáme původní údaje
    original_text = "".join(original_lines)
    original_size = len(original_text.encode("utf-8"))
    original_line_count = len(original_lines)

    new_lines = []
    file_line_log = []  # Log změn v tomto souboru
    for idx, line in enumerate(original_lines, start=1):
        new_line = process_line(line)
        if new_line != line:
            file_line_log.append(f"Line {idx}: {line.rstrip()} -> {new_line.rstrip()}")
        new_lines.append(new_line)

    new_text = "".join(new_lines)
    new_size = len(new_text.encode("utf-8"))
    new_line_count = len(new_lines)

    size_diff = new_size - original_size
    line_diff = new_line_count - original_line_count

    log_lines.append(f"[{datetime.datetime.now()}] Processed file: {filepath}\n")
    log_lines.append(f"  Original size: {original_size} bytes, {original_line_count} lines\n")
    log_lines.append(f"  New size:      {new_size} bytes, {new_line_count} lines\n")
    log_lines.append(f"  Difference:    {size_diff:+} bytes, {line_diff:+} lines\n")
    if file_line_log:
        log_lines.append("  Changes:\n")
        for change in file_line_log:
            log_lines.append(f"    {change}\n")
    else:
        log_lines.append("  No changes in this file.\n")
    log_lines.append("\n")

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        log_lines.append(f"[{datetime.datetime.now()}] ERROR: Cannot write file {filepath}: {e}\n")

# Funkce, která rekurzivně projde adresář a zpracuje pouze soubory s příponou .txt
def process_directory(directory, log_lines):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".txt"):
                filepath = os.path.join(root, file)
                process_file(filepath, log_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_coords.py <directory>")
        sys.exit(1)
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Directory {directory} does not exist.")
        sys.exit(1)

    log_lines = []
    log_lines.append(f"--- Processing started at {datetime.datetime.now()} ---\n\n")
    process_directory(directory, log_lines)
    log_lines.append(f"--- Processing finished at {datetime.datetime.now()} ---\n")

    log_filepath = "fix_coords.log"
    try:
        with open(log_filepath, "w", encoding="utf-8") as log_file:
            log_file.writelines(log_lines)
        print(f"Processing finished. Log saved to {log_filepath}")
    except Exception as e:
        print(f"ERROR: Cannot write log file {log_filepath}: {e}")

if __name__ == '__main__':
    main()
