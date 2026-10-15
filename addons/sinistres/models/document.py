"""
Modèles d'expertise, évaluation et provision (Tome 4 du CDC)
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base, AuditableMixin

class LometaDocument(Base, AuditableMixin):
    """Document centralisé (GED) — Tome 7"""
    __tablename__ = "lometa_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Rattachement polymorphe
    entite_type = Column(String(30), nullable=False, index=True)  # SINISTRE, EXPERTISE, REGLEMENT, RECOURS
    entite_id = Column(Integer, nullable=False, index=True)
    
    # Type de document (référentiel)
    type_document = Column(String(30), nullable=False)
    categorie = Column(String(50), nullable=True)
    
    # Fichier
    nom_fichier = Column(String(255), nullable=False)
    chemin_fichier = Column(String(500), nullable=False)
    taille = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    hash_fichier = Column(String(64), nullable=True)
    
    # Versioning (GED-001)
    version = Column(Integer, nullable=False, default=1)
    version_precedente_id = Column(Integer, ForeignKey("lometa_documents.id"), nullable=True)
    est_version_courante = Column(Boolean, default=True, nullable=False, index=True)
    
    # Propriétaire (GED-003)
    proprietaire_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    est_actif = Column(Boolean, default=True, nullable=False)
    
LometaDocument.version_precedente = relationship(
    "LometaDocument",
    remote_side="LometaDocument.id",
    foreign_keys=[LometaDocument.version_precedente_id]
)
