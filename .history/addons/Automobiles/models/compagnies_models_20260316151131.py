from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Compagnie(Base):
    __tablename__ = 'automobile_compagnies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    email = Column(String(100))
    telephone = Column(String(50))
    adresse = Column(String(255))
    num_debut = Column(String(20))
    num_fin = Column(String(20))
    is_active = Column(Boolean, default=True, nullable=False)

    # --- BLOC DE TRAÇABILITÉ ---
    created_at = Column(DateTime, default=datetime.now)
    create_by = Column(String(50))      # Login ou ID de l'utilisateur
    modify_at = Column(DateTime, onupdate=datetime.now)
    modify_by = Column(String(50))
    local_ip = Column(String(45))       # Supporte IPv4 et IPv6
    network_ip = Column(String(45))     # IP Publique/Réseau

    # Relation vers les tarifs
    tarifs = relationship("AutomobileTarif", back_populates="compagnie", cascade="all, delete-orphan")