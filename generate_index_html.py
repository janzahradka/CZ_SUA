import os


def generate_index(directory, root_directory, content_root_directory, relative_path=""):
    """
    Funkce rekurzivně generuje index.html pro všechny složky.
    Skládá správné relativní odkazy vůči content_root_directory a root_directory.
    """

    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        elif entry != "index.html":
            files.append(entry)

    # Vypočítání relativní URL od `content_root_directory`
    relative_url_path = os.path.relpath(directory, content_root_directory).replace(os.sep, "/")
    if relative_url_path == ".":
        relative_url_path = ""  # Pro kořenovou cestu vyprázdníme relativní část

    # Sestavení parent URL od root_directory
    parent_url = "/" + relative_url_path
    if not parent_url.endswith("/"):
        parent_url += "/"

    # Sestavení breadcrumb navigace
    breadcrumb = '<a href="/">🏠 Domů</a>'
    path_parts = relative_url_path.split("/") if relative_url_path else []
    cumulative_url = "/"
    for part in path_parts:
        if part:
            cumulative_url += part + "/"
            breadcrumb += f' > <a href="{cumulative_url}">{part}</a>'

    # HTML hlavička
    html_content = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obsah adresáře: {relative_path or 'Kořenová složka'}</title>
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
                <th>Akce</th>
            </tr>
        </thead>
        <tbody>
    """

    # Odkazy na podsložky
    for folder in sorted(directories):
        folder_url = parent_url + folder + "/"
        html_content += f"""
        <tr>
            <td><a href="{folder_url}">📁 {folder}</a></td>
            <td></td>
        </tr>
        """

    # Odkazy na soubory
    for file in sorted(files):
        file_url = parent_url + file
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext.lower()

        # Akce podle druhu souboru
        if file_ext in [".html", ".htm", ".md"]:
            # Odkazy pro otevření v prohlížeči
            action = f"""
                <a href="{file_url}" target="_blank" title="Open in browser">🌐</a>
            """
        elif file_ext in [".txt", ".cub"]:
            # Náhled a stažení
            preview_file_url = parent_url + "html/" + file_name + ".html"
            preview_icon = ""
            if os.path.exists(os.path.join(directory, "html", f"{file_name}.html")):
                preview_icon = f"""
                <a href="{preview_file_url}" target="_blank" title="Open preview">🔍</a>
                """
            download_icon = f"""
                <a href="{file_url}" download title="Download">⬇️</a>
            """
            action = f"{preview_icon} {download_icon}"
        else:
            action = ""

        html_content += f"""
        <tr>
            <td>📄 {file}</td>
            <td>{action}</td>
        </tr>
        """

    # Zakončení HTML obsahu
    html_content += """
        </tbody>
    </table>
</body>
</html>
"""

    # Uložení souboru index.html
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Vygenerován soubor: {index_path}")

    # Rekurzivní volání pro podadresáře
    for folder in directories:
        generate_index(
            os.path.join(directory, folder), root_directory, content_root_directory, os.path.join(relative_path, folder)
        )


# Spuštění
if __name__ == "__main__":
    # Definování cest
    script_directory = os.path.dirname(os.path.abspath(__file__))  # Složka, kde je skript
    root_directory = os.path.join(script_directory, "docs")  # Cesta ke kořenové složce
    content_root_directory = os.path.join(root_directory, "public")  # Cesta k obsahu

    # Zkontrolování existence content_root_directory
    if not os.path.exists(content_root_directory):
        print(f"Chyba: Složka {content_root_directory} neexistuje. Zkontrolujte strukturu.")
    else:
        generate_index(content_root_directory, root_directory, content_root_directory)
        print("Generování dokončeno.")