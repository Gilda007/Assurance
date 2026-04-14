# server/build_manifest.py
import os
import json
import zipfile
import hashlib
from datetime import datetime

def compute_checksum(file_path):
    """Calcule le checksum SHA256 d'un fichier"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def build_manifest(addons_dir, output_file="versions.json"):
    """Construit le manifest global à partir des manifest.json des modules"""
    
    modules_info = {}
    
    # Parcourir tous les dossiers de modules
    for module_name in os.listdir(addons_dir):
        module_path = os.path.join(addons_dir, module_name)
        manifest_path = os.path.join(module_path, "manifest.json")
        
        if os.path.isdir(module_path) and os.path.exists(manifest_path):
            # Lire le manifest.json du module
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Créer le fichier ZIP du module
            zip_path = os.path.join(addons_dir, f"{module_name}.zip")
            
            # Si le ZIP n'existe pas ou est plus ancien que le dossier, le recréer
            if not os.path.exists(zip_path) or \
               os.path.getmtime(module_path) > os.path.getmtime(zip_path):
                create_module_zip(module_path, zip_path)
            
            # Calculer la taille et le checksum
            zip_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
            checksum = compute_checksum(zip_path) if os.path.exists(zip_path) else ""
            
            modules_info[module_name] = {
                "version": manifest.get("version", "1.0.0"),
                "name": manifest.get("name", module_name),
                "summary": manifest.get("summary", ""),
                "changelog": manifest.get("changelog", ""),
                "size": zip_size,
                "checksum": checksum,
                "download_url": f"http://192.168.100.17:5000/addons/{module_name}.zip",
                "min_app_version": manifest.get("min_app_version", "1.0.0"),
                "dependencies": manifest.get("dependencies", []),
                "required": manifest.get("required", False)
            }
    
    # Construire le manifest global
    global_manifest = {
        "app_version": "1.2.0",  # À lire depuis l'application principale
        "last_updated": datetime.now().isoformat(),
        "modules": modules_info,
        "server_info": {
            "url": "http://192.168.100.17:5000",
            "api_version": "1.0"
        }
    }
    
    # Sauvegarder le manifest global
    output_path = os.path.join(os.path.dirname(addons_dir), "server", output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(global_manifest, f, indent=2)
    
    print(f"✅ Manifest généré: {output_path}")
    print(f"   {len(modules_info)} modules trouvés")
    
    return global_manifest

def create_module_zip(module_path, zip_path):
    """Crée un fichier ZIP du module"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(module_path):
            # Ignorer certains dossiers
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'temp']]
            
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(module_path))
                zipf.write(file_path, arcname)
    
    print(f"📦 ZIP créé: {zip_path}")

if __name__ == "__main__":
    ADDONS_DIR = "/home/fearless/Documents/Assurance/addons"
    build_manifest(ADDONS_DIR)