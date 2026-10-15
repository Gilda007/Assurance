# test_certificate_manager.py - Version autonome corrigée

import os
import sys
import json
from pathlib import Path

# ✅ Ajouter le chemin parent pour pouvoir importer certificate_manager
current_dir = Path(__file__).parent.parent  # Va jusqu'à lometa_module_generator/
sys.path.insert(0, str(current_dir))

try:
    from certificate_manager import CertificateManager
    CERT_MANAGER_AVAILABLE = True
except ImportError:
    CERT_MANAGER_AVAILABLE = False
    print("❌ CertificateManager non disponible")


def get_certificates_dir():
    """Détermine le dossier des certificats."""
    import sys
    
    # Mode compilé
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        candidates = [
            os.path.join(base_dir, 'certificates'),
            os.path.join(base_dir, '_internal', 'certificates'),
            os.path.join(base_dir, '..', 'certificates'),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return os.path.join(base_dir, 'certificates')
    
    # Mode développement
    if os.path.exists('certificates'):
        return 'certificates'
    
    # Fallback
    return os.path.join(os.path.expanduser("~"), ".lometa", "certificates")


def check_certificates():
    """Vérifie tous les certificats présents sur le système."""
    
    print("=" * 60)
    print("🔐 DIAGNOSTIC DES CERTIFICATS LOMETA")
    print("=" * 60)
    
    # 1. Dossier des certificats
    cert_dir = get_certificates_dir()
    print(f"\n📁 Dossier certificats: {cert_dir}")
    print(f"   Existe: {'✅' if os.path.exists(cert_dir) else '❌'}")
    
    if os.path.exists(cert_dir):
        print(f"   Contenu:")
        for item in os.listdir(cert_dir):
            item_path = os.path.join(cert_dir, item)
            if os.path.isdir(item_path):
                print(f"      📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                print(f"      📄 {item} ({size} octets)")
    
    # 2. Clés partagées
    shared_keys_file = os.path.join(cert_dir, "shared_keys.json")
    if os.path.exists(shared_keys_file):
        print(f"\n   ✅ shared_keys.json présent")
        try:
            with open(shared_keys_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"      Clés: {', '.join(data.keys())}")
        except Exception as e:
            print(f"      ⚠️ Erreur lecture: {e}")
    else:
        print(f"\n   ❌ shared_keys.json absent - les certificats peuvent être rejetés")
    
    # 3. Clé publique locale
    public_key_file = os.path.join(cert_dir, "public_key.pem")
    if os.path.exists(public_key_file):
        print(f"\n   ✅ public_key.pem présent")
    else:
        print(f"\n   ❌ public_key.pem absent")
    
    # 4. Modules
    addons_dirs = [
        "addons",
        os.path.join(current_dir, "addons"),
        os.path.join(current_dir.parent, "addons"),
        os.path.join(current_dir, "..", "addons"),
        os.path.join(os.path.dirname(current_dir), "addons"),
    ]
    
    addons_found = False
    for addons_dir in addons_dirs:
        if os.path.exists(addons_dir) and os.path.isdir(addons_dir):
            addons_found = True
            print(f"\n📦 Modules dans {addons_dir}:")
            for item in os.listdir(addons_dir):
                module_path = os.path.join(addons_dir, item)
                if os.path.isdir(module_path):
                    cert_path = os.path.join(module_path, "certificate.json")
                    manifest_path = os.path.join(module_path, "manifest.json")
                    
                    if os.path.exists(cert_path):
                        # Vérifier les détails du certificat
                        try:
                            with open(cert_path, 'r', encoding='utf-8') as f:
                                cert_data = json.load(f)
                                expiry = cert_data.get("expiry_date")
                                if expiry:
                                    print(f"   ✅ {item}: certificate.json (expire: {expiry[:10]})")
                                else:
                                    print(f"   ✅ {item}: certificate.json (pas de date d'expiration)")
                        except:
                            print(f"   ✅ {item}: certificate.json")
                    elif os.path.exists(manifest_path):
                        print(f"   ⚠️ {item}: manifest.json présent mais certificate.json manquant")
                    else:
                        print(f"   📁 {item}: aucun certificat")
    
    if not addons_found:
        print("\n📦 Aucun module trouvé dans les dossiers addons")
    
    # 5. CertificateManager
    if CERT_MANAGER_AVAILABLE:
        print("\n🔍 Test CertificateManager...")
        try:
            manager = CertificateManager(config_dir=cert_dir, use_shared_keys=True)
            print("   ✅ CertificateManager initialisé")
            
            if hasattr(manager, 'shared_key_manager'):
                keys = manager.shared_key_manager.list_keys()
                if keys:
                    print(f"   🔑 {len(keys)} clé(s) partagée(s): {', '.join(keys.keys())}")
                else:
                    print("   ⚠️ Aucune clé partagée trouvée")
            
            certs = manager.list_certificates()
            if certs:
                print(f"\n   📋 {len(certs)} certificat(s) émis:")
                for cert in certs[:5]:
                    status = "✅" if cert.get('status') == "Valide" else "❌"
                    remaining = cert.get('remaining_days', 0)
                    expiry = cert.get('expiry_date', 'N/A')[:10]
                    print(f"      {status} {cert.get('module_name')} v{cert.get('module_version')}")
                    print(f"         Expire: {expiry} (reste {remaining} jours)")
            else:
                print("   ⚠️ Aucun certificat émis trouvé")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    else:
        print("\n❌ CertificateManager non disponible")
    
    # 6. Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ")
    print("=" * 60)
    
    issues = []
    if not os.path.exists(cert_dir):
        issues.append("❌ Dossier certificats manquant")
    if not os.path.exists(shared_keys_file):
        issues.append("❌ shared_keys.json manquant")
    if not os.path.exists(public_key_file):
        issues.append("❌ public_key.pem manquant")
    
    if issues:
        print("⚠️ Problèmes détectés:")
        for issue in issues:
            print(f"   {issue}")
        print("\n👉 Solution: exécutez 'python certificate_manager.py setup'")
    else:
        print("✅ Tous les composants sont présents")
    
    print("=" * 60)


if __name__ == "__main__":
    check_certificates()