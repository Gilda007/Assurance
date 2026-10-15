"""
Modèles des référentiels - Adaptés pour Integer
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaWorkflow(Base, AuditableMixin):
    """Définition de workflow (Tome 2 §15)"""
    __tablename__ = "lometa_workflows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    libelle = Column(String(200), nullable=False)
    entite_cible = Column(String(30), nullable=False)  # SINISTRE, EXPERTISE, REGLEMENT
    est_actif = Column(Boolean, default=True, nullable=False)


class LometaWorkflowTransition(Base, AuditableMixin):
    """Transition d'un workflow (Tome 2 §15)"""
    __tablename__ = "lometa_workflow_transitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("lometa_workflows.id"), nullable=False)
    etat_source = Column(String(30), nullable=False)
    etat_cible = Column(String(30), nullable=False)
    action = Column(String(50), nullable=False)
    role_autorise = Column(String(50), nullable=True)
    genere_notification = Column(Boolean, default=False)
    genere_tache = Column(Boolean, default=False)
