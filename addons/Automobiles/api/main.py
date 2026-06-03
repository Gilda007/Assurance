# addons/Automobiles/api/main.py
"""
API ASAC - Point d'entrée principal
"""

import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings, LOGGING_CONFIG
from .routers import auth, productions
from .database import init_db
from . import models_db  # Import des modèles

# Configuration du logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    """
    # Démarrage
    logger.info(f"🚀 Démarrage de {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"📁 Stockage: {settings.STORAGE_PATH}")
    logger.info(f"🗄️ Base de données: {settings.DATABASE_URL}")
    
    # Initialiser la base de données (sera fait à l'étape 3)
    # init_database()
    
    yield
    
    # Arrêt
    logger.info("🛑 Arrêt de l'API ASAC")


# Création de l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    API ASAC pour l'édition d'attestations d'assurance automobile.
    
    ## Fonctionnalités
    
    - Authentification par token JWT
    - Création de productions d'attestations
    - Validation des données (champs, codifications, règles métier)
    - Contrôle tarifaire RC
    - Génération de certificats PDF
    
    ## Version 1.2
    
    Champs obligatoires ajoutés :
    - insured_profession, insured_city, taxpayer_number
    - driver_name, driver_birthdate, driver_licence_number
    - driver_licence_category, driver_licence_issued_at
    - circulation_zone, fiscal_power, DTA, CODE_ASSURE
    """,
    lifespan=lifespan,
)


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inclusion des routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(productions.router, prefix=settings.API_V1_PREFIX, tags=["Productions"])


# ============================================================================
# ENDPOINTS DE BASE
# ============================================================================

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé"""
    return {
        "status": "healthy",
        "timestamp": logging.Formatter().formatTime(None),
        "storage_path": str(settings.STORAGE_PATH),
        "debug": settings.DEBUG
    }


@app.get("/api/v1/status")
async def api_status():
    """Statut de l'API"""
    return {
        "status": "operational",
        "version": settings.VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }


# ============================================================================
# GESTIONNAIRES D'ERREURS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Une erreur interne est survenue",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


# Point d'entrée pour exécution directe
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "addons.Automobiles.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )