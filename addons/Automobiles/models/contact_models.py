# addons/Automobiles/models/contact_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    
    # --- I. ADMINISTRATION & STATUT ---
    type_client = Column(String(50))      
    nature = Column(String(50))           
    charge_clientele = Column("charge_clientele", String(100)) # Mappe le nom avec accent vers variable sans accent
    redacteur_production = Column(String(100))
    code_client = Column(String(50), unique=True)
    vip_status = Column(String(10))

    # --- II. ÉTAT CIVIL & IDENTITÉ ---
    civilite = Column(String(20))         
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    date_naissance = Column(Date)
    nationalite = Column(String(100))
    num_contribuable = Column(String(100))
    cat_socio_prof = Column(String(10))    
    libelle_socio_prof = Column(String(100))

    # --- III. COORDONNÉES ---
    telephone = Column(String(50))        
    tel_portable = Column(String(50))     
    fax = Column(String(50))              
    email = Column(String(100))           
    adresse = Column(Text)                
    adresse_2 = Column(Text)              
    ville = Column(String(100))           

    # --- IV. PERMIS ---
    cat_permis = Column(String(20))       
    num_permis = Column(String(100))      
    date_permis = Column(Date)
    photo_path = Column(String(255))      
    
    # --- RELATIONS (Utilisation stricte de chaînes de caractères) ---
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    fleets = relationship("Fleet", back_populates="owner", cascade="all, delete-orphan")
    contracts = relationship("Contrat", back_populates="owner", cascade="all, delete-orphan")

    # --- TRAÇABILITÉ ---
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))

    creator = relationship("User", foreign_keys=[created_by])

class ContactAuditLog(Base):
    __tablename__ = "contact_audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('utilisateurs.id'))
    contact_id = Column(Integer, nullable=True)
    action = Column(String(100))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)