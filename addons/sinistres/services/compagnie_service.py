"""
Service interne pour les compagnies (accès direct au modèle)
Ne dépend PAS du module Automobiles.
"""
from typing import List, Dict, Any

from addons.sinistres.services.base_service import BaseService


class CompagnieService(BaseService):
    """Service de lecture des compagnies d'assurance"""
    
    def __init__(self, session=None):
        super().__init__(session)
    
    def get_all_compagnies(self, actifs_only: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère les compagnies d'assurance depuis la base.
        
        Retourne une liste de dicts :
        [{'id': 1, 'code': 'AXA', 'libelle': 'AXA Assurances'}, ...]
        """
        try:
            # Essayer plusieurs emplacements du modèle
            Compagnie = self._resolve_compagnie_model()
            if not Compagnie:
                return []
            
            query = self.session.query(Compagnie)
            
            if actifs_only:
                if hasattr(Compagnie, 'est_actif'):
                    query = query.filter(Compagnie.est_actif == True)
                elif hasattr(Compagnie, 'is_active'):
                    query = query.filter(Compagnie.is_active == True)
            
            # Tri
            if hasattr(Compagnie, 'libelle'):
                query = query.order_by(Compagnie.libelle)
            elif hasattr(Compagnie, 'nom'):
                query = query.order_by(Compagnie.nom)
            
            compagnies = query.all()
            
            return [
                {
                    'id': c.id,
                    'code': getattr(c, 'code', None) or getattr(c, 'code_compagnie', None),
                    'libelle': getattr(c, 'libelle', None) or getattr(c, 'nom', None) or f"Compagnie #{c.id}",
                    'est_actif': getattr(c, 'est_actif', True),
                }
                for c in compagnies
            ]
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_compagnie(self, compagnie_id: int) -> Dict[str, Any]:
        """Récupère une compagnie par son ID"""
        try:
            Compagnie = self._resolve_compagnie_model()
            if not Compagnie:
                return {}
            
            c = self.session.query(Compagnie).filter(
                Compagnie.id == compagnie_id
            ).first()
            
            if not c:
                return {}
            
            return {
                'id': c.id,
                'code': getattr(c, 'code', None) or getattr(c, 'code_compagnie', None),
                'libelle': getattr(c, 'libelle', None) or getattr(c, 'nom', None),
                'est_actif': getattr(c, 'est_actif', True),
            }
        except Exception as e:
            self.session.rollback()
            raise e
    
    def _resolve_compagnie_model(self):
        """Essaie plusieurs emplacements du modèle Compagnie"""
        candidates = [
            ('addons.Automobiles.models.compagnies_models', 'Compagnie'),
            ('addons.Automobiles.models.compagnies_models', 'LometaCompagnie'),
            ('addons.sinistres.models.sinistre', 'LometaCompagnie'),
            ('addons.sinistres.models.referentiel', 'Compagnie'),
            ('addons.sinistres.models.referentiel', 'LometaCompagnie'),
        ]
        
        for module_path, class_name in candidates:
            try:
                module = __import__(module_path, fromlist=[class_name])
                model = getattr(module, class_name, None)
                if model:
                    print(f"✅ Modèle Compagnie trouvé : {module_path}.{class_name}")
                    return model
            except ImportError:
                continue
        
        print("⚠️ Aucun modèle Compagnie trouvé")
        return None