#!/usr/bin/env python3
"""
manifest_diff.py — Comparaison de deux manifestes LOMETA.

Usage :
    python manifest_diff.py manifest_v1.json manifest_v2.json
    python manifest_diff.py manifest_v1.json manifest_v2.json --json
    python manifest_diff.py manifest_v1.json manifest_v2.json --csv rapport.csv
    python manifest_diff.py manifest_v1.json manifest_v2.json --summary-only
    python manifest_diff.py manifest_v1.json manifest_v2.json --fail-on-change

Retourne :
    0  → aucune différence (ou différences mineures si --fail-on-change absent)
    1  → différences détectées et --fail-on-change actif
    2  → erreur (fichier introuvable, JSON invalide…)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# Modèles
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FileEntry:
    """Entrée d'un fichier dans le manifeste."""
    path: str
    size: int
    sha256: str

    @classmethod
    def from_dict(cls, d: dict) -> "FileEntry":
        return cls(
            path=d.get("path", ""),
            size=int(d.get("size", 0)),
            sha256=d.get("sha256", ""),
        )


@dataclass
class Manifest:
    """Manifeste de distribution."""
    version: str
    platform: str
    arch: str
    generated_at: Optional[str]
    binaire: str
    binaire_sha256: str
    binaire_taille: int
    fichiers: dict[str, FileEntry]
    total_fichiers: int
    total_taille: int

    @classmethod
    def load(cls, path: str | Path) -> "Manifest":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Manifeste introuvable : {p}")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide dans {p} : {e}") from e

        fichiers = {
            e["path"]: FileEntry.from_dict(e)
            for e in data.get("fichiers", [])
            if e.get("path")
        }
        return cls(
            version=data.get("version", "?"),
            platform=data.get("platform", "?"),
            arch=data.get("arch", "?"),
            generated_at=data.get("generated_at"),
            binaire=data.get("binaire", ""),
            binaire_sha256=data.get("binaire_sha256", ""),
            binaire_taille=int(data.get("binaire_taille", 0)),
            fichiers=fichiers,
            total_fichiers=int(data.get("total_fichiers", len(fichiers))),
            total_taille=int(data.get("total_taille", 0)),
        )


@dataclass
class DiffReport:
    """Rapport de différences entre deux manifestes."""
    old: Manifest
    new: Manifest
    ajoutes: list[FileEntry] = field(default_factory=list)
    supprimes: list[FileEntry] = field(default_factory=list)
    modifies: list[tuple[FileEntry, FileEntry]] = field(default_factory=list)
    inchanges: int = 0
    binaire_change: bool = False
    version_changee: bool = False
    plateforme_changee: bool = False

    # ─── Statistiques ───
    @property
    def total_ajouts(self) -> int:
        return len(self.ajoutes)

    @property
    def total_suppressions(self) -> int:
        return len(self.supprimes)

    @property
    def total_modifications(self) -> int:
        return len(self.modifies)

    @property
    def total_changements(self) -> int:
        return self.total_ajouts + self.total_suppressions + self.total_modifications

    @property
    def taille_telechargement(self) -> int:
        """Taille cumulée des fichiers à télécharger (ajouts + modifs + binaire si changé)."""
        total = sum(e.size for e in self.ajoutes)
        total += sum(new.size for _, new in self.modifies)
        if self.binaire_change:
            total += self.new.binaire_taille
        return total

    @property
    def taille_suppression(self) -> int:
        """Taille cumulée des fichiers qui seront supprimés."""
        return sum(e.size for e in self.supprimes)

    def resume(self) -> dict:
        return {
            "ancienne_version": self.old.version,
            "nouvelle_version": self.new.version,
            "version_changee": self.version_changee,
            "plateforme_changee": self.plateforme_changee,
            "binaire_change": self.binaire_change,
            "ajouts": self.total_ajouts,
            "suppressions": self.total_suppressions,
            "modifications": self.total_modifications,
            "inchanges": self.inchanges,
            "total_changements": self.total_changements,
            "taille_telechargement_octets": self.taille_telechargement,
            "taille_suppression_octets": self.taille_suppression,
        }


# ═══════════════════════════════════════════════════════════════════
# Comparaison
# ═══════════════════════════════════════════════════════════════════

def comparer(old: Manifest, new: Manifest) -> DiffReport:
    """Compare deux manifestes et retourne un rapport détaillé."""
    rapport = DiffReport(old=old, new=new)

    rapport.version_changee = old.version != new.version
    rapport.plateforme_changee = (old.platform, old.arch) != (new.platform, new.arch)
    rapport.binaire_change = old.binaire_sha256 != new.binaire_sha256

    old_paths = set(old.fichiers.keys())
    new_paths = set(new.fichiers.keys())

    # Ajoutés
    for p in sorted(new_paths - old_paths):
        rapport.ajoutes.append(new.fichiers[p])

    # Supprimés
    for p in sorted(old_paths - new_paths):
        rapport.supprimes.append(old.fichiers[p])

    # Modifiés / inchangés
    for p in sorted(old_paths & new_paths):
        a = old.fichiers[p]
        b = new.fichiers[p]
        if a.sha256 != b.sha256:
            rapport.modifies.append((a, b))
        else:
            rapport.inchanges += 1

    return rapport


# ═══════════════════════════════════════════════════════════════════
# Formatage
# ═══════════════════════════════════════════════════════════════════

def _fmt_size(n: int) -> str:
    """Formatte une taille en octets de manière lisible."""
    if n < 1024:
        return f"{n} o"
    if n < 1024 ** 2:
        return f"{n / 1024:.1f} Ko"
    if n < 1024 ** 3:
        return f"{n / 1024 ** 2:.1f} Mo"
    return f"{n / 1024 ** 3:.2f} Go"


def _fmt_sha(s: str, length: int = 12) -> str:
    """Tronque un hash SHA pour l'affichage."""
    return s[:length] + ("…" if len(s) > length else "")


def _barre_progression(pct: float, largeur: int = 20) -> str:
    """Génère une barre de progression ASCII."""
    rempli = int(pct / 100 * largeur)
    return "█" * rempli + "░" * (largeur - rempli)


def afficher_rapport(rapport: DiffReport, verbose: bool = True) -> None:
    """Affiche le rapport dans la console."""
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    WHITE = "\033[1;37m"
    GRAY = "\033[90m"
    NC = "\033[0m"

    print()
    print(f"{CYAN}{'═' * 70}{NC}")
    print(f"{WHITE}  RAPPORT DE DIFFÉRENCE — LOMETA{NC}")
    print(f"{CYAN}{'═' * 70}{NC}")

    # ─── En-tête ───
    print(f"\n{WHITE}📋 Versions :{NC}")
    if rapport.version_changee:
        print(f"   {RED}{rapport.old.version}{NC}  →  {GREEN}{rapport.new.version}{NC}")
    else:
        print(f"   {YELLOW}{rapport.old.version}{NC} (identique)")

    print(f"\n{WHITE}🖥  Plateforme :{NC}")
    if rapport.plateforme_changee:
        print(f"   {RED}{rapport.old.platform}/{rapport.old.arch}{NC}  →  "
              f"{GREEN}{rapport.new.platform}/{rapport.new.arch}{NC}")
    else:
        print(f"   {rapport.new.platform}/{rapport.new.arch}")

    if rapport.old.generated_at or rapport.new.generated_at:
        print(f"\n{WHITE}📅 Généré :{NC}")
        print(f"   {GRAY}{rapport.old.generated_at or '?'}{NC}")
        print(f"   {GRAY}{rapport.new.generated_at or '?'}{NC}")

    # ─── Binaire ───
    print(f"\n{WHITE}🔨 Binaire principal :{NC}")
    if rapport.binaire_change:
        print(f"   {RED}✓ MODIFIÉ{NC}  "
              f"({_fmt_sha(rapport.old.binaire_sha256)} → "
              f"{_fmt_sha(rapport.new.binaire_sha256)}, "
              f"{_fmt_size(rapport.new.binaire_taille)})")
    else:
        print(f"   {GREEN}✓ IDENTIQUE{NC}  ({_fmt_sha(rapport.new.binaire_sha256)})")

    # ─── Statistiques ───
    total_old = len(rapport.old.fichiers)
    total_new = len(rapport.new.fichiers)
    total_changes = rapport.total_changements
    pct_changes = (total_changes / max(total_old, 1)) * 100

    print(f"\n{WHITE}📊 Statistiques :{NC}")
    print(f"   Fichiers (ancien) : {total_old}")
    print(f"   Fichiers (nouveau): {total_new}")
    print(f"   {GREEN}+ Ajoutés       : {rapport.total_ajouts}{NC}")
    print(f"   {RED}- Supprimés      : {rapport.total_suppressions}{NC}")
    print(f"   {YELLOW}~ Modifiés       : {rapport.total_modifications}{NC}")
    print(f"   {GRAY}= Inchangés      : {rapport.inchanges}{NC}")
    print(f"   {WHITE}∑ Changements    : {total_changes} "
          f"({pct_changes:.1f}%){NC}")

    # ─── Barre de progression (pourcentage de fichiers impactés) ───
    if total_old > 0:
        barre = _barre_progression(pct_changes)
        couleur = GREEN if pct_changes < 10 else (YELLOW if pct_changes < 50 else RED)
        print(f"   {couleur}{barre}{NC} {pct_changes:.1f}%")

    # ─── Impact disque ───
    print(f"\n{WHITE}💾 Impact mise à jour :{NC}")
    print(f"   {GREEN}↓ Téléchargement : {_fmt_size(rapport.taille_telechargement)}{NC}")
    if rapport.taille_suppression > 0:
        print(f"   {RED}↑ Suppression    : {_fmt_size(rapport.taille_suppression)}{NC}")
    if rapport.new.total_taille > 0:
        print(f"   Total nouvelle distribution : {_fmt_size(rapport.new.total_taille)}")

    # ─── Détail par catégorie ───
    if verbose:
        if rapport.ajoutes:
            print(f"\n{GREEN}📁 Fichiers AJOUTÉS ({len(rapport.ajoutes)}) :{NC}")
            for e in rapport.ajoutes:
                print(f"   {GREEN}+{NC} {e.path}  {GRAY}({_fmt_size(e.size)}){NC}")

        if rapport.supprimes:
            print(f"\n{RED}🗑  Fichiers SUPPRIMÉS ({len(rapport.supprimes)}) :{NC}")
            for e in rapport.supprimes:
                print(f"   {RED}-{NC} {e.path}  {GRAY}({_fmt_size(e.size)}){NC}")

        if rapport.modifies:
            print(f"\n{YELLOW}✏️  Fichiers MODIFIÉS ({len(rapport.modifies)}) :{NC}")
            for old_e, new_e in rapport.modifies:
                delta = new_e.size - old_e.size
                signe = "+" if delta >= 0 else ""
                delta_str = f"{signe}{delta} o" if delta != 0 else "taille identique"
                print(f"   {YELLOW}~{NC} {new_e.path}")
                print(f"     {GRAY}sha: {_fmt_sha(old_e.sha256)} → {_fmt_sha(new_e.sha256)}{NC}")
                print(f"     {GRAY}taille: {_fmt_size(old_e.size)} → {_fmt_size(new_e.size)} ({delta_str}){NC}")

    print()
    print(f"{CYAN}{'═' * 70}{NC}")


def generer_notes_version(rapport: DiffReport) -> str:
    """Génère un texte de notes de version à partir du rapport."""
    lignes = []
    lignes.append(f"# Version {rapport.new.version}")
    lignes.append("")
    lignes.append(f"*Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}*")
    lignes.append("")

    if rapport.version_changee:
        lignes.append(f"Précédente version : `{rapport.old.version}`")
        lignes.append("")

    if not rapport.binaire_change and rapport.total_changements == 0:
        lignes.append("**Aucune modification** (build identique).")
        return "\n".join(lignes)

    if rapport.binaire_change:
        lignes.append("## 🔨 Binaire")
        lignes.append("")
        lignes.append(f"- Binaire principal recompilé "
                     f"({_fmt_size(rapport.new.binaire_taille)})")
        lignes.append("")

    if rapport.ajoutes:
        lignes.append(f"## ✨ Nouveaux fichiers ({len(rapport.ajoutes)})")
        lignes.append("")
        for e in rapport.ajoutes:
            lignes.append(f"- `{e.path}` ({_fmt_size(e.size)})")
        lignes.append("")

    if rapport.modifies:
        lignes.append(f"## ✏️ Fichiers modifiés ({len(rapport.modifies)})")
        lignes.append("")
        for old_e, new_e in rapport.modifies:
            delta = new_e.size - old_e.size
            if delta != 0:
                signe = "+" if delta > 0 else ""
                lignes.append(f"- `{new_e.path}` ({signe}{delta} o)")
            else:
                lignes.append(f"- `{new_e.path}`")
        lignes.append("")

    if rapport.supprimes:
        lignes.append(f"## 🗑️ Fichiers supprimés ({len(rapport.supprimes)})")
        lignes.append("")
        for e in rapport.supprimes:
            lignes.append(f"- `{e.path}`")
        lignes.append("")

    lignes.append("## 💾 Impact")
    lignes.append("")
    lignes.append(f"- **Téléchargement** : {_fmt_size(rapport.taille_telechargement)}")
    if rapport.taille_suppression > 0:
        lignes.append(f"- **Suppression** : {_fmt_size(rapport.taille_suppression)}")
    lignes.append(f"- **Distribution totale** : {_fmt_size(rapport.new.total_taille)}")

    return "\n".join(lignes)


def exporter_csv(rapport: DiffReport, chemin: str) -> None:
    """Exporte le rapport au format CSV."""
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["type", "path", "ancienne_taille", "nouvelle_taille",
                         "ancien_sha256", "nouveau_sha256"])
        for e in rapport.ajoutes:
            writer.writerow(["ajout", e.path, "", e.size, "", e.sha256])
        for e in rapport.supprimes:
            writer.writerow(["suppression", e.path, e.size, "", e.sha256, ""])
        for old_e, new_e in rapport.modifies:
            writer.writerow(["modification", new_e.path,
                             old_e.size, new_e.size,
                             old_e.sha256, new_e.sha256])


def exporter_json(rapport: DiffReport, chemin: str | None = None) -> str:
    """Exporte le rapport en JSON."""
    data = {
        "schema_version": 1,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "resume": rapport.resume(),
        "binaire": {
            "change": rapport.binaire_change,
            "ancien_sha256": rapport.old.binaire_sha256,
            "nouveau_sha256": rapport.new.binaire_sha256,
            "ancienne_taille": rapport.old.binaire_taille,
            "nouvelle_taille": rapport.new.binaire_taille,
        },
        "ajoutes": [e.__dict__ for e in rapport.ajoutes],
        "supprimes": [e.__dict__ for e in rapport.supprimes],
        "modifies": [
            {"ancien": old_e.__dict__, "nouveau": new_e.__dict__}
            for old_e, new_e in rapport.modifies
        ],
    }
    texte = json.dumps(data, indent=2, ensure_ascii=False)
    if chemin:
        Path(chemin).write_text(texte, encoding="utf-8")
    return texte


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare deux manifestes LOMETA et affiche les différences.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  %(prog)s manifest_v1.json manifest_v2.json
  %(prog)s v1/manifest.json v2/manifest.json --summary-only
  %(prog)s v1/manifest.json v2/manifest.json --json diff.json
  %(prog)s v1/manifest.json v2/manifest.json --csv rapport.csv
  %(prog)s v1/manifest.json v2/manifest.json --notes-version NOTES.md
  %(prog)s v1/manifest.json v2/manifest.json --fail-on-change
""",
    )
    parser.add_argument("ancien", help="Manifeste de référence")
    parser.add_argument("nouveau", help="Manifeste à comparer")
    parser.add_argument("--summary-only", action="store_true",
                        help="Affiche uniquement les statistiques (pas le détail)")
    parser.add_argument("--json", metavar="FICHIER",
                        help="Exporte le rapport en JSON")
    parser.add_argument("--csv", metavar="FICHIER",
                        help="Exporte le rapport en CSV")
    parser.add_argument("--notes-version", metavar="FICHIER",
                        help="Génère des notes de version Markdown")
    parser.add_argument("--fail-on-change", action="store_true",
                        help="Retourne 1 si des différences existent (utile en CI/CD)")
    parser.add_argument("--no-color", action="store_true",
                        help="Désactive les couleurs ANSI")

    args = parser.parse_args()

    # Désactiver les couleurs si demandé
    if args.no_color:
        import os
        os.environ["NO_COLOR"] = "1"

    try:
        old = Manifest.load(args.ancien)
        new = Manifest.load(args.nouveau)
    except (FileNotFoundError, ValueError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2

    rapport = comparer(old, new)
    afficher_rapport(rapport, verbose=not args.summary_only)

    if args.json:
        exporter_json(rapport, args.json)
        print(f"✅ JSON exporté : {args.json}")

    if args.csv:
        exporter_csv(rapport, args.csv)
        print(f"✅ CSV exporté : {args.csv}")

    if args.notes_version:
        notes = generer_notes_version(rapport)
        Path(args.notes_version).write_text(notes, encoding="utf-8")
        print(f"✅ Notes de version : {args.notes_version}")

    # Code de retour
    if args.fail_on_change:
        if rapport.total_changements > 0 or rapport.binaire_change:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())