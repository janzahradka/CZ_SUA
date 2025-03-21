import os


def generate_index(directory, root_directory, relative_path=""):
    """
    Rekurzivně generuje index.html ve všech složkách s podporou konzistentních relativních odkazů
    """
    # Získání všech vstupů v adresáři
    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        elif entry != "index.html":  # Vyloučit již existující `index.html`
            files.append(entry)

    # Určení parent_url podle relativní cesty od root_directory
    parent_url = "/" + relative_path.replace(os.sep, "/")  # Převést na URL-cestu
    if not parent_url.endswith("/"):
        parent_url += "/"

    # Navigace (breadcrumb)
    breadcrumb = '<a href="/">🏠 Domů</a>'
    path_parts = relative_path.split(os.sep) if relative_path else []
    cumulative_path = ""
    for part in path_parts:
        if part:
            cumulative_path = os.path.join(cumulative_path, part)
            cumulative_url = "/" + cumulative_path.replace(os.sep, "/")
            breadcrumb += f' > <a href="{cumulative_url}/">{part}</a>'

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
        .icon {{ margin-right: 8px; }}
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

    # Generování složek
    for folder in sorted(directories):
        folder_url = parent_url + folder + "/"
        html_content += f"""
        <tr>
            <td><a href="{folder_url}">📁 {folder}</a></td>
            <td></td>
        </tr>
        """

    # Generování souborů
    for file in sorted(files):
        file_url = parent_url + file  # Soubor URL
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext.lower()

        # Ikony a akce podle typu souboru
        if file_ext in [".html", ".htm", ".md"]:
            # Otevření v okně prohlížeče
            action = f"""
                <a href="{file_url}" target="_blank" title="Open in browser">🌐</a>
            """
        elif file_ext in [".txt", ".cub"]:
            # Náhled a stažení souboru
            preview_file_url = parent_url + "html/" + file_name + ".html"  # Náhled
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
            action = ""  # Pro ostatní typy souborů nejsou specifické akce

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

    # Uložení index.html do dané složky
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Vygenerován soubor: {index_path}")

    # Rekurzivní generování pro podadresáře
    for folder in directories:
        generate_index(os.path.join(directory, folder), root_directory, os.path.join(relative_path, folder))


# Spuštění generování pro root directory
if __name__ == "__main__":
    root_directory = "docs/public"
    if not os.path.exists(root_directory):
        print(f"Chyba: Složka {root_directory} neexistuje. Zkontrolujte cestu.")
    else:
        generate_index(root_directory, root_directory)
        print("Generování dokončeno.")