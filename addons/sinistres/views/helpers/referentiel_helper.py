"""
Helper pour peupler les combos et traduire les codes depuis les référentiels
"""
from typing import Optional, List
from PySide6.QtWidgets import QComboBox


class ReferentielHelper:
    """Helper centralisé d'accès aux référentiels pour l'UI"""
    
    _cache = {}  # Cache des mappings code→libellé
    
    @classmethod
    def populate_combo(
        cls,
        combo: QComboBox,
        famille: str,
        controller,  # ReferentielController
        add_empty: bool = False,
        empty_label: str = "— Sélectionner —",
        selected_code: Optional[str] = None
    ):
        """Peuple un QComboBox avec les options d'une famille"""
        combo.clear()
        
        if add_empty:
            combo.addItem(empty_label, None)
        
        try:
            options = controller.service.get_options(famille)
            for opt in options:
                display = opt.get('libelle', opt.get('code', ''))
                combo.addItem(display, opt.get('code'))
            
            # Sélectionner par défaut
            if selected_code:
                cls._select_by_data(combo, selected_code)
        except Exception as e:
            print(f"[ReferentielHelper] Erreur populate_combo({famille}): {e}")
    
    @classmethod
    def get_libelle(
        cls,
        famille: str,
        code: str,
        controller
    ) -> str:
        """Traduit un code en libellé (avec cache)"""
        cache_key = f"{famille}:{code}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        try:
            libelle = controller.service.get_libelle(famille, code)
            result = libelle or code or "—"
            cls._cache[cache_key] = result
            return result
        except Exception:
            return code or "—"
    
    @classmethod
    def get_libelles_map(cls, famille: str, controller) -> dict:
        """Retourne un mapping complet code → libellé"""
        cache_key = f"__map__:{famille}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        try:
            mapping = controller.service.get_libelles_map(famille)
            cls._cache[cache_key] = mapping
            return mapping
        except Exception:
            return {}
    
    @classmethod
    def clear_cache(cls):
        """Vide le cache"""
        cls._cache.clear()
    
    @staticmethod
    def _select_by_data(combo: QComboBox, code):
        """Sélectionne l'item par sa data"""
        for i in range(combo.count()):
            if combo.itemData(i) == code:
                combo.setCurrentIndex(i)
                return