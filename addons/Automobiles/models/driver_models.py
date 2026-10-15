# addons/Automobiles/models/driver_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Driver(Base):
    """Modèle pour les chauffeurs"""
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True)
    
    # --- IDENTITÉ ---
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    date_naissance = Column(Date)
    nationalite = Column(String(100))
    
    # --- COORDONNÉES ---
    telephone = Column(String(50))
    email = Column(String(100))
    adresse = Column(Text)
    ville = Column(String(100))
    
    # --- PERMIS DE CONDUIRE ---
    cat_permis = Column(String(20), nullable=False)
    num_permis = Column(String(100), nullable=False)
    date_permis = Column(Date)
    
    # --- INFORMATIONS SPÉCIFIQUES CHAUFFEUR ---
    code_chauffeur = Column(String(50), unique=True)
    specialite = Column(String(100))  # Transport de personnes, marchandises, etc.
    annees_experience = Column(Integer, default=0)
    notes = Column(Text)
    
    # --- RELATION AVEC LE SOUSCRIPTEUR ---
    subscriber_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    subscriber = relationship("Contact", back_populates="drivers")
    
    # --- RELATION AVEC LES VÉHICULES ---
    vehicles = relationship("Vehicle", back_populates="driver", foreign_keys="[Vehicle.driver_id]")
    
    # --- RELATION AVEC LES CONTRATS ---
    contract_id = Column(Integer, ForeignKey('contrats.id'), nullable=True)
    contract = relationship("Contrat", back_populates="drivers")
    
    # --- TRAÇABILITÉ ---
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    
    def __repr__(self):
        return f"<Driver(id={self.id}, nom={self.nom})>"
    
    def to_api_dict(self):
        """Convertit en dictionnaire pour l'API"""
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance.strftime("%Y-%m-%d") if self.date_naissance else None,
            "nationalite": self.nationalite,
            "telephone": self.telephone,
            "email": self.email,
            "adresse": self.adresse,
            "ville": self.ville,
            "cat_permis": self.cat_permis,
            "num_permis": self.num_permis,
            "date_permis": self.date_permis.strftime("%Y-%m-%d") if self.date_permis else None,
            "code_chauffeur": self.code_chauffeur,
            "specialite": self.specialite,
            "annees_experience": self.annees_experience,
            "subscriber_id": self.subscriber_id
        }