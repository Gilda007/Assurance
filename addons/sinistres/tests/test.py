"""
Vérifie que tous les appels self.service.xxx() des contrôleurs 
existent dans les services correspondants.
"""
import inspect
import re

from addons.sinistres.controllers import (
    SinistreController, ExpertiseController, EvaluationController,
    ReglementController, RecoursController, ReferentielController,
)
from addons.sinistres.services import (
    SinistreService, ExpertiseService, EvaluationService,
    ReglementService, RecoursService, ReferentielService,
)

PAIRES = [
    (SinistreController, SinistreService),
    (ExpertiseController, ExpertiseService),
    (EvaluationController, EvaluationService),
    (ReglementController, ReglementService),
    (RecoursController, RecoursService),
    (ReferentielController, ReferentielService),
]

def verifier():
    print("\n" + "=" * 70)
    print("🔍 VÉRIFICATION APPELS CONTRÔLEUR → SERVICE")
    print("=" * 70)
    
    for ctrl_cls, svc_cls in PAIRES:
        print(f"\n📦 {ctrl_cls.__name__} → {svc_cls.__name__}")
        print("-" * 70)
        
        source = inspect.getsource(ctrl_cls)
        appels = re.findall(r'self\.service\.(\w+)\s*\(', source)
        appels_uniques = sorted(set(appels))
        
        svc_methods = [
            name for name, _ in inspect.getmembers(svc_cls, inspect.isfunction)
            if not name.startswith('_')
        ]
        
        manquants = [a for a in appels_uniques if a not in svc_methods]
        
        if not manquants:
            print(f"   ✅ {len(appels_uniques)} appels OK")
        else:
            print(f"   ❌ {len(manquants)} méthode(s) manquante(s) :")
            for m in manquants:
                print(f"      - {m}()")

if __name__ == "__main__":
    verifier()