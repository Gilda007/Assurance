from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    
    # --- INFORMATIONS GÉNÉRALES ---
    type_contact = Column(String(50)) # Assuré, Bénéficiaire, Prospect
    nature = Column(String(50))       # Physique ou Morale
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    telephone = Column(String(20))
    email = Column(String(100))
    adresse = Column(Text)
    num_piece_id = Column(String(100)) # CNI, Passeport ou Registre Commerce
    
    # --- DOCUMENTS ---
    photo_path = Column(String(255))
    
    # --- RELATIONS MÉTIER (Lien avec les autres modules) ---
    # Liaison avec Vehicle (propriétaire)
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    
    # Liaison avec Fleet (gestion de flotte entreprise)
    fleets = relationship("Fleet", back_populates="owner", cascade="all, delete-orphan")
    
    # Liaison avec Contract (historique d'assurance)
    contracts = relationship("Contract", back_populates="contact", cascade="all, delete-orphan")
    
    # --- TRAÇABILITÉ & AUDIT ---
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Utilisateurs (liés au module user_manager)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    
    # Réseaux (Traçabilité demandée)
    created_ip = Column(String(45)) # IP lors de la création
    last_ip = Column(String(45))    # Dernière IP de modification

    # Objets Relations pour accès facile (ex: contact.creator.username)
    creator = relationship("User", foreign_keys=[created_by])
    editor = relationship("User", foreign_keys=[updated_by])
    # fleets = relationship("Fleet", back_populates="owner")

    def __repr__(self):
        return f"<Contact(ID={self.id}, Nom='{self.nom}', Nature='{self.nature}')>"
    
class ContactAuditLog(Base):
    __tablename__ = "contact_audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('utilisateurs.id'))
    contact_id = Column(Integer, nullable=True)
    action = Column(String(100)) # "CRÉATION", "MODIFICATION", "SUPPRESSION"
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True) # 45 pour supporter IPv6