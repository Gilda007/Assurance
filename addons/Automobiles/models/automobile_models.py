import enum

from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, Float, JSON, DateTime, func, Text, Enum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError, OperationalError


class VehicleCategory(enum.Enum):
    """Catégorie du véhicule (section 4.2)"""
    VEHICULE_TOURISME_PP = "VP01"
    TRANSPORT_PROPRE_COMPTE = "VP02"
    TRANSPORT_PUBLIC_MARCHANDISES = "VP03"
    TRANSPORT_PUBLIC_VOYAGEURS = "VP04"
    VEHICULE_2_3_ROUES = "VP05"
    VEHICULE_GARAGISTES = "VP06"
    VEHICULE_AUTO_ECOLE = "VP07"
    VEHICULE_LOCATION = "VP08"
    ENGIN_CHANTIER = "VP09"
    VEHICULES_SPECIAUX = "VP10"
    CATEGORIE_11 = "VP11"
    VEHICULE_TOURISME_PM = "VP12"

class VehicleGenre(enum.Enum):
    """Genre du véhicule (section 4.3)"""
    CAMION = "GV01"
    CAMIONNETTE = "GV02"
    CYCLOMOTEUR = "GV03"
    VOITURE = "GV04"
    ENGINS_CHANTIERS = "GV05"
    CAR = "GV06"
    FOURGONNETTE = "GV07"
    REMORQUE = "GV08"
    SCOOTER = "GV09"
    SEMI_REMORQUE = "GV10"
    TRACTEUR_AGRICOLE = "GV11"
    TRACTEUR_ROUTIER = "GV12"

class VehicleType(enum.Enum):
    """Type du véhicule (section 4.4)"""
    AMBULANCE = "TV01"
    AUTO_CAR = "TV02"
    CORBIARD = "TV03"
    MINI_CAR = "TV04"
    TAXI_COMMUNAUX = "TV05"
    TAXI_URBAIN = "TV06"
    VEHICULE_AUTO_ECOLE = "TV07"
    VEHICULE_SERVICE_PUBLIC = "TV08"
    VEHICULE_TOURISME = "TV09"
    VEHICULE_PARTICULIER = "TV10"
    VEHICULE_UTILITAIRE = "TV11"
    VOITURE_LOCATION = "TV12"
    CYCLOMOTEUR = "TV13"

class VehicleUsage(enum.Enum):
    """Usage du véhicule (section 4.5)"""
    PROMENADE_AFFAIRE = "UV01"
    TRANSPORT_PROPRE_COMPTE = "UV02"
    TRANSPORT_PRIVE_VOYAGEURS = "UV03"
    TRANSPORT_PUBLIC_MARCHANDISES = "UV04"
    TRANSPORT_PUBLIC_VOYAGEURS = "UV05"
    VEHICULES_AUTO_ECOLE = "UV06"
    VEHICULES_LOCATION = "UV07"
    VEHICULES_SPECIAUX = "UV08"
    ENGIN_CHANTIER = "UV09"
    VEHICULE_MOTORISE_2_3_ROUES = "UV10"

class VehicleEnergy(enum.Enum):
    """Énergie du véhicule (section 4.6)"""
    ESSENCE = "SEE"
    DIESEL = "SED"
    ELECTRIQUE = "SEE"
    HYBRIDE = "SEHY"

class CirculationZone(enum.Enum):
    """Zone de circulation (section 4.7)"""
    ZONE_A = "A"
    ZONE_B = "B"
    ZONE_C = "C"


# ============================================
# 2. DÉFINITION DES TABLES DE RÉFÉRENCE
# ============================================

class VehicleCategoryRef(Base):
    """Catégories de véhicules (référentiel)"""
    __tablename__ = 'vehicle_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VehicleGenreRef(Base):
    """Genres de véhicules (référentiel)"""
    __tablename__ = 'vehicle_genres'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VehicleTypeRef(Base):
    """Types de véhicules (référentiel)"""
    __tablename__ = 'vehicle_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VehicleUsageRef(Base):
    """Usages de véhicules (référentiel)"""
    __tablename__ = 'vehicle_usages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VehicleEnergyRef(Base):
    """Énergies de véhicules (référentiel)"""
    __tablename__ = 'vehicle_energies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class VehicleZoneRef(Base):
    """Zones de circulation (référentiel)"""
    __tablename__ = 'vehicle_zones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(5), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# ============================================
# 3. DÉFINITION DES TABLES DE GARANTIES (AVANT VEHICLE)
# ============================================

class VehicleGuarantee(Base):
    """Garanties principales du véhicule (Montants bruts)"""
    __tablename__ = 'vehicle_guarantees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
    rc = Column(Float, default=0.0)
    dr = Column(Float, default=0.0)
    vol = Column(Float, default=0.0)
    vb = Column(Float, default=0.0)
    ipt = Column(Float, default=0.0)
    bris = Column(Float, default=0.0)
    ar = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    in_garantie = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # La relation sera ajoutée après la définition de Vehicle
    vehicle = relationship("Vehicle", back_populates="guarantees", foreign_keys=[vehicle_id])


class VehicleGuaranteeReduction(Base):
    """Garanties avec réduction appliquée"""
    __tablename__ = 'vehicle_guarantee_reductions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
    rc = Column(Float, default=0.0)
    dr = Column(Float, default=0.0)
    vol = Column(Float, default=0.0)
    vb = Column(Float, default=0.0)
    ipt = Column(Float, default=0.0)
    bris = Column(Float, default=0.0)
    ar = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    in_garantie = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    vehicle = relationship("Vehicle", back_populates="guarantee_reductions", foreign_keys=[vehicle_id])


class VehicleGuaranteeRate(Base):
    """Taux des garanties"""
    __tablename__ = 'vehicle_guarantee_rates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
    rc = Column(Float, default=0.0)
    dr = Column(Float, default=0.0)
    vol = Column(Float, default=0.0)
    vb = Column(Float, default=0.0)
    ipt = Column(Float, default=0.0)
    bris = Column(Float, default=0.0)
    ar = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    in_garantie = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    vehicle = relationship("Vehicle", back_populates="guarantee_rates", foreign_keys=[vehicle_id])


class VehicleGuaranteeOption(Base):
    """Options des garanties (Checkbox)"""
    __tablename__ = 'vehicle_guarantee_options'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
    rc = Column(Boolean, default=False)
    dr = Column(Boolean, default=False)
    vol = Column(Boolean, default=False)
    vb = Column(Boolean, default=False)
    ipt = Column(Boolean, default=False)
    bris = Column(Boolean, default=False)
    ar = Column(Boolean, default=False)
    dta = Column(Boolean, default=False)
    in_garantie = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    vehicle = relationship("Vehicle", back_populates="guarantee_options", foreign_keys=[vehicle_id])


class VehicleFleetGuarantee(Base):
    """Garanties spécifiques à la flotte"""
    __tablename__ = 'vehicle_fleet_guarantees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
    rc = Column(Float, default=0.0)
    dr = Column(Float, default=0.0)
    vol = Column(Float, default=0.0)
    vb = Column(Float, default=0.0)
    ipt = Column(Float, default=0.0)
    bris = Column(Float, default=0.0)
    ar = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    in_garantie = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    vehicle = relationship("Vehicle", back_populates="fleet_guarantees", foreign_keys=[vehicle_id])


class VehicleClassification(Base):
    """Classification ASAC du véhicule"""
    __tablename__ = 'vehicle_classifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
    categorie_id = Column(String(10))
    genre_id = Column(String(10))
    type_id = Column(String(10))
    usage_id = Column(String(10))
    energie_id = Column(String(10))
    zone_id = Column(String(5))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    vehicle = relationship("Vehicle", back_populates="classification", foreign_keys=[vehicle_id])

class Vehicle(Base):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # --- RELATIONS EXISTANTES ---
    owner_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    compagny_id = Column(Integer, ForeignKey('automobile_compagnies.id'), nullable=True)
    fleet_id = Column(Integer, ForeignKey('fleets.id'), nullable=True)
    tarif_id = Column(Integer, ForeignKey('automobile_tarifs.id'), nullable=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=True)
    
    # --- INFORMATIONS DE BASE ---
    immatriculation = Column(String(50), nullable=False, unique=True)
    chassis = Column(String(100), nullable=False)
    marque = Column(String(100), nullable=False)
    modele = Column(String(100), nullable=False)
    annee = Column(Integer)
    
    # --- CARACTÉRISTIQUES TECHNIQUES ---
    puissance_fiscale = Column(Integer, default=5)
    places = Column(Integer, default=5)
    cylindree = Column(Integer, default=0)
    ptac = Column(Integer, default=0)           # Poids Total Autorisé en Charge
    charge_utile = Column(Integer, default=0)
    
    # --- VALEURS FINANCIÈRES ---
    valeur_neuf = Column(Float, default=0.0)
    valeur_venale = Column(Float, default=0.0)
    
    # --- OPTIONS SPÉCIFIQUES ---
    has_remorque = Column(Boolean, default=False)
    remorque_inflammable = Column(Boolean, default=False)
    remorque_immat = Column(String(50))
    double_commande = Column(Boolean, default=False)
    engin_portuaire = Column(Boolean, default=False)
    rc_eleves = Column(Boolean, default=False)  # Responsabilité Civile Élèves (auto-école)
    
    # --- CODES ET LIBELLÉS ---
    code_tarif = Column(String(50))
    libele_tarif = Column(String(255))
    code_assure = Column(String(50))
    
    # --- DATES ET DURÉES ---
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    date_mise_circulation = Column(DateTime)
    nbr_jour = Column(Integer, default=0)
    
    # --- FINANCES ---
    prime_brute = Column(Float, default=0.0)
    reduction = Column(Float, default=0.0)
    prime_nette = Column(Float, default=0.0)
    prime_emise = Column(Float, default=0.0)
    accessoires = Column(Float, default=0.0)
    tva = Column(Float, default=0.0)
    fichier_asac = Column(Float, default=0.0)
    carte_rose = Column(Float, default=0.0)
    vignette = Column(Float, default=0.0)
    pttc = Column(Float, default=0.0)  # Prix Toutes Taxes Comprises
    
    # --- STATUT ---
    statut = Column(String(20), default="ACTIF")
    is_active = Column(Boolean, default=True, nullable=False)
    
    # --- TRACABILITÉ ---
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))
    
    # --- RELATIONS ---
    # Relations principales
    owner = relationship("Contact", foreign_keys=[owner_id], back_populates="vehicles")
    compagny = relationship("Compagnie", foreign_keys=[compagny_id], back_populates="vehicles")
    fleet = relationship("Fleet", back_populates="vehicles")
    contract = relationship("Contrat", back_populates="vehicle", uselist=False)
    tarif = relationship("AutomobileTarif", back_populates="vehicles", foreign_keys=[tarif_id])
    
    # ✅ CLASSIFICATION ASAC
    classification = relationship("VehicleClassification", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")


    # ✅ INFORMATION CONDUCTEUR
    driver = relationship("Driver", back_populates="vehicles", foreign_keys=[driver_id])

    
    # ✅ GARANTIES
    guarantees = relationship("VehicleGuarantee", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    guarantee_reductions = relationship("VehicleGuaranteeReduction", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    guarantee_rates = relationship("VehicleGuaranteeRate", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    guarantee_options = relationship("VehicleGuaranteeOption", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    fleet_guarantees = relationship("VehicleFleetGuarantee", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    
    # --- PROPRIÉTÉS POUR LA COMPATIBILITÉ (ACCÈS DIRECT AUX VALEURS) ---
    @property
    def categorie(self):
        """Accès direct à la catégorie pour compatibilité"""
        return self.classification.categorie_id if self.classification else None
    
    @categorie.setter
    def categorie(self, value):
        """Définition directe de la catégorie pour compatibilité"""
        if not self.classification:
            self.classification = VehicleClassification()
        self.classification.categorie_id = value
    
    @property
    def genre(self):
        """Accès direct au genre pour compatibilité"""
        return self.classification.genre_id if self.classification else None
    
    @genre.setter
    def genre(self, value):
        """Définition directe du genre pour compatibilité"""
        if not self.classification:
            self.classification = VehicleClassification()
        self.classification.genre_id = value
    
    @property
    def type_vehicule(self):
        """Accès direct au type pour compatibilité"""
        return self.classification.type_id if self.classification else None
    
    @type_vehicule.setter
    def type_vehicule(self, value):
        """Définition directe du type pour compatibilité"""
        if not self.classification:
            self.classification = VehicleClassification()
        self.classification.type_id = value
    
    @property
    def usage(self):
        """Accès direct à l'usage pour compatibilité"""
        return self.classification.usage_id if self.classification else None
    
    @usage.setter
    def usage(self, value):
        """Définition directe de l'usage pour compatibilité"""
        if not self.classification:
            self.classification = VehicleClassification()
        self.classification.usage_id = value
    
    @property
    def energie(self):
        """Accès direct à l'énergie pour compatibilité"""
        return self.classification.energie_id if self.classification else None
    
    @energie.setter
    def energie(self, value):
        """Définition directe de l'énergie pour compatibilité"""
        if not self.classification:
            self.classification = VehicleClassification()
        self.classification.energie_id = value
    
    @property
    def zone(self):
        """Accès direct à la zone pour compatibilité"""
        return self.classification.zone_id if self.classification else None
    
    @zone.setter
    def zone(self, value):
        """Définition directe de la zone pour compatibilité"""
        if not self.classification:
            self.classification = VehicleClassification()
        self.classification.zone_id = value
    
    def __repr__(self):
        return f"<Vehicle(id={self.id}, immatriculation={self.immatriculation})>"
    
    @classmethod
    def safe_query(cls, session, *args, **kwargs):
        """Exécute une requête avec rollback automatique en cas d'erreur"""
        try:
            return session.query(cls).filter(*args, **kwargs).all()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur de requête Vehicle: {e}")
            return []
    
    @classmethod
    def safe_count(cls, session, *args, **kwargs):
        """Compte les enregistrements avec rollback automatique"""
        try:
            return session.query(cls).filter(*args, **kwargs).count()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Erreur de comptage Vehicle: {e}")
            return 0

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