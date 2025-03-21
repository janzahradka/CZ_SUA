import os


def generate_index(directory, root_directory, relative_path=""):
    """
    Rekurzivně generuje index.html ve všech složkách s podporou breadcrumb navigace a správných akcí u souborů.
    """
    # Získání seznamu složek a souborů
    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        elif entry != "index.html":  # Vyloučí index.html ze seznamu
            files.append(entry)

    # Sestavení breadcrumb navigace (bez obsahu kořenového adresáře)
    breadcrumb = '<a href="/">🏠 Domů</a>'
    path_parts = relative_path.split(os.sep) if relative_path else []
    breadcrumb_path = ""
    for part in path_parts:
        if part:
            breadcrumb_path = os.path.join(breadcrumb_path, part)
            breadcrumb += f' > <a href="{breadcrumb_path}/">{part}</a>'

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
        folder_path = os.path.join(relative_path, folder)
        html_content += f"""
        <tr>
            <td><a href="{folder}/">📁 {folder}</a></td>
            <td></td>
        </tr>
        """

    # Generování souborů
    for file in sorted(files):
        file_relative_path = os.path.join(relative_path, file)
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext.lower()

        # Ikony a akce podle typu souboru
        if file_ext in [".html", ".htm", ".md"]:
            # Odkaz pro otevření v prohlížeči
            action = f"""
                <a href="{file_relative_path}" target="_blank" title="Open in browser">🌐</a>
            """
        elif file_ext in [".txt", ".cub"]:
            # Náhled a stažení
            preview_file = f"html/{file_name}.html"  # Cesta k náhledu
            preview_icon = ""
            if os.path.exists(os.path.join(directory, "html", f"{file_name}.html")):  # Náhled existuje
                preview_icon = f"""
                    <a href="{os.path.join(relative_path, preview_file)}" target="_blank" title="Open preview">🔍</a>
                """
            download_icon = f"""
                <a href="{file_relative_path}" download title="Download">⬇️</a>
            """
            action = f"{preview_icon} {download_icon}"
        else:
            # Žádné speciální akce pro ostatní typy souborů
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

    # Uložení jako index.html ve složce
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Vygenerován soubor: {index_path}")

    # Rekurzivně generovat pro podadresáře
    for folder in directories:
        generate_index(os.path.join(directory, folder), root_directory, os.path.join(relative_path, folder))


# Spuštění generování pro root /docs/public
if __name__ == "__main__":
    root_directory = "./docs/public"
    if not os.path.exists(root_directory):
        print(f"Složka {root_directory} neexistuje. Zkontrolujte cestu.")
    else:
        generate_index(root_directory, root_directory)
        print("Generování dokončeno.")