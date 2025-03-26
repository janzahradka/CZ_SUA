import os
import re


# Konstanty

PROJECT_URL_ALIAS = "CZ_SUA/"
BASE_URL = "https://janzahradka.github.io/%s" % PROJECT_URL_ALIAS  # Základní URL pro GitHub Pages
CONTENT_ROOT = "public/"  # Kořen obsahu

def extract_last_changes(content_root_directory):
    """
    Extrahuje poslední změny z README.md
    """
    readme_path = os.path.join(content_root_directory, "readme.md")

    if not os.path.exists(readme_path):
        return ""

    with open(readme_path, "r", encoding="utf-8") as f:
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
        match = re.match(r"(\d{2}[A-Z]{3}\d{2})", line)
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

    changes_html = "<h2>Poslední změny</h2><ul>"
    for change in changes:
        changes_html += f"<li>{change.strip()}</li>"
    changes_html += "</ul>"

    return changes_html


def generate_special_table(directory, files):
    """
    Generuje speciální tabulku pro CZ_low, CZ_low_plus_CE a CZ_all soubory.
    """
    descriptions = [
        "Airspace below FL95, mostly recommended for gliding in Czechia.",
        "Contains the same as above plus closest abroad airspace. ",
        "All CZ airspace including above FL95. Recommended for databases."
    ]

    table_content = """
    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Note</th>
                <th>Download .txt</th>
                <th>Download .cub</th>
                <th>Preview</th>
            </tr>
        </thead>
        <tbody>
    """

    for file, description in zip(files, descriptions):
        file_name, _ = os.path.splitext(file)

        # .cub tlačítko
        cub_button = (
            f'<a href="{file_name}.cub">💾 Download</a>'
            if os.path.exists(os.path.join(directory, f"{file_name}.cub"))
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
            <td>{file}</td>
            <td><a href="{file}">💾 Download</a></td>
            <td>{cub_button}</td>
            <td>{html_preview_button}</td>
            <td>{description}</td>
        </tr>
        """

    table_content += "</tbody></table>"

    return table_content


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

    </style>
</head>
<body>
    <h1>Airspace files for gliding in Czechia</h1>
    <div class="breadcrumb">
        {breadcrumb}
    </div>
    """
    # Změny z README.md
    changes_html = extract_last_changes(content_root_directory)
    if changes_html:
        html_content += changes_html

    # Detekce speciálních souborů
    cz_low_file = next((f for f in files if re.match(r"CZ_low_\d{2}-\d{2}-\d{2}(.)*\.txt", f)), None)
    cz_low_plus_file = next((f for f in files if re.match(r"CZ_low_plus_CE_\d{2}-\d{2}-\d{2}(.)*\.txt", f)), None)
    cz_all_file = next((f for f in files if re.match(r"CZ_all_\d{2}-\d{2}-\d{2}(.)*\.txt", f)), None)

    if cz_low_file and cz_low_plus_file and cz_all_file:
        html_content += generate_special_table(directory, [cz_low_file, cz_low_plus_file, cz_all_file])
    else:
        html_content += f"""
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


    # Uzavření HTML obsahu
    html_content += """
        </tbody>
    </table>
"""
    html_content += """
            <hr>
            <footer>
                <p>
                    This content was created on behalf of <a href="https://www.aeroklub.cz/" target="_blank">Aeroklub České Republiky</a>, it is free to use.<br>
                    It's optimised for Gliding and provides info for avoiding unintentional incidents.<br>
                    The usage of this content is free of charge.<br>
                    Freely share this for any kind of general aviation purposes including commercial devices such as planning tools, IGC loggers, navigation devices, etc.<br>
                    Updates are released on a regular basis on page <a href="https://www.aeroklub.cz/vzdusny-prostor/" target="_blank">www.aeroklub.cz/vzdusny-prostor/</a>.
                </p>
                <p>
                    (c) 2025 Jan Zahradka
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