"""
Vérifie que chaque appel self.service.xxx() existe dans le service
"""
import inspect
import re
import pytest


PAIRES = [
    ('SinistreController', 'SinistreService'),
    ('ExpertiseController', 'ExpertiseService'),
    ('EvaluationController', 'EvaluationService'),
    ('ReglementController', 'ReglementService'),
    ('RecoursController', 'RecoursService'),
    ('ReferentielController', 'ReferentielService'),
    ('AutomobileController', 'AutomobileService'),
]


def get_cls(module_name, cls_name):
    """Import dynamique"""
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def test_all_controllers_calls_have_services():
    """Chaque appel self.service.X() a une méthode X() dans le service"""
    
    manquants_globaux = {}
    
    for ctrl_name, svc_name in PAIRES:
        ctrl_cls = get_cls(
            f'addons.sinistres.controllers.{ctrl_name.lower()}', 
            ctrl_name
        )
        svc_cls = get_cls(
            f'addons.sinistres.services.{svc_name.lower()}',
            svc_name
        )
        
        # Extraire les appels
        source = inspect.getsource(ctrl_cls)
        appels = set(re.findall(r'self\.service\.(\w+)\s*\(', source))
        
        # Méthodes du service
        svc_methods = {
            name for name, _ in inspect.getmembers(svc_cls, inspect.isfunction)
            if not name.startswith('_')
        }
        
        manquants = sorted(appels - svc_methods)
        if manquants:
            manquants_globaux[ctrl_name] = manquants
    
    # Afficher le rapport
    if manquants_globaux:
        print("\n" + "=" * 70)
        print("⚠️ MÉTHODES MANQUANTES")
        print("=" * 70)
        for ctrl, meths in manquants_globaux.items():
            print(f"\n{ctrl}:")
            for m in meths:
                print(f"   - {m}()")
    
    assert not manquants_globaux, f"Méthodes manquantes : {manquants_globaux}"