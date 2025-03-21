import os


def generate_index(directory, root_directory, content_root_directory, relative_path=""):
    """
    Funkce rekurzivně generuje index.html v adresáři.
    Skládá relativní odkazy vůči content_root_directory a root_directory.
    """

    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        elif entry != "index.html":  # Index.html ignorujeme
            files.append(entry)

    # Relativní cesta vůči content_root_directory (viditelná část URL)
    relative_url_path = os.path.relpath(directory, content_root_directory).replace(os.sep, "/")
    if relative_url_path == ".":
        relative_url_path = ""  # Pro root je prázdná relativní cesta

    # Sestavení Parent URL (zahrnující content_root_directory)
    parent_url = "/" + os.path.relpath(content_root_directory, root_directory).replace(os.sep, "/")
    if relative_url_path:
        parent_url += "/" + relative_url_path
    if not parent_url.endswith("/"):
        parent_url += "/"

    # Sestavení Breadcrumb (navigační cesta)
    breadcrumb = '<a href="/">🏠 Domů</a>'
    path_parts = relative_url_path.split("/") if relative_url_path else []
    cumulative_url = parent_url
    for part in path_parts:
        if part:
            cumulative_url += part + "/"
            breadcrumb += f' > <a href="{cumulative_url}">{part}</a>'

    # Začátek HTML souboru
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

    # Vytvoření odkazů na složky
    for folder in sorted(directories):
        folder_url = parent_url + folder + "/"
        html_content += f"""
        <tr>
            <td><a href="{folder_url}">📁 {folder}</a></td>
            <td></td>
        </tr>
        """

    # Vytvoření odkazů na soubory
    for file in sorted(files):
        file_url = parent_url + file
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext.lower()

        # Výběr akce podle typu souboru
        if file_ext in [".html", ".htm", ".md"]:
            # Otevření v prohlížeči
            action = f"""
                <a href="{file_url}" target="_blank" title="Open in browser">🌐</a>
            """
        elif file_ext in [".txt", ".cub"]:
            # Náhled (pokud existuje) + stažení
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
            action = ""  # Pro ostatní soubory nemáme specifickou akci

        html_content += f"""
        <tr>
            <td>📄 {file}</td>
            <td>{action}</td>
        </tr>
        """

    # Uzavření HTML souboru
    html_content += """
        </tbody>
    </table>
</body>
</html>
"""

    # Uložení index.html v aktuální složce
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
    # Nastavení cest
    script_directory = os.path.dirname(os.path.abspath(__file__))  # Adresář skriptu
    root_directory = os.path.join(script_directory, "docs")  # Kořenová složka (web doc)
    content_root_directory = os.path.join(root_directory, "public")  # Obsah (public)

    # Kontrola existence složky
    if not os.path.exists(content_root_directory):
        print(f"Chyba: Složka {content_root_directory} neexistuje. Zkontrolujte strukturu.")
    else:
        generate_index(content_root_directory, root_directory, content_root_directory)
        print(f"Generování dokončeno.")