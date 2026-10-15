# Sinistres

## 📋 Description
Module de gestion complête de sinistres

## 📦 Informations
- **Version**: 0.0.1
- **Auteur**: Fearless Cybertech
- **Catégorie**: generic
- **Licence**: MIT
- **Date de création**: 02/09/2026

## 🚀 Installation
```bash
# Activer le module
python manage.py enable_module Sinistres

# Appliquer les migrations
python manage.py migrate Sinistres
```

## 📁 Structure
```
Sinistres/
├── controllers/     # Logique métier
├── views/           # Interfaces utilisateur
├── models/          # Modèles de données
├── static/          # Fichiers statiques (CSS, JS, images)
├── templates/       # Templates HTML
├── tests/           # Tests unitaires
├── migrations/      # Migrations de base de données
├── main_ui.py       # Point d'entrée principal
├── manifest.json    # Configuration du module
└── README.md        # Documentation
```

## 🛠️ Développement
```bash
# Lancer les tests
python -m pytest Sinistres/tests/

# Formatage du code
black Sinistres/
```

## 📄 Licence
MIT
