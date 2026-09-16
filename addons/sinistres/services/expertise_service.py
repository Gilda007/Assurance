"""
Service de gestion des expertises (Tome 4 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import shutil

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.expertise import (
    LometaExpertise, LometaDocumentExpertise, LometaEvaluation, LometaRevisionEvaluation,
    LometaProvision, LometaMouvementProvision
)
from addons.sinistres.models.sinistre import LometaSinistre
from addons.Paramètres.models.models import User


class ExpertiseService(BaseService):
    """Service de gestion des expertises"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # GESTION DES MISSIONS D'EXPERTISE
    # ============================================================
    
    # def creer_mission(self, data: Dict[str, Any]) -> LometaExpertise:
    #     """Crée une nouvelle mission d'expertise"""
    #     try:
    #         # Vérifier que le sinistre existe
    #         sinistre = self.session.query(LometaSinistre).filter(
    #             LometaSinistre.id == data.get('sinistre_id'),
    #             LometaSinistre.is_active == True
    #         ).first()
    #         if not sinistre:
    #             raise ValueError("Sinistre non trouvé")
            
    #         # Vérifier que l'expert existe
    #         if data.get('expert_id'):
    #             expert = self.get_user(data['expert_id'])
    #             if not expert:
    #                 raise ValueError("Expert non trouvé")
            
    #         # Générer le numéro de mission
    #         numero = self.generate_numero("EXP", LometaSinistre, 'numero_mission')
            
    #         mission = LometaExpertise(
    #             numero_mission=numero,
    #             statut="CREEE",
    #             **data
    #         )
            
    #         self.session.add(mission)
    #         self.session.flush()
            
    #         # Mettre à jour le statut du sinistre
    #         if sinistre.statut not in ["EN_EXPERTISE", "CLOTURE"]:
    #             sinistre.statut = "EN_EXPERTISE"
    #             sinistre.updated_at = datetime.utcnow()
    #             sinistre.updated_by = data.get('created_by')
            
    #         # Log d'audit
    #         self.log_audit(
    #             utilisateur_id=data.get('created_by'),
    #             action="CREATION",
    #             entite="Expertise",
    #             entite_id=mission.id,
    #             entite_nom=mission.numero_mission,
    #             commentaire=f"Création de la mission {mission.numero_mission} pour le sinistre {sinistre.numero_sinistre}"
    #         )
            
    #         self.session.commit()
    #         return mission
            
    #     except Exception as e:
    #         self.session.rollback()
    #         raise e

    def creer_mission(self, data: Dict[str, Any]) -> LometaExpertise:
        """Crée une nouvelle mission d'expertise"""
        try:
            # Vérifier que le sinistre existe
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == data.get('sinistre_id'),
                LometaSinistre.is_active == True
            ).first()
            if not sinistre:
                raise ValueError("Sinistre non trouvé")
            
            # Vérifier que l'expert existe
            if data.get('expert_id'):
                expert = self.get_user(data['expert_id'])
                if not expert:
                    raise ValueError("Expert non trouvé")
            
            # ✅ CORRECTION : Utiliser LometaExpertise au lieu de LometaSinistre
            numero = self.generate_numero("EXP", LometaExpertise, 'numero_mission')

            if 'date_mission' not in data or not data['date_mission']:
                raise ValueError("La date de mission est obligatoire")
            
            mission = LometaExpertise(
                numero_mission=numero,
                statut="CREEE",
                **data
            )
            
            self.session.add(mission)
            self.session.flush()
            
            # Mettre à jour le statut du sinistre
            if sinistre.statut not in ["EN_EXPERTISE", "CLOTURE"]:
                sinistre.statut = "EN_EXPERTISE"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            
            # Log d'audit
            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Expertise",
                entite_id=mission.id,
                entite_nom=mission.numero_mission,
                commentaire=f"Création de la mission {mission.numero_mission} pour le sinistre {sinistre.numero_sinistre}"
            )
            
            self.session.commit()
            return mission
            
        except Exception as e:
            self.session.rollback()
            raise e

    def get_mission(self, mission_id: int) -> Optional[LometaExpertise]:
        """Récupère une mission par son ID"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.id == mission_id,
                LometaExpertise.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_missions(self) -> List[LometaExpertise]:
        """Récupère toutes les missions d'expertise (tous sinistres)"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.is_active == True
            ).order_by(LometaExpertise.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_mission_by_numero(self, numero: str) -> Optional[LometaExpertise]:
        """Récupère une mission par son numéro"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.numero_mission == numero,
                LometaExpertise.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_missions_by_sinistre(self, sinistre_id: int) -> List[LometaExpertise]:
        """Récupère toutes les missions d'un sinistre"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.sinistre_id == sinistre_id,
                LometaExpertise.is_active == True
            ).order_by(LometaExpertise.created_at.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_missions_by_expert(self, expert_id: int) -> List[LometaExpertise]:
        """Récupère toutes les missions d'un expert"""
        try:
            # ✅ Correction : utiliser LometaExpertise au lieu de LometaSinistre
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.expert_id == expert_id,
                LometaExpertise.is_active == True
            ).order_by(LometaExpertise.date_echeance.asc()).all()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_mission(self, mission_id: int, data: Dict[str, Any]) -> Optional[LometaExpertise]:
        """Met à jour une mission d'expertise"""
        try:
            mission = self.get_mission(mission_id)
            if not mission:
                raise ValueError("Mission non trouvée")
            
            for key, value in data.items():
                if hasattr(mission, key) and getattr(mission, key) != value:
                    setattr(mission, key, value)
            
            mission.updated_at = datetime.utcnow()
            mission.updated_by = data.get('updated_by')
            
            self.session.commit()
            return mission
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def affecter_expert(self, mission_id: int, expert_id: int, utilisateur_id: int) -> Optional[LometaExpertise]:
        """Affecte un expert à une mission"""
        try:
            mission = self.get_mission(mission_id)
            if not mission:
                raise ValueError("Mission non trouvée")
            
            if mission.statut not in ["CREEE", "AFFECTEE"]:
                raise ValueError("Cette mission ne peut plus être affectée")
            
            expert = self.get_user(expert_id)
            if not expert:
                raise ValueError("Expert non trouvé")
            
            mission.expert_id = expert_id
            mission.expert_nom = expert.full_name or expert.username
            mission.statut = "AFFECTEE"
            mission.updated_at = datetime.utcnow()
            mission.updated_by = utilisateur_id
            
            # Log d'audit
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="AFFECTATION",
                entite="Expertise",
                entite_id=mission.id,
                entite_nom=mission.numero_mission,
                commentaire=f"Affectation de l'expert {expert.full_name} à la mission {mission.numero_mission}"
            )
            
            self.session.commit()
            return mission
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def demarrer_mission(self, mission_id: int, utilisateur_id: int) -> Optional[LometaExpertise]:
        """Démarre une mission (passage en EN_COURS)"""
        try:
            mission = self.get_mission(mission_id)
            if not mission:
                raise ValueError("Mission non trouvée")
            
            if mission.statut != "AFFECTEE":
                raise ValueError("Seule une mission affectée peut être démarrée")
            
            mission.statut = "EN_COURS"
            mission.date_mission = datetime.utcnow()
            mission.updated_at = datetime.utcnow()
            mission.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="DEMARRAGE",
                entite="Expertise",
                entite_id=mission.id,
                entite_nom=mission.numero_mission,
                commentaire=f"Démarrage de la mission {mission.numero_mission}"
            )
            
            self.session.commit()
            return mission
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # def deposer_rapport(self, mission_id: int, data: Dict[str, Any], utilisateur_id: int) -> Optional[LometaExpertise]:
    #     """Dépose un rapport d'expertise"""
    #     try:
    #         mission = self.get_mission(mission_id)
    #         if not mission:
    #             raise ValueError("Mission non trouvée")
            
    #         if mission.statut not in ["EN_COURS", "RAPPORT_REÇU"]:
    #             raise ValueError("La mission n'est pas en cours")
            
    #         if data.get('rapport_path'):
    #             mission.rapport_path = data['rapport_path']
    #         if data.get('rapport_contenu'):
    #             mission.rapport_contenu = data['rapport_contenu']
    #         if data.get('montant_estime'):
    #             mission.montant_estime = data['montant_estime']
            
    #         mission.statut = "RAPPORT_REÇU"
    #         mission.date_reception_rapport = datetime.utcnow()
    #         mission.updated_at = datetime.utcnow()
    #         mission.updated_by = utilisateur_id
            
    #         # Log d'audit
    #         self.log_audit(
    #             utilisateur_id=utilisateur_id,
    #             action="RAPPORT_DEPOSE",
    #             entite="Expertise",
    #             entite_id=mission.id,
    #             entite_nom=mission.numero_mission,
    #             commentaire=f"Dépôt du rapport pour la mission {mission.numero_mission}"
    #         )
            
    #         self.session.commit()
    #         return mission
            
    #     except Exception as e:
    #         self.session.rollback()
    #         raise e

    def deposer_rapport(self, mission_id: int, data: Dict[str, Any], utilisateur_id: int) -> Optional[LometaExpertise]:
        """Dépose un rapport d'expertise"""
        try:
            mission = self.get_mission(mission_id)
            if not mission:
                raise ValueError("Mission non trouvée")
            
            if mission.statut not in ["EN_COURS", "RAPPORT_REÇU"]:
                raise ValueError(f"La mission n'est pas en cours (statut: {mission.statut})")
            
            # Mettre à jour les données du rapport
            if data.get('rapport_contenu'):
                mission.rapport_contenu = data['rapport_contenu']
            if data.get('montant_estime'):
                mission.montant_estime = data['montant_estime']
            
            # ✅ Gérer les fichiers multiples
            files = data.get('files', [])
            if files:
                # Créer un dossier pour la mission si nécessaire
                import os
                from pathlib import Path
                
                # Dossier de stockage des rapports
                base_dir = Path("uploads/expertises")
                base_dir.mkdir(parents=True, exist_ok=True)
                
                # Dossier spécifique à la mission
                mission_dir = base_dir / f"mission_{mission_id}"
                mission_dir.mkdir(exist_ok=True)
                
                # Copier les fichiers
                saved_files = []
                for file_path in files:
                    if os.path.exists(file_path):
                        file_name = os.path.basename(file_path)
                        dest_path = mission_dir / file_name
                        shutil.copy2(file_path, dest_path)
                        saved_files.append(str(dest_path))
                
                # Stocker le chemin du premier fichier dans rapport_path
                if saved_files:
                    mission.rapport_path = str(mission_dir)
                    # Ajouter les fichiers dans les logs
                    self.log_audit(
                        utilisateur_id=utilisateur_id,
                        action="FICHIERS_JOINTS",
                        entite="Expertise",
                        entite_id=mission.id,
                        entite_nom=mission.numero_mission,
                        commentaire=f"{len(saved_files)} fichier(s) joint(s) pour la mission {mission.numero_mission}"
                    )
            
            mission.statut = "RAPPORT_REÇU"
            mission.date_reception_rapport = datetime.utcnow()
            mission.updated_at = datetime.utcnow()
            mission.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="RAPPORT_DEPOSE",
                entite="Expertise",
                entite_id=mission.id,
                entite_nom=mission.numero_mission,
                commentaire=f"Dépôt du rapport pour la mission {mission.numero_mission}"
            )
            
            self.session.commit()
            return mission
            
        except Exception as e:
            self.session.rollback()
            raise e

    def valider_mission(self, mission_id: int, utilisateur_id: int) -> Optional[LometaExpertise]:
        """Valide une mission d'expertise"""
        try:
            mission = self.get_mission(mission_id)
            if not mission:
                raise ValueError("Mission non trouvée")
            
            if mission.statut != "RAPPORT_REÇU":
                raise ValueError("Aucun rapport à valider")
            
            mission.statut = "VALIDE"
            mission.date_validation = datetime.utcnow()
            mission.valide_par = utilisateur_id
            mission.updated_at = datetime.utcnow()
            mission.updated_by = utilisateur_id
            
            # Mettre à jour le statut du sinistre
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == mission.sinistre_id,
                LometaSinistre.is_active == True
            ).first()
            if sinistre and sinistre.statut == "EN_EXPERTISE":
                sinistre.statut = "EN_EVALUATION"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = utilisateur_id
            
            self.log_audit(
                utilisateur_id=utilisateur_id,
                action="VALIDATION",
                entite="Expertise",
                entite_id=mission.id,
                entite_nom=mission.numero_mission,
                commentaire=f"Validation de la mission {mission.numero_mission}"
            )
            
            self.session.commit()
            return mission
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # GESTION DES DOCUMENTS D'EXPERTISE
    # ============================================================
    
    def ajouter_document(self, expertise_id: int, data: Dict[str, Any]) -> LometaDocumentExpertise:
        """Ajoute un document à une expertise"""
        try:
            expertise = self.get_mission(expertise_id)
            if not expertise:
                raise ValueError("Expertise non trouvée")
            
            document = LometaDocumentExpertise(
                expertise_id=expertise_id,
                **data
            )
            
            self.session.add(document)
            self.session.commit()
            return document
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_documents(self, expertise_id: int) -> List[LometaDocumentExpertise]:
        """Récupère tous les documents d'une expertise"""
        try:
            return self.session.query(LometaDocumentExpertise).filter(
                LometaDocumentExpertise.expertise_id == expertise_id,
                LometaDocumentExpertise.is_active == True
            ).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_sinistre(self, sinistre_id: int) -> Optional[LometaSinistre]:
        """Récupère un sinistre par son ID"""
        try:
            return self.session.query(LometaSinistre).filter(
                LometaSinistre.id == sinistre_id,
                LometaSinistre.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
    
    # ============================================================
    # STATISTIQUES
    # ============================================================
    
    def get_statistiques(self, expert_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques des expertises"""
        try:
            query = self.session.query(LometaExpertise).filter(LometaExpertise.is_active == True)
            
            if expert_id:
                query = query.filter(LometaExpertise.expert_id == expert_id)
            
            total = query.count()
            
            # Par statut
            par_statut = {}
            for statut in ['CREEE', 'AFFECTEE', 'EN_COURS', 'RAPPORT_REÇU', 'VALIDE', 'ANNULE']:
                count = query.filter(LometaExpertise.statut == statut).count()
                if count > 0:
                    par_statut[statut] = count
            
            # Délai moyen
            from sqlalchemy import func
            delai_moyen = query.filter(
                LometaExpertise.date_reception_rapport.isnot(None),
                LometaExpertise.date_mission.isnot(None)
            ).with_entities(
                func.avg(func.extract('epoch', LometaExpertise.date_reception_rapport - LometaExpertise.date_mission) / 86400)
            ).scalar()
            
            return {
                'total': total,
                'par_statut': par_statut,
                'delai_moyen_rapport': round(delai_moyen, 1) if delai_moyen else None
            }
        except Exception as e:
            self.session.rollback()
            raise e