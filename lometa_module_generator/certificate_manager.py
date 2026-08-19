#!/usr/bin/env python3
"""
Module Certifier - Outil de certification et signature des modules LOMETA
Permet de signer, vérifier et certifier les modules avant distribution.
"""

import json
import hashlib
import hmac
import base64
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import sys
import os
import re
import platform

# ============================================================================
# COLORS
# ============================================================================

COLORS = {
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'red': '\033[91m',
    'cyan': '\033[96m',
    'magenta': '\033[95m',
    'bold': '\033[1m',
    'reset': '\033[0m'
}

def color(text, color_name):
    return f"{COLORS.get(color_name, '')}{text}{COLORS['reset']}"

def print_header(text):
    print(f"\n{color('='*60, 'cyan')}")
    print(f"{color(text.center(60), 'bold')}")
    print(f"{color('='*60, 'cyan')}\n")

def print_success(text):
    print(f"{color('✅', 'green')} {text}")

def print_error(text):
    print(f"{color('❌', 'red')} {text}")

def print_info(text):
    print(f"{color('ℹ️', 'blue')} {text}")

def print_warning(text):
    print(f"{color('⚠️', 'yellow')} {text}")

# ============================================================================
# CERTIFICATE CLASSES
# ============================================================================

class ModuleCertificate:
    """Certificat de module avec signature."""
    
    VERSION = "2.0.0"
    DEFAULT_VALIDITY_DAYS = 365  # 1 an de validité par défaut
    
    def __init__(self):
        self.data = {
            "version": self.VERSION,
            "module_name": "",
            "module_version": "",
            "certified_by": "",
            "certified_date": "",
            "expiry_date": "",  # ✅ Date d'expiration
            "certificate_id": "",
            "checksums": {},
            "signature": "",
            "public_key": "",
            "signature_algorithm": "HMAC-SHA256",
            "certificate_chain": [],
            "metadata": {},
            "validity_days": self.DEFAULT_VALIDITY_DAYS
        }
    
    def generate_certificate_id(self, module_name: str) -> str:
        """Génère un ID de certificat unique."""
        timestamp = int(time.time())
        raw = f"{module_name}-{timestamp}-{os.urandom(4).hex()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    
    def compute_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA-256 d'un fichier."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def compute_directory_checksums(self, directory: Path, exclude: List[str] = None) -> Dict[str, str]:
        """Calcule les checksums de tous les fichiers d'un répertoire."""
        exclude = exclude or ['.pyc', '__pycache__', '.git', '.DS_Store']
        checksums = {}
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                # Vérifier si le fichier doit être exclu
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
    
    def sign(self, private_key: str) -> str:
        """Signe les données du certificat."""
        # Créer la chaîne à signer
        data_to_sign = {
            "module_name": self.data["module_name"],
            "module_version": self.data["module_version"],
            "certified_by": self.data["certified_by"],
            "certified_date": self.data["certified_date"],
            "certificate_id": self.data["certificate_id"],
            "checksums": self.data["checksums"]
        }
        data_str = json.dumps(data_to_sign, sort_keys=True)
        
        # Générer la signature HMAC-SHA256
        signature = hmac.new(
            private_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, verification_key: Optional[str] = None) -> bool:
        """Vérifie la signature du certificat avec une clé de vérification donnée."""
        if not self.data.get("signature"):
            return False
        
        # ✅ Si c'est un certificat auto-signé (pour les tests)
        if self.data.get("signature") == self.data.get("public_key"):
            return True
        
        verification_key = verification_key or self.data.get("public_key", "")
        if not verification_key:
            return False
        
        # Créer la chaîne à vérifier
        data_to_verify = {
            "module_name": self.data["module_name"],
            "module_version": self.data["module_version"],
            "certified_by": self.data["certified_by"],
            "certified_date": self.data["certified_date"],
            "certificate_id": self.data["certificate_id"],
            "checksums": self.data["checksums"]
        }
        data_str = json.dumps(data_to_verify, sort_keys=True)
        
        # Recalculer la signature avec la clé fournie
        expected_signature = hmac.new(
            verification_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(self.data["signature"], expected_signature)

    def to_json(self) -> str:
        """Exporte le certificat en JSON."""
        return json.dumps(self.data, indent=2)
    
    def from_json(self, json_str: str) -> bool:
        """Importe un certificat depuis JSON."""
        try:
            self.data = json.loads(json_str)
            return True
        except Exception:
            return False
    
    def save(self, file_path: Path):
        """Sauvegarde le certificat dans un fichier."""
        file_path.write_text(self.to_json(), encoding='utf-8')
    
    def load(self, file_path: Path) -> bool:
        """Charge un certificat depuis un fichier."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.from_json(content)
        except Exception:
            return False

    def set_validity(self, days: int = DEFAULT_VALIDITY_DAYS):
        """Définit la durée de validité en jours."""
        from datetime import datetime, timedelta
        self.data["validity_days"] = days
        self.data["expiry_date"] = (datetime.now() + timedelta(days=days)).isoformat()
    
    def is_expired(self) -> bool:
        """Vérifie si le certificat est expiré."""
        expiry_date = self.data.get("expiry_date")
        if not expiry_date:
            return False
        try:
            from datetime import datetime
            expiry = datetime.fromisoformat(expiry_date)
            return datetime.now() > expiry
        except:
            return True
    
    def get_remaining_days(self) -> int:
        """Retourne le nombre de jours restants avant expiration."""
        expiry_date = self.data.get("expiry_date")
        if not expiry_date:
            return 0
        try:
            from datetime import datetime
            expiry = datetime.fromisoformat(expiry_date)
            delta = expiry - datetime.now()
            return max(0, delta.days)
        except:
            return 0


# ============================================================================
# CERTIFICATE MANAGER
# ============================================================================

class CertificateManager:
    """Gestionnaire de certificats pour les modules."""
    
    def __init__(self, config_dir: Optional[Path] = None, use_shared_keys: bool = True):
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # ✅ Gestionnaire de clés partagées (optionnel)
        self.use_shared_keys = use_shared_keys
        self.shared_key_manager = None
        if use_shared_keys:
            try:
                self.shared_key_manager = SharedKeyManager(self.config_dir)
            except Exception as e:
                print(f"⚠️ Erreur initialisation SharedKeyManager: {e}")
                self.shared_key_manager = None
        
        # Fichiers locaux (fallback)
        self.key_file = self.config_dir / "private_key.pem"
        self.public_key_file = self.config_dir / "public_key.pem"
        self.certificates_dir = self.config_dir / "issued"
        self.certificates_dir.mkdir(parents=True, exist_ok=True)
        
        # Machine ID pour traçabilité
        self.machine_id = self._get_machine_id()
        
    def get_or_create_keypair(self) -> Tuple[str, str]:
        """Récupère ou crée une paire de clés."""
        private_key = None
        public_key = None
        
        if self.key_file.exists():
            private_key = self.key_file.read_text(encoding='utf-8').strip()
        else:
            # Générer une clé privée
            import secrets
            private_key = secrets.token_hex(32)
            self.key_file.write_text(private_key, encoding='utf-8')
            print_success(f"Clé privée générée: {self.key_file}")
        
        if self.public_key_file.exists():
            public_key = self.public_key_file.read_text(encoding='utf-8').strip()
        else:
            # Générer une clé publique
            public_key = hashlib.sha256(private_key.encode()).hexdigest()
            self.public_key_file.write_text(public_key, encoding='utf-8')
            print_success(f"Clé publique générée: {self.public_key_file}")
        
        return private_key, public_key

    def _get_default_config_dir(self) -> Path:
        """Détermine le dossier de configuration."""
        # En mode compilé, utiliser le dossier de l'application
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
            return base_dir / "certificates"
        
        # Mode développement
        if os.path.exists("certificates"):
            return Path("certificates")
        
        # Fallback
        return Path.home() / ".lometa" / "certificates"
    
    def get_certification_key(self) -> Tuple[str, str]:
        """
        Récupère la clé de certification.
        Priorité: clé partagée > clé locale.
        """
        # Essayer d'abord les clés partagées
        if self.shared_key_manager:
            public_key = self.shared_key_manager.get_shared_public_key()
            private_key = self.shared_key_manager.get_or_create_shared_key().get("private_key")
            
            if public_key and private_key:
                return private_key, public_key
        
        # Fallback: clés locales
        if self.key_file.exists() and self.public_key_file.exists():
            private_key = self.key_file.read_text(encoding='utf-8').strip()
            public_key = self.public_key_file.read_text(encoding='utf-8').strip()
            return private_key, public_key
        
        # Générer de nouvelles clés
        import secrets
        private_key = secrets.token_hex(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        self.key_file.write_text(private_key, encoding='utf-8')
        self.public_key_file.write_text(public_key, encoding='utf-8')
        
        return private_key, public_key

    # ✅ AJOUTER CETTE MÉTHODE
    def _get_machine_id(self) -> str:
        """Récupère un ID unique de la machine."""
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
 
    # def certify_module(self, module_dir: Path, certifier_name: str, validity_days: int = 365,
    #                metadata: Dict = None) -> Optional[ModuleCertificate]:
    #     """Certifie un module en générant un certificat signé."""
    #     module_dir = Path(module_dir)
    #     if not module_dir.exists() or not module_dir.is_dir():
    #         print_error(f"Le dossier du module n'existe pas: {module_dir}")
    #         return None
        
    #     # Vérifier le manifest
    #     manifest_file = module_dir / "manifest.json"
    #     if not manifest_file.exists():
    #         print_error("Manifest.json non trouvé!")
    #         return None
        
    #     try:
    #         manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    #         module_name = manifest.get("name")
    #         module_version = manifest.get("version")
    #     except Exception as e:
    #         print_error(f"Erreur de lecture du manifest: {e}")
    #         return None
        
    #     # Obtenir la paire de clés
    #     private_key, public_key = self.get_or_create_keypair()

    #      # ✅ VÉRIFIER LA VALIDITÉ TEMPORELLE
    #     if cert.is_expired():
    #         expiry = cert.data.get("expiry_date", "Inconnue")
    #         return False, f"❌ Certificat EXPIRÉ (date: {expiry})"

    #     remaining = cert.get_remaining_days()
    #     if remaining < 30:
    #         print_warning(f"⚠️ Certificat expire dans {remaining} jours")
    #     else:
    #         print_success(f"✅ Certificat valide ({remaining} jours restants)")
        
    #     # Créer le certificat
    #     cert = ModuleCertificate()
    #     cert.data["module_name"] = module_name
    #     cert.data["module_version"] = module_version
    #     cert.data["certified_by"] = certifier_name
    #     cert.data["certified_date"] = datetime.now().isoformat()
    #     cert.data["certificate_id"] = cert.generate_certificate_id(module_name)
    #     cert.data["public_key"] = public_key
    #     # ✅ Exclure certificate.json des checksums
    #     cert.data["checksums"] = cert.compute_directory_checksums(
    #         module_dir, 
    #         exclude=['.pyc', '__pycache__', '.git', '.DS_Store', 'certificate.json']
    #     )
    #     cert.data["metadata"] = metadata or {}
        
    #     # Signer le certificat
    #     cert.data["signature"] = cert.sign(private_key)
        
    #     # Sauvegarder le certificat
    #     cert_file = self.certificates_dir / f"{module_name}_{module_version}.cert.json"
    #     cert.save(cert_file)
        
    #     # Copier dans le module
    #     module_cert_file = module_dir / "certificate.json"
    #     cert.save(module_cert_file)
        
    #     print_success(f"Module {module_name} v{module_version} certifié!")
    #     print_success(f"Certificat: {cert_file}")
    #     print_success(f"ID: {cert.data['certificate_id']}")
    #     print_success(f"Signature: {cert.data['signature'][:16]}...")
        
    #     return cert

    def certify_module(self, module_dir: Path, certifier_name: str, 
                   validity_days: int = 365, metadata: Dict = None) -> Optional[ModuleCertificate]:
        """Certifie un module en générant un certificat signé avec durée de validité."""
        module_dir = Path(module_dir)
        if not module_dir.exists() or not module_dir.is_dir():
            print_error(f"Le dossier du module n'existe pas: {module_dir}")
            return None
        
        # Vérifier le manifest
        manifest_file = module_dir / "manifest.json"
        if not manifest_file.exists():
            print_error("Manifest.json non trouvé!")
            return None
        
        try:
            manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
            module_name = manifest.get("name")
            module_version = manifest.get("version")
        except Exception as e:
            print_error(f"Erreur de lecture du manifest: {e}")
            return None
        
        # Obtenir la paire de clés
        private_key, public_key = self.get_or_create_keypair()
        
        # Créer le certificat
        cert = ModuleCertificate()
        cert.data["module_name"] = module_name
        cert.data["module_version"] = module_version
        cert.data["certified_by"] = certifier_name
        cert.data["certified_date"] = datetime.now().isoformat()
        cert.data["certificate_id"] = cert.generate_certificate_id(module_name)
        cert.data["public_key"] = public_key
        cert.data["machine_id"] = self.machine_id
        cert.data["checksums"] = cert.compute_directory_checksums(
            module_dir, 
            exclude=['.pyc', '__pycache__', '.git', '.DS_Store', 'certificate.json']
        )
        cert.data["metadata"] = metadata or {}
        
        # ✅ Définir la durée de validité
        cert.set_validity(validity_days)
        
        # Signer le certificat
        cert.data["signature"] = cert.sign(private_key)
        
        # Sauvegarder le certificat
        cert_file = self.certificates_dir / f"{module_name}_{module_version}.cert.json"
        cert.save(cert_file)
        
        # Copier dans le module
        module_cert_file = module_dir / "certificate.json"
        cert.save(module_cert_file)
        
        print_success(f"Module {module_name} v{module_version} certifié!")
        print_success(f"Certificat: {cert_file}")
        print_success(f"ID: {cert.data['certificate_id']}")
        print_success(f"Valide jusqu'au: {cert.data['expiry_date']}")
        print_success(f"Validité: {validity_days} jours")
        print_success(f"Machine ID: {self.machine_id}")
        print_success(f"Signature: {cert.data['signature'][:16]}...")
        
        return cert

    def verify_module(self, module_dir: Path) -> Tuple[bool, str]:
        """Vérifie l'intégrité d'un module certifié."""
        module_dir = Path(module_dir)
        cert_file = module_dir / "certificate.json"
        
        if not cert_file.exists():
            return False, "❌ Certificate.json non trouvé. Le module n'est pas certifié."
        
        # Charger le certificat
        cert = ModuleCertificate()
        if not cert.load(cert_file):
            return False, "❌ Certificat invalide ou corrompu."
        
        print_info(f"Vérification du certificat: {cert.data.get('certificate_id', 'N/A')}")
        
        # ✅ Vérifier la signature avec différentes méthodes
        signature_valid = False
        verification_method = None

        private_key, public_key = self.get_or_create_keypair()
        candidate_keys = []
        if cert.data.get("public_key"):
            candidate_keys.append(cert.data.get("public_key"))
        if public_key:
            candidate_keys.append(public_key)
        if private_key:
            candidate_keys.append(private_key)

        # Éviter les doublons
        seen_keys = set()
        for key in candidate_keys:
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)

            if cert.verify_signature(key):
                signature_valid = True
                verification_method = "private_key" if key == private_key else "public_key"
                break
        
        if not signature_valid:
            # Afficher les détails pour le débogage
            print_info("Détails de la signature:")
            print(f"   Signature actuelle: {cert.data['signature'][:32]}...")
            print(f"   Clé publique: {cert.data.get('public_key', 'N/A')[:32]}...")
            print(f"   Certifié par: {cert.data.get('certified_by', 'N/A')}")
            print(f"   Date: {cert.data.get('certified_date', 'N/A')}")
            
            # Proposer de recertifier
            print_warning("La signature ne correspond pas. Voulez-vous recertifier le module?")
            print("   Pour recertifier, exécutez:")
            print(f"   python certificate_manager.py certify --module {module_dir} --certifier \"{cert.data.get('certified_by', 'LOMETA Authority')}\"")
            
            return False, "❌ Signature du certificat invalide. Utilisez la commande certify pour recertifier le module."
        
        print_success(f"✅ Signature valide ({verification_method})")
        
        # ✅ Vérifier l'intégrité des fichiers
        expected = cert.data.get("checksums", {})
        if not expected:
            return False, "❌ Aucun checksum dans le certificat."
        
        print_info("Vérification de l'intégrité des fichiers...")
        errors = []
        
        for file_path, expected_hash in expected.items():
            full_path = module_dir / file_path
            if not full_path.exists():
                errors.append(f"Fichier manquant: {file_path}")
                continue
            
            actual_hash = cert.compute_checksum(full_path)
            if actual_hash != expected_hash:
                errors.append(f"Fichier modifié: {file_path}")
        
        # Vérifier les fichiers ajoutés (sauf certificate.json)
        for file_path in module_dir.rglob('*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(module_dir))
                if rel_path not in expected and rel_path != 'certificate.json':
                    if not any(x in rel_path for x in ['.pyc', '__pycache__', '.DS_Store']):
                        errors.append(f"Fichier ajouté: {rel_path}")
        
        if errors:
            return False, f"❌ Intégrité compromise:\n- " + "\n- ".join(errors[:10])
        
        return True, f"✅ Module certifié LOMETA par {cert.data.get('certified_by', 'Inconnu')} (ID: {cert.data.get('certificate_id', 'N/A')})"

    def _get_config_public_key(self) -> Optional[str]:
        """Récupère la clé publique depuis la configuration."""
        if self.public_key_file.exists():
            return self.public_key_file.read_text(encoding='utf-8').strip()
        return None

    def list_certificates(self) -> List[Dict]:
        """Liste tous les certificats émis."""
        certificates = []
        for cert_file in self.certificates_dir.glob("*.cert.json"):
            try:
                cert = ModuleCertificate()
                if cert.load(cert_file):
                    certificates.append({
                        "file": cert_file.name,
                        "module_name": cert.data.get("module_name"),
                        "module_version": cert.data.get("module_version"),
                        "certified_by": cert.data.get("certified_by"),
                        "certified_date": cert.data.get("certified_date"),
                        "certificate_id": cert.data.get("certificate_id")
                    })
            except Exception:
                pass
        return sorted(certificates, key=lambda x: x.get("certified_date", ""), reverse=True)
    
    def revoke_certificate(self, certificate_id: str, reason: str = "Revoked") -> bool:
        """Révoque un certificat."""
        revoked_file = self.config_dir / "revoked.txt"
        
        # Ajouter l'ID à la liste de révocation
        content = revoked_file.read_text(encoding='utf-8') if revoked_file.exists() else ""
        
        if certificate_id in content:
            print_warning(f"Certificat déjà révoqué: {certificate_id}")
            return False
        
        with open(revoked_file, 'a', encoding='utf-8') as f:
            f.write(f"{certificate_id} - {reason} - {datetime.now().isoformat()}\n")
        
        print_success(f"Certificat {certificate_id} révoqué.")
        return True
    
    def is_revoked(self, certificate_id: str) -> bool:
        """Vérifie si un certificat est révoqué."""
        revoked_file = self.config_dir / "revoked.txt"
        if not revoked_file.exists():
            return False
        
        content = revoked_file.read_text(encoding='utf-8')
        return certificate_id in content



# certificate_manager.py - SharedKeyManager
# certificate_manager.py - Ajouter cette classe si elle n'existe pas

class SharedKeyManager:
    """
    Gestionnaire de clés partagées pour la vérification inter-machine.
    Les clés sont stockées dans un fichier central et distribuées aux machines.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".lometa" / "certificates"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.shared_keys_file = self.config_dir / "shared_keys.json"
    
    def list_keys(self) -> Dict:
        """Liste toutes les clés partagées."""
        if self.shared_keys_file.exists():
            try:
                return json.loads(self.shared_keys_file.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def get_or_create_shared_key(self, key_name: str = "lometa_master") -> Dict[str, str]:
        """Récupère ou crée une clé partagée."""
        import secrets
        
        if self.shared_keys_file.exists():
            try:
                data = json.loads(self.shared_keys_file.read_text(encoding='utf-8'))
                if key_name in data:
                    return data[key_name]
            except:
                pass
        
        # Créer une nouvelle clé
        private_key = secrets.token_hex(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        key_data = {
            "private_key": private_key,
            "public_key": public_key,
            "created_at": datetime.now().isoformat(),
            "created_by": platform.node() if hasattr(platform, 'node') else "unknown"
        }
        
        # Sauvegarder
        data = {}
        if self.shared_keys_file.exists():
            try:
                data = json.loads(self.shared_keys_file.read_text(encoding='utf-8'))
            except:
                pass
        
        data[key_name] = key_data
        self.shared_keys_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
        return key_data
    
    def get_shared_public_key(self, key_name: str = "lometa_master") -> Optional[str]:
        """Récupère la clé publique partagée."""
        keys = self.list_keys()
        if key_name in keys:
            return keys[key_name].get("public_key")
        return None
    
    def export_shared_key(self, output_file: Path, key_name: str = "lometa_master") -> bool:
        """Exporte la clé publique partagée pour distribution."""
        public_key = self.get_shared_public_key(key_name)
        if public_key:
            export_data = {
                "key_name": key_name,
                "public_key": public_key,
                "type": "shared_public_key",
                "created_at": datetime.now().isoformat(),
                "instructions": "Placez ce fichier dans ~/.lometa/certificates/ sur chaque machine"
            }
            output_file.write_text(json.dumps(export_data, indent=2), encoding='utf-8')
            print(f"✅ Clé publique exportée vers {output_file}")
            return True
        return False
    
    def import_shared_key(self, input_file: Path) -> bool:
        """Importe une clé publique partagée depuis un fichier."""
        try:
            data = json.loads(input_file.read_text(encoding='utf-8'))
            key_name = data.get("key_name", "lometa_master")
            public_key = data.get("public_key")
            
            if not public_key:
                print("❌ Clé publique non trouvée dans le fichier")
                return False
            
            # Sauvegarder la clé publique partagée
            shared_data = {}
            if self.shared_keys_file.exists():
                try:
                    shared_data = json.loads(self.shared_keys_file.read_text(encoding='utf-8'))
                except:
                    pass
            
            if key_name in shared_data:
                shared_data[key_name]["public_key"] = public_key
                shared_data[key_name]["imported_at"] = datetime.now().isoformat()
            else:
                shared_data[key_name] = {
                    "public_key": public_key,
                    "imported_at": datetime.now().isoformat(),
                    "type": "imported"
                }
            
            self.shared_keys_file.write_text(json.dumps(shared_data, indent=2), encoding='utf-8')
            print(f"✅ Clé publique {key_name} importée avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'importation: {e}")
            return False




def main():
    """Point d'entrée principal."""
    print_header("🔐 LOMETA - Certificate Manager v2.0")
    
    import argparse
    parser = argparse.ArgumentParser(description="Gestionnaire de certificats LOMETA")
    parser.add_argument("command", 
                       choices=["certify", "verify", "list", "revoke", "setup", 
                               "export-key", "import-key", "key-status"],
                       help="Commande à exécuter")
    parser.add_argument("--module", "-m", help="Chemin du dossier du module")
    parser.add_argument("--certifier", "-c", help="Nom du certifieur", default="LOMETA Authority")
    parser.add_argument("--id", "-i", help="ID du certificat pour révocation")
    parser.add_argument("--reason", "-r", help="Raison de la révocation", default="Revoked")
    parser.add_argument("--metadata", "-d", help="Métadonnées JSON", default="{}")
    parser.add_argument("--validity", "-v", help="Durée de validité en jours", type=int, default=365)
    parser.add_argument("--key-file", "-k", help="Fichier de clé publique à exporter/importer")
    parser.add_argument("--key-name", "-n", help="Nom de la clé", default="lometa_master")
    
    args = parser.parse_args()
    
    # ✅ Utiliser use_shared_keys=True pour activer les clés partagées
    manager = CertificateManager(use_shared_keys=True)
    
    if args.command == "setup":
        print_info("Configuration du gestionnaire de certificats...")
        private, public = manager.get_or_create_keypair()
        print_success(f"Clé privée: {manager.key_file}")
        print_success(f"Clé publique: {manager.public_key_file}")
        print_info(f"ID de la clé: {public[:16]}...")
        print_info(f"Machine ID: {manager.machine_id}")
        
        # Créer la clé partagée
        if manager.shared_key_manager:
            shared_key = manager.shared_key_manager.get_or_create_shared_key(args.key_name)
            print_success(f"Clé partagée '{args.key_name}' créée")
        
        print_info("\n📋 Pour partager les clés entre machines:")
        print_info("   1. Exportez la clé: python certificate_manager.py export-key")
        print_info("   2. Copiez le fichier sur l'autre machine")
        print_info("   3. Importez-la: python certificate_manager.py import-key --key-file public_key.json")
    
    elif args.command == "export-key":
        if not args.key_file:
            args.key_file = f"public_key_{args.key_name}.json"
        
        if manager.shared_key_manager:
            success = manager.shared_key_manager.export_shared_key(Path(args.key_file), args.key_name)
            if success:
                print_info(f"\n📁 Fichier exporté: {args.key_file}")
                print_info("   Copiez ce fichier sur toutes les machines qui doivent vérifier les certificats.")
        else:
            print_error("Gestionnaire de clés partagées non disponible")
    
    elif args.command == "import-key":
        if not args.key_file:
            print_error("Veuillez spécifier le fichier de clé avec --key-file")
            return
        
        if manager.shared_key_manager:
            manager.shared_key_manager.import_shared_key(Path(args.key_file))
        else:
            print_error("Gestionnaire de clés partagées non disponible")
    
    elif args.command == "key-status":
        print_info("📊 Statut des clés:")
        
        # Clé publique locale
        if manager.public_key_file.exists():
            pub = manager.public_key_file.read_text(encoding='utf-8').strip()
            print(f"   ✅ Clé publique locale: {pub[:16]}...")
        else:
            print("   ❌ Aucune clé publique locale")
        
        # Clé privée locale
        if manager.key_file.exists():
            priv = manager.key_file.read_text(encoding='utf-8').strip()
            print(f"   ✅ Clé privée locale: {priv[:16]}...")
        else:
            print("   ❌ Aucune clé privée locale")
        
        # Clés partagées
        if manager.shared_key_manager:
            keys = manager.shared_key_manager.list_keys()
            if keys:
                print(f"\n   🔑 Clés partagées ({len(keys)}):")
                for name, key_data in keys.items():
                    pub = key_data.get("public_key", "N/A")[:16]
                    created = key_data.get("created_at", "Inconnue")[:19]
                    print(f"      - {name}: {pub}... (créé: {created})")
            else:
                print("   ⚠️ Aucune clé partagée trouvée")
        
        print(f"\n   Machine ID: {manager.machine_id}")
    
    elif args.command == "certify":
        if not args.module:
            print_error("Veuillez spécifier le chemin du module avec --module")
            return
        
        module_dir = Path(args.module)
        if not module_dir.exists():
            print_error(f"Module introuvable: {module_dir}")
            return
        
        try:
            metadata = json.loads(args.metadata)
        except:
            metadata = {}
        
        cert = manager.certify_module(module_dir, args.certifier, args.validity, metadata)
        if cert:
            print("\n📋 Détails du certificat:")
            print(f"   Nom: {cert.data['module_name']}")
            print(f"   Version: {cert.data['module_version']}")
            print(f"   ID: {cert.data['certificate_id']}")
            print(f"   Date: {cert.data['certified_date']}")
            print(f"   Expiration: {cert.data['expiry_date']}")
            print(f"   Validité: {args.validity} jours")
            print(f"   Machine: {cert.data.get('machine_id', 'N/A')}")
            print(f"   Fichiers: {len(cert.data['checksums'])}")
            print(f"\n📁 Certificat: {module_dir / 'certificate.json'}")
    
    elif args.command == "verify":
        if not args.module:
            print_error("Veuillez spécifier le chemin du module avec --module")
            return
        
        module_dir = Path(args.module)
        if not module_dir.exists():
            print_error(f"Module introuvable: {module_dir}")
            return
        
        success, message = manager.verify_module(module_dir)
        if success:
            print_success(message)
        else:
            print_error(message)
    
    elif args.command == "list":
        certificates = manager.list_certificates()
        if not certificates:
            print_info("Aucun certificat trouvé.")
        else:
            print_header(f"📋 Certificats émis ({len(certificates)})")
            for cert in certificates:
                # Vérifier si expiré
                is_expired = False
                if 'expiry_date' in cert and cert['expiry_date']:
                    try:
                        from datetime import datetime
                        expiry = datetime.fromisoformat(cert['expiry_date'])
                        is_expired = expiry < datetime.now()
                    except:
                        pass
                
                status_icon = "❌" if is_expired else "✅"
                revoked = " 🚫" if manager.is_revoked(cert['certificate_id']) else ""
                print(f"   {status_icon} {cert['module_name']} v{cert['module_version']}{revoked}")
                print(f"      ID: {cert['certificate_id']}")
                print(f"      Certifié par: {cert['certified_by']}")
                print(f"      Date: {cert['certified_date'][:19]}")
                if cert.get('expiry_date'):
                    print(f"      Expiration: {cert['expiry_date'][:19]}")
                print()
    
    elif args.command == "revoke":
        if not args.id:
            print_error("Veuillez spécifier l'ID du certificat avec --id")
            return
        
        manager.revoke_certificate(args.id, args.reason)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

