#!/usr/bin/env python3
"""
Script interactif pour créer un module LOMETA à partir de données saisies.
Version améliorée avec templates, gestion des dépendances et plus encore.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT

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
# UTILITIES
# ============================================================================

def ask(prompt, default="", required=False, choices=None):
    """Demande une entrée à l'utilisateur avec validation."""
    if choices:
        prompt = f"{prompt} [{', '.join(choices)}]"
    
    while True:
        value = input(f"{prompt} [{default}]: ").strip() if default else input(f"{prompt}: ").strip()
        value = value if value else default
        
        if required and not value:
            print_error("Ce champ est requis.")
            continue
        
        if choices and value not in choices:
            print_error(f"Valeur invalide. Choisissez parmi: {', '.join(choices)}")
            continue
        
        return value

def ask_bool(prompt, default=True):
    """Demande une réponse oui/non."""
    default_text = "y/n" if default else "n/y"
    value = ask(f"{prompt} ({default_text})", "y" if default else "n")
    return value.lower() in {"1", "true", "yes", "y", "oui", "o"}

def snake_case(text):
    """Convertit un texte en snake_case."""
    text = re.sub(r'([A-Z])', r'_\1', text).lower()
    text = re.sub(r'[^a-z0-9_]', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_')

def pascal_case(text):
    """Convertit un texte en PascalCase."""
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    words = text.split()
    return ''.join(word.capitalize() for word in words if word)

def kebab_case(text):
    """Convertit un texte en kebab-case."""
    text = re.sub(r'([A-Z])', r'-\1', text).lower()
    text = re.sub(r'[^a-z0-9-]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def ensure_dir(path):
    """Crée un répertoire s'il n'existe pas."""
    path.mkdir(parents=True, exist_ok=True)

def certify_module_after_creation(module_dir):
    """Certifie automatiquement un module après sa création."""
    try:
        from certificate_manager import CertificateManager
        manager = CertificateManager()
        cert = manager.certify_module(module_dir, "LOMETA Generator")
        if cert:
            print_success("Module certifié automatiquement !")
            return True
    except ImportError:
        print_warning("Certificate Manager non disponible. Module non certifié.")
        return False

# ============================================================================
# TEMPLATES
# ============================================================================

TEMPLATES = {
    'crud': {
        'name': 'CRUD',
        'description': 'Contrôleur, vues et modèles pour une entité simple',
        'files': ['controller.py', 'model.py', 'views.py']
    },
    'api': {
        'name': 'API REST',
        'description': 'API REST avec endpoints CRUD',
        'files': ['api.py', 'serializers.py']
    },
    'simple': {
        'name': 'Simple',
        'description': 'Module minimal avec point d\'entrée',
        'files': ['main.py']
    },
    'full': {
        'name': 'Complet',
        'description': 'Structure complète avec tout ce qu\'il faut',
        'files': ['controller.py', 'model.py', 'views.py', 'api.py', 'services.py']
    }
}

# ============================================================================
# MODULE CREATION
# ============================================================================

def create_module_structure(config):
    """Crée la structure du module selon la configuration."""
    module_name = config['name']
    output_dir = config['output_dir']
    template_type = config.get('template', 'simple')
    
    print_header(f"📦 Création du module {module_name}")
    
    # Structure de base
    ensure_dir(output_dir)
    ensure_dir(output_dir / "controllers")
    ensure_dir(output_dir / "views")
    ensure_dir(output_dir / "models")
    ensure_dir(output_dir / "static")
    ensure_dir(output_dir / "templates")
    ensure_dir(output_dir / "tests")
    ensure_dir(output_dir / "migrations")
    
    # Fichiers init
    init_files = [
        (output_dir / "__init__.py", f'"""Package du module {module_name}."""\n'),
        (output_dir / "controllers" / "__init__.py", '"""Contrôleurs du module."""\n'),
        (output_dir / "views" / "__init__.py", '"""Vues du module."""\n'),
        (output_dir / "models" / "__init__.py", '"""Modèles du module."""\n'),
        (output_dir / "tests" / "__init__.py", '"""Tests du module."""\n'),
        (output_dir / "migrations" / "__init__.py", '"""Migrations du module."""\n'),
    ]
    
    for file_path, content in init_files:
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
    
    # Manifest
    manifest = {
        "name": config['name'],
        "version": config['version'],
        "description": config['description'],
        "author": config['author'],
        "entry_point": config['entry_point'],
        "enabled": config['enabled'],
        "category": config['category'],
        "min_app_version": config['min_app_version'],
        "created_at": datetime.now().isoformat(),
        "dependencies": config.get('dependencies', []),
        "python_version": config.get('python_version', '>=3.8'),
        "license": config.get('license', 'MIT'),
        "repository": config.get('repository', ''),
        "keywords": config.get('keywords', []),
    }
    
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", 
        encoding="utf-8"
    )
    
    # ✅ README avec f-string correctement fermé (utilisation de ''' pour les blocs de code)
        # README - Version corrigée sans f-string avec triples guillemets
    readme_content = (
        f"# {module_name}\n\n"
        f"## 📋 Description\n{config['description']}\n\n"
        f"## 📦 Informations\n"
        f"- **Version**: {config['version']}\n"
        f"- **Auteur**: {config['author']}\n"
        f"- **Catégorie**: {config['category']}\n"
        f"- **Licence**: {config.get('license', 'MIT')}\n"
        f"- **Date de création**: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        f"## 🚀 Installation\n```bash\n"
        f"# Activer le module\n"
        f"python manage.py enable_module {module_name}\n\n"
        f"# Appliquer les migrations\n"
        f"python manage.py migrate {module_name}\n```\n\n"
        f"## 📁 Structure\n```\n"
        f"{module_name}/\n"
        f"├── controllers/     # Logique métier\n"
        f"├── views/           # Interfaces utilisateur\n"
        f"├── models/          # Modèles de données\n"
        f"├── static/          # Fichiers statiques (CSS, JS, images)\n"
        f"├── templates/       # Templates HTML\n"
        f"├── tests/           # Tests unitaires\n"
        f"├── migrations/      # Migrations de base de données\n"
        f"├── manifest.json    # Configuration du module\n"
        f"└── main.py          # Point d'entrée\n"
        f"```\n\n"
        f"## 🛠️ Développement\n```bash\n"
        f"# Lancer les tests\n"
        f"python -m pytest {module_name}/tests/\n\n"
        f"# Formatage du code\n"
        f"black {module_name}/\n```\n\n"
        f"## 📄 Licence\n{config.get('license', 'MIT')}\n"
    )
    
    (output_dir / "README.md").write_text(readme_content, encoding="utf-8")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Point d'entrée principal."""
    print_header("🚀 LOMETA - Module Creator v2.0")
    
    # Informations de base
    module_name = ask("Nom du module", "MonModule", required=True)
    version = ask("Version", "1.0.0")
    description = ask("Description", "Module créé automatiquement")
    author = ask("Auteur", "Votre nom")
    category = ask("Catégorie", "generic")
    min_app_version = ask("Version minimale de l'application", "1.0.0")
    enabled = ask_bool("Activer le module immédiatement ?", True)
    
    # Template
    print("\n📋 Types de templates disponibles:")
    for key, template in TEMPLATES.items():
        print(f"   [{key}] {template['name']}: {template['description']}")
    
    template_type = ask("Type de template", "simple", choices=list(TEMPLATES.keys()))
    
    # Dependencies
    print("\n📦 Dépendances (séparées par des virgules, ex: requests, flask):")
    deps_input = input("> ").strip()
    dependencies = [d.strip() for d in deps_input.split(',') if d.strip()]
    
    # Output directory
    default_dir = str(Path.cwd() / snake_case(module_name))
    output_dir = Path(ask("Dossier de destination", default_dir))
    
    # Options supplémentaires
    generate_routes = ask_bool("Générer les fichiers de routes ?", False)
    generate_tests = ask_bool("Générer les tests unitaires ?", True)
    
    # Configuration finale
    config = {
        'name': module_name,
        'version': version,
        'description': description,
        'author': author,
        'entry_point': 'main.py',
        'enabled': enabled,
        'category': category,
        'min_app_version': min_app_version,
        'dependencies': dependencies,
        'python_version': '>=3.8',
        'license': 'MIT',
        'template': template_type,
        'output_dir': output_dir,
        'generate_routes': generate_routes,
        'generate_tests': generate_tests,
    }
    
    # Créer le module
    try:
        create_module_structure(config)
        
        # Résumé final
        print_header("📋 Résumé du module créé")
        print(f"   Nom: {color(module_name, 'bold')}")
        print(f"   Version: {version}")
        print(f"   Auteur: {author}")
        print(f"   Catégorie: {category}")
        print(f"   Template: {template_type}")
        if dependencies:
            print(f"   Dépendances: {', '.join(dependencies)}")
        print(f"   Activé: {color('Oui' if enabled else 'Non', 'green' if enabled else 'red')}")
        print(f"\n📁 Emplacement: {output_dir}")
        
        print("\n" + color("="*60, 'cyan'))
        print(color("✅ Module créé avec succès !", 'bold'))
        print(f"\n{color('💡', 'yellow')} Prochaines étapes:")
        print("   1. Activez le module dans la configuration de l'application")
        print("   2. Appliquez les migrations si nécessaire")
        print("   3. Ajoutez votre logique métier")
        print("   4. Testez votre module")
        print("\n" + color("="*60, 'cyan'))
        
    except Exception as e:
        print_error(f"Erreur lors de la création du module: {e}")
        sys.exit(1)

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()