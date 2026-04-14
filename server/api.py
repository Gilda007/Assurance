# server/api.py
import os
import json
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = "/home/fearless/Documents/Assurance"
ADDONS_DIR = os.path.join(BASE_DIR, "addons")
MANIFEST_FILE = os.path.join(BASE_DIR, "server", "versions.json")

def load_global_manifest():
    """Charge le manifest global des versions"""
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"app_version": "1.0.0", "modules": {}}

@app.route('/api/check_updates', methods=['GET'])
def check_updates():
    """Vérifie les mises à jour disponibles"""
    
    # Version actuelle du client (envoyée dans les headers)
    client_app_version = request.headers.get('X-App-Version', '0.0.0')
    client_modules = request.headers.get('X-Modules-Versions', '{}')
    
    try:
        client_modules = json.loads(client_modules)
    except:
        client_modules = {}
    
    # Charger les versions du serveur
    server_manifest = load_global_manifest()
    
    # Vérifier les mises à jour
    available_updates = {}
    
    # Vérifier l'application principale
    if is_newer_version(server_manifest.get('app_version', '0'), client_app_version):
        available_updates['app'] = {
            'type': 'app',
            'name': 'Application principale',
            'current_version': client_app_version,
            'new_version': server_manifest['app_version'],
            'download_url': f"http://192.168.100.17:5000/updates/MonApp.zip",
            'changelog': server_manifest.get('app_changelog', ''),
            'size': server_manifest.get('app_size', 0)
        }
    
    # Vérifier les modules
    for module_name, server_info in server_manifest.get('modules', {}).items():
        client_version = client_modules.get(module_name, '0.0.0')
        
        if is_newer_version(server_info.get('version', '0'), client_version):
            available_updates[module_name] = {
                'type': 'module',
                'name': module_name,
                'current_version': client_version,
                'new_version': server_info['version'],
                'download_url': server_info['download_url'],
                'changelog': server_info.get('changelog', ''),
                'size': server_info.get('size', 0),
                'summary': server_info.get('summary', ''),
                'required': server_info.get('required', False),
                'dependencies': server_info.get('dependencies', [])
            }
    
    return jsonify({
        'server_time': datetime.now().isoformat(),
        'has_updates': len(available_updates) > 0,
        'updates': available_updates,
        'server_manifest_version': server_manifest.get('last_updated', '')
    })

@app.route('/addons/<module_name>.zip')
def download_module(module_name):
    """Télécharge un module"""
    zip_path = os.path.join(ADDONS_DIR, f"{module_name}.zip")
    
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f"{module_name}.zip")
    
    return jsonify({'error': f'Module {module_name} non trouvé'}), 404

@app.route('/addons/<module_name>/manifest.json')
def get_module_manifest(module_name):
    """Retourne le manifest.json d'un module spécifique"""
    manifest_path = os.path.join(ADDONS_DIR, module_name, 'manifest.json')
    
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    
    return jsonify({'error': 'Manifest non trouvé'}), 404

def is_newer_version(server_version, client_version):
    """Compare deux versions"""
    try:
        server_parts = [int(x) for x in server_version.split('.')]
        client_parts = [int(x) for x in client_version.split('.')]
        
        while len(server_parts) < 3:
            server_parts.append(0)
        while len(client_parts) < 3:
            client_parts.append(0)
        
        return server_parts > client_parts
    except:
        return False

if __name__ == '__main__':
    print(f"📁 Dossier addons: {ADDONS_DIR}")
    print(f"📄 Fichier manifest: {MANIFEST_FILE}")
    print(f"🚀 Serveur démarré sur http://192.168.100.17:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)