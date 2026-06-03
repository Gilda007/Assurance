# addons/Automobiles/api/routers/auth.py
"""
Routes d'authentification
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import logging

from ..schemas import TokenRequest, TokenResponse
from ..database import get_db
from .. import models_db, crud
from ..config import settings
from ..utils.security import create_access_token, get_current_user, get_token_from_header

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/tokens/app-key", response_model=TokenResponse)
async def generate_token(
    app_key: str,
    username: str,
    db: Session = Depends(get_db)
):
    """
    Génère un token d'authentification JWT
    
    - **app_key**: Clé applicative (obligatoire)
    - **username**: Nom d'utilisateur (obligatoire)
    
    Retourne un token JWT valide pour les requêtes ultérieures.
    """
    logger.info(f"Tentative d'authentification: username={username}")
    
    # Vérifier que les paramètres sont fournis
    if not app_key or not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="app_key et username sont requis"
        )
    
    # 1. Vérifier l'utilisateur par sa clé applicative
    user = crud.get_user_by_app_key(db, app_key)
    
    if not user:
        logger.warning(f"Clé applicative invalide: {app_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé applicative invalide"
        )
    
    # 2. Vérifier le nom d'utilisateur
    if user.username != username:
        logger.warning(f"Nom d'utilisateur invalide pour la clé {app_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur invalide"
        )
    
    # 3. Vérifier que l'utilisateur est actif
    if not user.is_active:
        logger.warning(f"Utilisateur inactif: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur désactivé"
        )
    
    # 4. Générer le token JWT
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "app_key": user.app_key
    }
    
    token = create_access_token(token_data)
    expires_at = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    
    # 5. Sauvegarder le token en base de données
    office_code = user.office.code if user.office else "NSIA"
    token_name = f"Logiciel Auto {office_code}"
    
    db_token = crud.create_user_token(
        db=db,
        user_id=user.id,
        token=token,
        token_name=token_name,
        expires_at=expires_at
    )
    
    # 6. Mettre à jour la dernière connexion
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"✅ Authentification réussie: {username}, token: {db_token.token_name}")
    
    return TokenResponse(
        token=token,
        token_name=token_name,
        expires_at=expires_at
    )


@router.post("/auth/tokens/revoke")
async def revoke_token(
    request: Request,
    current_user: models_db.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Révoque le token actuel (déconnexion)
    """
    token = get_token_from_header(request)
    
    if token:
        db_token = db.query(models_db.UserToken).filter(
            models_db.UserToken.token == token
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db.commit()
            logger.info(f"Token révoqué pour l'utilisateur: {current_user.username}")
    
    return {"message": "Token révoqué avec succès"}


@router.get("/auth/verify")
async def verify_token(
    current_user: models_db.User = Depends(get_current_user)
):
    """
    Vérifie la validité du token actuel
    """
    return {
        "status": "valid",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "office_code": current_user.office.code if current_user.office else None
        }
    }