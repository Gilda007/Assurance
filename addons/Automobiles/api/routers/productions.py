# addons/Automobiles/api/routers/productions.py - Version complète avec toutes les étapes

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import logging

from ..schemas import (
    ProductionRequestSchema,
    SuccessResponseSchema,
    ProductionResponseSchema,
    CertificateResponseSchema,
    ErrorResponseSchema
)
from ..services import (
    ProductionValidator, DateRangeValidator, 
    BusinessRuleValidator, AdditionalValidators,
    TariffController, ProductionAuthorizer
)
from ..utils.security import get_current_user
from ..database import get_db, get_lometa_db  # ← AJOUTER get_lometa_db
from .. import models_db
from ..lometa_client import LometaDataProvider  # ← AJOUTER

logger = logging.getLogger(__name__)
router = APIRouter()



@router.post(
    "/productions",
    response_model=SuccessResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseSchema},
        401: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema},
        500: {"model": ErrorResponseSchema}
    }
)
async def create_production(
    request: ProductionRequestSchema,
    current_user: models_db.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée une ou plusieurs productions d'attestations
    """
    logger.info(f"Réception d'une demande de production: {len(request.productions)} attestation(s)")
    logger.info(f"Utilisateur: {current_user.username}")
    logger.info(f"Bureau: {request.office_code}, Compagnie: {request.organization_code}")
    
    # ========== ÉTAPE 1: VALIDATION DES CHAMPS INDIVIDUELS ==========
    validator = ProductionValidator()
    is_valid, errors = validator.validate_production_request(request)
    
    if not is_valid:
        logger.warning(f"Erreurs de validation (étape 1): {errors}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Erreur de validation des données", "errors": errors}
        )
    
    # ========== ÉTAPE 2: VALIDATION DES DATES ==========
    for idx, prod in enumerate(request.productions):
        is_valid, error = DateRangeValidator.validate_starts_at(prod.starts_at)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erreur de validation des dates",
                    "errors": {f"productions.{idx}.starts_at": [error]}
                }
            )
        
        is_valid, error = DateRangeValidator.validate_contract_duration(
            prod.starts_at, prod.ends_at
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erreur de validation des dates",
                    "errors": {f"productions.{idx}.ends_at": [error]}
                }
            )
    
    # ========== ÉTAPE 3: RÈGLES MÉTIER ==========
    business_validator = BusinessRuleValidator(db)
    is_valid, business_errors = business_validator.validate_batch(request.productions)
    
    if not is_valid:
        logger.warning(f"Erreurs de règles métier: {business_errors}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Erreur de validation des règles métier", "errors": business_errors}
        )
    
    # ========== ÉTAPE 4: VALIDATIONS COMPLÉMENTAIRES ==========
    for idx, prod in enumerate(request.productions):
        if prod.insured_birthdate:
            is_valid, error = AdditionalValidators.validate_insured_age(prod.insured_birthdate)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "message": "Erreur de validation",
                        "errors": {f"productions.{idx}.insured_birthdate": [error]}
                    }
                )
        
        is_valid, error = AdditionalValidators.validate_driver_age(prod.driver_birthdate)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erreur de validation",
                    "errors": {f"productions.{idx}.driver_birthdate": [error]}
                }
            )
        
        is_valid, error = AdditionalValidators.validate_licence_experience(prod.driver_licence_issued_at)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erreur de validation",
                    "errors": {f"productions.{idx}.driver_licence_issued_at": [error]}
                }
            )
    
    # ========== ÉTAPE 5: CONTRÔLE TARIFAIRE RC ==========
    tariff_controller = TariffController(db)
    is_valid, tariff_errors = tariff_controller.validate_batch(request.productions)
    
    if not is_valid:
        logger.warning(f"Erreurs tarifaires: {tariff_errors}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=tariff_errors
        )
    
    # ========== ÉTAPE 6: VÉRIFICATION DES AUTORISATIONS ==========
    # Pour la première production, prendre les infos communes
    first_prod = request.productions[0]
    variant_code = first_prod.certificate_variant_code
    
    authorizer = ProductionAuthorizer(db)
    is_authorized, error_msg, auth_context = authorizer.authorize_production(
        office_code=request.office_code,
        organization_code=request.organization_code,
        certificate_variant_code=variant_code,
        user=current_user,
        quantity=len(request.productions)
    )
    
    if not is_authorized:
        logger.warning(f"Échec d'autorisation: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": error_msg}
        )
    
    # ========== ÉTAPE 7: CRÉATION DE LA PRODUCTION ==========
    # Récupérer les IDs
    organization = auth_context["organization"]
    office = auth_context["office"]
    variant = auth_context["certificate_variant"]
    
    # Générer les références
    production_id = f"pro_{uuid.uuid4().hex[:15]}"
    production_ref = f"PROD-{datetime.now().strftime('%m%Y')}-{uuid.uuid4().hex[:10].upper()}"
    now = datetime.now()
    
    # Créer la production en base
    db_production = models_db.Production(
        reference=production_ref,
        channel=request.channel,
        quantity=len(request.productions),
        office_code=request.office_code,
        organization_code=request.organization_code,
        certificate_type_id=1,  # TODO: Récupérer depuis la base
        certificate_variant_id=variant.id,
        user_id=current_user.id,
        office_id=office.id,
        organization_id=organization.id,
        state="processing"
    )
    db.add(db_production)
    db.flush()
    
    # Réserver le stock
    reserve_success = authorizer.reserve_certificates(auth_context, db_production.id, len(request.productions))
    if not reserve_success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Erreur lors de la réservation des attestations"}
        )
    
    # Créer les certificats
    certificates = []
    for prod in request.productions:
        cert_ref = f"ATD-{uuid.uuid4().hex[:10].upper()}"
        
        db_certificate = models_db.Certificate(
            reference=cert_ref,
            production_id=db_production.id,
            licence_plate=prod.licence_plate,
            chassis_number=prod.vehicle_chassis,
            police_number=prod.police_number,
            insured_name=prod.insured_name,
            insured_phone=prod.insured_phone,
            starts_at=prod.starts_at,
            ends_at=prod.ends_at,
            taxpayer_number=prod.taxpayer_number,
            dta_amount=prod.dta,
            rc_amount=prod.rc,
            state="active"
        )
        db.add(db_certificate)
        certificates.append(db_certificate)
    
    # Mettre à jour le statut de la production
    db_production.state = "completed"
    db_production.completed_at = now
    db.commit()
    
    # Construire la réponse
    cert_responses = []
    for cert in certificates:
        cert_responses.append(CertificateResponseSchema(
            reference=cert.reference,
            download_link=f"/api/v1/certificates/{cert.reference}/download",
            licence_plate=cert.licence_plate,
            chassis_number=cert.chassis_number,
            police_number=cert.police_number,
            insured_name=cert.insured_name,
            insured_phone=cert.insured_phone,
            starts_at=cert.starts_at.strftime("%d/%m/%Y"),
            ends_at=cert.ends_at.strftime("%d/%m/%Y")
        ))
    
    production_response = ProductionResponseSchema(
        id=db_production.reference,
        reference=db_production.reference,
        channel=db_production.channel,
        quantity=db_production.quantity,
        sent_to_storage=False,
        download_link=f"/api/v1/productions/{db_production.reference}/download",
        certificates=cert_responses,
        created_at=now,
        formatted_created_at=now.strftime("%d/%m/%Y %H:%M")
    )
    
    logger.info(f"✅ Production créée avec succès: {production_ref} ({len(certificates)} attestations)")
    
    return SuccessResponseSchema(
        status=201,
        message="La demande d'édition a été effectuée avec succès",
        data=production_response
    )

@router.post("/productions/from-vehicle/{vehicle_id}")
async def create_production_from_vehicle(
    vehicle_id: int,
    current_user: models_db.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    lometa_db: Session = Depends(get_lometa_db)  # Maintenant défini
):
    """
    Crée une production à partir d'un véhicule existant dans LOMETA
    """
    try:
        # Récupérer les données LOMETA
        provider = LometaDataProvider(lometa_db)
        production_request = provider.build_production_from_vehicle(vehicle_id)
        
        if not production_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Véhicule ou contrat non trouvé"
            )
        
        # Convertir en schéma Pydantic
        from ..schemas import ProductionRequestSchema
        request_schema = ProductionRequestSchema(**production_request)
        
        # Valider et créer la production (réutiliser la fonction existante)
        return await create_production(request_schema, current_user, db)
        
    except Exception as e:
        logger.error(f"Erreur lors de la création depuis LOMETA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/vehicles/{licence_plate}/asac-status")
async def check_vehicle_asac_status(
    licence_plate: str,
    current_user: models_db.User = Depends(get_current_user),
    lometa_db: Session = Depends(get_lometa_db)
):
    """
    Vérifie si un véhicule a déjà une attestation ASAC
    """
    try:
        provider = LometaDataProvider(lometa_db)
        vehicle = provider.get_vehicle_by_plate(licence_plate)
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Véhicule non trouvé"
            )
        
        # Vérifier dans la base ASAC si ce véhicule a déjà une attestation
        # À implémenter selon vos besoins
        
        return {
            "licence_plate": licence_plate,
            "has_asac_certificate": False,  # À remplacer par une vraie vérification
            "message": "Vérification effectuée"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )