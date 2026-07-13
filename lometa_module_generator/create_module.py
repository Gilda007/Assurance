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
# TEMPLATES POUR main_ui.py ET view.py
# ============================================================================

def get_main_ui_template(module_name, class_name):
    """Génère le template pour main_ui.py"""
    return f'''from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from core.alerts import AlertManager

from addons.{module_name}.views.view import {class_name}


# Style moderne pour le bouton de la barre latérale
MODERN_BTN_STYLE = """
QPushButton {{
    background-color: transparent;
    color: #546e7a;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding-left: 15px;
    font-size: 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: #f1f3f4;
    color: #1a73e8;
}}
QPushButton:checked {{
    background-color: #e8f0fe;
    color: #1a73e8;
    border-right: 3px solid #1a73e8;
}}
"""


class {class_name}Module(BaseModule):
    def __init__(self, main_window=None, controller=None):
        """Initialisation du module avec controller"""
        super().__init__(main_window)
        self.controller = controller
        self.db_session = None
        self.current_user = None
        self.view = None
        self.btn = None
        
    def setup(self):
        """Initialisation silencieuse du module"""
        # 1. Récupération sécurisée de la session
        self.db_session = getattr(self.main_window, 'db_session', None)
        self.current_user = getattr(self.main_window, 'current_user', None)
        
        # 2. Création du bouton avec un style Premium
        self.btn = QPushButton("  👤 {module_name}")
        self.btn.setCheckable(True)
        self.btn.setFixedHeight(50)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(MODERN_BTN_STYLE)
        
        # 3. Connexion de l'événement
        self.btn.clicked.connect(self.activate_module)
        
        # 4. Ajout au menu latéral
        if hasattr(self.main_window, 'sidebar_layout'):
            self.main_window.sidebar_layout.addWidget(self.btn)

    def activate_module(self):
        """Logique d'activation avec récupération dynamique de l'utilisateur"""
        try:
            # RECHERCHE DYNAMIQUE : On va chercher l'info fraîche dans la fenêtre principale
            user = getattr(self.main_window, 'current_user', None)
            db_session = getattr(self.main_window, 'db_session', None)

            if not user:
                AlertManager.show_error(self.main_window, "Sécurité", "Aucun utilisateur connecté détecté.")
                return

            # Mise à jour de la référence locale
            self.current_user = user
            self.db_session = db_session

            # Création de la vue avec le controller
            self.view = {class_name}(controller=self.controller, user=self.current_user)
            
            # Affichage dans la fenêtre principale
            self.main_window.set_content_widget(self.view)
            
            # Mettre à jour l'état du bouton
            self.btn.setChecked(True)

        except Exception as e:
            AlertManager.show_error(self.main_window, "Erreur", str(e))
'''

def get_view_template(module_name, class_name):
    """Génère le template pour view.py"""
    return f'''from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                             QListWidgetItem, QStackedWidget, QListWidget, QFrame, 
                             QMessageBox, QDialog, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QFont


class {class_name}(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.pages_cache = {{}}

        # Style Global du Widget Principal
        self.setObjectName("MainSettingsWindow")
        self.setStyleSheet("background-color: #f8fafc;")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Configurer la sidebar et le contenu
        self.setup_sidebar()
        self.setup_content_area()
        
        # Sélectionner la première page par défaut
        if hasattr(self, 'sidebar') and self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)

    def setup_sidebar(self):
        """Création de la barre latérale avec les pages"""
        # Conteneur de la sidebar
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(250)
        self.sidebar_container.setStyleSheet("""
            QFrame {{
                background-color: white;
                border-radius: 0px;
                border-right: 1px solid #e2e8f0;
            }}
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Titre de la sidebar
        title_label = QLabel("📋 Menu")
        title_label.setStyleSheet("""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: #1e293b;
                padding-bottom: 15px;
                border-bottom: 2px solid #e2e8f0;
            }}
        """)
        sidebar_layout.addWidget(title_label)
        
        # Liste des pages
        self.sidebar = QListWidget()
        self.sidebar.setStyleSheet("""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px 15px;
                border-radius: 8px;
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background-color: #f1f5f9;
                color: #1e293b;
            }}
            QListWidget::item:selected {{
                background-color: #e2e8f0;
                color: #1a73e8;
            }}
        """)
        self.sidebar.setFixedWidth(220)
        
        # Ajout des pages
        pages = [
            ("Accueil", "🏠"),
            ("Véhicules", "🚗"),
            ("Contrats", "📄"),
            ("Clients", "👤"),
            ("Rapports", "📊"),
            ("Paramètres", "⚙️")
        ]
        
        for text, icon in pages:
            item = QListWidgetItem(f"{{icon}} {{text}}")
            self.sidebar.addItem(item)
        
        self.sidebar.currentRowChanged.connect(self.switch_page)
        sidebar_layout.addWidget(self.sidebar)
        
        # Informations utilisateur en bas
        user_info = QFrame()
        user_info.setStyleSheet("""
            QFrame {{
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 10px;
                margin-top: 20px;
            }}
            QLabel {{
                color: #1e293b;
                font-size: 12px;
            }}
        """)
        user_layout = QVBoxLayout(user_info)
        
        user_name = QLabel(f"👤 {{self.user.username if self.user else 'Utilisateur'}}")
        user_name.setStyleSheet("font-weight: bold; font-size: 13px;")
        user_layout.addWidget(user_name)
        
        user_role = QLabel(f"Rôle: {{self.user.role if self.user else 'Non défini'}}")
        user_role.setStyleSheet("color: #64748b; font-size: 11px;")
        user_layout.addWidget(user_role)
        
        sidebar_layout.addWidget(user_info)
        
        # Ajout de la sidebar au layout principal
        self.layout.addWidget(self.sidebar_container)

    def setup_content_area(self):
        """Zone de contenu avec effet d'ombre interne"""
        self.content_container = QFrame()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(30, 30, 30, 30)

        # Stack d'affichage (Pages)
        self.container = QStackedWidget()
        self.container.setStyleSheet("""
            QStackedWidget {{
                background-color: white; 
                border-radius: 20px; 
                border: 1px solid #e2e8f0;
            }}
        """)
        
        # Ajout d'une ombre portée douce au conteneur de contenu
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.container.setGraphicsEffect(shadow)

        # --- PAGE 1 : ACCUEIL (Hello World) ---
        hello_page = QWidget()
        hello_layout = QVBoxLayout(hello_page)
        hello_layout.setAlignment(Qt.AlignCenter)
        
        hello_label = QLabel("Hello World")
        hello_label.setStyleSheet("""
            QLabel {{
                font-size: 48px;
                font-weight: bold;
                color: #1e293b;
                background-color: transparent;
                padding: 20px;
            }}
        """)
        hello_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Bienvenue dans LOMETA")
        subtitle_label.setStyleSheet("""
            QLabel {{
                font-size: 18px;
                color: #64748b;
                background-color: transparent;
            }}
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        hello_layout.addWidget(hello_label)
        hello_layout.addWidget(subtitle_label)
        self.container.addWidget(hello_page)

        # --- PAGE 2 : VÉHICULES ---
        vehicles_page = QWidget()
        vehicles_layout = QVBoxLayout(vehicles_page)
        vehicles_layout.setAlignment(Qt.AlignCenter)
        
        vehicles_label = QLabel("🚗 Gestion des Véhicules")
        vehicles_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        vehicles_label.setAlignment(Qt.AlignCenter)
        vehicles_layout.addWidget(vehicles_label)
        
        vehicles_sub = QLabel("Module en cours de développement")
        vehicles_sub.setStyleSheet("font-size: 14px; color: #64748b;")
        vehicles_sub.setAlignment(Qt.AlignCenter)
        vehicles_layout.addWidget(vehicles_sub)
        self.container.addWidget(vehicles_page)

        # --- PAGE 3 : CONTRATS ---
        contracts_page = QWidget()
        contracts_layout = QVBoxLayout(contracts_page)
        contracts_layout.setAlignment(Qt.AlignCenter)
        
        contracts_label = QLabel("📄 Gestion des Contrats")
        contracts_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        contracts_label.setAlignment(Qt.AlignCenter)
        contracts_layout.addWidget(contracts_label)
        
        contracts_sub = QLabel("Module en cours de développement")
        contracts_sub.setStyleSheet("font-size: 14px; color: #64748b;")
        contracts_sub.setAlignment(Qt.AlignCenter)
        contracts_layout.addWidget(contracts_sub)
        self.container.addWidget(contracts_page)

        # --- PAGE 4 : CLIENTS ---
        clients_page = QWidget()
        clients_layout = QVBoxLayout(clients_page)
        clients_layout.setAlignment(Qt.AlignCenter)
        
        clients_label = QLabel("👤 Gestion des Clients")
        clients_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        clients_label.setAlignment(Qt.AlignCenter)
        clients_layout.addWidget(clients_label)
        
        clients_sub = QLabel("Module en cours de développement")
        clients_sub.setStyleSheet("font-size: 14px; color: #64748b;")
        clients_sub.setAlignment(Qt.AlignCenter)
        clients_layout.addWidget(clients_sub)
        self.container.addWidget(clients_page)

        # --- PAGE 5 : RAPPORTS ---
        reports_page = QWidget()
        reports_layout = QVBoxLayout(reports_page)
        reports_layout.setAlignment(Qt.AlignCenter)
        
        reports_label = QLabel("📊 Rapports et Statistiques")
        reports_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        reports_label.setAlignment(Qt.AlignCenter)
        reports_layout.addWidget(reports_label)
        
        reports_sub = QLabel("Module en cours de développement")
        reports_sub.setStyleSheet("font-size: 14px; color: #64748b;")
        reports_sub.setAlignment(Qt.AlignCenter)
        reports_layout.addWidget(reports_sub)
        self.container.addWidget(reports_page)

        # --- PAGE 6 : PARAMÈTRES ---
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setAlignment(Qt.AlignCenter)
        
        settings_label = QLabel("⚙️ Paramètres")
        settings_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        settings_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(settings_label)
        
        settings_sub = QLabel("Configuration de l'application")
        settings_sub.setStyleSheet("font-size: 14px; color: #64748b;")
        settings_sub.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(settings_sub)
        self.container.addWidget(settings_page)

        # Ajout du conteneur principal
        self.content_layout.addWidget(self.container)
        self.layout.addWidget(self.content_container)

    def switch_page(self, index):
        """Changer la page affichée"""
        if index >= 0 and index < self.container.count():
            self.container.setCurrentIndex(index)
'''

# ============================================================================
# MODULE CREATION
# ============================================================================

def create_module_structure(config):
    """Crée la structure du module selon la configuration."""
    module_name = config['name']
    output_dir = config['output_dir']
    class_name = pascal_case(module_name) + "MainView"
    
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
    
    # Création de main_ui.py à la racine
    main_ui_content = get_main_ui_template(module_name, class_name)
    (output_dir / "main_ui.py").write_text(main_ui_content, encoding="utf-8")
    print_success(f"Fichier main_ui.py créé")
    
    # Création de view.py dans le dossier views
    view_content = get_view_template(module_name, class_name)
    (output_dir / "views" / "view.py").write_text(view_content, encoding="utf-8")
    print_success(f"Fichier views/view.py créé")
    
    # Manifest
    manifest = {
        "name": module_name,
        "version": config['version'],
        "description": config['description'],
        "author": config['author'],
        "entry_point": "main_ui.py",
        "enabled": config['enabled'],
        "category": config['category'],
        "min_app_version": config['min_app_version'],
        "created_at": datetime.now().isoformat(),
        "dependencies": config.get('dependencies', []),
        "python_version": config.get('python_version', '>=3.8'),
        "license": config.get('license', 'MIT'),
        "repository": config.get('repository', ''),
        "keywords": config.get('keywords', []),
        "main_class": f"{class_name}Module",
        "view_class": class_name
    }
    
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", 
        encoding="utf-8"
    )
    
    # README
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
        f"├── main_ui.py       # Point d'entrée principal\n"
        f"├── manifest.json    # Configuration du module\n"
        f"└── README.md        # Documentation\n"
        f"```\n\n"
        f"## 🛠️ Développement\n```bash\n"
        f"# Lancer les tests\n"
        f"python -m pytest {module_name}/tests/\n\n"
        f"# Formatage du code\n"
        f"black {module_name}/\n```\n\n"
        f"## 📄 Licence\n{config.get('license', 'MIT')}\n"
    )
    
    (output_dir / "README.md").write_text(readme_content, encoding="utf-8")
    print_success(f"README.md créé")

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
        'entry_point': 'main_ui.py',
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
        print(f"\n📄 Fichiers créés:")
        print(f"   - {output_dir}/main_ui.py")
        print(f"   - {output_dir}/views/view.py")
        print(f"   - {output_dir}/manifest.json")
        print(f"   - {output_dir}/README.md")
        
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()