# core/optimized_models.py
"""
Optimisations des relations et chargement eager par défaut
"""

from sqlalchemy.orm import defaultload, joinedload, selectinload
from sqlalchemy.ext.declarative import declared_attr

class OptimizedMixin:
    """Mixin pour optimiser les relations par défaut"""
    
    @declared_attr
    def __mapper_args__(cls):
        return {
            'eager_defaults': True,  # Charger les valeurs par défaut immédiatement
            'confirm_deleted_rows': False  # Désactiver la vérification des suppressions
        }


class OptimizedRelationship:
    """Classes de relations optimisées pour le serveur distant"""
    
    @staticmethod
    def one_to_many(cls, **kwargs):
        """Relation one-to-many avec chargement selectin par défaut"""
        return relationship(
            cls,
            lazy='selectin',  # Chargement en une seule requête au lieu de N+1
            join_depth=2,     # Limite la profondeur des jointures
            **kwargs
        )
    
    @staticmethod
    def many_to_one(cls, **kwargs):
        """Relation many-to-one avec chargement joined par défaut"""
        return relationship(
            cls,
            lazy='joined',    # Jointure directe
            **kwargs
        )
    
    @staticmethod
    def many_to_many(cls, **kwargs):
        """Relation many-to-many avec selectin"""
        return relationship(
            cls,
            lazy='selectin',
            **kwargs
        )