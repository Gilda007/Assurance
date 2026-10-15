"""
Service de gestion des paramètres applicatifs
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.parametre import LometaParametre


class ParametreService(BaseService):
    """Service de gestion des paramètres"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # LECTURE
    # ============================================================
    
    def get_parametre(self, code: str) -> Optional[LometaParametre]:
        """Récupère un paramètre par son code"""
        try:
            return self.session.query(LometaParametre).filter(
                LometaParametre.code == code,
                LometaParametre.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_valeur(self, code: str, default: Any = None) -> Any:
        """
        Récupère la valeur typée d'un paramètre.
        
        Convertit automatiquement selon `type_donnee` :
        - INT     → int
        - DECIMAL → float
        - BOOL    → bool
        - STRING  → str
        - JSON    → dict/list
        """
        try:
            param = self.get_parametre(code)
            if not param or param.valeur is None:
                return default
            
            type_d = (param.type_donnee or "STRING").upper()
            
            if type_d == "INT":
                return int(param.valeur)
            elif type_d == "DECIMAL":
                return float(param.valeur)
            elif type_d == "BOOL":
                return str(param.valeur).lower() in ('true', '1', 'yes', 'oui')
            elif type_d == "JSON":
                import json
                return json.loads(param.valeur)
            else:
                return str(param.valeur)
        except Exception as e:
            self.session.rollback()
            return default
    
    def get_parametres_by_categorie(self, categorie: str) -> List[LometaParametre]:
        """Récupère tous les paramètres d'une catégorie"""
        try:
            return self.session.query(LometaParametre).filter(
                LometaParametre.categorie == categorie,
                LometaParametre.is_active == True
            ).order_by(LometaParametre.ordre_affichage).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_all_parametres(self, categorie: str = None) -> List[LometaParametre]:
        """Récupère tous les paramètres actifs"""
        try:
            query = self.session.query(LometaParametre).filter(
                LometaParametre.is_active == True
            )
            if categorie:
                query = query.filter(LometaParametre.categorie == categorie)
            return query.order_by(
                LometaParametre.categorie,
                LometaParametre.ordre_affichage
            ).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # ÉCRITURE
    # ============================================================
    
    def set_valeur(self, code: str, valeur: Any, utilisateur_id: int) -> Optional[LometaParametre]:
        """
        Met à jour la valeur d'un paramètre existant.
        
        Historise l'ancienne et la nouvelle valeur dans le journal d'audit.
        """
        try:
            param = self.get_parametre(code)
            if not param:
                raise ValueError(f"Paramètre '{code}' introuvable")
            
            ancienne_valeur = param.valeur
            nouvelle_valeur = str(valeur) if valeur is not None else None
            
            if ancienne_valeur == nouvelle_valeur:
                return param  # Pas de changement
            
            param.valeur = nouvelle_valeur
            param.updated_at = self.get_current_datetime()
            param.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="MODIFICATION",
                entite="Parametre",
                entite_id=param.id,
                entite_nom=param.code,
                champ_modifie="valeur",
                ancienne_valeur=str(ancienne_valeur),
                nouvelle_valeur=str(nouvelle_valeur),
                commentaire=f"Modification du paramètre {param.code}"
            )
            
            self.session.commit()
            return param
        except Exception as e:
            self.session.rollback()
            raise e
    
    def creer_parametre(self, data: Dict[str, Any], utilisateur_id: int) -> LometaParametre:
        """Crée un nouveau paramètre"""
        try:
            code = data.get('code')
            if not code:
                raise ValueError("Le code du paramètre est obligatoire")
            
            # Vérifier l'unicité
            existing = self.session.query(LometaParametre).filter(
                LometaParametre.code == code
            ).first()
            if existing:
                raise ValueError(f"Le paramètre '{code}' existe déjà")
            
            data['created_by'] = utilisateur_id
            data.setdefault('is_active', True)
            
            param = LometaParametre(**data)
            self.session.add(param)
            self.session.commit()
            return param
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # RACCOURCIS SPÉCIFIQUES
    # ============================================================
    
    def get_delai_prescription_recours_mois(self) -> int:
        """Retourne le délai de prescription des recours (en mois)"""
        return self.get_valeur('DELAI_PRESCRIPTION_RECOURS_MOIS', 24)
    
    def get_quotepart_defaut(self, type_beneficiaire: str) -> float:
        """Retourne la quote-part par défaut pour un type de bénéficiaire"""
        mapping = {
            'CLIENT': 'REPARTITION_DEFAUT_CLIENT',
            'COMPAGNIE': 'REPARTITION_DEFAUT_COMPAGNIE',
            'HONORAIRES': 'REPARTITION_DEFAUT_HONORAIRES',
            'COASSUREUR': 'REPARTITION_DEFAUT_COASSUREURS',
        }
        code = mapping.get(type_beneficiaire.upper())
        if not code:
            return 0.0
        return self.get_valeur(code, 0.0)
    
    def get_compte_comptable(self, code_compte: str) -> str:
        """Retourne un numéro de compte comptable depuis le référentiel"""
        return self.get_valeur(code_compte, '')