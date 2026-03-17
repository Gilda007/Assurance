import enum

from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, Float, JSON, DateTime, func, Text, Enum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone

class Fleet(Base):
    __tablename__ = 'fleets'

    id = Column(Integer, primary_key=True)
    
    # Identification de la Flotte
    nom_flotte = Column(String(100), nullable=False)
    code_flotte = Column(String(50), unique=True, nullable=False)
    
    # Gestion & Assureur
    assureur = Column(String(100))
    type_gestion = Column(String(50))  # GLOBAL ou PAR_VEHICULE
    remise_flotte = Column(Float, default=0.0)
    statut = Column(String(50), default="Actif") # Actif, Bloqué, Résilié
    is_active = Column(Boolean, default=True)
    
    # Calendrier du contrat
    date_debut = Column(Date)
    date_fin = Column(Date)
    
    # Notes
    observations = Column(Text)

    # --- RELATIONS ---
    
    # Lien vers le Client (Contact) - On utilise une string "Contact"
    owner_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    owner = relationship("Contact", back_populates="fleets")
    contracts = relationship("Contract", back_populates="fleet")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))

    # Lien vers les Véhicules - On utilise une string "Vehicle"
    vehicles = relationship("Vehicle", back_populates="fleet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fleet(nom='{self.nom_flotte}', code='{self.code_flotte}')>"

