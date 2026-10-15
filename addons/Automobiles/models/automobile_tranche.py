from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import Base

class AutomobileTranche(Base):
    """
    Table de correspondance pour les tranches de puissance fiscale.
    Inclut désormais le tracking d'audit.
    """
    __tablename__ = 'automobile_tranches'

    # --- DONNÉES MÉTIER ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(50), nullable=False) # Ex: "1 - 2 CV"
    max_cv = Column(Integer, nullable=False)     # Ex: 2

    # --- ÉLÉMENTS D'AUDIT ---
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # ID de l'utilisateur (lié à ta table des utilisateurs)
    created_by = Column(Integer, nullable=True) 
    updated_by = Column(Integer, nullable=True)

    # Optionnel : IP ou Machine pour plus de sécurité
    local_ip = Column(String(45))
    network_ip = Column(String(45))

    def __repr__(self):
        return f"<Tranche(id={self.id}, libelle='{self.libelle}', max_cv={self.max_cv})>"