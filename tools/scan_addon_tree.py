#!/usr/bin/env python3
"""
scan_addon_tree.py — Inventaire exhaustif de l'arborescence d'un addon.

Aucun import du code de l'addon n'est effectué : scan 100% statique.
Sortie : JSON canonique (tree + flat + summary) sur stdout et/ou fichier.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ───
IGNORED_DIRS = {
    "__pycache__", ".history", ".git", ".svn", ".hg",
    ".pytest_cache", "_build", "node_modules", ".mypy_cache",
    ".ruff_cache", ".venv", "venv", "env", "migrations", 
}
IGNORED_FILE_EXTS = {".pyc", ".pyo"}
PYTHON_EXTS = {".py"}
PREBUILT_EXTS = {".so", ".pyd"}
HIDDEN_PREFIX = "."


# def classify_dir(dir_path: Path) -> str:
#     """Détermine le type d'un dossier sans descendre."""
#     name = dir_path.name
#     if name in IGNORED_DIRS:
#         return "ignored_dir"
#     if (dir_path / "__init__.py").is_file():
#         return "package"
#     # Namespace package : contient au moins un .py récursivement
#     for _ in dir_path.rglob("*.py"):
#         return "namespace_package"
#     return "data_dir"


def classify_dir(dir_path: Path) -> str:
    """Détermine le type d'un dossier sans descendre."""
    name = dir_path.name
    if name in IGNORED_DIRS:
        return "ignored_dir"
    # Un dossier dont un parent est ignoré ne devrait jamais être atteint,
    # mais on double la sécurité.
    if any(part in IGNORED_DIRS for part in dir_path.parts):
        return "ignored_dir"
    if (dir_path / "__init__.py").is_file():
        return "package"
    # Namespace package : contient au moins un .py hors dossiers ignorés
    for p in dir_path.rglob("*.py"):
        if not any(part in IGNORED_DIRS for part in p.parts):
            return "namespace_package"
    return "data_dir"


def classify_file(file_path: Path, parent_type: str) -> str:
    """Détermine le type d'un fichier."""
    name = file_path.name
    if name == "__init__.py":
        return "package_init"
    if name == "__main__.py":
        return "package_main"
    ext = file_path.suffix.lower()
    if ext in IGNORED_FILE_EXTS:
        return "ignored_compiled"
    if ext in PYTHON_EXTS:
        return "module"
    if ext in PREBUILT_EXTS:
        return "prebuilt_extension"
    return "data_file"


def to_dotted(addon: str, rel_path: Path, is_package: bool) -> str:
    """Convertit chemin relatif -> chemin Python pointé."""
    parts = list(rel_path.parts)
    if not is_package:
        # Retirer l'extension .py
        parts[-1] = Path(parts[-1]).stem
    return ".".join([addon] + parts) if parts else addon


def walk_dir(
    dir_path: Path,
    addon: str,
    rel_path: Path,
    flat: dict,
    depth: int = 0,
) -> dict:
    """Parcourt récursivement un dossier et retourne le nœud tree correspondant."""
    node_type = classify_dir(dir_path) if depth > 0 else "package"
    node = {
        "name": dir_path.name if depth > 0 else addon,
        "rel_path": str(rel_path) if rel_path != Path(".") else "",
        "type": node_type,
    }

    # Un dossier blacklisted : on ne descend pas (À FAIRE AVANT L'AJOUT)
    if node_type == "ignored_dir":
        node["reason"] = "blacklisted"
        flat["ignored"].append(str(rel_path))
        return node

    # Chemin pointé pour les packages / namespace packages
    if node_type in ("package", "namespace_package"):
        dotted = to_dotted(addon, rel_path, is_package=True)
        node["dotted"] = dotted
        if node_type == "package":
            flat["packages"].append(dotted)
        else:
            flat["namespace_packages"].append(dotted)

    children = []
    try:
        entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        node["error"] = "permission_denied"
        return node

    for entry in entries:
        entry_rel = rel_path / entry.name if rel_path != Path(".") else Path(entry.name)

        if entry.is_dir():
            child = walk_dir(entry, addon, entry_rel, flat, depth + 1)
        elif entry.is_file():
            file_type = classify_file(entry, node_type)
            child = {
                "name": entry.name,
                "rel_path": str(entry_rel),
                "type": file_type,
                "size": entry.stat().st_size,
            }

            # Classification dans les vues à plat
            if file_type == "module":
                child["dotted"] = to_dotted(addon, entry_rel, is_package=False)
                flat["modules"].append(child["dotted"])
            elif file_type == "package_main":
                child["dotted"] = to_dotted(
                    addon, entry_rel.parent if entry_rel.parent != Path(".") else Path(""),
                    is_package=True
                ) + ".__main__"
                flat["modules"].append(child["dotted"])
            elif file_type == "prebuilt_extension":
                flat["prebuilt_extensions"].append(str(entry_rel))
            elif file_type == "data_file":
                flat["data_files"].append(str(entry_rel))
            elif file_type == "ignored_compiled":
                flat["ignored"].append(str(entry_rel))
        else:
            # Symlinks, devices, etc.
            child = {
                "name": entry.name,
                "rel_path": str(entry_rel),
                "type": "other",
            }

        children.append(child)

    node["children"] = children
    return node


def scan(addon: str, project_root: Path) -> dict:
    root = project_root / "addons" / addon
    if not root.is_dir():
        raise SystemExit(f"Addon introuvable : {root}")

    flat = {
        "packages": [],
        "namespace_packages": [],
        "modules": [],
        "data_files": [],
        "prebuilt_extensions": [],
        "ignored": [],
    }

    tree = walk_dir(root, addon, Path("."), flat)

    # Déduplication + tri
    for k in flat:
        flat[k] = sorted(set(flat[k]))

    total_py_bytes = sum(
        c.get("size", 0)
        for c in _iter_nodes(tree)
        if c.get("type") in ("module", "package_init", "package_main")
    )

    summary = {
        "packages": len(flat["packages"]),
        "namespace_packages": len(flat["namespace_packages"]),
        "modules": len(flat["modules"]),
        "data_files": len(flat["data_files"]),
        "prebuilt_extensions": len(flat["prebuilt_extensions"]),
        "ignored": len(flat["ignored"]),
        "total_py_bytes": total_py_bytes,
    }

    return {
        "addon": addon,
        "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root_path": str(root.relative_to(project_root)),
        "summary": summary,
        "flat": flat,
        "tree": tree,
    }


def _iter_nodes(node):
    """Itère sur tous les nœuds du tree (profondeur d'abord)."""
    yield node
    for child in node.get("children", []):
        yield from _iter_nodes(child)


def render_ascii_tree(node: dict, prefix: str = "", is_last: bool = True) -> str:
    """Affiche un tree en ASCII pour debug humain."""
    if node is node:  # racine
        lines = [f"{node['name']}/"]
    else:
        lines = []

    children = node.get("children", [])
    for i, child in enumerate(children):
        last = i == len(children) - 1
        connector = "└── " if last else "├── "
        marker = "/" if child["type"] in ("package", "namespace_package", "data_dir", "ignored_dir") else ""
        suffix = ""
        if child["type"] in ("module", "package_init", "package_main"):
            suffix = f"  ({child['size']} B)" if "size" in child else ""
        elif child["type"] == "ignored_dir":
            suffix = "  [ignored]"
        lines.append(f"{prefix}{connector}{child['name']}{marker}{suffix}")
        if "children" in child:
            extension = "    " if last else "│   "
            lines.append(render_ascii_tree(child, prefix + extension, last))
    return "\n".join(l for l in lines if l)


def main():
    parser = argparse.ArgumentParser(description="Inventaire statique de l'arborescence d'un addon.")
    parser.add_argument("addon", help="Nom de l'addon (dossier dans addons/)")
    parser.add_argument("--output", "-o", help="Fichier JSON de sortie (défaut : stdout)")
    parser.add_argument("--project-root", default=".", help="Racine du projet")
    parser.add_argument("--ascii", action="store_true", help="Afficher un tree ASCII sur stderr")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    manifest = scan(args.addon, project_root)

    if args.ascii:
        print(render_ascii_tree(manifest["tree"]), file=sys.stderr)
        print(file=sys.stderr)

    payload = json.dumps(manifest, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"✓ Manifeste écrit : {args.output}", file=sys.stderr)
    else:
        print(payload)


if __name__ == "__main__":
    main()