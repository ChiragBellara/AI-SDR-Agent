from typing import List
from pathlib import Path

DEFAULT_STORAGE_DIR = Path("../storage/identities/")


def _load_all_icps(storage_dir: Path = DEFAULT_STORAGE_DIR) -> List[Path]:
    if not storage_dir.exists():
        return []

    icps: List[Path] = []
    for p in storage_dir.glob("*.json"):
        try:
            icps.append(p)
        except Exception:
            # If a single file is corrupt, don't brick the whole run
            continue

    return icps
