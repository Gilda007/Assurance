"""
Modèles des référentiels - Adaptés pour Integer
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaReferentiel(Base, AuditableMixin):
    """Référentiel paramétrable"""
    __tablename__ = "lometa_referentiels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    famille = Column(String(30), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    date_effet = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=True)
    
    societe = Column(String(100), nullable=True)
    branche = Column(String(50), nullable=True)
    valeur = Column(Float, nullable=True)
    donnees_supplementaires = Column(Text, nullable=True)
    
    est_actif = Column(Boolean, nullable=False, default=True, index=True)
    est_obsolete = Column(Boolean, nullable=False, default=False)
    
    version = Column(Integer, nullable=False, default=1)
    version_precedente_id = Column(Integer, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    historique = relationship("LometaReferentielHistorique", back_populates="referentiel", cascade="all, delete-orphan")


class LometaReferentielHistorique(Base, AuditableMixin):
    """Historique des modifications des référentiels"""
    __tablename__ = "lometa_referentiels_historique"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    referentiel_id = Column(Integer, ForeignKey("lometa_referentiels.id"), nullable=False, index=True)
    
    champ_modifie = Column(String(50), nullable=False)
    ancienne_valeur = Column(Text, nullable=True)
    nouvelle_valeur = Column(Text, nullable=True)
    
    date_modification = Column(DateTime, nullable=False, default=datetime.utcnow)
    modifie_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    ip_adresse = Column(String(45), nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    referentiel = relationship("LometaReferentiel", back_populates="historique")