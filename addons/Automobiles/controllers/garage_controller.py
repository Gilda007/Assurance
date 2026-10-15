# addons/Automobiles/controllers/garage_controller.py
"""
Contrôleur pour la gestion des garages agréés
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from core import logger
from addons.Automobiles.models.garage_models import Garage, TypeGarage, StatutAgrement, Intervention


class GarageController:
    """Contrôleur des garages"""

    def __init__(self, session: Session, current_user_id: int = None):
        self.session = session
        self.current_user_id = current_user_id

    # ========================================================================
    # GESTION DES GARAGES
    # ========================================================================

    def get_all(self, filters: Dict = None) -> List[Garage]:
        """Récupère tous les garages avec filtres"""
        try:
            query = self.session.query(Garage)

            if filters:
                if filters.get('type'):
                    query = query.filter_by(type=filters['type'])
                if filters.get('ville'):
                    query = query.filter_by(ville=filters['ville'])
                if filters.get('statut'):
                    query = query.filter_by(agrement_statut=filters['statut'])
                if filters.get('est_agree'):
                    query = query.filter_by(agrement_statut=StatutAgrement.ACTIF)
                if filters.get('search'):
                    search = filters['search']
                    query = query.filter(
                        Garage.nom.contains(search) |
                        Garage.ville.contains(search) |
                        Garage.code.contains(search)
                    )

            return query.order_by(Garage.nom).all()

        except Exception as e:
            logger.error(f"Erreur récupération garages: {e}")
            return []

    def get_by_id(self, garage_id: int) -> Optional[Garage]:
        """Récupère un garage par son ID"""
        try:
            return self.session.query(Garage).filter_by(id=garage_id).first()
        except Exception as e:
            logger.error(f"Erreur récupération garage {garage_id}: {e}")
            return None

    def get_by_code(self, code: str) -> Optional[Garage]:
        """Récupère un garage par son code"""
        try:
            return self.session.query(Garage).filter_by(code=code).first()
        except Exception as e:
            logger.error(f"Erreur récupération garage par code: {e}")
            return None

    def create(self, data: Dict) -> Optional[Garage]:
        """
        Crée un nouveau garage
        
        Args:
            data: {
                'nom': str,
                'raison_sociale': str,
                'type': TypeGarage,
                'telephone': str,
                'email': str,
                'site_web': str,
                'adresse': str,
                'ville': str,
                'quartier': str,
                'coordonnees': str,
                'agrement_numero': str,
                'agrement_date_debut': datetime,
                'agrement_date_fin': datetime,
                'agrement_delivre_par': str,
                'specialites': list,
                'marques_agrees': list,
                'capacite_vehicules': int,
                'nombre_mecaniciens': int,
                'nombre_ponts': int,
                'equipements': list,
                'taux_horaire': float,
                'forfait_remorquage': float,
                'horaires': dict,
                'disponible_urgence': bool
            }
        """
        try:
            import time
            code = f"GAR-{int(time.time())}"

            garage = Garage(
                code=code,
                nom=data['nom'],
                raison_sociale=data.get('raison_sociale'),
                type=data.get('type', TypeGarage.GENERALISTE),
                telephone=data.get('telephone'),
                email=data.get('email'),
                site_web=data.get('site_web'),
                adresse=data.get('adresse'),
                ville=data.get('ville'),
                quartier=data.get('quartier'),
                coordonnees=data.get('coordonnees'),
                agrement_numero=data.get('agrement_numero'),
                agrement_statut=StatutAgrement.EN_ATTENTE,
                agrement_date_debut=data.get('agrement_date_debut'),
                agrement_date_fin=data.get('agrement_date_fin'),
                agrement_delivre_par=data.get('agrement_delivre_par'),
                specialites=json.dumps(data.get('specialites', [])),
                marques_agrees=json.dumps(data.get('marques_agrees', [])),
                capacite_vehicules=data.get('capacite_vehicules', 0),
                nombre_mecaniciens=data.get('nombre_mecaniciens', 0),
                nombre_ponts=data.get('nombre_ponts', 0),
                equipements=json.dumps(data.get('equipements', [])),
                taux_horaire=data.get('taux_horaire', 0.0),
                forfait_remorquage=data.get('forfait_remorquage', 0.0),
                horaires=json.dumps(data.get('horaires', {})),
                disponible_urgence=data.get('disponible_urgence', False),
                created_by=self.current_user_id
            )

            self.session.add(garage)
            self.session.commit()
            logger.info(f"Garage créé: {garage.nom} ({garage.code})")
            return garage

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur création garage: {e}")
            return None

    def update(self, garage_id: int, data: Dict) -> bool:
        """Met à jour un garage"""
        try:
            garage = self.get_by_id(garage_id)
            if not garage:
                return False

            editable_fields = [
                'nom', 'raison_sociale', 'type', 'telephone', 'email',
                'site_web', 'adresse', 'ville', 'quartier', 'coordonnees',
                'agrement_numero', 'agrement_date_debut', 'agrement_date_fin',
                'agrement_delivre_par', 'capacite_vehicules', 'nombre_mecaniciens',
                'nombre_ponts', 'taux_horaire', 'forfait_remorquage',
                'disponible_urgence'
            ]

            # Champs JSON
            json_fields = ['specialites', 'marques_agrees', 'equipements', 'horaires']

            for field in editable_fields:
                if field in data:
                    setattr(garage, field, data[field])

            for field in json_fields:
                if field in data:
                    setattr(garage, field, json.dumps(data[field]))

            garage.updated_at = datetime.utcnow()
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur mise à jour garage: {e}")
            return False

    def delete(self, garage_id: int) -> bool:
        """Supprime un garage (soft delete)"""
        try:
            garage = self.get_by_id(garage_id)
            if not garage:
                return False

            # Soft delete : désactiver l'agrément
            garage.agrement_statut = StatutAgrement.REVOQUE
            garage.nom = f"[SUPPRIMÉ] {garage.nom}"
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur suppression garage: {e}")
            return False

    # ========================================================================
    # AGRÉMENT
    # ========================================================================

    def valider_agrement(self, garage_id: int) -> bool:
        """Valide l'agrément d'un garage"""
        try:
            garage = self.get_by_id(garage_id)
            if not garage:
                return False

            garage.agrement_statut = StatutAgrement.ACTIF
            self.session.commit()
            logger.info(f"Agrément validé pour: {garage.nom}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur validation agrément: {e}")
            return False

    def suspendre_agrement(self, garage_id: int, motif: str = None) -> bool:
        """Suspend l'agrément d'un garage"""
        try:
            garage = self.get_by_id(garage_id)
            if not garage:
                return False

            garage.agrement_statut = StatutAgrement.SUSPENDU
            if motif:
                garage.notes = (garage.notes or "") + f"\n[SUSPENSION] {motif}"
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur suspension agrément: {e}")
            return False

    def revoquer_agrement(self, garage_id: int, motif: str = None) -> bool:
        """Révoque l'agrément d'un garage"""
        try:
            garage = self.get_by_id(garage_id)
            if not garage:
                return False

            garage.agrement_statut = StatutAgrement.REVOQUE
            if motif:
                garage.notes = (garage.notes or "") + f"\n[RÉVOCATION] {motif}"
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur révocation agrément: {e}")
            return False

    # ========================================================================
    # RECHERCHE
    # ========================================================================

    def get_garages_by_ville(self, ville: str) -> List[Garage]:
        """Récupère les garages dans une ville"""
        try:
            return self.session.query(Garage).filter(
                Garage.ville == ville,
                Garage.agrement_statut == StatutAgrement.ACTIF
            ).order_by(Garage.nom).all()
        except Exception as e:
            logger.error(f"Erreur récupération garages ville: {e}")
            return []

    def get_garages_by_specialite(self, specialite: str) -> List[Garage]:
        """Récupère les garages avec une spécialité donnée"""
        try:
            return self.session.query(Garage).filter(
                Garage.specialites.contains(specialite),
                Garage.agrement_statut == StatutAgrement.ACTIF
            ).all()
        except Exception as e:
            logger.error(f"Erreur récupération garages spécialité: {e}")
            return []

    def get_garages_proches(self, ville: str, rayon_km: int = 50) -> List[Garage]:
        """Récupère les garages proches d'une ville"""
        try:
            # Dans une vraie implémentation, on utiliserait des coordonnées GPS
            return self.session.query(Garage).filter(
                Garage.ville == ville,
                Garage.agrement_statut == StatutAgrement.ACTIF
            ).all()
        except Exception as e:
            logger.error(f"Erreur recherche garages proches: {e}")
            return []

    # ========================================================================
    # STATISTIQUES
    # ========================================================================

    def get_stats(self) -> Dict:
        """Statistiques des garages"""
        try:
            total = self.session.query(Garage).count()

            # Par statut d'agrément
            by_status = {}
            for statut in StatutAgrement:
                count = self.session.query(Garage).filter_by(
                    agrement_statut=statut
                ).count()
                if count > 0:
                    by_status[statut.value] = count

            # Par type
            by_type = {}
            for type_ in TypeGarage:
                count = self.session.query(Garage).filter_by(type=type_).count()
                if count > 0:
                    by_type[type_.value] = count

            # Par ville
            by_ville = {}
            results = self.session.query(
                Garage.ville,
                func.count(Garage.id)
            ).group_by(Garage.ville).all()
            for ville, count in results:
                if ville:
                    by_ville[ville] = count

            # Taux d'agrément
            agrees = by_status.get('actif', 0)

            return {
                'total': total,
                'agrees': agrees,
                'taux_agrement': round((agrees / total * 100) if total > 0 else 0, 1),
                'by_status': by_status,
                'by_type': by_type,
                'by_ville': by_ville
            }

        except Exception as e:
            logger.error(f"Erreur statistiques garages: {e}")
            return {
                'total': 0,
                'agrees': 0,
                'taux_agrement': 0,
                'by_status': {},
                'by_type': {},
                'by_ville': {}
            }

    # ========================================================================
    # EXPORT
    # ========================================================================

    def to_dict(self, garage: Garage) -> Dict:
        """Convertit un garage en dictionnaire pour export"""
        return {
            'id': garage.id,
            'code': garage.code,
            'nom': garage.nom,
            'raison_sociale': garage.raison_sociale,
            'type': garage.type.value if garage.type else None,
            'telephone': garage.telephone,
            'email': garage.email,
            'adresse': garage.adresse,
            'ville': garage.ville,
            'quartier': garage.quartier,
            'agrement_numero': garage.agrement_numero,
            'agrement_statut': garage.agrement_statut.value if garage.agrement_statut else None,
            'agrement_date_debut': garage.agrement_date_debut.isoformat() if garage.agrement_date_debut else None,
            'agrement_date_fin': garage.agrement_date_fin.isoformat() if garage.agrement_date_fin else None,
            'capacite_vehicules': garage.capacite_vehicules,
            'nombre_mecaniciens': garage.nombre_mecaniciens,
            'taux_horaire': garage.taux_horaire,
            'note_moyenne': garage.note_moyenne,
            'disponible_urgence': garage.disponible_urgence,
            'created_at': garage.created_at.isoformat() if garage.created_at else None,
        }


# ========================================================================
# CONTRÔLEUR DES INTERVENTIONS
# ========================================================================

class InterventionController:
    """Contrôleur des interventions"""

    def __init__(self, session: Session, current_user_id: int = None):
        self.session = session
        self.current_user_id = current_user_id

    def get_all(self, filters: Dict = None) -> List[Intervention]:
        """Récupère toutes les interventions"""
        try:
            query = self.session.query(Intervention).options(
                joinedload(Intervention.garage),
                joinedload(Intervention.vehicule),
                joinedload(Intervention.sinistre)
            )

            if filters:
                if filters.get('garage_id'):
                    query = query.filter_by(garage_id=filters['garage_id'])
                if filters.get('vehicule_id'):
                    query = query.filter_by(vehicule_id=filters['vehicule_id'])
                if filters.get('sinistre_id'):
                    query = query.filter_by(sinistre_id=filters['sinistre_id'])
                if filters.get('statut'):
                    query = query.filter_by(statut=filters['statut'])

            return query.order_by(Intervention.date_debut.desc()).all()

        except Exception as e:
            logger.error(f"Erreur récupération interventions: {e}")
            return []

    def get_by_id(self, intervention_id: int) -> Optional[Intervention]:
        """Récupère une intervention par son ID"""
        try:
            return self.session.query(Intervention).options(
                joinedload(Intervention.garage),
                joinedload(Intervention.vehicule)
            ).filter_by(id=intervention_id).first()
        except Exception as e:
            logger.error(f"Erreur récupération intervention {intervention_id}: {e}")
            return None

    def create(self, data: Dict) -> Optional[Intervention]:
        """
        Crée une nouvelle intervention
        
        Args:
            data: {
                'garage_id': int,
                'vehicule_id': int,
                'sinistre_id': int (optional),
                'type_intervention': str,
                'description': str,
                'date_debut': datetime,
                'montant_devis': float,
                'pieces_remplacees': list,
                'main_d_oeuvre': float
            }
        """
        try:
            intervention = Intervention(
                garage_id=data['garage_id'],
                vehicule_id=data['vehicule_id'],
                sinistre_id=data.get('sinistre_id'),
                type_intervention=data.get('type_intervention'),
                description=data.get('description'),
                date_debut=data.get('date_debut', datetime.utcnow()),
                montant_devis=data.get('montant_devis', 0.0),
                pieces_remplacees=json.dumps(data.get('pieces_remplacees', [])),
                main_d_oeuvre=data.get('main_d_oeuvre', 0.0),
                statut='en_attente'
            )

            self.session.add(intervention)
            self.session.commit()
            return intervention

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur création intervention: {e}")
            return None

    def update(self, intervention_id: int, data: Dict) -> bool:
        """Met à jour une intervention"""
        try:
            intervention = self.get_by_id(intervention_id)
            if not intervention:
                return False

            editable_fields = [
                'type_intervention', 'description', 'date_debut', 'date_fin',
                'montant_devis', 'montant_final', 'pieces_remplacees',
                'main_d_oeuvre', 'statut'
            ]

            for field in editable_fields:
                if field in data:
                    if field in ['pieces_remplacees'] and isinstance(data[field], list):
                        setattr(intervention, field, json.dumps(data[field]))
                    else:
                        setattr(intervention, field, data[field])

            if data.get('statut') == 'terminee':
                intervention.date_fin = datetime.utcnow()

            intervention.updated_at = datetime.utcnow()
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur mise à jour intervention: {e}")
            return False

    def valider_intervention(self, intervention_id: int) -> bool:
        """Valide une intervention"""
        try:
            intervention = self.get_by_id(intervention_id)
            if not intervention:
                return False

            intervention.statut = 'terminee'
            intervention.date_fin = datetime.utcnow()
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur validation intervention: {e}")
            return False