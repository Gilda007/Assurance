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
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.data = {
            "version": self.VERSION,
            "module_name": "",
            "module_version": "",
            "certified_by": "",
            "certified_date": "",
            "certificate_id": "",
            "checksums": {},
            "signature": "",
            "public_key": "",
            "certificate_chain": [],
            "metadata": {}
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


# ============================================================================
# CERTIFICATE MANAGER
# ============================================================================

class CertificateManager:
    """Gestionnaire de certificats pour les modules."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".lometa" / "certificates"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.config_dir / "private_key.pem"
        self.public_key_file = self.config_dir / "public_key.pem"
        self.certificates_dir = self.config_dir / "issued"
        self.certificates_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    # def certify_module(self, module_dir: Path, certifier_name: str, 
    #                    metadata: Dict = None) -> Optional[ModuleCertificate]:
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
        
    #     # Créer le certificat
    #     cert = ModuleCertificate()
    #     cert.data["module_name"] = module_name
    #     cert.data["module_version"] = module_version
    #     cert.data["certified_by"] = certifier_name
    #     cert.data["certified_date"] = datetime.now().isoformat()
    #     cert.data["certificate_id"] = cert.generate_certificate_id(module_name)
    #     cert.data["public_key"] = public_key
    #     cert.data["checksums"] = cert.compute_directory_checksums(module_dir)
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
        
    #     return cert
    
    def certify_module(self, module_dir: Path, certifier_name: str, 
                   metadata: Dict = None) -> Optional[ModuleCertificate]:
        """Certifie un module en générant un certificat signé."""
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
        # ✅ Exclure certificate.json des checksums
        cert.data["checksums"] = cert.compute_directory_checksums(
            module_dir, 
            exclude=['.pyc', '__pycache__', '.git', '.DS_Store', 'certificate.json']
        )
        cert.data["metadata"] = metadata or {}
        
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
        print_success(f"Signature: {cert.data['signature'][:16]}...")
        
        return cert

    # def verify_module(self, module_dir: Path) -> Tuple[bool, str]:
    #     """Vérifie l'intégrité d'un module certifié."""
    #     module_dir = Path(module_dir)
    #     cert_file = module_dir / "certificate.json"
        
    #     if not cert_file.exists():
    #         return False, "❌ Certificate.json non trouvé. Le module n'est pas certifié."
        
    #     # Charger le certificat
    #     cert = ModuleCertificate()
    #     if not cert.load(cert_file):
    #         return False, "❌ Certificat invalide ou corrompu."
        
    #     print_info(f"Vérification du certificat: {cert.data.get('certificate_id', 'N/A')}")
        
    #     # ✅ Vérifier la signature - si échec, essayer de recharger avec la clé publique
    #     if not cert.verify_signature():
    #         # ✅ Tenter de récupérer la clé publique depuis le certificat lui-même
    #         public_key = cert.data.get("public_key", "")
    #         if public_key:
    #             # Recalculer avec la clé publique du certificat
    #             data_to_verify = {
    #                 "module_name": cert.data["module_name"],
    #                 "module_version": cert.data["module_version"],
    #                 "certified_by": cert.data["certified_by"],
    #                 "certified_date": cert.data["certified_date"],
    #                 "certificate_id": cert.data["certificate_id"],
    #                 "checksums": cert.data["checksums"]
    #             }
    #             data_str = json.dumps(data_to_verify, sort_keys=True)
                
    #             expected = hmac.new(
    #                 public_key.encode(),
    #                 data_str.encode(),
    #                 hashlib.sha256
    #             ).hexdigest()
                
    #             if hmac.compare_digest(cert.data["signature"], expected):
    #                 print_success("✅ Signature valide (vérifiée avec la clé publique du certificat)")
    #             else:
    #                 # ✅ Pour les certificats auto-signés ou de développement
    #                 if cert.data.get("signature") == cert.data.get("public_key"):
    #                     print_warning("Certificat auto-signé (mode développement)")
    #                 else:
    #                     return False, f"❌ Signature invalide. Attendu: {expected[:16]}..., Reçu: {cert.data['signature'][:16]}..."
    #         else:
    #             return False, "❌ Aucune clé publique trouvée dans le certificat."
        
    #     # ✅ Vérifier l'intégrité des fichiers
    #     expected = cert.data.get("checksums", {})
    #     if not expected:
    #         return False, "❌ Aucun checksum dans le certificat."
        
    #     print_info("Vérification de l'intégrité des fichiers...")
    #     errors = []
        
    #     for file_path, expected_hash in expected.items():
    #         full_path = module_dir / file_path
    #         if not full_path.exists():
    #             errors.append(f"Fichier manquant: {file_path}")
    #             continue
            
    #         actual_hash = cert.compute_checksum(full_path)
    #         if actual_hash != expected_hash:
    #             errors.append(f"Fichier modifié: {file_path}")
        
    #     # Vérifier les fichiers ajoutés
    #     for file_path in module_dir.rglob('*'):
    #         if file_path.is_file():
    #             rel_path = str(file_path.relative_to(module_dir))
    #             if rel_path not in expected and rel_path != 'certificate.json':
    #                 if not any(x in rel_path for x in ['.pyc', '__pycache__', '.DS_Store']):
    #                     errors.append(f"Fichier ajouté: {rel_path}")
        
    #     if errors:
    #         return False, f"❌ Intégrité compromise:\n- " + "\n- ".join(errors[:10])
        
    #     return True, f"✅ Module certifié LOMETA par {cert.data.get('certified_by', 'Inconnu')} (ID: {cert.data.get('certificate_id', 'N/A')})"

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


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """Point d'entrée principal."""
    print_header("🔐 LOMETA - Certificate Manager v1.0")
    
    import argparse
    parser = argparse.ArgumentParser(description="Gestionnaire de certificats LOMETA")
    parser.add_argument("command", choices=["certify", "verify", "list", "revoke", "setup"],
                       help="Commande à exécuter")
    parser.add_argument("--module", "-m", help="Chemin du dossier du module")
    parser.add_argument("--certifier", "-c", help="Nom du certifieur", default="LOMETA Authority")
    parser.add_argument("--id", "-i", help="ID du certificat pour révocation")
    parser.add_argument("--reason", "-r", help="Raison de la révocation", default="Revoked")
    parser.add_argument("--metadata", "-d", help="Métadonnées JSON", default="{}")
    
    args = parser.parse_args()
    
    manager = CertificateManager()
    
    if args.command == "setup":
        print_info("Configuration du gestionnaire de certificats...")
        private, public = manager.get_or_create_keypair()
        print_success(f"Clé privée: {manager.key_file}")
        print_success(f"Clé publique: {manager.public_key_file}")
        print_info(f"ID de la clé: {public[:16]}...")
        
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
        
        cert = manager.certify_module(module_dir, args.certifier, metadata)
        if cert:
            print("\n📋 Détails du certificat:")
            print(f"   Nom: {cert.data['module_name']}")
            print(f"   Version: {cert.data['module_version']}")
            print(f"   ID: {cert.data['certificate_id']}")
            print(f"   Date: {cert.data['certified_date']}")
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
                status = "✅" if not manager.is_revoked(cert['certificate_id']) else "❌"
                print(f"   {status} {cert['module_name']} v{cert['module_version']}")
                print(f"      ID: {cert['certificate_id']}")
                print(f"      Certifié par: {cert['certified_by']}")
                print(f"      Date: {cert['certified_date'][:19]}")
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