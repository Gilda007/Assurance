"""
Service de gestion des référentiels (Tome 2 du CDC)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid
from typing import Optional, List, Dict, Any

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.referentiel import LometaReferentiel, LometaReferentielHistorique
from addons.sinistres.models.referentiel_data import  REFERENTIELS_INITIAUX


class ReferentielService(BaseService):
    """Service de gestion des référentiels"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # CRUD
    # ============================================================
    
    def creer_referentiel(self, data: Dict[str, Any]) -> LometaReferentiel:
        """Crée un nouveau référentiel"""
        referentiel = LometaReferentiel(
            date_effet=datetime.utcnow(),
            **data
        )
        
        self.session.add(referentiel)
        self.session.commit()
        
        return referentiel
    
    def get_referentiel(self, referentiel_id: int) -> Optional[LometaReferentiel]:
        """Récupère un référentiel par son ID"""
        return self.session.query(LometaReferentiel).filter(
            LometaReferentiel.id == referentiel_id,
            LometaReferentiel.is_active == True
        ).first()
    
    def get_referentiel_by_code(self, famille: str, code: str) -> Optional[LometaReferentiel]:
        """Récupère un référentiel par sa famille et son code"""
        return self.session.query(LometaReferentiel).filter(
            LometaReferentiel.famille == famille,
            LometaReferentiel.code == code,
            LometaReferentiel.est_actif == True,
            LometaReferentiel.is_active == True
        ).first()
    
    def get_referentiels_by_famille(self, famille: str) -> List[LometaReferentiel]:
        """Récupère tous les référentiels d'une famille"""
        return self.session.query(LometaReferentiel).filter(
            LometaReferentiel.famille == famille,
            LometaReferentiel.est_actif == True,
            LometaReferentiel.is_active == True
        ).order_by(LometaReferentiel.code).all()
    
    def update_referentiel(self, referentiel_id: int, data: Dict[str, Any]) -> Optional[LometaReferentiel]:
        """Met à jour un référentiel avec historisation"""
        referentiel = self.get_referentiel(referentiel_id)
        if not referentiel:
            return None
        
        # Enregistrer l'historique
        for key, value in data.items():
            if hasattr(referentiel, key) and getattr(referentiel, key) != value:
                ancienne = getattr(referentiel, key)
                
                historique = LometaReferentielHistorique(
                    referentiel_id=referentiel.id,
                    champ_modifie=key,
                    ancienne_valeur=str(ancienne) if ancienne else None,
                    nouvelle_valeur=str(value) if value else None,
                    modifie_par=data.get('updated_by'),
                    date_modification=datetime.utcnow()
                )
                self.session.add(historique)
                
                setattr(referentiel, key, value)
        
        referentiel.updated_at = datetime.utcnow()
        referentiel.updated_by = data.get('updated_by')
        
        self.session.commit()
        return referentiel
    
    def desactiver_referentiel(self, referentiel_id: int) -> bool:
        """Désactive un référentiel (suppression logique)"""
        referentiel = self.get_referentiel(referentiel_id)
        if not referentiel:
            return False
        
        referentiel.est_actif = False
        referentiel.is_active = False
        self.session.commit()
        return True
    
    # ============================================================
    # IMPORTS / EXPORTS
    # ============================================================
    
    def export_to_list(self, famille: str = None) -> List[Dict[str, Any]]:
        """
        Exporte les référentiels vers une liste de dictionnaires
        """
        query = self.session.query(LometaReferentiel).filter(
            LometaReferentiel.is_active == True,
            LometaReferentiel.est_actif == True
        )
        
        if famille:
            query = query.filter(LometaReferentiel.famille == famille)
        
        return [
            {
                'id': str(r.id),
                'famille': r.famille,
                'code': r.code,
                'libelle': r.libelle,
                'description': r.description,
                'date_effet': r.date_effet.isoformat() if r.date_effet else None,
                'date_fin': r.date_fin.isoformat() if r.date_fin else None,
                'valeur': r.valeur,
                'societe': r.societe,
                'branche': r.branche,
                'donnees_supplementaires': r.donnees_supplementaires
            }
            for r in query.all()
        ]
    
    def import_from_list(self, data_list: List[Dict[str, Any]], utilisateur_id: int) -> Dict[str, Any]:
        """
        Importe des référentiels depuis une liste de dictionnaires
        """
        result = {'crees': 0, 'mis_a_jour': 0, 'erreurs': []}
        
        for data in data_list:
            try:
                # Vérifier si le référentiel existe déjà
                existant = self.session.query(LometaReferentiel).filter(
                    LometaReferentiel.famille == data['famille'],
                    LometaReferentiel.code == data['code'],
                    LometaReferentiel.is_active == True
                ).first()
                
                if existant:
                    # Mettre à jour
                    data['updated_by'] = utilisateur_id
                    self.update_referentiel(existant.id, data)
                    result['mis_a_jour'] += 1
                else:
                    # Créer
                    data['created_by'] = utilisateur_id
                    self.creer_referentiel(data)
                    result['crees'] += 1
                    
            except Exception as e:
                result['erreurs'].append(f"{data.get('code', 'inconnu')}: {str(e)}")
        
        return result
    
    # ============================================================
    # DONNÉES INITIALES
    # ============================================================
    
    def init_donnees_initiales(self, utilisateur_id: int) -> Dict[str, Any]:
        """
        Initialise les données des référentiels à partir des données prédéfinies
        """
        result = {'crees': 0, 'mis_a_jour': 0, 'erreurs': []}
        
        for famille, items in REFERENTIELS_INITIAUX.items():
            for item in items:
                try:
                    # Vérifier si le référentiel existe déjà
                    existant = self.session.query(LometaReferentiel).filter(
                        LometaReferentiel.famille == famille,
                        LometaReferentiel.code == item['code'],
                        LometaReferentiel.is_active == True
                    ).first()
                    
                    if existant:
                        # Mettre à jour si nécessaire
                        if item.get('libelle') != existant.libelle or item.get('valeur') != existant.valeur:
                            existant.libelle = item.get('libelle', existant.libelle)
                            existant.description = item.get('description', existant.description)
                            existant.valeur = item.get('valeur', existant.valeur)
                            existant.updated_at = datetime.utcnow()
                            existant.updated_by = utilisateur_id
                            result['mis_a_jour'] += 1
                    else:
                        # Créer
                        referentiel = LometaReferentiel(
                            famille=famille,
                            date_effet=datetime.utcnow(),
                            created_by=utilisateur_id,
                            **item
                        )
                        self.session.add(referentiel)
                        result['crees'] += 1
                        
                except Exception as e:
                    result['erreurs'].append(f"{famille}/{item.get('code', 'inconnu')}: {str(e)}")
        
        self.session.commit()
        return result
