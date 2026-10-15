"""
Modèles d'expertise, évaluation et provision (Tome 4 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base, AuditableMixin

class LometaNotification(Base, AuditableMixin):
    """Notification système (Tome 7 §13)"""
    __tablename__ = "lometa_notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    destinataire_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False, index=True)
    canal = Column(String(20), nullable=False)  # EMAIL, SMS, APP, WHATSAPP, TEAMS
    
    # Contenu
    sujet = Column(String(200), nullable=True)
    contenu = Column(Text, nullable=False)
    
    # Déclencheur
    evenement = Column(String(50), nullable=False)  # ClaimCreated, PaymentExecuted, etc.
    entite_type = Column(String(30), nullable=True)
    entite_id = Column(Integer, nullable=True)
    
    # État
    statut = Column(String(20), nullable=False, default="EN_ATTENTE")  # EN_ATTENTE, ENVOYEE, ECHEC, LUE
    date_envoi = Column(DateTime, nullable=True)
    date_lecture = Column(DateTime, nullable=True)
    erreur = Column(Text, nullable=True)
