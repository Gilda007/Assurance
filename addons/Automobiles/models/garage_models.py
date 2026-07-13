# addons/Automobiles/models/garage.py
"""
Modèles pour la gestion des garages agréés
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from core.database import Base


class TypeGarage(str, enum.Enum):
    """Types de garages"""
    GENERALISTE = "generaliste"
    SPECIALISE = "specialise"
    CARROSSERIE = "carrosserie"
    MECANIQUE = "mecanique"
    ELECTRONIQUE = "electronique"
    PNEUS = "pneus"
    AGREE = "agree"


class StatutAgrement(str, enum.Enum):
    """Statuts d'agrément"""
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    EXPIRE = "expire"
    REVOQUE = "revogue"
    EN_ATTENTE = "en_attente"


class Garage(Base):
    """Modèle des garages"""
    __tablename__ = "garages"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    
    # Identité
    nom = Column(String(255), nullable=False)
    raison_sociale = Column(String(255))
    type = Column(Enum(TypeGarage), default=TypeGarage.GENERALISTE)
    
    # Contact
    telephone = Column(String(50))
    email = Column(String(255))
    site_web = Column(String(255))
    
    # Adresse
    adresse = Column(String(255))
    ville = Column(String(100))
    pays = Column(String(50), default="Cameroun")
    quartier = Column(String(100))
    coordonnees = Column(String(100))  # GPS
    
    # Agrément
    agrement_numero = Column(String(50))
    agrement_statut = Column(Enum(StatutAgrement), default=StatutAgrement.EN_ATTENTE)
    agrement_date_debut = Column(DateTime)
    agrement_date_fin = Column(DateTime)
    agrement_delivre_par = Column(String(255))
    
    # Spécialités
    specialites = Column(Text)  # JSON
    marques_agrees = Column(Text)  # JSON
    
    # Capacités
    capacite_vehicules = Column(Integer, default=0)
    nombre_mecaniciens = Column(Integer, default=0)
    nombre_ponts = Column(Integer, default=0)
    
    # Équipements
    equipements = Column(Text)  # JSON
    
    # Tarifs
    taux_horaire = Column(Float, default=0.0)
    forfait_remorquage = Column(Float, default=0.0)
    
    # Évaluation
    note_moyenne = Column(Float, default=0.0)
    nombre_avis = Column(Integer, default=0)
    
    # Disponibilité
    horaires = Column(Text)  # JSON
    disponible_urgence = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("utilisateurs.id"))
    
    # Relations
    interventions = relationship("Intervention", back_populates="garage")
    
    def __repr__(self):
        return f"<Garage {self.code} - {self.nom}>"
    
    @property
    def est_agree(self):
        return self.agrement_statut == StatutAgrement.ACTIF
    
    @property
    def est_disponible(self):
        return self.est_agree and self.disponible_urgence


class Intervention(Base):
    """Interventions réalisées dans les garages"""
    __tablename__ = "interventions_auto"
    
    id = Column(Integer, primary_key=True, index=True)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)
    sinistre_id = Column(Integer, ForeignKey("sinistres_auto.id"), nullable=True)
    vehicule_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    # Détails
    type_intervention = Column(String(50))
    description = Column(Text)
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    
    # Devis
    devis_url = Column(String(255))
    montant_devis = Column(Float, default=0.0)
    montant_final = Column(Float, default=0.0)
    
    # Pièces
    pieces_remplacees = Column(Text)  # JSON
    main_d_oeuvre = Column(Float, default=0.0)
    
    # Statut
    statut = Column(String(50), default="en_attente")
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    garage = relationship("Garage", back_populates="interventions")
    vehicule = relationship("Vehicle", back_populates="interventions")