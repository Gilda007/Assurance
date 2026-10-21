"""
Service de gestion des expertises (Tome 4 du CDC)
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import shutil
import os
from pathlib import Path

from addons.sinistres.services.base_service import BaseService
from addons.sinistres.models.expertise import (
    LometaExpertise, LometaDocumentExpertise, LometaEvaluation, LometaRevisionEvaluation,
    LometaProvision, LometaMouvementProvision
)
from addons.sinistres.models.sinistre import LometaSinistre
from addons.Paramètres.models.models import User
from addons.sinistres.services.file_service import UPLOAD_ROOT, get_file_service
from addons.sinistres.models.expertise import LometaAvocat


class ExpertiseService(BaseService):
    """Service de gestion des expertises"""
    
    def __init__(self, session: Session = None):
        super().__init__(session)
    
    # ============================================================
    # ✅ RÉFÉRENTIEL TYPES DE MISSION (Tome 2)
    # ============================================================

    # ============================================================
    # ✅ RÉFÉRENTIEL TYPES DE MISSION (via lometa_referentiels)
    # ============================================================

    def get_types_mission(self, actifs_only: bool = True) -> List[dict]:
        """
        Récupère les types de mission depuis le référentiel générique (Tome 2).
        Retourne une liste de dicts prêts à l'emploi pour l'UI.
        """
        try:
            from addons.sinistres.models.referentiel import LometaReferentiel
            import json

            q = self.session.query(LometaReferentiel).filter(
                LometaReferentiel.famille == "types_mission",
                LometaReferentiel.is_active == True,
                LometaReferentiel.est_obsolete == False,
            )
            if actifs_only:
                q = q.filter(LometaReferentiel.est_actif == True)

            referentiels = q.all()

            UI_DEFAULTS = {
                "EXPERTISE":        {"prefixe_numero": "EXP", "couleur": "#2563eb"},
                "GARAGISTE":        {"prefixe_numero": "GAR", "couleur": "#ea580c"},
                "CONTRE_EXPERTISE": {"prefixe_numero": "CEX", "couleur": "#7c3aed"},
                "MEDICALE":         {"prefixe_numero": "MED", "couleur": "#0891b2"},
                "JUDICIAIRE":       {"prefixe_numero": "JUD", "couleur": "#dc2626"},
            }

            result = []
            for ref in referentiels:
                extra = {}
                if ref.donnees_supplementaires:
                    try:
                        extra = json.loads(ref.donnees_supplementaires)
                    except Exception:
                        extra = {}

                defaults = UI_DEFAULTS.get(ref.code, {"prefixe_numero": "EXP", "couleur": "#64748b"})

                result.append({
                    "code": ref.code,
                    "libelle": ref.libelle,
                    "description": ref.description,
                    "prefixe_numero": extra.get("prefixe_numero", defaults["prefixe_numero"]),
                    "couleur": extra.get("couleur", defaults["couleur"]),
                    "necessite_mission_parente": bool(extra.get("necessite_mission_parente", False)),
                    "type_mission_parente_code": extra.get("type_mission_parente_code"),
                    "ordre": extra.get("ordre", 99),
                    "est_actif": ref.est_actif,
                })

            # Tri par 'ordre' (champ extra) puis par libellé
            result.sort(key=lambda t: (t["ordre"], t["libelle"]))
            return result

        except Exception as e:
            self.session.rollback()
            raise e


    def get_type_mission_by_code(self, code: str) -> Optional[dict]:
        """Récupère un type de mission par son code depuis lometa_referentiels"""
        try:
            from addons.sinistres.models.referentiel import LometaReferentiel
            import json

            ref = self.session.query(LometaReferentiel).filter(
                LometaReferentiel.famille == "types_mission",
                LometaReferentiel.code == code,
                LometaReferentiel.is_active == True,
                LometaReferentiel.est_obsolete == False,
            ).first()

            if not ref:
                return None

            extra = {}
            if ref.donnees_supplementaires:
                try:
                    extra = json.loads(ref.donnees_supplementaires)
                except Exception:
                    extra = {}

            UI_DEFAULTS = {
                "EXPERTISE":        {"prefixe_numero": "EXP", "couleur": "#2563eb"},
                "GARAGISTE":        {"prefixe_numero": "GAR", "couleur": "#ea580c"},
                "CONTRE_EXPERTISE": {"prefixe_numero": "CEX", "couleur": "#7c3aed"},
                "MEDICALE":         {"prefixe_numero": "MED", "couleur": "#0891b2"},
                "JUDICIAIRE":       {"prefixe_numero": "JUD", "couleur": "#dc2626"},
            }
            defaults = UI_DEFAULTS.get(ref.code, {"prefixe_numero": "EXP", "couleur": "#64748b"})

            return {
                "code": ref.code,
                "libelle": ref.libelle,
                "description": ref.description,
                "prefixe_numero": extra.get("prefixe_numero", defaults["prefixe_numero"]),
                "couleur": extra.get("couleur", defaults["couleur"]),
                "necessite_mission_parente": bool(extra.get("necessite_mission_parente", False)),
                "type_mission_parente_code": extra.get("type_mission_parente_code"),
                "ordre": extra.get("ordre", 99),
                "est_actif": ref.est_actif,
            }

        except Exception as e:
            self.session.rollback()
            raise e

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
    #             expert = self.get_expert(data['expert_id'])
    #             if not expert:
    #                 raise ValueError("Expert non trouvé")
            
    #         # ✅ CORRECTION : Utiliser LometaExpertise au lieu de LometaSinistre
    #         numero = self.generate_numero("EXP", LometaExpertise, 'numero_mission')

    #         if 'date_mission' not in data or not data['date_mission']:
    #             raise ValueError("La date de mission est obligatoire")
            
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
        """
        Crée une mission d'expertise (expertise, garagiste, contre-expertise…).
        Les types de mission sont lus depuis le référentiel générique
        (lometa_referentiels, famille='types_mission').
        """
        try:
            # ----- Validations de base -----
            sinistre = self.session.query(LometaSinistre).filter(
                LometaSinistre.id == data.get('sinistre_id'),
                LometaSinistre.is_active == True
            ).first()
            if not sinistre:
                raise ValueError("Sinistre non trouvé")

            if not data.get('date_mission'):
                raise ValueError("La date de mission est obligatoire")
            if not data.get('date_echeance'):
                raise ValueError("La date d'échéance est obligatoire (EXP-004)")

            if data.get('expert_id'):
                expert = self.get_expert(data['expert_id'])
                if not expert:
                    raise ValueError("Expert non trouvé")
                if not expert.est_actif:
                    raise ValueError("L'expert sélectionné est inactif (EXP-003)")

            # ----- Type de mission via référentiel générique -----
            type_code = data.get('type_mission_code') or 'EXPERTISE'
            type_mission = self.get_type_mission_by_code(type_code)
            if not type_mission:
                raise ValueError(
                    f"Type de mission '{type_code}' introuvable dans le référentiel"
                )
            if not type_mission.get('est_actif', True):
                raise ValueError(f"Le type de mission '{type_code}' est désactivé")

            # ----- Validation contre-expertise -----
            parente = None
            if type_mission.get('necessite_mission_parente'):
                parent_id = data.get('mission_parente_id')
                if not parent_id:
                    raise ValueError(
                        f"Une mission de type '{type_mission['libelle']}' "
                        f"doit référencer une mission parente"
                    )

                parente = self.get_mission(parent_id)
                if not parente:
                    raise ValueError("Mission parente introuvable")
                if parente.sinistre_id != sinistre.id:
                    raise ValueError("La mission parente doit appartenir au même sinistre")

                # Contrainte de type parente définie dans le référentiel
                expected_parent_type = type_mission.get('type_mission_parente_code')
                if expected_parent_type and parente.type_mission_code != expected_parent_type:
                    raise ValueError(
                        f"La mission parente doit être de type '{expected_parent_type}'"
                    )

                # La parente doit avoir un rapport reçu/validé
                if parente.statut not in ("RAPPORT_RECU", "RAPPORT_REÇU", "VALIDE"):
                    raise ValueError(
                        "La mission parente doit avoir un rapport reçu avant contre-expertise"
                    )

                # Une seule contre-expertise active par parente
                existing = [c for c in (parente.contre_expertises or []) if c.is_active]
                if existing:
                    raise ValueError(
                        f"La mission {parente.numero_mission} a déjà une contre-expertise "
                        f"({existing[0].numero_mission})"
                    )

                # Motif obligatoire
                if not data.get('motif_contre_expertise'):
                    raise ValueError("Le motif de la contre-expertise est obligatoire")

            # ----- Numérotation dynamique depuis le référentiel -----
            numero = self.generate_numero(
                type_mission['prefixe_numero'] or "EXP",
                LometaExpertise,
                'numero_mission'
            )

            # ----- Création -----
            mission = LometaExpertise(
                numero_mission=numero,
                statut="CREEE",
                type_mission_code=type_mission['code'],
                **{
                    k: v for k, v in data.items()
                    if k not in ('type_mission_code')
                }
            )
            self.session.add(mission)
            self.session.flush()

            # ----- Audit -----
            commentaire = (
                f"Création de la mission {mission.numero_mission} "
                f"({type_mission['libelle']})"
            )
            if parente:
                commentaire += f" — contre-expertise de {parente.numero_mission}"

            self.log_audit(
                utilisateur_id=data.get('created_by'),
                action="CREATION",
                entite="Expertise",
                entite_id=mission.id,
                entite_nom=mission.numero_mission,
                commentaire=commentaire,
            )

            # ----- Mise à jour statut sinistre (Tome 3) -----
            if sinistre.statut not in ("EN_EXPERTISE", "CLOTURE"):
                sinistre.statut = "EN_EXPERTISE"
                sinistre.updated_at = datetime.utcnow()
                sinistre.updated_by = data.get('created_by')
            elif sinistre.statut == "CLOTURE" and type_mission['code'] == "CONTRE_EXPERTISE":
                # Réouverture implicite tracée (SIN-106)
                sinistre.statut = "EN_EXPERTISE"
                self.log_audit(
                    utilisateur_id=data.get('created_by'),
                    action="REOUVERTURE",
                    entite="Sinistre",
                    entite_id=sinistre.id,
                    entite_nom=sinistre.numero_sinistre,
                    commentaire=(
                        f"Réouverture implicite par contre-expertise "
                        f"{mission.numero_mission}"
                    ),
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

    def get_missions_parentes_possibles(self, sinistre_id: int,
                                    type_parent_code: str = "GARAGISTE") -> List[LometaExpertise]:
        """Retourne les missions éligibles comme parentes pour une contre-expertise"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.sinistre_id == sinistre_id,
                LometaExpertise.type_mission_code == type_parent_code,
                LometaExpertise.is_active == True,
                LometaExpertise.statut.in_(["RAPPORT_RECU", "RAPPORT_REÇU", "VALIDE"]),
                ~LometaExpertise.contre_expertises.any(LometaExpertise.is_active == True),
            ).order_by(LometaExpertise.date_mission.desc()).all()
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
            
            expert = self.get_expert(expert_id)
            if not expert:
                raise ValueError("Expert non trouvé")
            
            mission.expert_id = expert_id
            mission.expert_nom = expert.nom or expert.username
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
                commentaire=f"Affectation de l'expert {expert.nom} à la mission {mission.numero_mission}"
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
    # GESTION DES EXPERTS (référentiel)
    # ============================================================

    def get_experts(self) -> List:
        """Récupère tous les experts"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            return self.session.query(LometaExpert).filter(
                LometaExpert.is_active == True
            ).order_by(LometaExpert.nom).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_expert(self, expert_id: int):
        """Récupère un expert par son ID"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            return self.session.query(LometaExpert).filter(
                LometaExpert.id == expert_id,
                LometaExpert.is_active == True
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e


    def creer_expert(self, data: Dict[str, Any]):
        """Crée un nouvel expert"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            
            # Générer un code si absent
            if not data.get('code'):
                data['code'] = self.generate_numero("EXP", LometaExpert, 'code')
            
            # Vérifier l'unicité de l'agrément
            existant = self.session.query(LometaExpert).filter(
                LometaExpert.agrement == data.get('agrement'),
                LometaExpert.is_active == True
            ).first()
            if existant:
                raise ValueError(f"L'agrément {data.get('agrement')} existe déjà")
            
            expert = LometaExpert(**data)
            self.session.add(expert)
            self.session.commit()
            return expert
        except Exception as e:
            self.session.rollback()
            raise e


    def save_expert_photo(
        self,
        expert_code: str,
        source_path: str,
        compress: bool = True,
        max_width: int = 800,
    ) -> Optional[str]:
        """
        Copie une photo d'expert dans uploads/experts/<code>/
        
        Returns:
            Chemin relatif : 'experts/EXP-001/20260924_143022_photo.jpg'
        """
        try:
            if not os.path.exists(source_path):
                return None
            
            # Dossier destination
            safe_code = self._sanitize_filename(expert_code or "unknown")
            dest_dir = UPLOAD_ROOT / "experts" / safe_code
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Nom unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = Path(source_path).suffix.lower()
            dest_filename = f"{timestamp}_photo{ext}"
            dest_path = dest_dir / dest_filename
            
            # Copier ou compresser
            if compress and ext in {'.jpg', '.jpeg', '.png'}:
                self._compress_and_save(source_path, str(dest_path), max_width)
            else:
                shutil.copy2(source_path, dest_path)
            
            return f"experts/{safe_code}/{dest_filename}"
        
        except Exception as e:
            print(f"Erreur save_expert_photo: {e}")
            return None


    def update_expert(self, expert_id: int, data: Dict[str, Any]):
        """Met à jour un expert"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            expert = self.get_expert(expert_id)
            if not expert:
                return None
            
            for key, value in data.items():
                if hasattr(expert, key):
                    setattr(expert, key, value)
            
            self.session.commit()
            return expert
        except Exception as e:
            self.session.rollback()
            raise e


    def toggle_expert(self, expert_id: int, actif: bool, utilisateur_id: int) -> bool:
        """Active/désactive un expert"""
        try:
            expert = self.get_expert(expert_id)
            if not expert:
                return False
            
            expert.est_actif = actif
            expert.updated_by = utilisateur_id
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e


    def get_experts_by_domaine(self, domaine: str) -> List:
        """Récupère les experts d'un domaine donné"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            # JSON contains : on filtre côté Python (plus simple)
            experts = self.session.query(LometaExpert).filter(
                LometaExpert.is_active == True,
                LometaExpert.est_actif == True,
            ).all()
            return [e for e in experts if domaine in (e.domaines or [])]
        except Exception as e:
            self.session.rollback()
            raise e


    def get_experts_actifs(self) -> List:
        """Récupère tous les experts actifs"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            return self.session.query(LometaExpert).filter(
                LometaExpert.is_active == True,
                LometaExpert.est_actif == True,
            ).order_by(LometaExpert.nom).all()
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

    def get_documents_by_expertise(self, expertise_id: int) -> List[dict]:
        """Récupère tous les documents GED liés à une expertise"""
        try:
            from addons.sinistres.models.expertise import LometaDocumentExpertise
            from addons.sinistres.models.referentiel import LometaDocument
            
            liens = self.session.query(LometaDocumentExpertise).filter(
                LometaDocumentExpertise.expertise_id == expertise_id,
                LometaDocumentExpertise.is_active == True
            ).all()
            
            result = []
            for lien in liens:
                doc = self.session.query(LometaDocument).filter(
                    LometaDocument.id == lien.document_id
                ).first()
                if doc:
                    result.append({
                        'id': doc.id,
                        'nom_fichier': doc.nom_fichier,
                        'chemin_fichier': doc.chemin_fichier,
                        'type_document': doc.type_document,
                        'type_lien': lien.type_lien,
                        'taille': doc.taille,
                        'version': doc.version,
                        'created_at': doc.created_at.isoformat() if doc.created_at else None,
                    })
            return result
        except Exception as e:
            self.session.rollback()
            raise e

    def ajouter_document_expertise(
        self,
        expertise_id: int,
        document_id: int,
        type_lien: str,
        utilisateur_id: int
    ) -> bool:
        """Lie un document GED à une expertise"""
        try:
            from addons.sinistres.models.expertise import LometaDocumentExpertise
            
            lien = LometaDocumentExpertise(
                expertise_id=expertise_id,
                document_id=document_id,
                type_lien=type_lien,
                created_by=utilisateur_id
            )
            self.session.add(lien)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e

    def supprimer_document_expertise(self, document_expertise_id: int) -> bool:
        """Supprime la liaison document ↔ expertise"""
        try:
            from addons.sinistres.models.expertise import LometaDocumentExpertise
            lien = self.session.query(LometaDocumentExpertise).filter(
                LometaDocumentExpertise.id == document_expertise_id
            ).first()
            if lien:
                lien.is_active = False
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e

    def get_avocats(self, actifs_only: bool = True) -> List[dict]:
        """Récupère la liste des avocats"""
        try:
            from addons.sinistres.models.expertise import LometaAvocat
            query = self.session.query(LometaAvocat).filter(
                LometaAvocat.is_active == True
            )
            if actifs_only:
                query = query.filter(LometaAvocat.est_actif == True)
            
            return [
                {
                    'id': a.id,
                    'code': a.code,
                    'cabinet': a.cabinet,
                    'nom': a.nom,
                    'prenom': a.prenom,
                    'agrement': a.agrement,
                    'specialite': a.specialite,
                    'telephone': a.telephone,
                    'email': a.email,
                    'adresse': a.adresse,
                    'ville': a.ville,
                    'est_actif': a.est_actif,
                }
                for a in query.order_by(LometaAvocat.nom).all()
            ]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_avocat(self, avocat_id: int) -> Optional[dict]:
        """Récupère un avocat par ID"""
        try:
            from addons.sinistres.models.expertise import LometaAvocat
            a = self.session.query(LometaAvocat).filter(
                LometaAvocat.id == avocat_id,
                LometaAvocat.is_active == True
            ).first()
            if not a:
                return None
            return {
                'id': a.id,
                'code': a.code,
                'cabinet': a.cabinet,
                'nom': a.nom,
                'prenom': a.prenom,
                'agrement': a.agrement,
                'specialite': a.specialite,
                'telephone': a.telephone,
                'email': a.email,
                'adresse': a.adresse,
                'ville': a.ville,
                'est_actif': a.est_actif,
            }
        except Exception as e:
            self.session.rollback()
            raise e

    def creer_avocat(self, data: Dict[str, Any]) -> Optional['LometaAvocat']:
        """Crée un avocat dans le référentiel"""
        try:
            from addons.sinistres.models.expertise import LometaAvocat
            if not data.get('code'):
                data['code'] = self.generate_numero("AVO", LometaAvocat, 'code')
            
            avocat = LometaAvocat(**data)
            self.session.add(avocat)
            self.session.commit()
            return avocat
        except Exception as e:
            self.session.rollback()
            raise e

    def update_avocat(self, avocat_id: int, data: Dict[str, Any]) -> Optional['LometaAvocat']:
        """Met à jour un avocat"""
        try:
            from addons.sinistres.models.expertise import LometaAvocat
            avocat = self.session.query(LometaAvocat).filter(
                LometaAvocat.id == avocat_id
            ).first()
            if not avocat:
                return None
            for key, value in data.items():
                if hasattr(avocat, key):
                    setattr(avocat, key, value)
            self.session.commit()
            return avocat
        except Exception as e:
            self.session.rollback()
            raise e

    def toggle_avocat(self, avocat_id: int, actif: bool) -> bool:
        """Active/désactive un avocat"""
        try:
            from addons.sinistres.models.expertise import LometaAvocat
            avocat = self.session.query(LometaAvocat).filter(
                LometaAvocat.id == avocat_id
            ).first()
            if not avocat:
                return False
            avocat.est_actif = actif
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
        
    def get_experts_by_zone(self, zone: str) -> List:
        """Récupère les experts actifs intervenant dans une zone géographique"""
        try:
            from addons.sinistres.models.expertise import LometaExpert
            experts = self.session.query(LometaExpert).filter(
                LometaExpert.is_active == True,
                LometaExpert.est_actif == True,
            ).all()
            return [e for e in experts if zone in (e.zones or [])]
        except Exception as e:
            self.session.rollback()
            raise e

    def get_statistiques_expertises(self, sinistre_id: Optional[int] = None) -> dict:
        """Récupère les statistiques d'expertise (par sinistre ou globales)"""
        try:
            query = self.session.query(LometaExpertise).filter(
                LometaExpertise.is_active == True
            )
            if sinistre_id:
                query = query.filter(LometaExpertise.sinistre_id == sinistre_id)
            
            total = query.count()
            par_statut = {}
            for statut in ['CREEE', 'AFFECTEE', 'EN_COURS', 'RAPPORT_REÇU', 'VALIDE', 'ANNULE']:
                count = query.filter(LometaExpertise.statut == statut).count()
                if count > 0:
                    par_statut[statut] = count
            
            return {'total': total, 'par_statut': par_statut}
        except Exception as e:
            self.session.rollback()
            raise e

    def get_missions_parentes_possibles(self, sinistre_id: int,
                                        type_parent_code: str = "GARAGISTE") -> List[LometaExpertise]:
        """Retourne les missions éligibles comme parentes pour une contre-expertise"""
        try:
            return self.session.query(LometaExpertise).filter(
                LometaExpertise.sinistre_id == sinistre_id,
                LometaExpertise.type_mission_code == type_parent_code,
                LometaExpertise.is_active == True,
                LometaExpertise.statut.in_(["RAPPORT_RECU", "RAPPORT_REÇU", "VALIDE"]),
                ~LometaExpertise.contre_expertises.any(LometaExpertise.is_active == True),
            ).order_by(LometaExpertise.date_mission.desc()).all()
        except Exception as e:
            self.session.rollback()
            raise e

