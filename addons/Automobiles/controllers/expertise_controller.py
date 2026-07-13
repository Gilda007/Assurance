# addons/Automobiles/controllers/expertise_controller.py
"""
Contrôleur pour la gestion des expertises automobiles
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from core import logger
from addons.Automobiles.models.expertise_models import Expertise, TypeExpertise, StatutExpertise


class ExpertiseController:
    """Contrôleur des expertises"""

    def __init__(self, session: Session, current_user_id: int = None):
        self.session = session
        self.current_user_id = current_user_id

    # ========================================================================
    # CRUD PRINCIPAL
    # ========================================================================

    def get_all(self, filters: Dict = None) -> List[Expertise]:
        """Récupère toutes les expertises avec filtres"""
        try:
            query = self.session.query(Expertise).options(
                joinedload(Expertise.sinistre)
            )

            if filters:
                if filters.get('statut'):
                    query = query.filter_by(statut=filters['statut'])
                if filters.get('type'):
                    query = query.filter_by(type=filters['type'])
                if filters.get('expert_id'):
                    query = query.filter_by(expert_id=filters['expert_id'])
                if filters.get('sinistre_id'):
                    query = query.filter_by(sinistre_id=filters['sinistre_id'])

            return query.order_by(Expertise.date_planifiee.desc()).all()

        except Exception as e:
            logger.error(f"Erreur récupération expertises: {e}")
            return []

    def get_by_id(self, expertise_id: int) -> Optional[Expertise]:
        """Récupère une expertise par son ID"""
        try:
            return self.session.query(Expertise).options(
                joinedload(Expertise.sinistre)
            ).filter_by(id=expertise_id).first()
        except Exception as e:
            logger.error(f"Erreur récupération expertise {expertise_id}: {e}")
            return None

    def get_by_sinistre(self, sinistre_id: int) -> Optional[Expertise]:
        """Récupère l'expertise d'un sinistre"""
        try:
            return self.session.query(Expertise).filter_by(
                sinistre_id=sinistre_id
            ).first()
        except Exception as e:
            logger.error(f"Erreur récupération expertise sinistre: {e}")
            return None

    def create_for_sinistre(self, sinistre_id: int, data: Dict = None) -> Optional[Expertise]:
        """
        Crée une expertise pour un sinistre
        
        Args:
            sinistre_id: ID du sinistre
            data: {
                'type': TypeExpertise,
                'statut': StatutExpertise,
                'expert_id': int,
                'expert_nom': str,
                'expert_specialite': str,
                'date_planifiee': datetime,
                'lieu': str
            }
        """
        try:
            data = data or {}
            
            expertise = Expertise(
                sinistre_id=sinistre_id,
                type=data.get('type', TypeExpertise.PRELIMINAIRE),
                statut=data.get('statut', StatutExpertise.PLANIFIEE),
                expert_id=data.get('expert_id'),
                expert_nom=data.get('expert_nom'),
                expert_specialite=data.get('expert_specialite'),
                date_planifiee=data.get('date_planifiee'),
                lieu=data.get('lieu'),
                created_by=self.current_user_id
            )

            self.session.add(expertise)
            self.session.commit()
            return expertise

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur création expertise: {e}")
            return None

    def update(self, expertise_id: int, data: Dict) -> bool:
        """Met à jour une expertise"""
        try:
            expertise = self.get_by_id(expertise_id)
            if not expertise:
                return False

            editable_fields = [
                'type', 'statut', 'expert_id', 'expert_nom',
                'expert_specialite', 'lieu', 'date_debut', 'date_fin',
                'estimation_vehicule', 'estimation_reparations',
                'estimation_valeur_residuelle', 'frais_expertise',
                'frais_deplacement', 'rapport_contenu', 'conclusion',
                'recommandations', 'dommages_carrosserie',
                'dommages_mecanique', 'dommages_equipements',
                'photos_urls', 'pieces_joites'
            ]

            for field in editable_fields:
                if field in data:
                    setattr(expertise, field, data[field])

            # Si expertise terminée, mettre à jour la date de fin
            if data.get('statut') == StatutExpertise.TERMINEE:
                expertise.date_fin = datetime.utcnow()

            expertise.updated_at = datetime.utcnow()
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur mise à jour expertise: {e}")
            return False

    def delete(self, expertise_id: int) -> bool:
        """Supprime une expertise"""
        try:
            expertise = self.get_by_id(expertise_id)
            if not expertise:
                return False

            self.session.delete(expertise)
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur suppression expertise: {e}")
            return False

    # ========================================================================
    # CHANGEMENT DE STATUT
    # ========================================================================

    def planifier(self, expertise_id: int) -> bool:
        """Planifie une expertise"""
        return self._changer_statut(expertise_id, StatutExpertise.PLANIFIEE)

    def demarrer(self, expertise_id: int) -> bool:
        """Démarre une expertise"""
        try:
            expertise = self.get_by_id(expertise_id)
            if not expertise:
                return False

            expertise.statut = StatutExpertise.EN_COURS
            expertise.date_debut = datetime.utcnow()
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur démarrage expertise: {e}")
            return False

    def terminer(self, expertise_id: int, data: Dict = None) -> bool:
        """Termine une expertise avec le rapport"""
        try:
            expertise = self.get_by_id(expertise_id)
            if not expertise:
                return False

            expertise.statut = StatutExpertise.TERMINEE
            expertise.date_fin = datetime.utcnow()

            if data:
                for key, value in data.items():
                    if hasattr(expertise, key):
                        setattr(expertise, key, value)

            # Mettre à jour l'estimation du sinistre
            if expertise.sinistre and data and data.get('estimation_reparations'):
                expertise.sinistre.estimation_finale = data['estimation_reparations']

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur finalisation expertise: {e}")
            return False

    def valider(self, expertise_id: int) -> bool:
        """Valide une expertise"""
        return self._changer_statut(expertise_id, StatutExpertise.VALIDEE)

    def rejeter(self, expertise_id: int) -> bool:
        """Rejette une expertise"""
        return self._changer_statut(expertise_id, StatutExpertise.REJETEE)

    def _changer_statut(self, expertise_id: int, nouveau_statut: StatutExpertise) -> bool:
        """Change le statut d'une expertise"""
        try:
            expertise = self.get_by_id(expertise_id)
            if not expertise:
                return False

            expertise.statut = nouveau_statut
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur changement statut expertise: {e}")
            return False

    # ========================================================================
    # STATISTIQUES
    # ========================================================================

    def get_stats(self) -> Dict:
        """Statistiques des expertises"""
        try:
            total = self.session.query(Expertise).count()

            by_status = {}
            for statut in StatutExpertise:
                count = self.session.query(Expertise).filter_by(statut=statut).count()
                if count > 0:
                    by_status[statut.value] = count

            by_type = {}
            for type_ in TypeExpertise:
                count = self.session.query(Expertise).filter_by(type=type_).count()
                if count > 0:
                    by_type[type_.value] = count

            # Montant total estimé des réparations
            total_reparations = self.session.query(
                func.sum(Expertise.estimation_reparations)
            ).scalar() or 0.0

            return {
                'total': total,
                'by_status': by_status,
                'by_type': by_type,
                'total_reparations': total_reparations,
                'moyenne_reparations': round(total_reparations / total if total > 0 else 0, 2)
            }

        except Exception as e:
            logger.error(f"Erreur statistiques expertises: {e}")
            return {
                'total': 0,
                'by_status': {},
                'by_type': {},
                'total_reparations': 0,
                'moyenne_reparations': 0
            }

    # ========================================================================
    # EXPORT
    # ========================================================================

    def to_dict(self, expertise: Expertise) -> Dict:
        """Convertit une expertise en dictionnaire pour export"""
        return {
            'id': expertise.id,
            'sinistre_id': expertise.sinistre_id,
            'numero_dossier': expertise.sinistre.numero_dossier if expertise.sinistre else None,
            'type': expertise.type.value if expertise.type else None,
            'statut': expertise.statut.value if expertise.statut else None,
            'expert_nom': expertise.expert_nom,
            'date_planifiee': expertise.date_planifiee.isoformat() if expertise.date_planifiee else None,
            'date_debut': expertise.date_debut.isoformat() if expertise.date_debut else None,
            'date_fin': expertise.date_fin.isoformat() if expertise.date_fin else None,
            'lieu': expertise.lieu,
            'estimation_vehicule': expertise.estimation_vehicule,
            'estimation_reparations': expertise.estimation_reparations,
            'estimation_valeur_residuelle': expertise.estimation_valeur_residuelle,
            'conclusion': expertise.conclusion,
            'created_at': expertise.created_at.isoformat() if expertise.created_at else None,
        }