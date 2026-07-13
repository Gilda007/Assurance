# -*- coding: utf-8 -*-
# ⚠️ MODULE COMPILÉ - Code source non disponible
import os
import sys
import importlib.util

def __load_compiled():
    """Charge le module compilé en .pyc"""
    module_name = __name__
    pyc_path = __file__ + 'c'
    
    if not os.path.isfile(pyc_path):
        raise ImportError(f"Fichier compilé manquant: {pyc_path}")
    
    spec = importlib.util.spec_from_file_location(module_name, pyc_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Remplacer dans sys.modules
    sys.modules[module_name] = module
    
    # Exporter le contenu
    for attr_name in dir(module):
        if not attr_name.startswith('_'):
            globals()[attr_name] = getattr(module, attr_name)
    
    if hasattr(module, '__all__'):
        globals()['__all__'] = module.__all__
    
    return module

__load_compiled()
