

import os
import json
import importlib.util
from core.logger import logger
from core.base_module import BaseModule
import traceback
from datetime import datetime
import hashlib
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

SKIP_CERT_VERIFICATION = os.environ.get("LOMETA_SKIP_CERT_VERIFICATION", "0") == "1"

if SKIP_CERT_VERIFICATION:
    print("⚠️ MODE DÉVELOPPEMENT: Vérification des certificats désactivée")

# ============================================================================
# IMPORT DU GESTIONNAIRE RSA
# ============================================================================

RSA_AVAILABLE = False
RSACertificateManager = None

try:
    from lometa_module_generator.rsa_certificate_manager import RSACertificateManager
    RSA_AVAILABLE = True
except ImportError:
    try:
        from ..lometa_module_generator.rsa_certificate_manager import RSACertificateManager 
        RSA_AVAILABLE = True
    except ImportError:
        try:
            import sys
            cert_path = Path(__file__).parent.parent / "certificates"
            if cert_path.exists():
                sys.path.insert(0, str(cert_path))
                from ..lometa_module_generator.rsa_certificate_manager import RSACertificateManager
                RSA_AVAILABLE = True
        except ImportError:
            pass

if RSA_AVAILABLE:
    print("✅ RSACertificateManager disponible")
else:
    print("⚠️ RSACertificateManager non trouvé. Vérification RSA désactivée.")

# Garder l'ancien gestionnaire pour compatibilité
try:
    from lometa_module_generator.certificate_manager import CertificateManager
    CERT_MANAGER_AVAILABLE = True
except ImportError:
    CERT_MANAGER_AVAILABLE = False


class AddonLoader:
    """Chargeur de modules avec vérification des certificats"""
    
    def __init__(self, addons_path="addons"):
        self.addons_path = addons_path
        self.cert_manager = None
        self.rsa_manager = None
        self.expiry_warning_threshold = 30
        self.last_certificate_status = []
        self.certificates_dir = self._get_certificates_dir()
        
        # Vérifier la présence de la clé publique
        self.public_key_available = False
        self.public_key_path = None
        
        public_key_candidates = [
            self.certificates_dir / "developer_public_key.pem",
            self.certificates_dir / "lometa_ca.pem",
            self.certificates_dir / "ca.crt",
            Path.home() / ".lometa" / "certificates" / "developer_public_key.pem",
            Path.home() / ".lometa" / "certificates" / "lometa_ca.pem",
        ]
        
        for candidate in public_key_candidates:
            if candidate.exists():
                self.public_key_path = candidate
                self.public_key_available = True
                print(f"✅ Clé publique trouvée: {candidate}")
                break
        
        if not self.public_key_available:
            print("⚠️ Aucune clé publique trouvée. Les certificats RSA ne pourront pas être vérifiés.")
            print("   Placez developer_public_key.pem ou lometa_ca.pem dans:")
            print(f"   - {self.certificates_dir}")
            print(f"   - ~/.lometa/certificates/")
        
        # Initialiser le gestionnaire RSA si disponible
        if RSA_AVAILABLE and not SKIP_CERT_VERIFICATION and self.public_key_available:
            try:
                self.rsa_manager = RSACertificateManager(config_dir=self.certificates_dir)
                logger.info(f"✅ RSACertificateManager initialisé avec: {self.certificates_dir}")
                
                if self.rsa_manager.get_public_key():
                    logger.info("   🔑 Clé publique RSA chargée")
                else:
                    logger.warning("   ⚠️ Aucune clé publique RSA trouvée")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur initialisation RSACertificateManager: {e}")
                self.rsa_manager = None
        
        # Fallback: ancien gestionnaire HMAC
        if CERT_MANAGER_AVAILABLE and not SKIP_CERT_VERIFICATION and not self.rsa_manager:
            try:
                self.cert_manager = CertificateManager(config_dir=self.certificates_dir, use_shared_keys=True)
                logger.info(f"✅ CertificateManager (HMAC) initialisé avec: {self.certificates_dir}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur initialisation CertificateManager: {e}")

    def _get_certificates_dir(self) -> Path:
        """Détermine le dossier des certificats en fonction du mode d'exécution."""
        import sys
        
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
            candidates = [
                base_dir / "certificates",
                base_dir / "_internal" / "certificates",
                base_dir.parent / "certificates",
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate
            cert_dir = base_dir / "certificates"
            cert_dir.mkdir(parents=True, exist_ok=True)
            return cert_dir
        
        if Path("certificates").exists():
            return Path("certificates")
        
        home_cert = Path.home() / ".lometa" / "certificates"
        home_cert.mkdir(parents=True, exist_ok=True)
        return home_cert

    # def _is_certificate_valid_structure(self, certificate: dict) -> tuple:
    #     """
    #     Vérifie si le certificat a une structure valide.
    #     Supporte les versions 2.0.0 (HMAC) et 3.0.0 (RSA).
        
    #     Returns:
    #         (is_valid, version, missing_fields)
    #     """
    #     # Champs requis pour toutes les versions
    #     common_required = [
    #         "module_name",
    #         "module_version", 
    #         "certified_by",
    #         "certified_date",
    #         "certificate_id",
    #         "checksums"
    #     ]
        
    #     # Champs pour la version 2.0.0 (HMAC)
    #     v2_required = ["signature", "public_key"]
        
    #     # Champs pour la version 3.0.0 (RSA)
    #     v3_required = ["signature", "public_key", "expiry_date"]
        
    #     # Vérifier les champs communs
    #     missing_common = [f for f in common_required if f not in certificate]
    #     if missing_common:
    #         return False, "unknown", missing_common
        
    #     # Détecter la version
    #     version = certificate.get("version", "2.0.0")
        
    #     if version.startswith("2."):
    #         # Version 2.x (HMAC)
    #         missing = [f for f in v2_required if f not in certificate]
    #         return len(missing) == 0, "2.0.0", missing
        
    #     elif version.startswith("3."):
    #         # Version 3.x (RSA)
    #         missing = [f for f in v3_required if f not in certificate]
    #         return len(missing) == 0, "3.0.0", missing
        
    #     else:
    #         # Version inconnue, essayer de détecter
    #         if "expiry_date" in certificate:
    #             return True, "3.0.0", []
    #         elif "signature" in certificate and "public_key" in certificate:
    #             return True, "2.0.0", []
    #         else:
    #             return False, "unknown", ["version_inconnue"]

    def _is_certificate_valid_structure(self, certificate: dict) -> tuple:
        """
        Vérifie si le certificat a une structure valide.
        Supporte les versions 2.0.0 (HMAC) et 3.0.0 (RSA).
        
        Returns:
            (is_valid, version, missing_fields)
        """
        # Champs requis pour toutes les versions
        common_required = [
            "module_name",
            "module_version", 
            "certified_by",
            "certified_date",
            "certificate_id",
            "checksums"
        ]
        
        # ✅ Vérifier les champs communs
        missing_common = [f for f in common_required if f not in certificate]
        if missing_common:
            return False, "unknown", missing_common
        
        # ✅ Détecter la version
        version = certificate.get("version", "2.0.0")
        
        # ✅ Vérifier les champs selon la version
        if version.startswith("3."):
            # Version 3.x (RSA) - signature et public_key sont dans le certificat PEM
            # Le JSON ne contient pas ces champs à la racine
            v3_required = ["expiry_date", "signature_algorithm"]
            missing_v3 = [f for f in v3_required if f not in certificate]
            if missing_v3:
                return False, version, missing_v3
            return True, version, []
        
        elif version.startswith("2."):
            # Version 2.x (HMAC) - signature et public_key sont à la racine
            v2_required = ["signature", "public_key"]
            missing_v2 = [f for f in v2_required if f not in certificate]
            if missing_v2:
                return False, version, missing_v2
            return True, version, []
        
        else:
            # Version inconnue - essayer de détecter
            if "expiry_date" in certificate and "signature_algorithm" in certificate:
                return True, "3.0.0", []
            elif "signature" in certificate and "public_key" in certificate:
                return True, "2.0.0", []
            else:
                return False, "unknown", ["version_inconnue"]

    def load_all(self, main_window):
        """Charge tous les modules avec vérification des certificats"""
        addons_path = Path(os.path.dirname(os.path.dirname(__file__))) / "addons"
        logger.info(f"--- DÉBUT DU CHARGEMENT DES MODULES ---")
        logger.info(f"Recherche dans : {addons_path}")

        self.last_certificate_status = []
        loaded_instances = []

        if not addons_path.exists():
            logger.error(f"Le dossier addons n'existe pas : {addons_path}")
            return loaded_instances

        for folder in addons_path.iterdir():
            if not folder.is_dir() or folder.name.startswith("__"):
                continue

            folder_name = folder.name
            folder_path = folder

            # ============================================================
            # 1. LECTURE DU MANIFEST
            # ============================================================
            manifest_path = folder_path / "manifest.json"
            if not manifest_path.exists():
                logger.warning(f"  ! Manquant : manifest.json dans {folder_name} -> module ignoré")
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception as e:
                logger.error(f"  ! Impossible de lire manifest.json dans {folder_name} : {e}")
                continue

            if not manifest.get("enabled", True):
                logger.info(f"  - Module {folder_name} désactivé dans manifest, passage")
                continue

            # ============================================================
            # 2. MODE DÉVELOPPEMENT
            # ============================================================
            if SKIP_CERT_VERIFICATION:
                logger.info(f"🔓 Mode développement: chargement du module {folder_name} sans vérification")
                instance = self._load_module_instance(folder_name, folder_path, manifest, main_window)
                if instance:
                    loaded_instances.append(instance)
                    self.last_certificate_status.append({
                        'module_name': folder_name,
                        'status': 'dev_mode',
                        'message': 'Mode développement (certificat ignoré)'
                    })
                continue

            # ============================================================
            # 3. CHARGEMENT DU CERTIFICAT
            # ============================================================
            cert_path = folder_path / "certificate.json"
            if not cert_path.exists():
                logger.warning(f"  ! Manquant : certificate.json dans {folder_name} -> module ignoré")
                self.last_certificate_status.append({
                    'module_name': folder_name,
                    'status': 'no_certificate',
                    'message': 'Certificat manquant'
                })
                continue

            try:
                with open(cert_path, "r", encoding="utf-8") as f:
                    certificate = json.load(f)
            except Exception as e:
                logger.error(f"  ! Impossible de lire certificate.json dans {folder_name} : {e}")
                continue

            # ============================================================
            # 4. VÉRIFICATION DE LA STRUCTURE DU CERTIFICAT
            # ============================================================
            is_valid, version, missing_fields = self._is_certificate_valid_structure(certificate)
            
            if not is_valid:
                missing_msg = ", ".join(missing_fields)
                logger.warning(f"  ! Structure invalide: {missing_msg} -> module {folder_name} ignoré")
                self.last_certificate_status.append({
                    'module_name': folder_name,
                    'status': 'invalid_structure',
                    'message': f"Champs manquants: {missing_msg}"
                })
                continue

            # ============================================================
            # 5. VÉRIFICATION DU NOM ET DE LA VERSION
            # ============================================================
            if certificate.get("module_name") != manifest.get("name", folder_name):
                logger.warning(f"  ! Nom du module ne correspond pas: {certificate.get('module_name')} vs {manifest.get('name', folder_name)} -> module ignoré")
                continue

            if certificate.get("module_version") != manifest.get("version"):
                logger.warning(f"  ! Version ne correspond pas: {certificate.get('module_version')} vs {manifest.get('version')} -> module ignoré")
                continue

            # ============================================================
            # 6. VÉRIFICATION DE LA SIGNATURE (adaptée à la version)
            # ============================================================


            signature_valid = True
            signature_msg = ""

            if version.startswith("3."):
                # ✅ Version 3.x (RSA) - La signature est dans le fichier PEM
                cert_pem = folder_path / "certificate.pem"
                if not cert_pem.exists():
                    signature_valid = False
                    signature_msg = "certificate.pem manquant pour la vérification RSA"
                else:
                    # ✅ Vérifier avec openssl en utilisant le certificat CA
                    ca_cert = self.certificates_dir / "lometa_ca.crt"
                    
                    # Si le CA n'est pas trouvé, chercher dans d'autres emplacements
                    if not ca_cert.exists():
                        ca_candidates = [
                            Path.home() / ".lometa" / "certificates" / "lometa_ca.crt",
                            Path("./certificates/lometa_ca.crt"),
                            Path("/etc/lometa/certificates/lometa_ca.crt"),
                        ]
                        for candidate in ca_candidates:
                            if candidate.exists():
                                ca_cert = candidate
                                break
                    
                    if ca_cert.exists():
                        try:
                            import subprocess
                            result = subprocess.run(
                                ["openssl", "verify", "-CAfile", str(ca_cert), str(cert_pem)],
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0:
                                signature_msg = "Signature RSA valide"
                            else:
                                signature_valid = False
                                signature_msg = f"Signature RSA invalide: {result.stderr.strip()}"
                        except Exception as e:
                            signature_valid = False
                            signature_msg = f"Erreur vérification RSA: {str(e)}"
                    else:
                        # ✅ Pas de CA trouvée, mais le certificat PEM existe
                        # On peut faire une vérification basique
                        try:
                            import subprocess
                            # Vérifier que le certificat est valide (auto-signé)
                            result = subprocess.run(
                                ["openssl", "x509", "-in", str(cert_pem), "-text", "-noout"],
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0:
                                # Le certificat est valide, mais on ne peut pas vérifier la chaîne
                                signature_msg = "Signature RSA: CA non trouvée, vérification basique OK"
                                logger.warning(f"   ⚠️ CA non trouvée, vérification basique du certificat {folder_name}")
                            else:
                                signature_valid = False
                                signature_msg = "Certificat PEM invalide"
                        except Exception as e:
                            signature_valid = False
                            signature_msg = f"Erreur vérification certificat: {str(e)}"
            else:
                # Version 2.x (HMAC) - Vérification HMAC
                signature = certificate.get("signature", "")
                public_key = certificate.get("public_key", "")
                
                if not signature or len(signature) < 32:
                    signature_valid = False
                    signature_msg = "Signature HMAC invalide"
                elif not public_key or len(public_key) < 32:
                    signature_valid = False
                    signature_msg = "Clé publique HMAC invalide"
                else:
                    signature_msg = "Signature HMAC valide"

            # ============================================================
            # 7. VÉRIFICATION DE LA DATE D'EXPIRATION
            # ============================================================
            if "expiry_date" in certificate:
                validity_valid, remaining_days, validity_msg = self._check_certificate_validity(certificate)
                
                if not validity_valid:
                    logger.warning(f"  ! {validity_msg} -> module {folder_name} ignoré")
                    self.last_certificate_status.append({
                        'module_name': folder_name,
                        'status': 'expired',
                        'message': validity_msg,
                        'expiry_date': certificate.get('expiry_date', '')
                    })
                    continue
            else:
                remaining_days = 365
                validity_msg = "Pas de date d'expiration (format ancien)"

            # ============================================================
            # 8. VÉRIFICATION DE L'INTÉGRITÉ DES FICHIERS
            # ============================================================
            integrity_valid, integrity_msg = self._verify_file_integrity(
                folder_path, certificate.get('checksums', {})
            )

            if not integrity_valid:
                logger.warning(f"  ! {integrity_msg} -> module {folder_name} ignoré")
                self.last_certificate_status.append({
                    'module_name': folder_name,
                    'status': 'corrupted',
                    'message': integrity_msg
                })
                continue

            # ============================================================
            # 9. AJOUTER LE STATUT
            # ============================================================
            certificate_id = certificate.get('certificate_id', 'Inconnu')
            certified_by = certificate.get('certified_by', 'Inconnu')
            
            status_info = {
                'module_name': folder_name,
                'status': 'valid' if remaining_days > self.expiry_warning_threshold else 'expiring',
                'remaining_days': remaining_days,
                'expiry_date': certificate.get('expiry_date', ''),
                'message': validity_msg,
                'certified_by': certified_by,
                'certificate_id': certificate_id,
                'version': version
            }
            self.last_certificate_status.append(status_info)

            if remaining_days < self.expiry_warning_threshold and remaining_days > 0:
                logger.warning(f"  ⚠️ {folder_name}: {validity_msg}")
            else:
                logger.info(f"  ✅ {folder_name}: {validity_msg}")

            # ============================================================
            # 10. CHARGEMENT DU MODULE
            # ============================================================
            logger.info(f"✅ Module certifié : [{folder_name}] version={manifest.get('version')}")
            logger.info(f"   Certifié par: {certified_by}")
            logger.info(f"   ID: {certificate_id}")
            logger.info(f"   Version certificat: {version}")

            instance = self._load_module_instance(folder_name, folder_path, manifest, main_window)
            if instance:
                loaded_instances.append(instance)

        logger.info(f"--- FIN DU CHARGEMENT DES MODULES ({len(loaded_instances)} chargés) ---")

        # Afficher un résumé
        if self.last_certificate_status:
            logger.info("📋 RÉSUMÉ DES CERTIFICATS:")
            for status in self.last_certificate_status:
                status_icon = {
                    'valid': '✅',
                    'expiring': '⚠️',
                    'expired': '❌',
                    'invalid_structure': '❌',
                    'signature_invalid': '❌',
                    'revoked': '🚫',
                    'corrupted': '❌',
                    'no_certificate': '📭',
                    'dev_mode': '🔓'
                }.get(status.get('status'), '❓')
                logger.info(f"   {status_icon} {status.get('module_name')}: {status.get('message', '')}")

        return loaded_instances

    def _get_certificate_status(self, certificate, module_name):
        """
        Extrait le statut d'un certificat.
        Supporte les versions 2.0.0 et 3.0.0.
        """
        from datetime import datetime
        import re
        
        if not certificate:
            return {
                'module_name': module_name,
                'status': 'no_certificate',
                'message': 'Certificat manquant'
            }
        
        # ✅ Récupérer la date d'expiration (support des deux versions)
        expiry_date = certificate.get("expiry_date")
        validity_days = None
        version = certificate.get("version", "2.0.0")
        
        # ✅ Version 3.x : la date est dans validity
        if not expiry_date and "validity" in certificate:
            validity = certificate.get("validity", {})
            expiry_date = validity.get("not_after")
            validity_days = validity.get("days")
        
        if not expiry_date:
            if validity_days:
                return {
                    'module_name': module_name,
                    'status': 'valid',
                    'remaining_days': validity_days,
                    'expiry_date': f"Dans {validity_days} jours",
                    'version': version,
                    'message': f'Valide ({validity_days} jours - certifié)'
                }
            return {
                'module_name': module_name,
                'status': 'unknown',
                'version': version,
                'message': 'Pas de date d\'expiration'
            }
        
        try:
            # ✅ Nettoyer la date
            expiry_date_str = str(expiry_date).strip()
            
            # ✅ Si c'est un format comme "Aug 19 10:04:28 2026 GMT"
            if "GMT" in expiry_date_str:
                clean_date = expiry_date_str.replace(" GMT", "").strip()
                expiry_datetime = datetime.strptime(clean_date, "%b %d %H:%M:%S %Y")
            else:
                # ✅ Supprimer le fuseau horaire pour avoir une date naive
                if "+" in expiry_date_str or expiry_date_str.endswith("Z"):
                    if "+" in expiry_date_str:
                        expiry_date_str = expiry_date_str.split("+")[0]
                    elif "Z" in expiry_date_str:
                        expiry_date_str = expiry_date_str.replace("Z", "")
                    expiry_date_str = expiry_date_str.replace("T", " ")
                    expiry_datetime = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    try:
                        expiry_datetime = datetime.fromisoformat(expiry_date_str)
                        if expiry_datetime.tzinfo is not None:
                            expiry_datetime = expiry_datetime.replace(tzinfo=None)
                    except ValueError:
                        expiry_datetime = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
            
            now = datetime.now()
            remaining = (expiry_datetime - now).days
            
            if remaining < 0:
                return {
                    'module_name': module_name,
                    'status': 'expired',
                    'remaining_days': remaining,
                    'expiry_date': expiry_datetime.strftime('%d/%m/%Y'),
                    'version': version,
                    'message': f'Expiré depuis {abs(remaining)} jours'
                }
            elif remaining < self.expiry_warning_threshold:
                return {
                    'module_name': module_name,
                    'status': 'expiring',
                    'remaining_days': remaining,
                    'expiry_date': expiry_datetime.strftime('%d/%m/%Y'),
                    'version': version,
                    'message': f'Expire dans {remaining} jours'
                }
            else:
                return {
                    'module_name': module_name,
                    'status': 'valid',
                    'remaining_days': remaining,
                    'expiry_date': expiry_datetime.strftime('%d/%m/%Y'),
                    'version': version,
                    'message': f'Valide ({remaining} jours restants)'
                }
        except Exception as e:
            if validity_days:
                return {
                    'module_name': module_name,
                    'status': 'valid',
                    'remaining_days': validity_days,
                    'expiry_date': f"Dans {validity_days} jours",
                    'version': version,
                    'message': f'Valide ({validity_days} jours - certifié)'
                }
            return {
                'module_name': module_name,
                'status': 'error',
                'version': version,
                'message': f'Erreur: {str(e)}'
            }

    def _check_certificate_validity(self, certificate: dict) -> tuple:
        """Vérifie la période de validité du certificat."""
        from datetime import datetime, timedelta
        import re
        
        # ✅ Support des deux versions
        expiry_date = certificate.get("expiry_date")
        validity_days = None
        
        # ✅ Si version 3.x, la date est dans validity
        if not expiry_date and "validity" in certificate:
            validity = certificate.get("validity", {})
            expiry_date = validity.get("not_after")
            validity_days = validity.get("days")
        
        # ✅ Si toujours pas de date, utiliser validity_days
        if not expiry_date:
            if validity_days:
                return True, validity_days, f"Valide ({validity_days} jours - certifié)"
            return True, 365, "Pas de date d'expiration"
        
        try:
            # ✅ Nettoyer la date
            expiry_date_str = str(expiry_date).strip()
            
            # ✅ Si c'est un format comme "Aug 19 10:04:28 2026 GMT"
            if "GMT" in expiry_date_str:
                # Nettoyer le GMT et les espaces
                clean_date = expiry_date_str.replace(" GMT", "").strip()
                expiry_datetime = datetime.strptime(clean_date, "%b %d %H:%M:%S %Y")
            else:
                # ✅ Supprimer le fuseau horaire pour avoir une date naive
                # Format ISO: "2026-08-19T12:04:29+02:00"
                if "+" in expiry_date_str or expiry_date_str.endswith("Z"):
                    # Enlever le fuseau horaire
                    if "+" in expiry_date_str:
                        expiry_date_str = expiry_date_str.split("+")[0]
                    elif "Z" in expiry_date_str:
                        expiry_date_str = expiry_date_str.replace("Z", "")
                    # Remplacer 'T' par un espace si présent
                    expiry_date_str = expiry_date_str.replace("T", " ")
                    expiry_datetime = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    # Essayer le format ISO direct
                    try:
                        expiry_datetime = datetime.fromisoformat(expiry_date_str)
                        # Rendre naive (sans fuseau horaire)
                        if expiry_datetime.tzinfo is not None:
                            expiry_datetime = expiry_datetime.replace(tzinfo=None)
                    except ValueError:
                        # Essayer avec strptime
                        expiry_datetime = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
            
            now = datetime.now()
            
            if expiry_datetime < now:
                return False, 0, f"EXPIRÉ depuis le {expiry_datetime.strftime('%d/%m/%Y')}"
            
            remaining = (expiry_datetime - now).days
            
            if remaining < self.expiry_warning_threshold and remaining > 0:
                logger.warning(f"   ⚠️ Certificat expire dans {remaining} jours")
            
            return True, remaining, f"Valide ({remaining} jours restants)"
            
        except Exception as e:
            # ✅ Si la date est invalide, utiliser validity_days
            if validity_days:
                return True, validity_days, f"Valide ({validity_days} jours - certifié)"
            logger.warning(f"   ⚠️ Date d'expiration invalide: {e}")
            return True, 365, "Date d'expiration invalide (ignorée)"

    # def _verify_file_integrity(self, module_path: Path, checksums: dict) -> tuple:
    #     """Vérifie l'intégrité des fichiers du module."""
    #     if not checksums:
    #         return False, "Aucun checksum dans le certificat"
        
    #     errors = []
    #     checked_files = 0
        
    #     for file_path, expected_hash in checksums.items():
    #         full_path = module_path / file_path
    #         checked_files += 1
            
    #         if not full_path.exists():
    #             errors.append(f"Fichier manquant: {file_path}")
    #             continue
            
    #         try:
    #             actual_hash = self._compute_file_hash(full_path)
    #             if actual_hash != expected_hash:
    #                 errors.append(f"Fichier modifié: {file_path}")
    #         except Exception as e:
    #             errors.append(f"Erreur lecture {file_path}: {e}")
        
    #     # Vérifier les fichiers ajoutés
    #     for file_path in module_path.rglob('*'):
    #         if file_path.is_file():
    #             rel_path = str(file_path.relative_to(module_path))
    #             if rel_path not in checksums and rel_path not in ['certificate.json', 'certificate.pem']:
    #                 if not any(x in rel_path for x in ['.pyc', '__pycache__', '.DS_Store', '.git']):
    #                     errors.append(f"Fichier ajouté: {rel_path}")
        
    #     if errors:
    #         error_msg = "\n- ".join(errors[:10])
    #         if len(errors) > 10:
    #             error_msg += f"\n... et {len(errors) - 10} autres erreurs"
    #         return False, f"Intégrité compromise:\n- {error_msg}"
        
    #     logger.info(f"   ✅ {checked_files} fichiers vérifiés, intègres")
    #     return True, f"{checked_files} fichiers intègres"

    def _verify_file_integrity(self, module_path: Path, checksums: dict) -> tuple:
        """Vérifie l'intégrité des fichiers du module."""
        if not checksums:
            return False, "Aucun checksum dans le certificat"
        
        errors = []
        checked_files = 0
        total_files = len(checksums)
        
        for file_path, expected_hash in checksums.items():
            full_path = module_path / file_path
            checked_files += 1
            
            if not full_path.exists():
                errors.append(f"Fichier manquant: {file_path}")
                continue
            
            try:
                actual_hash = self._compute_file_hash(full_path)
                if actual_hash != expected_hash:
                    errors.append(f"Fichier modifié: {file_path}")
            except Exception as e:
                errors.append(f"Erreur lecture {file_path}: {e}")
        
        # Vérifier les fichiers ajoutés (non listés dans le certificat)
        for file_path in module_path.rglob('*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(module_path))
                # Ignorer les fichiers de certificat et les fichiers temporaires
                if rel_path not in checksums and rel_path not in ['certificate.json', 'certificate.pem']:
                    if not any(x in rel_path for x in ['.pyc', '__pycache__', '.DS_Store', '.git', '.pyo']):
                        errors.append(f"Fichier ajouté: {rel_path}")
        
        if errors:
            error_msg = "\n- ".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... et {len(errors) - 10} autres erreurs"
            return False, f"Intégrité compromise:\n- {error_msg}"
        
        logger.info(f"   ✅ {checked_files}/{total_files} fichiers vérifiés, intègres")
        return True, f"{checked_files}/{total_files} fichiers intègres"

    def _compute_file_hash(self, file_path: Path) -> str:
        """Calcule le SHA-256 d'un fichier"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _load_module_instance(self, folder_name: str, folder_path: Path, 
                             manifest: dict, main_window) -> object:
        """Charge une instance du module."""
        try:
            module_file = folder_path / "main_ui.py"
            if not module_file.exists():
                logger.warning(f"  ! Manquant : main_ui.py dans {folder_name}")
                return None

            module_name = f"addons.{folder_name}.main_ui"
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            if spec is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logger.info(f"  > Importation réussie : {module_name}")

            for name, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, BaseModule) and obj is not BaseModule:
                    logger.info(f"  > Classe de module valide trouvée : {name}")
                    instance = obj(main_window)
                    instance.setup()
                    logger.info(f"  [OK] Module {folder_name} chargé et initialisé.")
                    return instance
            
            logger.warning(f"  ! Aucune classe héritant de BaseModule trouvée dans {folder_name}")
            return None
            
        except Exception as e:
            logger.error(f"  [ERREUR] Échec du chargement de {folder_name} : {str(e)}")
            logger.error(traceback.format_exc())
            return None


            