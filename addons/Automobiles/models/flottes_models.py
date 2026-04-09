import enum

from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, Integer, JSON, DateTime, func, Text, Enum
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
    remise_flotte = Column(Integer, default=0.0)
    statut = Column(String(50), default="Actif") # Actif, Bloqué, Résilié
    is_active = Column(Boolean, default=True)

    total_rc = Column(Integer, default=0.0)
    total_dr = Column(Integer, default=0.0)
    total_vol = Column(Integer, default=0.0)
    total_vb = Column(Integer, default=0.0)
    total_in = Column(Integer, default=0.0)
    total_bris = Column(Integer, default=0.0)
    total_ar = Column(Integer, default=0.0)
    total_dta = Column(Integer, default=0.0)

    total_prime_nette = Column(Integer, default=0.0)
    
    # Calendrier du contrat
    date_debut = Column(Date)
    date_fin = Column(Date)
    
    # Notes
    observations = Column(Text)

    # --- RELATIONS ---
    
    # Lien vers le Client (Contact) - On utilise une string "Contact"
    owner_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    owner = relationship("Contact", back_populates="fleets")
    contract = relationship("Contrat", back_populates="fleet")

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

class AuditFlotteLog(Base):
    __tablename__ = 'audit_flotte_logs'
    
    # Permet de recharger le modèle sans erreur si déjà présent dans MetaData
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # ex: 'CREATE', 'UPDATE', 'JOIN_VEHICLES'
    module = Column(String(50), default="FLEETS")
    item_id = Column(Integer, nullable=False)    # ID de la flotte concernée
    
    # Stockage des changements au format JSON
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    
    # Traçabilité Réseau
    ip_local = Column(String(50), nullable=True)
    ip_public = Column(String(50), nullable=True)
    
    # Timestamp (Utilisation de timezone.utc pour Python 3.13+)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditFlotteLog(action={self.action}, fleet_id={self.item_id})>"