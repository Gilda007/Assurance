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
    chassis = Column(String(50), unique=False, nullable=False)
    zone = Column(String(1), nullable=False)
    marque = Column(String(50), nullable=False)
    categorie = Column(String(50), nullable=False)  # Changé de Integer à String
    modele = Column(String(50), nullable=False)
    annee = Column(Integer, nullable=False)
    energie = Column(String(20))
    usage = Column(String(50), nullable=False)
    places = Column(Integer, default=5)
    has_remorque = Column(Boolean, default=False)
    libele_tarif = Column(String(50), nullable=False)
    code_tarif = Column(String(50), nullable=True)  # Ajout du champ code_tarif

    # --- PROPRIÉTAIRE & FLOTTE ---
    owner_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    compagny_id = Column(Integer, ForeignKey('automobile_compagnies.id'), nullable=True)
    fleet_id = Column(Integer, ForeignKey('fleets.id'), nullable=True)
    tarif_id = Column(Integer, ForeignKey('automobile_tarifs.id'))
    
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
    amt_rc = Column(Float, default=0.0)  # Montant brut
    red_rc = Column(Float, default=0.0)  # Taux de réduction (%)
    amt_red_rc = Column(Float, default=0.0)  # Montant après réduction
    
    # Défense Recours
    check_dr = Column(Boolean, default=False)
    amt_dr = Column(Float, default=0.0)
    red_dr = Column(Float, default=0.0)
    amt_red_dr = Column(Float, default=0.0)
    
    # Vol
    check_vol = Column(Boolean, default=False)
    amt_vol = Column(Float, default=0.0)
    red_vol = Column(Float, default=0.0)
    amt_red_vol = Column(Float, default=0.0)
    
    # Vandalisme / VB
    check_vb = Column(Boolean, default=False)
    amt_vb = Column(Float, default=0.0)
    red_vb = Column(Float, default=0.0)
    amt_red_vb = Column(Float, default=0.0)
    
    # Incendie
    check_in = Column(Boolean, default=False)
    amt_in = Column(Float, default=0.0)
    red_in = Column(Float, default=0.0)
    amt_red_in = Column(Float, default=0.0)
    
    # Bris de Glace
    check_bris = Column(Boolean, default=False)
    amt_bris = Column(Float, default=0.0)
    red_bris = Column(Float, default=0.0)
    amt_red_bris = Column(Float, default=0.0)
    
    # Assistance Réparation
    check_ar = Column(Boolean, default=False)
    amt_ar = Column(Float, default=0.0)
    red_ar = Column(Float, default=0.0)
    amt_red_ar = Column(Float, default=0.0)
    
    # Dommages Tous Accidents (DTA)
    check_dta = Column(Boolean, default=False)
    amt_dta = Column(Float, default=0.0)
    red_dta = Column(Float, default=0.0)
    amt_red_dta = Column(Float, default=0.0)
    
    # Individuelle Personnes Transportées (IPT)
    check_ipt = Column(Boolean, default=False)
    amt_ipt = Column(Float, default=0.0)
    red_ipt = Column(Float, default=0.0)
    amt_red_ipt = Column(Float, default=0.0)
    
    # --- TRAÇABILITÉ & CLE ETRANGERES ---
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))
    is_active = Column(Boolean, default=True)

    # --- RELATIONS ---
    fleet = relationship("Fleet", back_populates="vehicles")
    owner = relationship("Contact", back_populates="vehicles")
    compagny = relationship("Compagnie", back_populates="vehicles")
    contracts = relationship("Contract", back_populates="vehicle")
    tarif = relationship("AutomobileTarif", back_populates="vehicles")
    
    # --- PROPRIÉTÉS CALCULÉES ---
    @property
    def total_guarantees_brut(self):
        """Total des montants bruts des garanties"""
        return sum([
            self.amt_rc or 0, self.amt_dr or 0, self.amt_vol or 0,
            self.amt_vb or 0, self.amt_in or 0, self.amt_bris or 0,
            self.amt_ar or 0, self.amt_dta or 0, self.amt_ipt or 0
        ])
    
    @property
    def total_guarantees_net(self):
        """Total des montants nets après réduction des garanties"""
        return sum([
            self.amt_red_rc or 0, self.amt_red_dr or 0, self.amt_red_vol or 0,
            self.amt_red_vb or 0, self.amt_red_in or 0, self.amt_red_bris or 0,
            self.amt_red_ar or 0, self.amt_red_dta or 0, self.amt_red_ipt or 0
        ])
    
    @property
    def total_reduction_amount(self):
        """Total des réductions appliquées"""
        return self.total_guarantees_brut - self.total_guarantees_net

    def __repr__(self):
        return f"<Vehicle(Immat={self.immatriculation}, Marque={self.marque})>"


class AuditVehicleLog(Base):
    __tablename__ = "audit_vehicle_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('utilisateurs.id'))
    action = Column(String(50))
    module = Column(String(50))
    item_id = Column(Integer)
    old_values = Column(Text)
    new_values = Column(Text)
    ip_public = Column(String(45))
    ip_local = Column(String(45))
    timestamp = Column(DateTime, default=datetime.now)
    
    user = relationship("User", backref="audit_logs")