#!/usr/bin/env python3
"""
Module Certifier RSA - Gestionnaire de certificats avec RSA
Version sécurisée avec clés asymétriques
"""

import json
import hashlib
import base64
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import sys
import os
import platform

# ============================================================================
# CRYPTOGRAPHIE RSA
# ============================================================================

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    print("⚠️ cryptography non installé. Installez: pip install cryptography")


class RSASignature:
    """Gestionnaire de signatures RSA"""
    
    KEY_SIZE = 2048
    SALT_LENGTH = 32
    
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]:
        """
        Génère une paire de clés RSA.
        
        Returns:
            Tuple (private_key_pem, public_key_pem)
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography est requis pour RSA")
        
        # Générer la clé privée
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=RSASignature.KEY_SIZE,
            backend=default_backend()
        )
        
        # Exporter la clé privée au format PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Exporter la clé publique au format PEM
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def sign(data: bytes, private_key_pem: bytes) -> bytes:
        """
        Signe des données avec RSA-PSS.
        
        Args:
            data: Données à signer
            private_key_pem: Clé privée au format PEM
        
        Returns:
            bytes: Signature
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography est requis pour RSA")
        
        # Charger la clé privée
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Calculer le hash des données
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(data)
        digest = hasher.finalize()
        
        # Signer avec RSA-PSS
        signature = private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=RSASignature.SALT_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    @staticmethod
    def verify(data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
        """
        Vérifie une signature RSA-PSS.
        
        Args:
            data: Données signées
            signature: Signature à vérifier
            public_key_pem: Clé publique au format PEM
        
        Returns:
            bool: True si la signature est valide
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptographie est requis pour RSA")
        
        try:
            # Charger la clé publique
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )
            
            # Calculer le hash des données
            hasher = hashes.Hash(hashes.SHA256())
            hasher.update(data)
            digest = hasher.finalize()
            
            # Vérifier la signature
            public_key.verify(
                signature,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=RSASignature.SALT_LENGTH
                ),
                hashes.SHA256()
            )
            return True
            
        except Exception as e:
            print(f"❌ Erreur de vérification RSA: {e}")
            return False


class RSACertificate:
    """Certificat signé avec RSA"""
    
    VERSION = "3.0.0"
    
    def __init__(self):
        self.data = {
            "version": self.VERSION,
            "certificate_type": "MODULE",
            "module_name": "",
            "module_version": "",
            "module_id": "",
            "certified_by": "",
            "certified_date": "",
            "expiry_date": "",
            "certificate_id": "",
            "public_key": "",
            "signature": "",
            "signature_algorithm": "RSA-PSS-SHA256",
            "checksum_algorithm": "SHA-256",
            "checksums": {},
            "metadata": {},
            "machine_id": "",
            "certificate_chain": []
        }
    
    def generate_certificate_id(self) -> str:
        """Génère un ID unique pour le certificat"""
        import secrets
        return f"LOMETA-{datetime.now().strftime('%Y%m')}-{secrets.token_hex(8).upper()}"
    
    def compute_checksum(self, file_path: Path) -> str:
        """Calcule le SHA-256 d'un fichier"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def compute_directory_checksums(self, directory: Path, exclude: List[str] = None) -> Dict[str, str]:
        """Calcule les checksums de tous les fichiers d'un répertoire"""
        exclude = exclude or ['.pyc', '__pycache__', '.git', '.DS_Store', 'certificate.json']
        checksums = {}
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                skip = False
                for pattern in exclude:
                    if pattern in str(file_path):
                        skip = True
                        break
                if skip:
                    continue
                
                rel_path = str(file_path.relative_to(directory))
                checksums[rel_path] = self.compute_checksum(file_path)
        
        return checksums
    
    def sign(self, private_key_pem: bytes) -> bool:
        """
        Signe le certificat avec RSA.
        La signature inclut : module_name, module_version, certified_by, certified_date, expiry_date, checksums
        """
        # ✅ Inclure la date d'expiration dans la signature
        data_to_sign = {
            "module_name": self.data["module_name"],
            "module_version": self.data["module_version"],
            "module_id": self.data["module_id"],
            "certified_by": self.data["certified_by"],
            "certified_date": self.data["certified_date"],
            "expiry_date": self.data["expiry_date"],  # ✅ Protégée par la signature
            "certificate_id": self.data["certificate_id"],
            "checksums": self.data["checksums"]
        }
        
        # Convertir en JSON trié
        data_str = json.dumps(data_to_sign, sort_keys=True, indent=2)
        
        # Signer avec RSA
        try:
            signature = RSASignature.sign(data_str.encode('utf-8'), private_key_pem)
            self.data["signature"] = base64.b64encode(signature).decode('ascii')
            return True
        except Exception as e:
            print(f"❌ Erreur de signature: {e}")
            return False
    
    def verify(self, public_key_pem: bytes) -> bool:
        """
        Vérifie la signature du certificat.
        """
        if not self.data.get("signature"):
            return False
        
        # Reconstruire les données signées
        data_to_verify = {
            "module_name": self.data["module_name"],
            "module_version": self.data["module_version"],
            "module_id": self.data["module_id"],
            "certified_by": self.data["certified_by"],
            "certified_date": self.data["certified_date"],
            "expiry_date": self.data["expiry_date"],
            "certificate_id": self.data["certificate_id"],
            "checksums": self.data["checksums"]
        }
        
        data_str = json.dumps(data_to_verify, sort_keys=True, indent=2)
        
        try:
            signature = base64.b64decode(self.data["signature"])
            return RSASignature.verify(data_str.encode('utf-8'), signature, public_key_pem)
        except Exception as e:
            print(f"❌ Erreur de vérification: {e}")
            return False
    
    def is_expired(self) -> bool:
        """Vérifie si le certificat est expiré"""
        expiry = self.data.get("expiry_date")
        if not expiry:
            return False
        try:
            expiry_date = datetime.fromisoformat(expiry)
            return datetime.now() > expiry_date
        except:
            return True
    
    def get_remaining_days(self) -> int:
        """Retourne le nombre de jours restants"""
        expiry = self.data.get("expiry_date")
        if not expiry:
            return 0
        try:
            expiry_date = datetime.fromisoformat(expiry)
            delta = expiry_date - datetime.now()
            return max(0, delta.days)
        except:
            return 0
    
    def to_json(self) -> str:
        """Exporte le certificat en JSON"""
        return json.dumps(self.data, indent=2)
    
    def from_json(self, json_str: str) -> bool:
        """Importe un certificat depuis JSON"""
        try:
            self.data = json.loads(json_str)
            return True
        except:
            return False
    
    def save(self, file_path: Path):
        """Sauvegarde le certificat"""
        file_path.write_text(self.to_json(), encoding='utf-8')
    
    def load(self, file_path: Path) -> bool:
        """Charge un certificat"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.from_json(content)
        except:
            return False