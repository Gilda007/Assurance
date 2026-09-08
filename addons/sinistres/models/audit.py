"""
Modèles d'audit - Adaptés pour Integer
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from datetime import datetime

from core.database import Base


class LometaAuditLog(Base):
    """Journal d'audit global"""
    __tablename__ = "lometa_audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    utilisateur_id = Column(Integer, nullable=False, index=True)
    utilisateur_nom = Column(String(100), nullable=True)
    utilisateur_role = Column(String(50), nullable=True)
    
    date_action = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    action = Column(String(50), nullable=False, index=True)
    entite = Column(String(50), nullable=False, index=True)
    entite_id = Column(Integer, nullable=True, index=True)
    entite_nom = Column(String(200), nullable=True)
    
    champ_modifie = Column(String(50), nullable=True)
    ancienne_valeur = Column(Text, nullable=True)
    nouvelle_valeur = Column(Text, nullable=True)
    
    ip_adresse = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    session_id = Column(String(100), nullable=True)
    application = Column(String(50), nullable=True)
    commentaire = Column(Text, nullable=True)
    niveau = Column(String(20), nullable=False, default="INFO")