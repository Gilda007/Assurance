"""
Audit des relations SQLAlchemy — détecte les back_populates orphelins
Version robuste : ne plante pas si configure_mappers() échoue
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ⚠️ Import de TOUS les modèles pour les enregistrer dans le registre
try:
    import addons.sinistres.models  # noqa: F401
except Exception as e:
    print(f"⚠️ Erreur d'import des modèles : {e}")

from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers
from core.database import Base


def audit_relations():
    """Détecte les relations SQLAlchemy mal configurées"""
    
    print("\n" + "=" * 70)
    print("🔍 AUDIT DES RELATIONS SQLALCHEMY")
    print("=" * 70)
    
    # ============================================================
    # ÉTAPE 1 : Tenter configure_mappers()
    # ============================================================
    configuration_ok = False
    try:
        configure_mappers()
        print("\n✅ configure_mappers() OK — toutes les relations sont cohérentes")
        configuration_ok = True
    except Exception as e:
        print(f"\n❌ configure_mappers() a échoué :")
        print(f"   {type(e).__name__}: {e}")
        print("\n👉 Analyse manuelle des mappers...\n")
    
    # ============================================================
    # ÉTAPE 2 : Analyser les mappers SANS forcer la config
    # ============================================================
    # Important : on utilise `Base.registry.mappers` directement
    # et on capture les erreurs au cas par cas
    
    print("-" * 70)
    print("📋 INVENTAIRE DES RELATIONS")
    print("-" * 70)
    
    problemes = []
    
    for mapper in Base.registry.mappers:
        cls_name = mapper.class_.__name__
        
        try:
            # ⚠️ Peut lever une exception si la relation n'est pas résolue
            relations = list(mapper.relationships)
        except Exception as e:
            problemes.append({
                'source': cls_name,
                'probleme': f"Impossible de lire les relations : {e}",
            })
            continue
        
        for rel in relations:
            try:
                target_cls_name = rel.mapper.class_.__name__
                back = rel.back_populates
                
                if back:
                    target_cls = rel.mapper.class_
                    if not hasattr(target_cls, back):
                        problemes.append({
                            'source': f"{cls_name}.{rel.key}",
                            'target': target_cls_name,
                            'back_populates': back,
                            'probleme': f"{target_cls_name}.{back} n'existe pas",
                        })
                    else:
                        print(f"   ✅ {cls_name}.{rel.key} ⇄ {target_cls_name}.{back}")
                else:
                    print(f"   ⚪ {cls_name}.{rel.key} → {target_cls_name} (pas de back_populates)")
            except Exception as e:
                problemes.append({
                    'source': f"{cls_name}.{rel.key}",
                    'probleme': f"Erreur relation : {e}",
                })
    
    # ============================================================
    # ÉTAPE 3 : Rapport final
    # ============================================================
    print("\n" + "=" * 70)
    if problemes:
        print(f"❌ {len(problemes)} PROBLÈME(S) DÉTECTÉ(S)")
        print("=" * 70)
        for p in problemes:
            print(f"\n🔴 {p['source']}")
            if 'target' in p:
                print(f"   → cible : {p['target']}")
                print(f"   → back_populates = '{p['back_populates']}'")
            print(f"   → PROBLÈME : {p['probleme']}")
    else:
        print("🎉 AUCUN PROBLÈME DÉTECTÉ")
    print("=" * 70 + "\n")
    
    return problemes


if __name__ == "__main__":
    audit_relations()