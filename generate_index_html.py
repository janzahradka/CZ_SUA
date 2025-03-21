import os


def generate_index(directory, root_directory, relative_path=""):
    """
    Rekurzivně generuje index.html ve všech složkách, přičemž bere v úvahu nadřazené složky, breadcrumb navigaci a akce u souborů.
    """
    # Získej seznam složek a souborů
    entries = os.listdir(directory)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        else:
            files.append(entry)

    # Sestav cesty pro navigaci zpět (breadcrumb)
    breadcrumb = '<a href="/">🏠 Domů</a> '  # Ikona domečku
    path_parts = relative_path.split(os.sep) if relative_path else []
    breadcrumb_path = ""
    for part in path_parts:
        if part:  # pokud část existuje, sestav odkaz
            breadcrumb_path = os.path.join(breadcrumb_path, part)
            breadcrumb += f'> <a href="{breadcrumb_path}/">{part}</a> '

    # Začátek HTML dokumentu
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

    # Generování záznamů pro složky
    for folder in sorted(directories):
        folder_path = os.path.join(relative_path, folder)
        html_content += f"""
        <tr>
            <td><a href="{folder}/">📁 {folder}</a></td> <!-- Unicode symbol 📁 pro složku -->
            <td></td>
        </tr>
        """

    # Generování záznamů pro soubory
    for file in sorted(files):
        file_path = os.path.join(directory, file)
        file_name, file_ext = os.path.splitext(file)
        file_ext = file_ext.lower()
        file_relative_path = os.path.join(relative_path, file)

        # Ikony pro akce a typy souborů
        if file_ext in [".html", ".htm", ".md"]:
            action = f"""
            <a href="{file_relative_path}" target="_blank" title="Otevřít v prohlížeči">
                🌐
            </a>
            """
        elif file_ext in [".txt", ".cub"]:
            preview_link = ""
            if os.path.exists(os.path.join(directory, "html", f"{file_name}.html")):
                preview_link = f"""
                <a href="{relative_path}/html/{file_name}.html" target="_blank" title="Náhled">
                    🔍
                </a>
                """
            action = f"""
            {preview_link}
            <a href="{file_relative_path}" download title="Stáhnout">
                ⬇️
            </a>
            """
        else:
            action = ""  # Pro ostatní typy se ikona nezobrazuje

        html_content += f"""
        <tr>
            <td>📄 {file}</td> <!-- Unicode symbol 📄 pro obecný soubor -->
            <td>{action}</td>
        </tr>
        """

    # Uzavření HTML dokumentu
    html_content += """
        </tbody>
    </table>
</body>
</html>
"""

    # Uložení do index.html v aktuálním adresáři
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Vygenerován soubor: {index_path}")

    # Rekurzivně generuj index.html pro podadresáře
    for folder in directories:
        generate_index(os.path.join(directory, folder), root_directory, os.path.join(relative_path, folder))


# Spustit generování pro hlavní složku (např. ./docs/public)
if __name__ == "__main__":
    root_directory = "./docs/public"  # Nastav kořenový adresář
    if not os.path.exists(root_directory):
        print(f"Složka {root_directory} neexistuje. Ujisti se, že cesta je správná.")
    else:
        generate_index(root_directory, root_directory)
        print("Generování dokončeno.")