import os
import re
from datetime import datetime



# Konstanty

PROJECT_URL_ALIAS = "CZ_SUA/"
BASE_URL = "https://janzahradka.github.io/%s" % PROJECT_URL_ALIAS  # Základní URL pro GitHub Pages
CONTENT_ROOT = "public/"  # Kořen obsahu


def extract_date_from_name(name: str) -> datetime:
    """
    Z názvu souboru extrahuje datum ve formátu yy-mm-dd a vrátí objekt datetime.date.

    :param name: Název souboru
    :return: Nalezené datum jako objekt datetime.date nebo None, pokud nenalezeno
    """
    # Regulární výraz pro formát yy-mm-dd
    match = re.search(r"\b(\d{2}-\d{2}-\d{2})\b", name)

    if match:
        date_str = match.group(1)  # Extrahovaný textový řetězec s datem
        # Převod na datetime objekt (předpoklad: yy-mm-dd)
        return datetime.strptime(date_str, "%y-%m-%d").date()

    return None  # Pokud není datum nalezeno, vrátíme None


def extract_last_changes(content_root_directory, relative_path_from_content_root=""):
    """
    Extrahuje poslední změny z README.md
    """
    readme_path = os.path.join(content_root_directory, relative_path_from_content_root, "ReadMe.md")

    if not os.path.exists(readme_path):
        return ""

    # Pokus o robustní otevření souboru, detekce kódování
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # Revidujeme kódování a ignorujeme chyby
        with open(readme_path, "r", encoding="latin-1", errors="replace") as f:
            lines = f.readlines()

    changes_start = None
    for i, line in enumerate(lines):
        if "Changes History" in line:
            changes_start = i + 1
            break

    if changes_start is None:
        return ""

    # Najdi poslední záznam změn
    changes = []
    last_date = None

    for line in lines[changes_start:]:
        match = re.search(r"(\d{2}[A-Z]{3}\d{2})", line)
        if match:
            date = match.group(1)
            if last_date is None:
                last_date = date
            if date == last_date:
                changes.append(line)
            else:
                break

    if not changes:
        return ""

    changes_html = "<ul>"
    for change in changes:
        change = change.replace("* ", "")
        changes_html += f"<li>{change.strip()}</li>"
    changes_html += "</ul>"

    return changes_html



def generate_special_table(directory, files, descriptions):
    """
    Generuje speciální tabulku pro soubory (např. CZ_low, CZ_low_plus_CE, CZ_all).
    """
    table_content = """
    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Preview</th>
                <th>Description</th>
                <th>TXT</th>
                <th>CUB</th>
            </tr>
        </thead>
        <tbody>
    """

    for file, description in zip(files, descriptions):
        file_name, _ = os.path.splitext(file)

        # .cub tlačítko
        cub_button = (
            f'<a href="{file_name}.cub" download>💾 Download</a>'
            if os.path.exists(os.path.join(directory, f"{file_name}.cub"))
            else "N/A"
        )

        txt_view_button = (
            f'<a href="{file_name}.txt" target="_blank">📄 Open</a>'
            if os.path.exists(os.path.join(directory, f"{file_name}.txt"))
            else "N/A"
        )

        txt_download_button = (
            f'<a href="{file_name}.txt" download>💾 Download</a>'
            if os.path.exists(os.path.join(directory, f"{file_name}.txt"))
            else "N/A"
        )

        # Náhled tlačítko
        html_preview_button = (
            f'<a href="html/{file_name}.html" target="_blank">🗺️ Preview</a>'
            if os.path.exists(os.path.join(directory, "html", f"{file_name}.html"))
            else "N/A"
        )

        # Řádek tabulky
        table_content += f"""
        <tr>
            <td><strong>{file_name}</strong></td>
            <td>{html_preview_button}</td>
            <td>{description}</td>
            <td>{txt_view_button} {txt_download_button}</td>
            <td>{cub_button}</td>
        </tr>
        """

    table_content += "</tbody></table>"

    return table_content

def generate_directory_and_file_table(directories, files, directory, parent_url):
    """
    Generuje HTML tabulku pro výpis adresářů a souborů s odpovídajícími odkazy a akcemi.

    :param directories: Seznam adresářů
    :param files: Seznam souborů
    :param directory: Cesta k aktuálnímu adresáři
    :param parent_url: Relativní URL aktuálního adresáře
    :return: HTML obsah tabulky
    """
    html_content = """
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th class="actions">Action</th>
            </tr>
        </thead>
        <tbody>
    """
    # Odkazy na podsložky (adresáře)
    for folder in directories:
        folder_url = f"{parent_url}{folder}/"
        html_content += f"""
        <tr>
            <td><a href="{folder_url}">📁 {folder}</a></td>
            <td class="actions"></td>
        </tr>
        """

    # Odkazy na soubory
    for file in files:
        file_url = f"{parent_url}{file}"
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext.lower()
        actions = ""

        if file_ext in [".html", ".htm", ".md"]:
            actions += f'''
                <button onclick="window.open('{file_url}','_blank')"
                    title="Open">🌍️ Open</button>
                '''
        elif file_ext in [".txt", ".cub"]:
            # Ikona náhledu (pokud existuje) a ikona uložení
            html_preview_path = os.path.join(directory, "html", f"{file_name}.html")
            html_preview_url = f"{parent_url}html/{file_name}.html"
            if os.path.exists(html_preview_path):
                actions += f'''
                    <button onclick="window.open('{html_preview_url}', '_blank')"
                        title="Map Preview">🗺️ Preview</button>
                    '''
            actions += f'''
                    <button onclick="window.location.href='{file_url}'" title="Download">💾 Download</button>
                    '''

        if file_ext in [".txt", ".html", ".htm", ".md"]:
            file_tag = f'<a href="{file_url}" target="_blank" title="Otevřít">📄 {file}</a>'
        else:
            file_tag = f'📄 {file}'

        html_content += f"""
        <tr>
            <td>{file_tag}</td>
            <td class="actions">{actions}</td>
        </tr>
        """

    # Uzavření tabulky
    html_content += """
        </tbody>
    </table>
    """
    return html_content


def filter_files_for_special_table(files, special_files_patterns):
    """
    Odstraní z pole `files` všechny soubory odpovídající zadaným vzorcům, včetně jejich variant
    (.txt, .cub, .html).

    :param files: Seznam všech souborů v aktuálním adresáři
    :param special_files_patterns: Seznam regulárních výrazů pro identifikaci zvláštních souborů
                                   (např. CZ_low, CZ_low_plus_CE, CZ_all)
    :return: Filtrovaný seznam souborů
    """
    # Identifikace všech odpovídajících souborů
    special_files = set()

    for pattern in special_files_patterns:
        for file in files:
            if re.match(pattern, file):
                base_name, _ = os.path.splitext(file)
                # Přidej všechny možnosti (.txt, .cub, .html) do seznamu odstraněných souborů
                special_files.update([f"{base_name}.txt", f"{base_name}.cub", f"{base_name}.html"])

    # Vytvoření filtrovaného seznamu bez vyhrazených souborů
    filtered_files = [file for file in files if file not in special_files]

    return filtered_files



def generate_index(directory, content_root_directory, relative_path_from_content_root=""):
    """
    Rekurzivně generuje index.html v zadaném adresáři s odkazy na soubory/složky a odpovídajícími akcemi.
    """
    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        # Rozdělení na adresáře a soubory
        if os.path.isdir(full_path):
            directories.append(entry)  # Adresáře jdou sem
        elif entry != "index.html":  # Ignorovat existující index.html
            files.append(entry)  # Soubory jdou sem

    # Filtrování adresáře "html", pokud jsme v kořenovém adresáři
    if relative_path_from_content_root == "":
        directories = [d for d in directories if d != "html"]

    # Řazení adresářů sestupně (nejnovější nahoře)
    directories = sorted(directories, reverse=True)

    # Řazení souborů:
    # 1. Nejdříve podle přípony (sestupně)
    # 2. Poté abecedně uvnitř stejné přípony (sestupně)
    files = sorted(files, key=lambda x: (os.path.splitext(x)[1].lower(), x.lower()), reverse=True)

    # Vypočítání relativní cesty od content_root_directory
    relative_url_from_content_root = os.path.relpath(directory, content_root_directory).replace(os.sep, "/")
    if relative_url_from_content_root == ".":
        relative_url_from_content_root = ""  # Pro kořenový adresář nastavíme prázdnou relativní část

    # Sestavení parent_url
    parent_url = f"{BASE_URL}{CONTENT_ROOT}{relative_url_from_content_root}"
    if not parent_url.endswith("/"):
        parent_url += "/"

    # Sestavení breadcrumb navigace
    breadcrumb = f'<a href="{BASE_URL}{CONTENT_ROOT}">🏠 Home</a>'  # Domů vždy začíná BASE_URL + /public/
    if relative_url_from_content_root:
        parts = relative_url_from_content_root.split("/")
        cumulative_url = f"{BASE_URL}{CONTENT_ROOT}"
        for part in parts:
            cumulative_url += f"{part}/"
            breadcrumb += f' > <a href="{cumulative_url}">{part}</a>'

    # Vytvoření začátku HTML souboru
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{relative_path_from_content_root or PROJECT_URL_ALIAS}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:hover {{ background-color: #f1f1f1; }}
        td.actions {{ text-align: left; }}
        a {{ color: #4CAF50; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .breadcrumb {{ margin-bottom: 20px; }}
        @media (max-width: 600px) {{
            table {{ font-size: 14px; }}
            th, td {{ padding: 8px; }}
        }}
                
         button {{
            border: none;
            color: white;
            padding: 10px 15px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 5px 2px;
            cursor: pointer;
            border-radius: 5px;
            background-color: #008CBA;
        }}
        
        button:hover {{
            box-shadow: 0px 4px 8px 0px rgba(0, 0, 0, 0.2);
        }}
    footer {{
        font-size: 10px; /* Menší písmo */
        text-align: center; /* Zarovnání na střed */
        margin-top: 20px; /* Volitelně: odstup od obsahu */
        color: #666; /* Mírně šedý text */
    }}

    </style>
</head>
<body>
    <h1>Airspace files for gliding in Czechia</h1>
    <div class="breadcrumb">
        {breadcrumb}
    </div>
    """
    # Změny z README.md
    changes_html = extract_last_changes(content_root_directory, relative_path_from_content_root=relative_path_from_content_root)
    if changes_html:
        html_content += "<h3>Last updates</h3>"
        html_content += changes_html

    # Detekce speciálních souborů
    special_files = []
    descriptions = []
    special_file_patterns = [
        r"CZ_low_\d{2}-\d{2}-\d{2}.*\.txt",
        r"CZ_low_plus_CE_\d{2}-\d{2}-\d{2}.*\.txt",
        r"CZ_all_\d{2}-\d{2}-\d{2}.*\.txt"
    ]

    # Přidávání nalezených souborů a odpovídajících popisů
    cz_low_file = next((f for f in files if re.match(special_file_patterns[0], f)), None)
    if cz_low_file:
        special_files.append(cz_low_file)
        descriptions.append("Airspace below FL95, mostly <b>recommended for gliding in Czechia</b>.")

    cz_low_plus_file = next((f for f in files if re.match(special_file_patterns[1], f)), None)
    if cz_low_plus_file:
        special_files.append(cz_low_plus_file)
        descriptions.append(
            "Contains the same as above plus the closest abroad airspace. <b>Recommended as a basefile for competitions</b>.")

    cz_all_file = next((f for f in files if re.match(special_file_patterns[2], f)), None)
    if cz_all_file:
        special_files.append(cz_all_file)
        descriptions.append("All CZ airspace including above FL95. <b>Recommended for databases</b>.")

    # Filtrování souborů - odstranění speciálních souborů a jejich variant
    files = filter_files_for_special_table(files, special_file_patterns)

    # pouze pro kořenový adresář
    if relative_path_from_content_root == "":
        if special_files:
            html_content += "<h2>Actual files</h2>"
            html_content += generate_special_table(directory, special_files, descriptions)
            html_content += generate_directory_and_file_table(directories, files, directory, parent_url)
        else:
            html_content += "<h2>Other contents</h2>"
            html_content += generate_directory_and_file_table(directories, files, directory, parent_url)
    # jiný než kořenový adresář
    else:
        # Pokud existuje alespoň jeden speciální soubor, vygeneruj speciální tabulku
        if special_files:
            html_content += generate_special_table(directory, special_files, descriptions)
        else:
            html_content += generate_directory_and_file_table(directories, files, directory, parent_url)

    html_content += """
            <hr>
            <footer>
                <p>
                    This content was created on behalf of <a href="https://www.aeroklub.cz/" target="_blank">Aeroklub České Republiky</a> and is free to use.<br>
                    It is optimized for Gliding and provides information to help avoid unintentional incidents.<br>
                    The use of this content is completely free of charge.<br>
                    Feel free to share it for any type of general aviation purposes, including commercial devices such as planning tools, IGC loggers, navigation devices, etc.<br>
                    Updates are regularly released on the page <a href="https://www.aeroklub.cz/vzdusny-prostor/" target="_blank">www.aeroklub.cz/vzdusny-prostor/</a>.
                </p>
                <p>
                    &copy; 2025 Jan Zahradka
                </p>
            </footer>
        """
    html_content += """
</body>
</html>
"""

    # Uložení do souboru index.html
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Vygenerován soubor: {index_path}")

    # Rekurzivně zpracovat podsložky
    for folder in directories:
        generate_index(
            os.path.join(directory, folder), content_root_directory,
            os.path.join(relative_path_from_content_root, folder)
        )


if __name__ == "__main__":
    # Nastavení cest
    script_directory = os.path.dirname(os.path.abspath(__file__))  # Adresář, kde je skript
    root_directory = os.path.join(script_directory, "docs")  # Absolutní cesta ke kořeni "docs"
    content_root_directory = os.path.join(root_directory, "public")  # Absolutní cesta k "public"

    # Kontrola existence adresáře "public"
    if not os.path.exists(content_root_directory):
        print(f"Chyba: Složka {content_root_directory} neexistuje. Zkontrolujte strukturu.")
    else:
        # Spuštění generování
        generate_index(content_root_directory, content_root_directory)
        print("Hotovo! Všechny index.html soubory byly vygenerovány.")