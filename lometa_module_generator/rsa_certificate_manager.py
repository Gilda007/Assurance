#!/usr/bin/env python3
"""
Gestionnaire de Certificats RSA pour LOMETA
Version sécurisée avec clés asymétriques
"""

import json
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import secrets
import base64

# Import des classes RSA
from certificate_manager_rsa import RSACertificate, RSASignature, HAS_CRYPTOGRAPHY


class RSACertificateManager:
    """
    Gestionnaire de certificats RSA pour les modules LOMETA.
    
    Fonctionnalités:
    - Génération de certificats signés RSA
    - Vérification des certificats
    - Gestion des clés publiques
    - Validation d'intégrité
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Dossiers
        self.keys_dir = self.config_dir / "keys"
        self.certs_dir = self.config_dir / "certificates"
        self.public_keys_dir = self.keys_dir / "public"
        self.private_keys_dir = self.keys_dir / "private"
        
        for d in [self.keys_dir, self.certs_dir, self.public_keys_dir, self.private_keys_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Clés du gestionnaire
        self.private_key_path = self.private_keys_dir / "lometa_ca.pem"
        self.public_key_path = self.public_keys_dir / "lometa_ca.pub"
        
        # Vérifier ou créer les clés
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            self._init_ca_keys()
        
        # Charger les clés
        self.private_key = self.private_key_path.read_bytes() if self.private_key_path.exists() else None
        self.public_key = self.public_key_path.read_bytes() if self.public_key_path.exists() else None
        
        # Machine ID
        self.machine_id = self._get_machine_id()
    
    def _get_default_config_dir(self) -> Path:
        """Détermine le dossier de configuration"""
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
            return base_dir / "certificates"
        
        if os.path.exists("certificates"):
            return Path("certificates")
        
        return Path.home() / ".lometa" / "certificates"
    
    def _get_machine_id(self) -> str:
        """Récupère un ID unique de la machine"""
        import uuid
        import platform
        
        identifiers = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            str(uuid.getnode())
        ]
        combined = "".join(identifiers)
        return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
    
    def _init_ca_keys(self):
        """Initialise les clés de l'autorité de certification"""
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptographie est requis pour générer des clés RSA")
        
        print(f"🔑 Génération des clés CA (2048 bits)...")
        private_pem, public_pem = RSASignature.generate_keypair()
        
        # Sauvegarder les clés
        self.private_key_path.write_bytes(private_pem)
        self.public_key_path.write_bytes(public_pem)
        
        # Restreindre les permissions
        if os.name != 'nt':
            os.chmod(self.private_key_path, 0o600)
        
        print(f"✅ Clé privée: {self.private_key_path}")
        print(f"✅ Clé publique: {self.public_key_path}")
    
    def get_public_key(self) -> Optional[bytes]:
        """Retourne la clé publique du CA"""
        return self.public_key
    
    def get_private_key(self) -> Optional[bytes]:
        """Retourne la clé privée du CA"""
        return self.private_key
    
    def generate_certificate(self, module_dir: Path, certifier_name: str,
                            validity_days: int = 365,
                            module_id: str = None,
                            metadata: Dict = None) -> Optional[RSACertificate]:
        """
        Génère un certificat RSA pour un module.
        
        Args:
            module_dir: Dossier du module
            certifier_name: Nom du certifieur
            validity_days: Durée de validité en jours
            module_id: ID unique du module (optionnel)
            metadata: Métadonnées supplémentaires
        
        Returns:
            RSACertificate: Certificat généré ou None en cas d'erreur
        """
        module_dir = Path(module_dir)
        if not module_dir.exists() or not module_dir.is_dir():
            print(f"❌ Module introuvable: {module_dir}")
            return None
        
        # Vérifier le manifest
        manifest_file = module_dir / "manifest.json"
        if not manifest_file.exists():
            print("❌ manifest.json non trouvé!")
            return None
        
        try:
            manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
            module_name = manifest.get("name", module_dir.name)
            module_version = manifest.get("version", "1.0.0")
        except Exception as e:
            print(f"❌ Erreur de lecture du manifest: {e}")
            return None
        
        # Créer le certificat
        cert = RSACertificate()
        cert.data["module_name"] = module_name
        cert.data["module_version"] = module_version
        cert.data["module_id"] = module_id or f"lometa.{module_dir.name}.v{module_version}"
        cert.data["certified_by"] = certifier_name
        cert.data["certified_date"] = datetime.now().isoformat()
        cert.data["expiry_date"] = (datetime.now() + timedelta(days=validity_days)).isoformat()
        cert.data["certificate_id"] = cert.generate_certificate_id()
        cert.data["machine_id"] = self.machine_id
        cert.data["public_key"] = base64.b64encode(self.public_key).decode('ascii')
        cert.data["metadata"] = metadata or {}
        
        # Calculer les checksums
        print("📄 Calcul des checksums des fichiers...")
        cert.data["checksums"] = cert.compute_directory_checksums(
            module_dir,
            exclude=['.pyc', '__pycache__', '.git', '.DS_Store', 'certificate.json', 'certificate.pem']
        )
        print(f"   ✅ {len(cert.data['checksums'])} fichiers vérifiés")
        
        # Signer le certificat
        if not cert.sign(self.private_key):
            print("❌ Erreur de signature")
            return None
        
        # Sauvegarder
        cert_file = self.certs_dir / f"{module_name}_{module_version}.cert.json"
        cert.save(cert_file)
        
        # Copier dans le module
        module_cert_file = module_dir / "certificate.json"
        cert.save(module_cert_file)
        
        # Créer aussi un fichier .pem pour compatibilité
        pem_file = module_dir / "certificate.pem"
        pem_file.write_text(cert.to_json(), encoding='utf-8')
        
        print(f"\n✅ Certificat généré avec succès!")
        print(f"   Module: {module_name} v{module_version}")
        print(f"   ID: {cert.data['certificate_id']}")
        print(f"   Valide jusqu'au: {cert.data['expiry_date']}")
        print(f"   Durée: {validity_days} jours")
        print(f"   Fichiers: {len(cert.data['checksums'])}")
        print(f"   Certificat: {module_cert_file}")
        
        return cert
    
    def verify_certificate(self, module_dir: Path) -> Tuple[bool, Dict]:
        """
        Vérifie un certificat RSA.
        
        Returns:
            Tuple (valide, détails)
        """
        module_dir = Path(module_dir)
        cert_file = module_dir / "certificate.json"
        
        if not cert_file.exists():
            return False, {"error": "certificate.json non trouvé"}
        
        # Charger le certificat
        cert = RSACertificate()
        if not cert.load(cert_file):
            return False, {"error": "Certificat invalide ou corrompu"}
        
        details = {
            "module_name": cert.data.get("module_name", ""),
            "module_version": cert.data.get("module_version", ""),
            "certificate_id": cert.data.get("certificate_id", ""),
            "certified_by": cert.data.get("certified_by", ""),
            "certified_date": cert.data.get("certified_date", ""),
            "expiry_date": cert.data.get("expiry_date", ""),
            "file_count": len(cert.data.get("checksums", {}))
        }
        
        print(f"🔍 Vérification du certificat: {details['certificate_id']}")
        
        # 1. Vérifier la signature RSA
        if not cert.verify(self.public_key):
            return False, {**details, "error": "Signature RSA invalide"}
        
        print("   ✅ Signature RSA valide")
        
        # 2. Vérifier la date d'expiration
        if cert.is_expired():
            return False, {**details, "error": f"Certificat expiré (expiration: {details['expiry_date']})"}
        
        print(f"   ✅ Certificat valide (expire le {details['expiry_date']})")
        
        # 3. Vérifier l'intégrité des fichiers
        print("   📄 Vérification de l'intégrité...")
        expected = cert.data.get("checksums", {})
        errors = []
        
        for file_path, expected_hash in expected.items():
            full_path = module_dir / file_path
            if not full_path.exists():
                errors.append(f"Fichier manquant: {file_path}")
                continue
            
            actual_hash = cert.compute_checksum(full_path)
            if actual_hash != expected_hash:
                errors.append(f"Fichier modifié: {file_path}")
        
        # Vérifier les fichiers ajoutés
        for file_path in module_dir.rglob('*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(module_dir))
                if rel_path not in expected and rel_path not in ['certificate.json', 'certificate.pem']:
                    if not any(x in rel_path for x in ['.pyc', '__pycache__', '.DS_Store']):
                        errors.append(f"Fichier ajouté: {rel_path}")
        
        if errors:
            return False, {**details, "error": f"Intégrité compromise", "errors": errors}
        
        print(f"   ✅ {len(expected)} fichiers intègres")
        
        # 4. Jours restants
        remaining = cert.get_remaining_days()
        details["remaining_days"] = remaining
        
        if remaining < 30 and remaining > 0:
            print(f"   ⚠️ Avertissement: expire dans {remaining} jours")
        elif remaining == 0:
            print("   ⚠️ Expire aujourd'hui!")
        
        return True, details