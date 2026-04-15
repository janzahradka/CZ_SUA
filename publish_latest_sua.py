import re
from pathlib import Path
from datetime import datetime

from utils.export_workflow import prompt_yes_no, publish_standard_release


ROOT = Path(__file__).resolve().parent
EXPORT_DIR = ROOT / "Export"

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
def main() -> None:
    print(f"ROOT: {ROOT}")
    latest = find_latest_release()
    print(f"Nalezený nejnovější release: {latest.name}")
    if not prompt_yes_no("Chceš tento release skutečně publikovat do 'docs/public'?", default=False):
        print("Publikace zrušena uživatelem.")
        return

    publish_standard_release(latest)
    print("Publikace dokončena.")


if __name__ == "__main__":
    main()

