"""
Audit : détecte les méthodes appelées par les contrôleurs
mais absentes des services.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import inspect
import re

from addons.sinistres.controllers import (
    SinistreController, ExpertiseController, EvaluationController,
    ReglementController, RecoursController, ReferentielController,
    AutomobileController,
)
from addons.sinistres.services import (
    SinistreService, ExpertiseService, EvaluationService,
    ReglementService, RecoursService, ReferentielService,
    AutomobileService,
)

PAIRES = [
    (SinistreController, SinistreService),
    (ExpertiseController, ExpertiseService),
    (EvaluationController, EvaluationService),
    (ReglementController, ReglementService),
    (RecoursController, RecoursService),
    (ReferentielController, ReferentielService),
    (AutomobileController, AutomobileService),
]


def verifier():
    print("\n" + "=" * 70)
    print("🔍 VÉRIFICATION APPELS CONTRÔLEUR → SERVICE")
    print("=" * 70)
    
    total_manquants = 0
    
    for ctrl_cls, svc_cls in PAIRES:
        print(f"\n📦 {ctrl_cls.__name__} → {svc_cls.__name__}")
        print("-" * 70)
        
        try:
            source = inspect.getsource(ctrl_cls)
        except Exception as e:
            print(f"   ⚠️ Impossible de lire la source : {e}")
            continue
        
        # Extraire les appels "self.service.xxx("
        appels = set(re.findall(r'self\.service\.(\w+)\s*\(', source))
        
        # Méthodes publiques du service
        svc_methods = {
            name for name, _ in inspect.getmembers(svc_cls, inspect.isfunction)
            if not name.startswith('_')
        }
        
        manquants = sorted(appels - svc_methods)
        
        if not manquants:
            print(f"   ✅ {len(appels)} appel(s) couvert(s)")
        else:
            print(f"   ❌ {len(manquants)} méthode(s) manquante(s) :")
            for m in manquants:
                print(f"      - {m}()")
            total_manquants += len(manquants)
    
    print("\n" + "=" * 70)
    if total_manquants == 0:
        print("🎉 TOUS LES APPELS SONT COUVERTS !")
    else:
        print(f"⚠️ {total_manquants} méthode(s) manquante(s) au total")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    verifier()