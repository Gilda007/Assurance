"""
Modèles financiers - Adaptés pour Integer
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaBeneficiaire(Base, AuditableMixin):
    """Bénéficiaire d'un règlement"""
    __tablename__ = "lometa_beneficiaires"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    type_beneficiaire = Column(String(30), nullable=False)
    code_beneficiaire = Column(String(20), unique=True, nullable=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=True)
    societe = Column(String(100), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    adresse = Column(Text, nullable=True)
    code_postal = Column(String(10), nullable=True)
    ville = Column(String(50), nullable=True)
    pays = Column(String(50), nullable=False)
    iban = Column(String(34), nullable=True)
    bic_swift = Column(String(11), nullable=True)
    banque = Column(String(100), nullable=True)
    numero_mobile = Column(String(20), nullable=True)
    operateur_mobile = Column(String(20), nullable=True)
    est_actif = Column(Boolean, nullable=False, default=True, index=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)


class LometaCompteBancaire(Base, AuditableMixin):
    """Compte bancaire de la compagnie"""
    __tablename__ = "lometa_comptes_bancaires"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    code_banque = Column(String(20), nullable=False, unique=True, index=True)
    libelle = Column(String(100), nullable=False)
    iban = Column(String(34), nullable=False, unique=True)
    bic_swift = Column(String(11), nullable=True)
    devise = Column(String(3), nullable=False)
    banque = Column(String(100), nullable=False)
    agence = Column(String(100), nullable=True)
    solde = Column(Float, nullable=False, default=0.0)
    date_dernier_mouvement = Column(DateTime, nullable=True)
    statut = Column(String(20), nullable=False, default="ACTIF")
    est_actif = Column(Boolean, nullable=False, default=True, index=True)
    est_par_defaut = Column(Boolean, nullable=False, default=False)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)


class LometaReglement(Base, AuditableMixin):
    """Règlement (demande de paiement)"""
    __tablename__ = "lometa_reglements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    numero_reglement = Column(String(20), unique=True, nullable=False, index=True)
    beneficiaire_id = Column(Integer, ForeignKey("lometa_beneficiaires.id"), nullable=False, index=True)
    beneficiaire_nom = Column(String(100), nullable=True)
    
    montant = Column(Float, nullable=False)
    montant_lettres = Column(String(200), nullable=True)
    type_paiement = Column(String(20), nullable=False)
    
    date_demande = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_validation = Column(DateTime, nullable=True)
    date_paiement = Column(DateTime, nullable=True)
    
    statut = Column(String(30), nullable=False, default="CREE", index=True)
    
    # Chèque
    numero_cheque = Column(String(20), nullable=True)
    banque_emetteur = Column(String(100), nullable=True)
    date_emission_cheque = Column(DateTime, nullable=True)
    
    # Virement
    reference_virement = Column(String(50), nullable=True)
    date_virement = Column(DateTime, nullable=True)
    
    # Mobile Money
    numero_mobile = Column(String(20), nullable=True)
    operateur_mobile = Column(String(20), nullable=True)
    reference_mobile = Column(String(50), nullable=True)
    
    # Validation
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    paiement_effectue_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    note_credit_id = Column(Integer, nullable=True)
    est_note_credit = Column(Boolean, nullable=False, default=False)
    evaluation_id = Column(Integer, nullable=True)
    lot_paiement_id = Column(Integer, ForeignKey("lometa_lots_paiement.id"), nullable=True)

    
    # Comptabilité
    journal_comptable = Column(String(20), nullable=True)
    est_comptabilise = Column(Boolean, nullable=False, default=False)
    date_comptabilisation = Column(DateTime, nullable=True)
    
    observations = Column(Text, nullable=True)
    motif_annulation = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    sinistre = relationship(
        "LometaSinistre", 
        back_populates="reglements"
    )
    beneficiaire = relationship(
        "LometaBeneficiaire"
    )
    lot = relationship(
        "LometaLotPaiement",
        foreign_keys=[lot_paiement_id],
        back_populates="reglements"
    )


class LometaLotPaiement(Base, AuditableMixin):
    """Lot de paiement"""
    __tablename__ = "lometa_lots_paiement"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    numero_lot = Column(String(20), nullable=False, unique=True, index=True)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_traitement = Column(DateTime, nullable=True)
    date_comptabilisation = Column(DateTime, nullable=True)
    
    banque_id = Column(Integer, nullable=False)
    compte_bancaire_id = Column(Integer, ForeignKey("lometa_comptes_bancaires.id"), nullable=False)
    
    nombre_paiements = Column(Integer, nullable=False, default=0)
    montant_total = Column(Float, nullable=False, default=0.0)
    
    statut = Column(String(20), nullable=False, default="OUVERT", index=True)
    type_lot = Column(String(20), nullable=False, default="STANDARD")
    
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    date_validation = Column(DateTime, nullable=True)
    
    observations = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    
    reglements = relationship(
        "LometaReglement",
        primaryjoin="LometaLotPaiement.id == LometaReglement.lot_paiement_id",
        foreign_keys="LometaReglement.lot_paiement_id",
        back_populates="lot",
        cascade="all, delete-orphan"
    )


class LometaNoteCredit(Base, AuditableMixin):
    """Note de crédit"""
    __tablename__ = "lometa_notes_credit"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sinistre_id = Column(Integer, ForeignKey("lometa_sinistres.id"), nullable=False, index=True)
    
    numero_note = Column(String(20), nullable=False, unique=True, index=True)
    reglement_origine_id = Column(Integer, nullable=True)
    type_note = Column(String(30), nullable=False)
    montant = Column(Float, nullable=False)
    motif = Column(Text, nullable=False)
    
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_validation = Column(DateTime, nullable=True)
    valide_par = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    est_comptabilise = Column(Boolean, nullable=False, default=False)
    
    # Audit
    created_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)