# testModule

## 📋 Description
Module créé automatiquement

## 📦 Informations
- **Version**: 1.0.0
- **Auteur**: Votre nom
- **Catégorie**: generic
- **Icône sidebar**: `fa5s.cube`
- **Label sidebar**: testModule
- **Date**: 14/10/2026

## 🏗️ Architecture
Ce module utilise le **pattern LOMETA Lazy Loading** :
- Chaque page est créée **à la demande**
- Un `LoadingPage` s'affiche pendant la création
- L'UI ne gèle **jamais**

## 📁 Structure
```
testModule/
├── controllers/          # Logique métier
├── views/                # Interfaces utilisateur
│   ├── widgets/
│   │   └── loading_page.py  # Loader réutilisable
│   └── view.py           # Vue principale (lazy loading)
├── models/               # Modèles de données
├── main_ui.py            # Point d'entrée principal
├── manifest.json         # Configuration du module
└── README.md             # Documentation
```

## ✨ Développement

### Remplacer une page par défaut
Dans `views/view.py`, remplace le corps de `_make_<page_id>()` :
```python
def _make_items(self):
    from .items_view import ItemsView
    return ItemsView(controller=self.controller, user=self.user)
```

### Ajouter une page
1. Ajoute une entrée dans `SIDEBAR_ITEMS`
2. Ajoute une factory dans `_register_page_factories`

## 📄 Licence
MIT
