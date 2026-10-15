"""
Modèle des paramètres applicatifs (configurables depuis l'UI)
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from datetime import datetime

from core.database import Base, AuditableMixin


class LometaParametre(Base, AuditableMixin):
    """
    Paramètre applicatif.
    
    Permet de rendre configurables :
    - Délais (prescription, relance, etc.)
    - Seuils (validation, etc.)
    - Comptes comptables
    - Taux de répartition par défaut
    - Etc.
    """
    __tablename__ = "lometa_parametres"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    valeur = Column(Text, nullable=True)
    type_donnee = Column(String(20), nullable=False, default="STRING")
    # Valeurs : INT, DECIMAL, STRING, BOOL, DATE, JSON
    
    categorie = Column(String(50), nullable=True, index=True)
    # Valeurs : RECOURS, COMPTABILITE, REGLEMENT, EXPERTISE, GENERAL
    
    description = Column(Text, nullable=True)
    ordre_affichage = Column(Integer, nullable=False, default=0)
    
    # Relations
    
    def __repr__(self):
        return f"<LometaParametre {self.code}={self.valeur}>"