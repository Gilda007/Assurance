# models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, Float, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModuleVersion(Base):
    """Version d'un module"""
    __tablename__ = 'module_versions'
    
    id = Column(Integer, primary_key=True)
    module_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    display_name = Column(String(200))
    description = Column(Text)
    author = Column(String(100))
    icon = Column(String(10), default='📦')
    category = Column(String(50))
    changelog = Column(Text)
    file_size = Column(Integer, default=0)
    checksum = Column(String(256))
    download_url = Column(String(500))
    requirements = Column(Text)  # JSON list des dépendances
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    downloads = relationship("Download", back_populates="module_version")
    
    __table_args__ = (
        UniqueConstraint('module_name', 'version', name='uq_module_version'),
        Index('idx_module_name_active', 'module_name', 'is_active'),
        Index('idx_module_version', 'module_name', 'version'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_name': self.module_name,
            'version': self.version,
            'display_name': self.display_name,
            'description': self.description,
            'author': self.author,
            'icon': self.icon,
            'category': self.category,
            'changelog': self.changelog,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'download_url': self.download_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<ModuleVersion {self.module_name} v{self.version}>"


class Download(Base):
    """Historique des téléchargements"""
    __tablename__ = 'downloads'
    
    id = Column(Integer, primary_key=True)
    module_version_id = Column(Integer, ForeignKey('module_versions.id'))
    client_id = Column(String(100))
    client_name = Column(String(200))
    client_version = Column(String(50))
    client_ip = Column(String(50))
    user_agent = Column(String(500))
    download_date = Column(DateTime, default=datetime.now)
    
    # Relation
    module_version = relationship("ModuleVersion", back_populates="downloads")
    
    __table_args__ = (
        Index('idx_download_date', 'download_date'),
        Index('idx_client_id', 'client_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_name': self.module_version.module_name if self.module_version else None,
            'version': self.module_version.version if self.module_version else None,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'client_ip': self.client_ip,
            'download_date': self.download_date.isoformat() if self.download_date else None,
        }


class Client(Base):
    """Clients enregistrés"""
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(String(100), unique=True, nullable=False)
    client_name = Column(String(200))
    app_version = Column(String(50))
    last_check = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_client_id_active', 'client_id', 'is_active'),
        Index('idx_last_check', 'last_check'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'app_version': self.app_version,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'is_active': self.is_active,
        }


class UpdateLog(Base):
    """Logs des mises à jour"""
    __tablename__ = 'update_logs'
    
    id = Column(Integer, primary_key=True)
    action = Column(String(50), nullable=False)
    module_name = Column(String(100))
    version = Column(String(50))
    status = Column(String(20), default='info')
    message = Column(Text)
    client_id = Column(String(100))
    client_ip = Column(String(50))
    timestamp = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_action_status', 'action', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'module_name': self.module_name,
            'version': self.version,
            'status': self.status,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }