# flottes_models.py - Version mise à jour

import enum

from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, Integer, JSON, DateTime, func, Text, Enum, Float
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
    assureur = Column(Integer, ForeignKey('automobile_compagnies.id'), nullable=True)
    type_gestion = Column(String(50))  # GLOBAL ou PAR_VEHICULE
    remise_flotte = Column(Float, default=0.0)  # Changé: Integer -> Float pour les pourcentages
    statut = Column(String(50), default="Actif")  # Actif, Bloqué, Résilié
    is_active = Column(Boolean, default=True)

    # ⭐ TOTAUX DES GARANTIES DANS LA FLOTTE (colonne PTTC)
    total_rc = Column(Float, default=0.0)      # Changé: Integer -> Float
    total_dr = Column(Float, default=0.0)
    total_vol = Column(Float, default=0.0)
    total_vb = Column(Float, default=0.0)
    total_in = Column(Float, default=0.0)
    total_bris = Column(Float, default=0.0)
    total_ar = Column(Float, default=0.0)
    total_dta = Column(Float, default=0.0)
    total_ipt = Column(Float, default=0.0)      # ⭐ NOUVEAU: Ajout de IPT manquant

    total_prime_nette = Column(Float, default=0.0)  # Changé: Integer -> Float
    
    # ⭐ NOUVEAU: PTTC total de la flotte (somme des PTTC des véhicules sélectionnés)
    total_pttc = Column(Float, default=0.0)
    
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
    compagnie = relationship("Compagnie", foreign_keys=[assureur], backref="fleets")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))

    # Lien vers les Véhicules - On utilise une string "Vehicle"
    vehicles = relationship("Vehicle", back_populates="fleet", cascade="all, delete-orphan")

    # ⭐ PROPRIÉTÉS CALCULÉES POUR LA FLOTTE
    @property
    def total_garanties(self):
        """Total de toutes les garanties de la flotte"""
        return sum([
            self.total_rc or 0,
            self.total_dr or 0,
            self.total_vol or 0,
            self.total_vb or 0,
            self.total_in or 0,
            self.total_bris or 0,
            self.total_ar or 0,
            self.total_dta or 0,
            self.total_ipt or 0
        ])
    
    @property
    def nombre_vehicules(self):
        """Nombre de véhicules dans la flotte"""
        return len(self.vehicles) if self.vehicles else 0
    
    @property
    def prime_moyenne_par_vehicule(self):
        """Prime moyenne par véhicule dans la flotte"""
        if self.nombre_vehicules > 0:
            return self.total_pttc / self.nombre_vehicules
        return 0
    
    @property
    def taux_remise_applique(self):
        """Taux de remise effectivement appliqué"""
        if self.total_garanties > 0:
            return ((self.total_garanties - self.total_pttc) / self.total_garanties) * 100
        return 0

    def recalculer_totaux_depuis_vehicules(self):
        """
        Recalcule tous les totaux de la flotte à partir des véhicules associés.
        Utilise les champs amt_fleet_*_val des véhicules.
        """
        if not self.vehicles:
            self.total_rc = 0
            self.total_dr = 0
            self.total_vol = 0
            self.total_vb = 0
            self.total_in = 0
            self.total_bris = 0
            self.total_ar = 0
            self.total_dta = 0
            self.total_ipt = 0
            self.total_pttc = 0
            return
        
        total_rc = 0
        total_dr = 0
        total_vol = 0
        total_vb = 0
        total_in = 0
        total_bris = 0
        total_ar = 0
        total_dta = 0
        total_ipt = 0
        total_pttc = 0
        
        for vehicle in self.vehicles:
            # Vérifier si le véhicule est actif et associé à cette flotte
            if vehicle.fleet_id == self.id and vehicle.is_active:
                total_rc += vehicle.amt_fleet_rc_val or 0
                total_dr += vehicle.amt_fleet_dr_val or 0
                total_vol += vehicle.amt_fleet_vol_val or 0
                total_vb += vehicle.amt_fleet_vb_val or 0
                total_in += vehicle.amt_fleet_in_val or 0
                total_bris += vehicle.amt_fleet_bris_val or 0
                total_ar += vehicle.amt_fleet_ar_val or 0
                total_dta += vehicle.amt_fleet_dta_val or 0
                total_ipt += vehicle.amt_fleet_ipt_val or 0
                total_pttc += vehicle.total_fleet_amount or 0
        
        self.total_rc = total_rc
        self.total_dr = total_dr
        self.total_vol = total_vol
        self.total_vb = total_vb
        self.total_in = total_in
        self.total_bris = total_bris
        self.total_ar = total_ar
        self.total_dta = total_dta
        self.total_ipt = total_ipt
        self.total_pttc = total_pttc

    def __repr__(self):
        return f"<Fleet(nom='{self.nom_flotte}', code='{self.code_flotte}', vehicles={self.nombre_vehicules})>"


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