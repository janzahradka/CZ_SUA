from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime


ROOT = Path(__file__).resolve().parent
EXPORT_DIR = ROOT / "Export"
PUBLIC_DIR = ROOT / "docs" / "public"
ALL_RELEASES_DIR = PUBLIC_DIR / "All releases"

PATTERN = re.compile(r"^CZ_SUA_(\d{2}-\d{2}-\d{2})$")


def find_latest_release() -> Path:
    """Najde nejnovější složku CZ_SUA_YY-MM-DD v adresáři Export."""
    if not EXPORT_DIR.exists():
        raise RuntimeError(f"Adresář '{EXPORT_DIR}' neexistuje.")

    candidates: list[tuple[datetime, Path]] = []

    for d in EXPORT_DIR.iterdir():
        if not d.is_dir():
            continue
        match = PATTERN.match(d.name)
        if not match:
            continue
        date_str = match.group(1)  # YY-MM-DD
        dt = datetime.strptime(date_str, "%y-%m-%d")
        candidates.append((dt, d))

    if not candidates:
        raise RuntimeError("Nenalezena žádná složka 'CZ_SUA_YY-MM-DD' v adresáři Export.")

    candidates.sort()
    return candidates[-1][1]  # nejnovější


def copy_to_all_releases(src: Path) -> None:
    """Zkopíruje celý release do 'docs/public/All releases/'."""
    ALL_RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    dst = ALL_RELEASES_DIR / src.name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def clean_public_root() -> None:
    """
    Vyčistí pouze KOŘEN adresáře docs/public:
    - smaže soubory s příponami .txt, .cub, .html, .md
    - smaže podadresář html (pokud existuje)
    """
    if not PUBLIC_DIR.exists():
        raise RuntimeError(f"Adresář '{PUBLIC_DIR}' neexistuje.")

    extensions_to_remove = {".txt", ".cub", ".html", ".md"}

    for item in PUBLIC_DIR.iterdir():
        if item.is_file():
            if item.suffix.lower() in extensions_to_remove:
                print(f"Mažu soubor: {item}")
                item.unlink()
        elif item.is_dir() and item.name.lower() == "html":
            print(f"Mažu adresář: {item}")
            shutil.rmtree(item)


def copy_release_to_public(src: Path) -> None:
    """
    Zkopíruje OBSAH složky release (včetně podsložek) do docs/public,
    přičemž vždy nahradí existující soubory/složky stejného jména.
    """
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        target = PUBLIC_DIR / item.name
        if item.is_file():
            if target.exists():
                target.unlink()
            shutil.copy2(item, target)
        elif item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)


def regenerate_indexes() -> None:
    """Spustí skript generate_index_html.py z kořene projektu."""
    script = ROOT / "generate_index_html.py"
    if not script.exists():
        raise RuntimeError(f"Skript '{script}' neexistuje.")

    print("Spouštím generate_index_html.py ...")
    subprocess.run(
        ["python", str(script)],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    print(f"ROOT: {ROOT}")
    latest = find_latest_release()
    print(f"Nalezený nejnovější release: {latest.name}")
    answer = input("Chceš tento release skutečně publikovat do 'docs/public'? [Y/N] ").strip().lower()
    if answer not in ("y", "yes", ""):
        print("Publikace zrušena uživatelem.")
        return

    print("Kopíruji do 'All releases' ...")
    copy_to_all_releases(latest)

    print("Čistím kořen 'docs/public' ...")
    clean_public_root()

    print("Kopíruji obsah release do 'docs/public' ...")
    copy_release_to_public(latest)

    print("Regeneruji HTML indexy ...")
    regenerate_indexes()

    print("Publikace dokončena.")


if __name__ == "__main__":
    main()

