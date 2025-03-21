import os

# Konstanty
BASE_URL = "https://janzahradka.github.io/CZ_SUA/"  # Základní URL pro GitHub Pages
CONTENT_ROOT = "public/"  # Kořen obsahu


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

    # Řazení adresářů abecedně vzestupně
    directories = sorted(directories)

    # Řazení souborů:
    # 1. Nejprve podle přípony (od nejmenší do největší)
    # 2. Poté abecedně uvnitř stejné přípony
    files = sorted(files, key=lambda x: (os.path.splitext(x)[1].lower(), x.lower()))

    # Vypočítání relativní cesty od content_root_directory
    relative_url_from_content_root = os.path.relpath(directory, content_root_directory).replace(os.sep, "/")
    if relative_url_from_content_root == ".":
        relative_url_from_content_root = ""  # Pro kořenový adresář nastavíme prázdnou relativní část

    # Sestavení parent_url
    parent_url = f"{BASE_URL}{CONTENT_ROOT}{relative_url_from_content_root}"
    if not parent_url.endswith("/"):
        parent_url += "/"

    # Sestavení breadcrumb navigace
    breadcrumb = f'<a href="{BASE_URL}{CONTENT_ROOT}">🏠 Domů</a>'  # Domů vždy začíná BASE_URL + /public/
    if relative_url_from_content_root:
        parts = relative_url_from_content_root.split("/")
        cumulative_url = f"{BASE_URL}{CONTENT_ROOT}"
        for part in parts:
            cumulative_url += f"{part}/"
            breadcrumb += f' > <a href="{cumulative_url}">{part}</a>'

    # Vytvoření začátku HTML souboru
    html_content = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obsah adresáře: {relative_path_from_content_root or 'Kořenový adresář'}</title>
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
    </style>
</head>
<body>
    <div class="breadcrumb">
        {breadcrumb}
    </div>
    <h1>Obsah adresáře</h1>
    <table>
        <thead>
            <tr>
                <th>Název</th>
                <th class="actions">Akce</th>
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
            # Ikona pro prohlížeč nebo přímo dokument
            actions = f'<a href="{file_url}" target="_blank" title="Otevřít">🌍️</a>'
        elif file_ext in [".txt", ".cub"]:
            # Ikona náhledu (pokud existuje) a ikona uložení
            html_preview_path = os.path.join(directory, "html", f"{file_name}.html")
            html_preview_url = f"{parent_url}html/{file_name}.html"
            if os.path.exists(html_preview_path):
                actions += f'<a href="{html_preview_url}" target="_blank" title="Náhled obsahu">🗺️</a> '
            actions += f'<a href="{file_url}" download title="Uložit soubor">💾</a>'

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