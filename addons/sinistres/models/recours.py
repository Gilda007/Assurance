"""
Modèles de recours - Adaptés pour Integer
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaRecours(Base, AuditableMixin):
    """Recours contre un tiers responsable"""
    __tablename__ = "lometa_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    numero_recours = Column(String(20), nullable=False, unique=True, index=True)
    type_recours = Column(String(30), nullable=False)
    
    debiteur_id = Column(Integer, nullable=False, index=True)
    debiteur_nom = Column(String(100), nullable=True)
    
    montant_reclame = Column(Float, nullable=False)
    montant_accepte = Column(Float, nullable=True)
    montant_encaisse = Column(Float, nullable=False, default=0.0)
    solde = Column(Float, nullable=False, default=0.0)
    
    date_ouverture = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_accord = Column(DateTime, nullable=True)
    date_derniere_relance = Column(DateTime, nullable=True)
    date_prochaine_relance = Column(DateTime, nullable=True)
    date_cloture = Column(DateTime, nullable=True)
    
    statut = Column(String(30), nullable=False, default="OUVERT", index=True)
    
    responsable_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    nombre_relances = Column(Integer, nullable=False, default=0)
    relance_max = Column(Integer, nullable=False, default=5)
    
    reference_accord = Column(String(50), nullable=True)
    document_justificatif = Column(String(255), nullable=True)
    observations = Column(Text, nullable=True)
    motif_cloture = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    sinistre = relationship(
        "LometaSinistre", 
        back_populates="recours"
    )
    encaissements = relationship(
        "LometaEncaissementRecours", 
        back_populates="recours", 
        cascade="all, delete-orphan"
    )
    reversements = relationship(
        "LometaReversementRecours", 
        back_populates="recours", 
        cascade="all, delete-orphan"
    )
    relances = relationship(
        "LometaRelanceRecours", 
        back_populates="recours", 
        cascade="all, delete-orphan"
    )


class LometaEncaissementRecours(Base, AuditableMixin):
    """Encaissement d'un recours"""
    __tablename__ = "lometa_encaissements_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(Integer, ForeignKey("lometa_recours.id"), nullable=False, index=True)
    
    montant = Column(Float, nullable=False)
    mode_encaissement = Column(String(20), nullable=False)
    reference_bancaire = Column(String(50), nullable=True)
    date_encaissement = Column(DateTime, nullable=False)
    banque = Column(String(100), nullable=True)
    compte_bancaire_id = Column(Integer, nullable=True)
    
    est_partiel = Column(Boolean, nullable=False, default=False)
    solde_apres_encaissement = Column(Float, nullable=False)
    
    journal_comptable = Column(String(20), nullable=True)
    est_comptabilise = Column(Boolean, nullable=False, default=False)
    date_comptabilisation = Column(DateTime, nullable=True)
    note_credit_id = Column(Integer, nullable=True)
    observations = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    recours = relationship(
        "LometaRecours", 
        back_populates="encaissements"
    )


class LometaReversementRecours(Base, AuditableMixin):
    """Reversement au client"""
    __tablename__ = "lometa_reversements_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(Integer, ForeignKey("lometa_recours.id"), nullable=False, index=True)
    
    beneficiaire_id = Column(Integer, nullable=False)
    beneficiaire_nom = Column(String(100), nullable=True)
    montant = Column(Float, nullable=False)
    quote_part = Column(Float, nullable=False)
    type_reversement = Column(String(20), nullable=False)
    
    reglement_id = Column(Integer, nullable=True)
    mode_paiement = Column(String(20), nullable=False)
    reference_paiement = Column(String(50), nullable=True)
    
    date_reversement = Column(DateTime, nullable=False)
    date_comptabilisation = Column(DateTime, nullable=True)
    
    est_paye = Column(Boolean, nullable=False, default=False)
    est_comptabilise = Column(Boolean, nullable=False, default=False)
    observations = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    recours = relationship(
        "LometaRecours", 
        back_populates="reversements"
    )

class LometaRelanceRecours(Base, AuditableMixin):
    """Historique des relances"""
    __tablename__ = "lometa_relances_recours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recours_id = Column(Integer, ForeignKey("lometa_recours.id"), nullable=False, index=True)
    
    date_relance = Column(DateTime, nullable=False, default=datetime.utcnow)
    type_relance = Column(String(20), nullable=False)
    contenu = Column(Text, nullable=True)
    
    reponse_recue = Column(Boolean, nullable=False, default=False)
    date_reponse = Column(DateTime, nullable=True)
    contenu_reponse = Column(Text, nullable=True)
    
    effectue_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    prochaine_relance = Column(DateTime, nullable=True)
    statut = Column(String(20), nullable=False, default="EN_ATTENTE")
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    recours = relationship(
        "LometaRecours", 
        back_populates="relances"
    )