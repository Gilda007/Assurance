# # addons/Automobiles/models/vehicle_classification.py

# import datetime

# from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Enum as SQLEnum, Text
# from sqlalchemy.orm import relationship
# import enum
# from core.database import Base
# from sqlalchemy import func 


# class VehicleCategory(enum.Enum):
#     """Catégorie du véhicule (section 4.2)"""
#     VP01 = "VP01"  # Véhicule de tourisme (Personne physique)
#     VP02 = "VP02"  # Transport pour propre compte
#     VP03 = "VP03"  # Transport public de marchandises
#     VP04 = "VP04"  # Transport public de voyageurs
#     VP05 = "VP05"  # Véhicule motorisé à 2 ou 3 roues
#     VP06 = "VP06"  # Véhicule des garagistes
#     VP07 = "VP07"  # Véhicule d'auto-écoles
#     VP08 = "VP08"  # Véhicule de location
#     VP09 = "VP09"  # Engin de chantier
#     VP10 = "VP10"  # Véhicules spéciaux
#     VP11 = "VP11"  # Catégorie 11
#     VP12 = "VP12"  # Véhicule de tourisme (Personne morale)


# class VehicleGenre(enum.Enum):
#     """Genre du véhicule (section 4.3)"""
#     GV01 = "GV01"  # Camion
#     GV02 = "GV02"  # Camionnette
#     GV03 = "GV03"  # Cyclomoteur (2/3 Roues)
#     GV04 = "GV04"  # Voiture (4 Roues)
#     GV05 = "GV05"  # Engins de chantiers
#     GV06 = "GV06"  # Car
#     GV07 = "GV07"  # Fourgonnette
#     GV08 = "GV08"  # Remorque
#     GV09 = "GV09"  # Scooter
#     GV10 = "GV10"  # Semi-remorque
#     GV11 = "GV11"  # Tracteur agricole
#     GV12 = "GV12"  # Tracteur routier


# class VehicleType(enum.Enum):
#     """Type du véhicule (section 4.4)"""
#     TV01 = "TV01"  # Ambulance
#     TV02 = "TV02"  # Auto Car (Plus de 41 places)
#     TV03 = "TV03"  # Corbiard
#     TV04 = "TV04"  # Mini Car (9 à 40 places)
#     TV05 = "TV05"  # Taxi Communaux
#     TV06 = "TV06"  # Taxi Urbain (MATCA, VTC)
#     TV07 = "TV07"  # Véhicule Auto-École
#     TV08 = "TV08"  # Véhicule de Service Public
#     TV09 = "TV09"  # Véhicule de Tourisme (max 9 places, avec chauffeur)
#     TV10 = "TV10"  # Véhicule Particulier (PTAC max 3,5 T)
#     TV11 = "TV11"  # Véhicule Utilitaire
#     TV12 = "TV12"  # Voiture de Location
#     TV13 = "TV13"  # Cyclomoteur (2/3 Roues)


# class VehicleUsage(enum.Enum):
#     """Usage du véhicule (section 4.5)"""
#     UV01 = "UV01"  # Promenade ou Affaire
#     UV02 = "UV02"  # Transport pour propre compte
#     UV03 = "UV03"  # Transport privé de voyageurs
#     UV04 = "UV04"  # Transport public de marchandises
#     UV05 = "UV05"  # Transport public de voyageurs
#     UV06 = "UV06"  # Véhicules Auto-école
#     UV07 = "UV07"  # Véhicules de Location
#     UV08 = "UV08"  # Véhicules Spéciaux
#     UV09 = "UV09"  # Engin de Chantier
#     UV10 = "UV10"  # Véhicule motorisé 2 à 3 roues


# class VehicleEnergy(enum.Enum):
#     """Énergie du véhicule (section 4.6)"""
#     SEE = "SEE"    # Essence
#     SED = "SED"    # Diesel
#     SEL = "SEL"    # Électrique
#     SEHY = "SEHY"  # Hybride


# class CirculationZone(enum.Enum):
#     """Zone de circulation (section 4.7)"""
#     ZA = "ZA"  # Zone A
#     ZB = "ZB"  # Zone B
#     ZC = "ZC"  # Zone C


# class VehicleClassification(Base):
#     """Classification ASAC du véhicule"""
#     __tablename__ = 'vehicle_classifications'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, nullable=False)
    
#     # Classification ASAC
#     categorie_id = Column(String(10))  # VP01, VP02, etc.
#     genre_id = Column(String(10))      # GV01, GV02, etc.
#     type_id = Column(String(10))       # TV01, TV02, etc.
#     usage_id = Column(String(10))      # UV01, UV02, etc.
#     energie_id = Column(String(10))    # SEE, SED, etc.
#     zone_id = Column(String(5))        # A, B, C
    
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
#     # Relations
#     vehicle = relationship("Vehicle", back_populates="classification", foreign_keys=[vehicle_id])


# class VehicleCategory(Base):
#     """Catégories de véhicules (référentiel)"""
#     __tablename__ = 'vehicle_categories'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(10), unique=True, nullable=False)  # VP01, VP02, etc.
#     libelle = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# class VehicleGenre(Base):
#     """Genres de véhicules (référentiel)"""
#     __tablename__ = 'vehicle_genres'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(10), unique=True, nullable=False)  # GV01, GV02, etc.
#     libelle = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# class VehicleType(Base):
#     """Types de véhicules (référentiel)"""
#     __tablename__ = 'vehicle_types'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(10), unique=True, nullable=False)  # TV01, TV02, etc.
#     libelle = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# class VehicleUsage(Base):
#     """Usages de véhicules (référentiel)"""
#     __tablename__ = 'vehicle_usages'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(10), unique=True, nullable=False)  # UV01, UV02, etc.
#     libelle = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# class VehicleEnergy(Base):
#     """Énergies de véhicules (référentiel)"""
#     __tablename__ = 'vehicle_energies'
#     __table_args__ = {'extend_existing': True}
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(10), unique=True, nullable=False)  # SEE, SED, etc.
#     libelle = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# class VehicleZone(Base):
#     """Zones de circulation (référentiel)"""
#     __tablename__ = 'vehicle_zones'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(5), unique=True, nullable=False)  # A, B, C
#     libelle = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())