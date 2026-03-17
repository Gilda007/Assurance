from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
import bcrypt
from core.database import Base

class User(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="agent")  # admin, agent, superviseur
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hache le mot de passe avant de l'enregistrer."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hachage."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class AuditUserLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('utilisateurs.id'))
    action = Column(String(100)) # ex: "CRÉATION UTILISATEUR", "SUPPRESSION"
    details = Column(Text)       # ex: "Utilisateur 'Dams' supprimé"
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)