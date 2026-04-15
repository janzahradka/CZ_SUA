from pathlib import Path
import shutil
import subprocess

from AirspaceManager.controller import airspace_from_openair, split_openair_blocks
from AirspaceManager.renderer import Renderer


ROOT = Path(__file__).resolve().parent.parent
DOCS_PUBLIC_DIR = ROOT / "docs" / "public"
ALL_RELEASES_DIR = DOCS_PUBLIC_DIR / "All releases"
GENERATE_INDEX_SCRIPT = ROOT / "generate_index_html.py"


def generate_html_maps(export_files, export_path):
    """
    Vytvori HTML mapy pro exportovane OpenAir soubory a ulozi je do slozky html.
    """
    print("Generating HTML maps for exported files...")

    export_path = Path(export_path)
    html_dir = export_path / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    for export_file in export_files:
        export_file = Path(export_file)
        try:
            airspace_data = export_file.read_text(encoding="utf-8")

            airspaces = []
            blocks = split_openair_blocks(airspace_data)
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                try:
                    airspaces.append(airspace_from_openair(block))
                except Exception as e:
                    print(f"Skipping invalid block: {e}")

            if not airspaces:
                print(f"No valid airspaces found in {export_file}, map skipped.")
                continue

            map_title = export_file.stem
            map_filename = f"{map_title}.html"

            renderer = Renderer(airspaces)
            renderer.render_map(title=map_title, filename=map_filename, output_dir=str(html_dir))

            print(f"Map '{map_filename}' generated successfully.")
        except Exception as e:
            print(f"Error generating map for {export_file}: {e}")


def regenerate_indexes():
    """Spusti skript generate_index_html.py z korene projektu."""
    if not GENERATE_INDEX_SCRIPT.exists():
        raise RuntimeError(f"Skript '{GENERATE_INDEX_SCRIPT}' neexistuje.")

    print("Spoustim generate_index_html.py ...")
    subprocess.run(
        ["python", str(GENERATE_INDEX_SCRIPT)],
        cwd=ROOT,
        check=True,
    )


def prompt_yes_no(prompt, default=False):
    """
    Jednoduche potvrzeni [Y/N].
    Pri Enter se vrati hodnota default.
    """
    suffix = "Y/n" if default else "y/N"
    answer = input(f"{prompt} [{suffix}] ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def publish_directory_to_docs(source_dir, docs_relative_dir=""):
    """
    Zkopiruje cely exportni adresar do zvolene podslozky docs/public a pregeneruje indexy.
    """
    source_dir = Path(source_dir)
    if not source_dir.exists():
        raise RuntimeError(f"Zdrojovy adresar '{source_dir}' neexistuje.")

    target_parent = DOCS_PUBLIC_DIR / docs_relative_dir if docs_relative_dir else DOCS_PUBLIC_DIR
    target_parent.mkdir(parents=True, exist_ok=True)

    target_dir = target_parent / source_dir.name
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)

    regenerate_indexes()
    return target_dir


def clean_public_root():
    """
    Vycisti pouze KOREN adresare docs/public:
    - smaze soubory s priponami .txt, .cub, .html, .md
    - smaze podadresar html (pokud existuje)
    """
    if not DOCS_PUBLIC_DIR.exists():
        raise RuntimeError(f"Adresar '{DOCS_PUBLIC_DIR}' neexistuje.")

    extensions_to_remove = {".txt", ".cub", ".html", ".md"}

    for item in DOCS_PUBLIC_DIR.iterdir():
        if item.is_file() and item.suffix.lower() in extensions_to_remove:
            print(f"Mazu soubor: {item}")
            item.unlink()
        elif item.is_dir() and item.name.lower() == "html":
            print(f"Mazu adresar: {item}")
            shutil.rmtree(item)


def copy_release_contents_to_public(source_dir):
    """
    Zkopiruje obsah release adresare do docs/public a nahradi kolidujici polozky.
    """
    source_dir = Path(source_dir)
    if not source_dir.exists():
        raise RuntimeError(f"Zdrojovy adresar '{source_dir}' neexistuje.")

    DOCS_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    for item in source_dir.iterdir():
        target = DOCS_PUBLIC_DIR / item.name
        if item.is_file():
            if target.exists():
                target.unlink()
            shutil.copy2(item, target)
        elif item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)


def publish_standard_release(source_dir):
    """
    Publikace standardniho release:
    - kopie do docs/public/All releases/<release>
    - vycisteni korene docs/public
    - zkopirovani obsahu release do docs/public
    - pregenerovani indexu
    """
    source_dir = Path(source_dir)
    if not source_dir.exists():
        raise RuntimeError(f"Zdrojovy adresar '{source_dir}' neexistuje.")

    ALL_RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    release_archive_dir = ALL_RELEASES_DIR / source_dir.name

    if release_archive_dir.exists():
        shutil.rmtree(release_archive_dir)
    shutil.copytree(source_dir, release_archive_dir)

    clean_public_root()
    copy_release_contents_to_public(source_dir)
    regenerate_indexes()

    return release_archive_dir
