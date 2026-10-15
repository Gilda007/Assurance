"""
Modèles de gestion des rôles et permissions (RBAC)
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base, AuditableMixin


# ============================================================
# TABLE D'ASSOCIATION Role ↔ Permission
# ============================================================
role_permissions = Table(
    'lometa_role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('lometa_roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('lometa_permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
)


# ============================================================
# TABLE Role
# ============================================================
class LometaRole(Base, AuditableMixin):
    """
    Rôle système (admin, gestionnaire, responsable, comptable, expert)
    """
    __tablename__ = 'lometa_roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    libelle = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    niveau = Column(Integer, nullable=False, default=0)  # 0=base, 100=admin
    est_systeme = Column(Boolean, default=False, nullable=False)  # Non supprimable
    est_actif = Column(Boolean, default=True, nullable=False, index=True)

    created_by = Column(Integer, ForeignKey('utilisateurs.id'), nullable=False)
    
    # Relations
    permissions = relationship(
        "LometaPermission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    
    def __repr__(self):
        return f"<LometaRole {self.code}>"
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Vérifie si ce rôle possède une permission"""
        for perm in self.permissions:
            if perm.ressource == resource and perm.action == action:
                return perm.autorise
        return False


# ============================================================
# TABLE Permission
# ============================================================
class LometaPermission(Base, AuditableMixin):
    """
    Permission élémentaire (ressource + action)
    Exemple: ('sinistre', 'create')
    """
    __tablename__ = 'lometa_permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    ressource = Column(String(50), nullable=False, index=True)
    action = Column(String(20), nullable=False)  # CREATE, READ, UPDATE, DELETE
    autorise = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relations
    roles = relationship(
        "LometaRole",
        secondary=role_permissions,
        back_populates="permissions",
    )
    
    def __repr__(self):
        return f"<Permission {self.code}>"


# ============================================================
# TABLE UserRole (association Utilisateur ↔ Rôle)
# ============================================================
class LometaUserRole(Base, AuditableMixin):
    """
    Association entre utilisateur et rôle (un user peut avoir plusieurs rôles)
    """
    __tablename__ = 'lometa_user_roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateurs.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('lometa_roles.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Contexte (optionnel) — pour multi-société
    societe = Column(String(100), nullable=True)
    branche = Column(String(50), nullable=True)
    
    # Dates
    date_debut = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_fin = Column(DateTime, nullable=True)
    est_actif = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relations
    role = relationship("LometaRole")
    
    def __repr__(self):
        return f"<UserRole user={self.utilisateur_id} role={self.role_id}>"