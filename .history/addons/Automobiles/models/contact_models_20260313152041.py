# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from core.database import Base

# from addons.Automobiles.models.flottes_models import Fleet

# class Contact(Base):
#     __tablename__ = 'contacts'

#     id = Column(Integer, primary_key=True)
    
#     # --- INFORMATIONS GÉNÉRALES ---
#     type_contact = Column(String(50)) # Assuré, Bénéficiaire, Prospect
#     nature = Column(String(50))       # Physique ou Morale
#     nom = Column(String(100), nullable=False)
#     prenom = Column(String(100))
#     telephone = Column(String(20))
#     email = Column(String(100))
#     adresse = Column(Text)
#     num_piece_id = Column(String(100)) # CNI, Passeport ou Registre Commerce
    
#     # --- DOCUMENTS ---
#     photo_path = Column(String(255))
    
#     # --- RELATIONS MÉTIER (Lien avec les autres modules) ---
#     # Liaison avec Vehicle (propriétaire)
#     vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    
#     # Liaison avec Fleet (gestion de flotte entreprise)
#     fleets = relationship("Fleet", back_populates="owner", cascade="all, delete-orphan")
    
#     # Liaison avec Contract (historique d'assurance)
#     contracts = relationship("Contract", back_populates="contact", cascade="all, delete-orphan")
    
#     # --- TRAÇABILITÉ & AUDIT ---
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
#     # Utilisateurs (liés au module user_manager)
#     created_by = Column(Integer, ForeignKey('utilisateurs.id'))
#     updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    
#     # Réseaux (Traçabilité demandée)
#     created_ip = Column(String(45)) # IP lors de la création
#     last_ip = Column(String(45))    # Dernière IP de modification

#     # Objets Relations pour accès facile (ex: contact.creator.username)
#     creator = relationship("User", foreign_keys=[created_by])
#     editor = relationship("User", foreign_keys=[updated_by])
#     # fleets = relationship("Fleet", back_populates="owner")

#     def __repr__(self):
#         return f"<Contact(ID={self.id}, Nom='{self.nom}', Nature='{self.nature}')>"

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

# Note: Assurez-vous que Fleet et Vehicle sont bien importés pour les relations
# from addons.Automobiles.models.flottes_models import Fleet

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    
    # --- I. ADMINISTRATION & STATUT (Bloc 1 du formulaire) ---
    type_client = Column(String(50))      # Standard, VIP
    nature = Column(String(50))           # Particulier, Société (ou Physique/Morale)
    charge_clientèle = Column(String(100)) # Chargé de clientèle
    redacteur_production = Column(String(100)) # Rédacteur
    code_client = Column(String(50), unique=True) # Visible sur la capture
    vip_status = Column(String(10))       # Oui/Non

    # --- II. ÉTAT CIVIL & IDENTITÉ (Bloc 2 du formulaire) ---
    civilite = Column(String(20))         # M., Mme, Mlle (Intitulé sur capture)
    nom = Column(String(100), nullable=False) # Nom Client / Raison Sociale
    prenom = Column(String(100))          # Prénoms
    date_naissance = Column(Date)         # Date de Naissance
    nationalite = Column(String(100))     # Nationalité
    num_contribuable = Column(String(100)) # N° Contribuable (IFU)
    
    # Nouveaux champs de la capture d'écran
    cat_socio_prof = Column(String(10))    # Code catégorie socio-pro
    libelle_socio_prof = Column(String(100)) # Libellé (ex: Ingénieur)

    # --- III. COORDONNÉES & CONTACT (Bloc 3 du formulaire) ---
    telephone = Column(String(50))        # Téléphone Bureau
    tel_portable = Column(String(50))     # Téléphone Portable
    fax = Column(String(50))              # Fax
    email = Column(String(100))           # Email
    adresse = Column(Text)                # Adresse 1
    adresse_2 = Column(Text)              # Adresse 2
    ville = Column(String(100))           # Ville

    # --- IV. PERMIS DE CONDUIRE (Bloc 4 du formulaire) ---
    cat_permis = Column(String(20))       # Catégorie (A, B, C...)
    num_permis = Column(String(100))      # N° de Permis
    date_permis = Column(Date)            # Date d'Obtention

    # --- DOCUMENTS & MÉDIA ---
    photo_path = Column(String(255))      # Chemin vers l'image biométrique
    
    # --- RELATIONS ---
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    fleets = relationship("Fleet", back_populates="owner", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="contact", cascade="all, delete-orphan")

    # Dans contact_models.py
vehicles = relationship("Vehicle", back_populates="owner") # "Vehicle" en string

# Dans flottes_models.py
owner = relationship("Contact", back_populates="vehicles") # "Contact" en string
    
    # --- TRAÇABILITÉ ---
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey('utilisateurs.id'))
    updated_by = Column(Integer, ForeignKey('utilisateurs.id'))
    created_ip = Column(String(45))
    last_ip = Column(String(45))

    creator = relationship("User", foreign_keys=[created_by])
    editor = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<Contact(ID={self.id}, Nom='{self.nom}', Nature='{self.nature}')>"
    
class ContactAuditLog(Base):
    __tablename__ = "contact_audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('utilisateurs.id'))
    contact_id = Column(Integer, nullable=True)
    action = Column(String(100)) # "CRÉATION", "MODIFICATION", "SUPPRESSION"
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True) # 45 pour supporter IPv6