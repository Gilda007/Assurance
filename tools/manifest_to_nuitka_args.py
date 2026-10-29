#!/usr/bin/env python3
"""manifest_to_nuitka_args.py — Traduit un manifeste scan_addon_tree en args Nuitka.

Filtre défensif : retire les entrées parasites (__pycache__, __pypackages__,
.history, _build, tests/, etc.) même si le manifeste en contient.
"""
import json
import sys
from pathlib import Path

# Parties de chemin pointé à ne JAMAIS inclure dans un build
EXCLUDED_PARTS = {
    "__pycache__", "__pypackages__",
    ".history", "_build",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".git", ".hg", ".svn",
    ".venv", "venv", "env",
}

# Dossiers optionnels à exclure du build de production (à adapter)
EXCLUDED_TOP_DIRS = {"tests"}  # ex. {"tests", "docs", "examples"}


def _is_clean(dotted: str) -> bool:
    """Vrai si aucun segment du chemin pointé n'est blacklisted."""
    parts = dotted.split(".")
    if any(p in EXCLUDED_PARTS for p in parts):
        return False
    # Exclure un sous-dossier de premier niveau (ex. addons.X.tests.*)
    # parts = [addons, X, <top>, ...]
    if len(parts) >= 3 and parts[2] in EXCLUDED_TOP_DIRS:
        return False
    return True


def main():
    manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    addon = manifest["addon"]
    flat = manifest["flat"]

    emitted = 0
    dropped = 0

    def emit(prefix: str, entries):
        nonlocal emitted, dropped
        for entry in entries:
            if _is_clean(entry):
                print(f"{prefix}={entry}")
                emitted += 1
            else:
                dropped += 1

    emit("--include-package", flat["packages"])
    emit("--include-package", flat["namespace_packages"])
    emit("--include-module",  flat["modules"])

    if flat["data_files"] or flat["prebuilt_extensions"]:
        print(f"--include-package-data=addons.{addon}")

    if dropped:
        print(f"# manifest_to_nuitka_args: {emitted} arg(s) émis, "
              f"{dropped} entrée(s) parasite(s) ignorée(s)", file=sys.stderr)


if __name__ == "__main__":
    main()