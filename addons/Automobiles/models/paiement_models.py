# addons/Automobiles/models/payment_models.py
import socket
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class PaymentMode(enum.Enum):
    """Modes de paiement disponibles"""
    CASH = "especes"
    CARD = "carte_bancaire"
    TRANSFER = "virement"
    CHECK = "cheque"
    ORANGE_MONEY = "orange_money"
    MTN_MONEY = "mtn_money"
    WAVE = "wave"
    BANK_DEPOSIT = "depot_bancaire"


class PaymentStatus(enum.Enum):
    """Statuts d'un paiement"""
    PENDING = "en_attente"
    COMPLETED = "complete"
    CANCELLED = "annule"
    FAILED = "echoue"
    REFUNDED = "rembourse"


class Paiement(Base):
    __tablename__ = "paiements"
    
    id = Column(Integer, primary_key=True)
    contrat_id = Column(Integer, ForeignKey("contrats.id"), nullable=False)
    
    # Numéro de reçu unique (généré automatiquement)
    numero_recu = Column(String(100), unique=True, nullable=False)
    
    # Montant et mode
    montant = Column(Float, nullable=False)
    mode_paiement = Column(SQLEnum(PaymentMode), nullable=False, default=PaymentMode.CASH)
    
    # Références externes
    reference_externe = Column(String(100), nullable=True)  # Référence transaction Mobile Money, chèque, etc.
    transaction_id = Column(String(100), nullable=True)     # ID de transaction bancaire
    numero_cheque = Column(String(50), nullable=True)       # Numéro de chèque
    banque = Column(String(100), nullable=True)             # Banque émettrice
    
    # Statut du paiement
    statut = Column(SQLEnum(PaymentStatus), default=PaymentStatus.COMPLETED)
    motif_annulation = Column(String(255), nullable=True)
    is_annule = Column(Boolean, default=False)
    
    # Informations complémentaires
    notes = Column(Text, nullable=True)
    date_paiement = Column(DateTime, default=datetime.now)
    
    # Chemin du fichier reçu PDF (si généré)
    recu_pdf_path = Column(String(500), nullable=True)
    
    # --- AUDIT ---
    date_operation = Column(DateTime, default=datetime.now)
    caissier_id = Column(Integer, ForeignKey('utilisateurs.id'), nullable=False)
    terminal_name = Column(String(100), default=socket.gethostname())
    
    # IP de l'utilisateur qui a effectué l'opération
    created_ip = Column(String(45), nullable=True)
    updated_ip = Column(String(45), nullable=True)
    
    # Dates de création et modification
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(50))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(String(50))
    
    # --- RELATIONS ---
    contrat = relationship("Contrat", back_populates="paiements")
    caissier = relationship("User", foreign_keys=[caissier_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.numero_recu:
            self.numero_recu = self.generate_receipt_number()
    
    def generate_receipt_number(self) -> str:
        """Génère un numéro de reçu unique"""
        from datetime import datetime
        annee = datetime.now().strftime('%Y')
        mois = datetime.now().strftime('%m')
        jour = datetime.now().strftime('%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"REC-{annee}{mois}{jour}-{unique_id}"
    
    def annuler(self, motif: str, user_id: int, ip: str = None) -> bool:
        """Annule le paiement"""
        if self.is_annule:
            return False
        
        self.is_annule = True
        self.statut = PaymentStatus.CANCELLED
        self.motif_annulation = motif
        self.updated_ip = ip
        self.updated_at = datetime.now()
        
        # Mettre à jour le contrat associé
        if self.contrat:
            self.contrat.montant_paye -= self.montant
            self.contrat.montant_restant = self.contrat.prime_totale_ttc - self.contrat.montant_paye
            
            if self.contrat.montant_paye >= self.contrat.prime_totale_ttc:
                self.contrat.statut_paiement = "PAYE"
            elif self.contrat.montant_paye > 0:
                self.contrat.statut_paiement = "PARTIEL"
            else:
                self.contrat.statut_paiement = "NON_PAYE"
        
        return True
    
    def to_dict(self) -> dict:
        """Convertit le paiement en dictionnaire"""
        return {
            'id': self.id,
            'contrat_id': self.contrat_id,
            'numero_recu': self.numero_recu,
            'montant': self.montant,
            'mode_paiement': self.mode_paiement.value if hasattr(self.mode_paiement, 'value') else str(self.mode_paiement),
            'statut': self.statut.value if hasattr(self.statut, 'value') else str(self.statut),
            'reference_externe': self.reference_externe,
            'transaction_id': self.transaction_id,
            'numero_cheque': self.numero_cheque,
            'banque': self.banque,
            'notes': self.notes,
            'date_paiement': self.date_paiement.strftime('%d/%m/%Y %H:%M') if self.date_paiement else None,
            'caissier_id': self.caissier_id,
            'terminal_name': self.terminal_name,
            'is_annule': self.is_annule,
            'motif_annulation': self.motif_annulation,
            'recu_pdf_path': self.recu_pdf_path
        }
    
    def __repr__(self):
        return f"<Paiement(id={self.id}, numero_recu={self.numero_recu}, montant={self.montant}, statut={self.statut})>"


class AuditPaiementLog(Base):
    __tablename__ = 'audit_paiement_logs'
    
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, CANCEL, etc.
    module = Column(String(50), default="PAIEMENT")
    payment_id = Column(Integer, nullable=False)  # ID du paiement concerné
    contrat_id = Column(Integer, nullable=True)   # ID du contrat associé
    
    # Stockage des changements au format JSON
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    
    # Informations supplémentaires
    notes = Column(Text, nullable=True)
    
    # Traçabilité Réseau
    ip_local = Column(String(50), nullable=True)
    ip_public = Column(String(50), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditPaiementLog(action={self.action}, payment_id={self.payment_id})>"