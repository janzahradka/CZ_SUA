import os

# Konstanty
BASE_URL = "https://janzahradka.github.io/CZ_SUA/"  # Základní URL pro GitHub Pages
CONTENT_ROOT = "public/"  # Kořen obsahu


def generate_index(directory, content_root_directory, relative_path_from_content_root=""):
    """
    Rekurzivně generuje index.html s odkazy odpovídajícími formátu GitHub Pages.
    """
    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        elif entry != "index.html":  # Ignorovat případný existující index.html
            files.append(entry)

    # Vypočítání relativní cesty od content_root_directory
    relative_url_from_content_root = os.path.relpath(directory, content_root_directory).replace(os.sep, "/")
    if relative_url_from_content_root == ".":
        relative_url_from_content_root = ""  # Kořen public/ má prázdnou relativní část

    # Sestavení parent_url
    parent_url = f"{BASE_URL}{CONTENT_ROOT}{relative_url_from_content_root}"
    if not parent_url.endswith("/"):
        parent_url += "/"

    # Sestavení breadcrumb navigace
    breadcrumb = f'<a href="{BASE_URL}">🏠 Domů</a>'
    if relative_url_from_content_root:
        parts = relative_url_from_content_root.split("/")
        cumulative_url = f"{BASE_URL}{CONTENT_ROOT}"
        for part in parts:
            cumulative_url += f"{part}/"
            breadcrumb += f' > <a href="{cumulative_url}">{part}</a>'

    # Vytvoření HTML souboru
    html_content = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obsah adresáře: {relative_path_from_content_root or 'Kořenový adresář'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:hover {{ background-color: #f1f1f1; }}
        a {{ color: #4CAF50; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .breadcrumb {{ margin-bottom: 20px; }}
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
                <th>Odkaz</th>
            </tr>
        </thead>
        <tbody>
    """

    # Odkazy na podsložky
    for folder in sorted(directories):
        folder_url = f"{parent_url}{folder}/"
        html_content += f"""
        <tr>
            <td><a href="{folder_url}">📁 {folder}</a></td>
            <td><a href="{folder_url}">Otevřít</a></td>
        </tr>
        """

    # Odkazy na soubory
    for file in sorted(files):
        file_url = f"{parent_url}{file}"
        html_content += f"""
        <tr>
            <td>📄 {file}</td>
            <td><a href="{file_url}" target="_blank" title="Otevřít v prohlížeči">🌐 Otevřít</a></td>
        </tr>
        """

    # Konec HTML obsahu
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