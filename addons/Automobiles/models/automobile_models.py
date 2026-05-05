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
    categorie = Column(String(50), nullable=False)
    modele = Column(String(50), nullable=False)
    annee = Column(Integer, nullable=False)
    energie = Column(String(20))
    usage = Column(String(50), nullable=False)
    places = Column(Integer, default=5)
    has_remorque = Column(Boolean, default=False)
    libele_tarif = Column(String(50), nullable=False)
    code_tarif = Column(String(50), nullable=True)

    # --- PROPRIÉTAIRE & FLOTTE ---
    owner_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    compagny_id = Column(Integer, ForeignKey('automobile_compagnies.id'), nullable=True)
    fleet_id = Column(Integer, ForeignKey('fleets.id'), nullable=True)
    tarif_id = Column(Integer, ForeignKey('automobile_tarifs.id'))
    
    # --- DATES & STATUT ---
    date_debut = Column(Date)
    date_fin = Column(Date)
    statut = Column(String(20), default="En Circulation")
    nbr_jour = Column(Integer, default=0)  # Nombre de jours de couverture

    # --- RÉCAPITULATIF FINANCIER GLOBAL ---
    valeur_neuf = Column(Float, default=0.0)
    valeur_venale = Column(Float, default=0.0)
    prime_brute = Column(Float, default=0.0)
    reduction = Column(Float, default=0.0)
    prime_nette = Column(Float, default=0.0)
    prime_emise = Column(Float, default=0.0)
    
    # --- FRAIS SUPPLÉMENTAIRES ---
    carte_rose = Column(Float, default=0.0)      # Carte rose
    accessoires = Column(Float, default=0.0)     # Accessoires
    tva = Column(Float, default=0.0)            # TVA (19.25%)
    fichier_asac = Column(Float, default=0.0)   # Fichier ASAC
    vignette = Column(Float, default=0.0)       # Vignette
    pttc = Column(Float, default=0.0)           # Prime Toute Taxe Comprise

    # --- DÉTAIL DES GARANTIES (ÉTAT ET MONTANT) ---
    # RC
    check_rc = Column(Boolean, default=False)
    amt_rc = Column(Float, default=0.0)      # Montant brut
    red_rc = Column(Float, default=0.0)      # Taux de réduction (%)
    amt_red_rc = Column(Float, default=0.0)  # Montant après réduction
    amt_val_red_rc = Column(Float, default=0.0)  # Valeur de la réduction en FCFA
    amt_fleet_rc_val = Column(Float, default=0.0)      # Montant RC dans la flotte
    
    # Défense Recours
    check_dr = Column(Boolean, default=False)
    amt_dr = Column(Float, default=0.0)
    red_dr = Column(Float, default=0.0)
    amt_red_dr = Column(Float, default=0.0)
    amt_val_red_dr = Column(Float, default=0.0)
    amt_fleet_dr_val = Column(Float, default=0.0)      # Montant DR dans la flotte
    
    # Vol
    check_vol = Column(Boolean, default=False)
    amt_vol = Column(Float, default=0.0)
    red_vol = Column(Float, default=0.0)
    amt_red_vol = Column(Float, default=0.0)
    amt_val_red_vol = Column(Float, default=0.0)
    amt_fleet_vol_val = Column(Float, default=0.0)     # Montant Vol dans la flotte
    
    # Vandalisme / VB
    check_vb = Column(Boolean, default=False)
    amt_vb = Column(Float, default=0.0)
    red_vb = Column(Float, default=0.0)
    amt_red_vb = Column(Float, default=0.0)
    amt_val_red_vb = Column(Float, default=0.0)
    amt_fleet_vb_val = Column(Float, default=0.0)      # Montant VB dans la flotte
    
    # Incendie
    check_in = Column(Boolean, default=False)
    amt_in = Column(Float, default=0.0)
    red_in = Column(Float, default=0.0)
    amt_red_in = Column(Float, default=0.0)
    amt_val_red_in = Column(Float, default=0.0)
    amt_fleet_in_val = Column(Float, default=0.0)      # Montant Incendie dans la flotte
    
    # Bris de Glace
    check_bris = Column(Boolean, default=False)
    amt_bris = Column(Float, default=0.0)
    red_bris = Column(Float, default=0.0)
    amt_red_bris = Column(Float, default=0.0)
    amt_val_red_bris = Column(Float, default=0.0)
    amt_fleet_bris_val = Column(Float, default=0.0)    # Montant Bris dans la flotte
    
    # Assistance Réparation
    check_ar = Column(Boolean, default=False)
    amt_ar = Column(Float, default=0.0)
    red_ar = Column(Float, default=0.0)
    amt_red_ar = Column(Float, default=0.0)
    amt_val_red_ar = Column(Float, default=0.0)
    amt_fleet_ar_val = Column(Float, default=0.0)      # Montant AR dans la flotte
    
    # Dommages Tous Accidents (DTA)
    check_dta = Column(Boolean, default=False)
    amt_dta = Column(Float, default=0.0)
    red_dta = Column(Float, default=0.0)
    amt_red_dta = Column(Float, default=0.0)
    amt_val_red_dta = Column(Float, default=0.0)
    amt_fleet_dta_val = Column(Float, default=0.0)     # Montant DTA dans la flotte
    
    # Individuelle Personnes Transportées (IPT)
    check_ipt = Column(Boolean, default=False)
    amt_ipt = Column(Float, default=0.0)
    red_ipt = Column(Float, default=0.0)
    amt_red_ipt = Column(Float, default=0.0)
    amt_val_red_ipt = Column(Float, default=0.0)
    amt_fleet_ipt_val = Column(Float, default=0.0)     # Montant IPT dans la flotte
    
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
    contract = relationship("Contrat", back_populates="vehicle", uselist=False)
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
        return sum([
            self.amt_val_red_rc or 0, self.amt_val_red_dr or 0, self.amt_val_red_vol or 0,
            self.amt_val_red_vb or 0, self.amt_val_red_in or 0, self.amt_val_red_bris or 0,
            self.amt_val_red_ar or 0, self.amt_val_red_dta or 0, self.amt_val_red_ipt or 0
        ])
    
    @property
    def total_fleet_amount(self):
        """Total des réductions appliquées"""
        return sum([
            self.amt_fleet_rc_val or 0, self.amt_fleet_dr_val or 0, self.amt_fleet_vol_val or 0,
            self.amt_fleet_vb_val or 0, self.amt_fleet_in_val or 0, self.amt_fleet_bris_val or 0,
            self.amt_fleet_ar_val or 0, self.amt_fleet_dta_val or 0, self.amt_fleet_ipt_val or 0
        ])
    
    @property
    def total_frais(self):
        """Total des frais supplémentaires"""
        return sum([
            self.carte_rose or 0, self.accessoires or 0, 
            self.tva or 0, self.fichier_asac or 0, self.vignette or 0
        ])
    
    @property
    def total_ttc(self):
        """Total TTC (Prime nette + tous frais)"""
        return (self.prime_nette or 0) + self.total_frais
    
    @property
    def total_original_amount(self):
        """Total des garanties originales (hors flotte)"""
        return sum([
            self.amt_rc or 0,
            self.amt_dr or 0,
            self.amt_vol or 0,
            self.amt_vb or 0,
            self.amt_in or 0,
            self.amt_bris or 0,
            self.amt_ar or 0,
            self.amt_dta or 0,
            self.amt_ipt or 0
        ])
    
    @property
    def total_fleet_reduction(self):
        """Différence entre montant original et montant flotte"""
        return self.total_original_amount - self.total_fleet_amount
    
    @property
    def fleet_reduction_percent(self):
        """Pourcentage de réduction appliqué dans la flotte"""
        if self.total_original_amount > 0:
            return (self.total_fleet_reduction / self.total_original_amount) * 100
        return 0
    
    @property
    def has_custom_fleet_guarantees(self):
        """Vérifie si le véhicule a des garanties personnalisées dans la flotte"""
        return any([
            self.amt_fleet_rc_val != self.amt_rc if self.amt_fleet_rc_val else False,
            self.amt_fleet_dr_val != self.amt_dr if self.amt_fleet_dr_val else False,
            self.amt_fleet_vol_val != self.amt_vol if self.amt_fleet_vol_val else False,
            self.amt_fleet_vb_val != self.amt_vb if self.amt_fleet_vb_val else False,
            self.amt_fleet_in_val != self.amt_in if self.amt_fleet_in_val else False,
            self.amt_fleet_bris_val != self.amt_bris if self.amt_fleet_bris_val else False,
            self.amt_fleet_ar_val != self.amt_ar if self.amt_fleet_ar_val else False,
            self.amt_fleet_dta_val != self.amt_dta if self.amt_fleet_dta_val else False,
            self.amt_fleet_ipt_val != self.amt_ipt if self.amt_fleet_ipt_val else False,
        ])
    
    def reset_fleet_guarantees(self):
        """Remet les garanties de la flotte aux valeurs originales"""
        self.amt_fleet_rc_val = self.amt_rc
        self.amt_fleet_dr_val = self.amt_dr
        self.amt_fleet_vol_val = self.amt_vol
        self.amt_fleet_vb_val = self.amt_vb
        self.amt_fleet_in_val = self.amt_in
        self.amt_fleet_bris_val = self.amt_bris
        self.amt_fleet_ar_val = self.amt_ar
        self.amt_fleet_dta_val = self.amt_dta
        self.amt_fleet_ipt_val = self.amt_ipt
    
    def get_fleet_guarantees_dict(self):
        """Retourne un dictionnaire des garanties de la flotte"""
        return {
            'rc': self.amt_fleet_rc_val or 0,
            'dr': self.amt_fleet_dr_val or 0,
            'vol': self.amt_fleet_vol_val or 0,
            'vb': self.amt_fleet_vb_val or 0,
            'in': self.amt_fleet_in_val or 0,
            'bris': self.amt_fleet_bris_val or 0,
            'ar': self.amt_fleet_ar_val or 0,
            'dta': self.amt_fleet_dta_val or 0,
            'ipt': self.amt_fleet_ipt_val or 0,
        }
    
    def get_original_guarantees_dict(self):
        """Retourne un dictionnaire des garanties originales"""
        return {
            'rc': self.amt_rc or 0,
            'dr': self.amt_dr or 0,
            'vol': self.amt_vol or 0,
            'vb': self.amt_vb or 0,
            'in': self.amt_in or 0,
            'bris': self.amt_bris or 0,
            'ar': self.amt_ar or 0,
            'dta': self.amt_dta or 0,
            'ipt': self.amt_ipt or 0,
        }

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