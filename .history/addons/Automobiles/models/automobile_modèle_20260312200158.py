import enum

from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, Float, JSON, DateTime, func, Text, Enum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- IDENTIFICATION ---
    immatriculation = Column(String(20), unique=True, index=True, nullable=False)
    chassis = Column(String(50), unique=True, nullable=False)
    marque = Column(String(50))
    modele = Column(String(50))
    annee = Column(Integer)
    energie = Column(String(20))
    usage = Column(String(50))
    places = Column(Integer, default=5)
    has_remorque = Column(Boolean, default=False)

    # --- PROPRIÉTAIRE & FLOTTE ---
    owner_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    fleet_id = Column(Integer, ForeignKey('fleets.id'), nullable=True)
    
    # --- DATES & STATUT ---
    date_debut = Column(Date)
    date_fin = Column(Date)
    statut = Column(String(20), default="En Circulation")

    # --- RÉCAPITULATIF FINANCIER GLOBAL ---
    valeur_neuf = Column(Float, default=0.0)
    valeur_venale = Column(Float, default=0.0)
    prime_brute = Column(Float, default=0.0)
    reduction = Column(Float, default=0.0)
    prime_nette = Column(Float, default=0.0)
    prime_emise = Column(Float, default=0.0)

    # --- DÉTAIL DES GARANTIES (ÉTAT ET MONTANT) ---
    # RC
    check_rc = Column(Boolean, default=False)
    amt_rc = Column(Float, default=0.0)
    # Défense Recours
    check_dr = Column(Boolean, default=False)
    amt_dr = Column(Float, default=0.0)
    # Vol
    check_vol = Column(Boolean, default=False)
    amt_vol = Column(Float, default=0.0)
    # Vandalisme / VB
    check_vb = Column(Boolean, default=False)
    amt_vb = Column(Float, default=0.0)
    # Incendie
    check_in = Column(Boolean, default=False)
    amt_in = Column(Float, default=0.0)
    # Bris de Glace
    check_bris = Column(Boolean, default=False)
    amt_bris = Column(Float, default=0.0)
    # Accessoires / AR
    check_ar = Column(Boolean, default=False)
    amt_ar = Column(Float, default=0.0)
    # DTA
    check_dta = Column(Boolean, default=False)
    amt_dta = Column(Float, default=0.0)
    # IPT
    check_ipt = Column(Boolean, default=False)
    amt_ipt = Column(Float, default=0.0)
    
    # --- TRAÇABILITÉ & CLE ETRANGERES ---
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))
    is_active = Column(Boolean, default=True)

    # --- RELATIONS (Une seule définition par relation !) ---
    statut = Column(String(20), default="ACTIF") # ACTIF, EXPIRE, ATTENTE

    # Relation vers la flotte
    fleet = relationship("Fleet", back_populates="vehicles")
    owner = relationship("Contact", back_populates="vehicles")
    contracts = relationship("Contract", back_populates="vehicle")
    

    def __repr__(self):
        return f"<Vehicle(Immat={self.immatriculation}, Marque={self.marque})>"
    
