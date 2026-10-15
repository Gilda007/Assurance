"""
Helper pour peupler les combos et traduire les codes depuis les référentiels
Version robuste avec fallbacks
"""
from typing import Optional, List, Dict
from PySide6.QtWidgets import QComboBox


class ReferentielHelper:
    """Helper centralisé d'accès aux référentiels pour l'UI"""
    
    _cache: Dict[str, str] = {}
    _cache_maps: Dict[str, Dict[str, str]] = {}
    
    # ============================================================
    # POPULATE COMBO
    # ============================================================
    
    @classmethod
    def populate_combo(
        cls,
        combo: QComboBox,
        famille: str,
        controller,
        add_empty: bool = False,
        empty_label: str = "— Sélectionner —",
        selected_code: Optional[str] = None
    ):
        """Peuple un QComboBox avec les options d'une famille"""
        combo.clear()
        
        if add_empty:
            combo.addItem(empty_label, None)
        
        # ✅ Garde : pas de controller
        if controller is None:
            combo.addItem("— Non disponible —", None)
            return
        
        try:
            # ✅ Essayer plusieurs méthodes par ordre de priorité
            options = cls._load_options(famille, controller)
            
            if not options:
                combo.addItem("— Aucune option —", None)
                return
            
            for opt in options:
                code = opt.get('code')
                libelle = opt.get('libelle') or code or ''
                combo.addItem(libelle, code)
            
            # Sélectionner par défaut
            if selected_code:
                cls._select_by_data(combo, selected_code)
        
        except Exception as e:
            print(f"[ReferentielHelper] Erreur populate_combo({famille}): {e}")
            combo.addItem("— Erreur —", None)
    
    @classmethod
    def _load_options(cls, famille: str, controller) -> List[dict]:
        """Charge les options avec fallback multi-méthodes"""
        # Méthode 1 : controller.service.get_options()
        if hasattr(controller, 'service') and hasattr(controller.service, 'get_options'):
            return controller.service.get_options(famille) or []
        
        # Méthode 2 : controller.get_referentiels_by_famille()
        if hasattr(controller, 'get_referentiels_by_famille'):
            return controller.get_referentiels_by_famille(famille) or []
        
        # Méthode 3 : controller.service.get_referentiels_by_famille()
        if hasattr(controller, 'service') and hasattr(controller.service, 'get_referentiels_by_famille'):
            refs = controller.service.get_referentiels_by_famille(famille) or []
            return [
                {'code': r.code, 'libelle': r.libelle, 'valeur': getattr(r, 'valeur', None)}
                for r in refs
            ]
        
        return []
    
    # ============================================================
    # GET LIBELLE
    # ============================================================
    
    @classmethod
    def get_libelle(cls, famille: str, code: str, controller) -> str:
        """Traduit un code en libellé (avec cache)"""
        if not code:
            return "—"
        
        cache_key = f"{famille}:{code}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        # ✅ Garde
        if controller is None:
            return code
        
        try:
            # Méthode 1 : service.get_libelle()
            if hasattr(controller, 'service') and hasattr(controller.service, 'get_libelle'):
                libelle = controller.service.get_libelle(famille, code)
                if libelle:
                    cls._cache[cache_key] = libelle
                    return libelle
            
            # Méthode 2 : construire depuis les options
            options = cls._load_options(famille, controller)
            for opt in options:
                if opt.get('code') == code:
                    libelle = opt.get('libelle') or code
                    cls._cache[cache_key] = libelle
                    return libelle
            
            # Fallback : retourner le code
            cls._cache[cache_key] = code
            return code
        
        except Exception:
            return code
    
    # ============================================================
    # GET MAPPING COMPLET
    # ============================================================
    
    @classmethod
    def get_libelles_map(cls, famille: str, controller) -> Dict[str, str]:
        """Retourne un mapping complet code → libellé"""
        cache_key = f"__map__:{famille}"
        if cache_key in cls._cache_maps:
            return cls._cache_maps[cache_key]
        
        if controller is None:
            return {}
        
        try:
            # Méthode 1 : service.get_libelles_map()
            if hasattr(controller, 'service') and hasattr(controller.service, 'get_libelles_map'):
                mapping = controller.service.get_libelles_map(famille) or {}
                cls._cache_maps[cache_key] = mapping
                return mapping
            
            # Méthode 2 : construire depuis les options
            options = cls._load_options(famille, controller)
            mapping = {o['code']: o.get('libelle', o['code']) for o in options if o.get('code')}
            cls._cache_maps[cache_key] = mapping
            return mapping
        
        except Exception:
            return {}
    
    # ============================================================
    # CACHE
    # ============================================================
    
    @classmethod
    def clear_cache(cls):
        """Vide tout le cache"""
        cls._cache.clear()
        cls._cache_maps.clear()
    
    # ============================================================
    # HELPERS INTERNES
    # ============================================================
    
    @staticmethod
    def _select_by_data(combo: QComboBox, code):
        """Sélectionne l'item par sa data"""
        for i in range(combo.count()):
            if combo.itemData(i) == code:
                combo.setCurrentIndex(i)
                return