#!/usr/bin/env python3
"""
Script d'audit des contrôleurs LOMETA.

Compare les méthodes publiques de chaque service avec celles du contrôleur
correspondant pour détecter les manques.

Usage:
    python tools/audit_controllers.py
    python tools/audit_controllers.py --verbose
    python tools/audit_controllers.py --output rapport.md
"""
import argparse
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ============================================================
# CONFIGURATION
# ============================================================

# Couples (service, contrôleur) à auditer
PAIRS = [
    (
        "addons.sinistres.services.sinistre_service",
        "SinistreService",
        "addons.sinistres.controllers.sinistre_controller",
        "SinistreController",
    ),
    (
        "addons.sinistres.services.expertise_service",
        "ExpertiseService",
        "addons.sinistres.controllers.expertise_controller",
        "ExpertiseController",
    ),
    (
        "addons.sinistres.services.evaluation_service",
        "EvaluationService",
        "addons.sinistres.controllers.evaluation_controller",
        "EvaluationController",
    ),
    (
        "addons.sinistres.services.reglement_service",
        "ReglementService",
        "addons.sinistres.controllers.reglement_controller",
        "ReglementController",
    ),
    (
        "addons.sinistres.services.recours_service",
        "RecoursService",
        "addons.sinistres.controllers.recours_controller",
        "RecoursController",
    ),
    (
        "addons.sinistres.services.comptabilite_service",
        "ComptabiliteService",
        "addons.sinistres.controllers.comptabilite_controller",
        "ComptabiliteController",
    ),
    (
        "addons.sinistres.services.referentiel_service",
        "ReferentielService",
        "addons.sinistres.controllers.referentiel_controller",
        "ReferentielController",
    ),
    (
        "addons.sinistres.services.audit_service",
        "AuditService",
        "addons.sinistres.controllers.audit_controller",
        "AuditController",
    ),
    (
        "addons.sinistres.services.parametre_service",
        "ParametreService",
        "addons.sinistres.controllers.parametre_controller",
        "ParametreController",
    ),
    (
        "addons.sinistres.services.permission_service",
        "PermissionService",
        "addons.sinistres.controllers.permission_controller",
        "PermissionController",
    ),
]

# Méthodes à ignorer (internes, magiques, héritées)
IGNORED_PREFIXES = ("_", "__")
IGNORED_NAMES = {
    # BaseService
    "session", "close", "get_user", "get_user_info",
    "get_by_id", "get_all", "soft_delete", "generate_numero",
    "log_audit", "execute_with_retry",
    "__enter__", "__exit__", "__init__",
    # BaseController
    "set_current_user", "get_current_user", "get_current_user_id",
    "get_current_user_name", "handle_error", "handle_success",
    "heartbeat", "error_occurred", "success_occurred", "data_updated",
}

# Méthodes "évidentes" qu'on ne veut pas voir dans le rapport
# (car souvent inutiles à exposer dans le contrôleur)
IGNORED_METHODS = {
    # Méthodes CRUD basiques souvent inutiles à exposer
    "get_evaluation", "get_mission", "get_recours", "get_reglement",
}


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def get_public_methods(cls) -> Set[str]:
    """Retourne l'ensemble des méthodes publiques d'une classe."""
    methods = set()
    for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith(IGNORED_PREFIXES):
            continue
        if name in IGNORED_NAMES:
            continue
        methods.add(name)
    return methods


def import_class(module_path: str, class_name: str):
    """Importe une classe depuis un chemin de module."""
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        print(f"  ❌ Impossible d'importer {module_path}.{class_name} : {e}")
        return None


# ============================================================
# AUDIT D'UN COUPLE SERVICE / CONTRÔLEUR
# ============================================================

def audit_pair(
    service_module: str,
    service_name: str,
    controller_module: str,
    controller_name: str,
) -> Dict:
    """Audite un couple (service, contrôleur)."""
    
    print(f"\n{'=' * 70}")
    print(f"📊 Audit : {service_name}  vs  {controller_name}")
    print(f"{'=' * 70}")
    
    ServiceClass = import_class(service_module, service_name)
    ControllerClass = import_class(controller_module, controller_name)
    
    if not ServiceClass or not ControllerClass:
        return {
            'service': service_name,
            'controller': controller_name,
            'error': 'Import échoué',
        }
    
    service_methods = get_public_methods(ServiceClass)
    controller_methods = get_public_methods(ControllerClass)
    
    # Méthodes du service non exposées dans le contrôleur
    missing = service_methods - controller_methods
    
    # Méthodes du contrôleur qui ne sont pas dans le service
    # (ce sont souvent des méthodes de sérialisation ou d'orchestration)
    extra = controller_methods - service_methods
    
    # Filtrer les "extra" qui sont juste des sérialiseurs
    extra_filtered = {
        m for m in extra
        if not m.startswith(("_serialize_", "get_", "verifier_", "creer_"))
    }
    
    # Filtrer les "missing" qui sont explicitement ignorés
    missing_filtered = missing - IGNORED_METHODS
    
    print(f"  Méthodes du service     : {len(service_methods)}")
    print(f"  Méthodes du contrôleur  : {len(controller_methods)}")
    print(f"  Couverture              : "
          f"{len(service_methods & controller_methods)}/{len(service_methods)} "
          f"({100 * len(service_methods & controller_methods) / max(len(service_methods), 1):.0f}%)")
    
    if missing_filtered:
        print(f"\n  ⚠️  Méthodes du service NON exposées ({len(missing_filtered)}) :")
        for m in sorted(missing_filtered):
            print(f"     - {m}")
    
    if extra_filtered:
        print(f"\n  ℹ️  Méthodes du contrôleur absentes du service ({len(extra_filtered)}) :")
        for m in sorted(extra_filtered):
            print(f"     - {m}")
    
    return {
        'service': service_name,
        'controller': controller_name,
        'service_count': len(service_methods),
        'controller_count': len(controller_methods),
        'common_count': len(service_methods & controller_methods),
        'missing': sorted(missing_filtered),
        'extra': sorted(extra_filtered),
        'coverage': (
            len(service_methods & controller_methods)
            / max(len(service_methods), 1) * 100
        ),
    }


# ============================================================
# RAPPORT
# ============================================================

def generate_report(results: List[Dict], output_path: str = None) -> str:
    """Génère un rapport markdown."""
    
    lines = []
    lines.append("# 📋 Rapport d'audit des contrôleurs LOMETA\n")
    lines.append(f"*Généré le {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}*\n")
    lines.append("---\n")
    
    # Tableau récapitulatif
    lines.append("## 📊 Vue d'ensemble\n")
    lines.append("| Service | Contrôleur | Couverture | Manquants |")
    lines.append("|---------|------------|:----------:|:---------:|")
    
    for r in results:
        if 'error' in r:
            lines.append(
                f"| {r['service']} | {r['controller']} | ❌ | {r['error']} |"
            )
        else:
            coverage_emoji = (
                "✅" if r['coverage'] >= 90
                else "⚠️" if r['coverage'] >= 70
                else "🚨"
            )
            lines.append(
                f"| {r['service']} | {r['controller']} | "
                f"{coverage_emoji} {r['coverage']:.0f}% | "
                f"{len(r['missing'])} |"
            )
    
    lines.append("\n---\n")
    
    # Détails par couple
    lines.append("## 🔍 Détails\n")
    
    for r in results:
        if 'error' in r:
            continue
        
        lines.append(f"### {r['service']}  →  {r['controller']}\n")
        lines.append(f"- Méthodes du service : **{r['service_count']}**")
        lines.append(f"- Méthodes du contrôleur : **{r['controller_count']}**")
        lines.append(f"- Couverture : **{r['coverage']:.0f}%**\n")
        
        if r['missing']:
            lines.append("**⚠️ Méthodes du service non exposées :**\n")
            for m in r['missing']:
                lines.append(f"- `{m}`")
            lines.append("")
        
        if r['extra']:
            lines.append("**ℹ️ Méthodes du contrôleur absentes du service :**\n")
            for m in r['extra']:
                lines.append(f"- `{m}`")
            lines.append("")
        
        lines.append("---\n")
    
    report = "\n".join(lines)
    
    if output_path:
        Path(output_path).write_text(report, encoding='utf-8')
        print(f"\n📄 Rapport écrit dans : {output_path}")
    
    return report


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Audit des contrôleurs LOMETA"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Affiche les méthodes extra",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Chemin du rapport markdown à générer",
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🔍 AUDIT DES CONTRÔLEURS LOMETA")
    print("=" * 70)
    
    # Ajouter le répertoire du projet au path
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    
    results = []
    for service_module, service_name, controller_module, controller_name in PAIRS:
        try:
            result = audit_pair(
                service_module, service_name,
                controller_module, controller_name,
            )
            results.append(result)
        except Exception as e:
            print(f"  ❌ Erreur audit {service_name} : {e}")
            results.append({
                'service': service_name,
                'controller': controller_name,
                'error': str(e),
            })
    
    # Synthèse
    print("\n" + "=" * 70)
    print("📊 SYNTHÈSE")
    print("=" * 70)
    
    total_missing = 0
    for r in results:
        if 'error' in r:
            print(f"  ❌ {r['service']:30s} → {r['controller']:30s} : ERREUR")
            continue
        
        coverage_emoji = (
            "✅" if r['coverage'] >= 90
            else "⚠️" if r['coverage'] >= 70
            else "🚨"
        )
        
        print(
            f"  {coverage_emoji} {r['service']:30s} → "
            f"{r['controller']:30s} : "
            f"{r['coverage']:5.0f}%  "
            f"({len(r['missing'])} manquant(s))"
        )
        
        total_missing += len(r['missing'])
    
    print(f"\n  📌 Total de méthodes non exposées : {total_missing}")
    
    # Génération du rapport
    if args.output:
        generate_report(results, args.output)
    
    # Code de sortie
    sys.exit(0 if total_missing == 0 else 1)


if __name__ == "__main__":
    main()