# update_server.py
"""
Serveur HTTP minimaliste pour le téléchargement de modules
Démarrage: python -m update_server 8000
Le serveur liste et permet de télécharger tous les fichiers .zip du dossier courant
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import argparse
from pathlib import Path


class ModuleServerHandler(SimpleHTTPRequestHandler):
    """Handler qui sert les fichiers ZIP et liste les modules disponibles"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def do_GET(self):
        """Gère les requêtes GET"""
        parsed = urlparse(self.path)
        
        # Page d'accueil - Liste tous les ZIP
        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self._generate_html().encode('utf-8'))
        
        # API JSON - Liste des modules disponibles
        elif parsed.path == '/api/modules':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self._get_modules_list(), indent=2).encode('utf-8'))
        
        # Téléchargement de fichier
        else:
            super().do_GET()
    
    def _get_modules_list(self):
        """Récupère la liste de tous les fichiers ZIP"""
        modules = []
        current_dir = Path(os.getcwd())
        
        for zip_file in current_dir.glob("*.zip"):
            stat = zip_file.stat()
            modules.append({
                "id": zip_file.stem,
                "name": zip_file.stem.replace("_", " ").replace("-", " ").title(),
                "filename": zip_file.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "download_url": f"/{zip_file.name}"
            })
        
        # Trier par nom
        modules.sort(key=lambda x: x['name'])
        return modules
    
    def _generate_html(self):
        """Génère la page HTML avec la liste des modules"""
        modules = self._get_modules_list()
        
        modules_html = ""
        for m in modules:
            modules_html += f"""
            <div class="module">
                <div class="module-info">
                    <div class="module-name">📦 {m['name']}</div>
                    <div class="module-detail">📄 {m['filename']} • 💾 {m['size_mb']} MB</div>
                </div>
                <a href="{m['download_url']}" class="download-btn" download>📥 Télécharger</a>
            </div>
            """
        
        if not modules_html:
            modules_html = '<div class="empty">📂 Aucun module disponible. Déposez des fichiers .zip ici.</div>'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>LOMETA - Serveur de modules</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                }}
                .header {{
                    background: white;
                    border-radius: 20px;
                    padding: 30px;
                    text-align: center;
                    margin-bottom: 20px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }}
                .header h1 {{ color: #333; font-size: 28px; margin-bottom: 10px; }}
                .header p {{ color: #666; }}
                .stats {{
                    background: #e8f5e9;
                    border-radius: 10px;
                    padding: 8px 15px;
                    display: inline-block;
                    margin-top: 15px;
                }}
                .modules {{
                    display: grid;
                    gap: 12px;
                }}
                .module {{
                    background: white;
                    border-radius: 12px;
                    padding: 18px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                .module:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                }}
                .module-name {{ font-weight: bold; font-size: 16px; color: #333; margin-bottom: 5px; }}
                .module-detail {{ font-size: 12px; color: #888; }}
                .download-btn {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: transform 0.2s;
                }}
                .download-btn:hover {{ transform: scale(1.05); }}
                .empty {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    text-align: center;
                    color: #999;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: rgba(255,255,255,0.8);
                    font-size: 12px;
                }}
                .api {{
                    background: #1e293b;
                    color: #94a3b8;
                    border-radius: 8px;
                    padding: 10px;
                    margin-top: 20px;
                    font-family: monospace;
                    font-size: 11px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 LOMETA - Modules disponibles</h1>
                    <p>Déposez vos fichiers .zip dans ce dossier pour les rendre disponibles</p>
                    <div class="stats">📦 {len(modules)} module(s) disponible(s)</div>
                </div>
                
                <div class="modules">
                    {modules_html}
                </div>
                
                <div class="api">
                    🔧 API: <a href="/api/modules" style="color: #60a5fa;">GET /api/modules</a> - Liste des modules (JSON)
                </div>
                
                <div class="footer">
                    Serveur LOMETA | Ctrl+C pour arrêter
                </div>
            </div>
        </body>
        </html>
        """
    
    def log_message(self, format, *args):
        """Log personnalisé"""
        print(f"📡 {format % args}")


def run_server(port=8000):
    """Démarre le serveur"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ModuleServerHandler)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         🚀 SERVEUR DE MODULES LOMETA                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📡 Serveur: http://localhost:{port}
📁 Dossier: {os.getcwd()}

📋 Endpoints:
   🌐 GET  /              → Page d'accueil
   📥 GET  /fichier.zip   → Télécharger un module
   🔧 GET  /api/modules   → Liste des modules (JSON)

💡 Utilisation:
   1. Placez vos fichiers .zip dans ce dossier
   2. Accédez à http://localhost:{port}
   3. Cliquez sur "Télécharger"

⚠️  Ctrl+C pour arrêter
""")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Serveur arrêté")
        httpd.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serveur de modules LOMETA')
    parser.add_argument('port', type=int, nargs='?', default=8000,
                       help='Port (défaut: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)