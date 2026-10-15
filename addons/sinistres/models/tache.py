"""
Modèles d'expertise, évaluation et provision (Tome 4 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base, AuditableMixin

class LometaTache(Base, AuditableMixin):
    """Tâche (workflow ou manuelle)"""
    __tablename__ = "lometa_taches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Rattachement
    entite_type = Column(String(30), nullable=False)
    entite_id = Column(Integer, nullable=False, index=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=True, index=True)
    
    # Contenu
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type_tache = Column(String(30), nullable=False)  # AUTOMATIQUE, MANUELLE
    suite_a_donner = Column(String(50), nullable=True)  # Référentiel
    priorite = Column(String(20), nullable=False, default="NORMALE")
    
    # Assignation
    assignee_a = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True, index=True)
    cree_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    # Échéances
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_echeance = Column(DateTime, nullable=True, index=True)
    date_realisation = Column(DateTime, nullable=True)
    
    # État (Tome 7 §15)
    statut = Column(String(20), nullable=False, default="A_FAIRE", index=True)
    # A_FAIRE, EN_COURS, TERMINEE, ANNULEE
