# 📋 CONTEXTE LOMETA - MISE À JOUR COMPLÈTE
## Version : 2.1 | Date : 4 Septembre 2026

---

## 1. ÉTAT D'AVANCEMENT GÉNÉRAL

### ✅ COMPLÉTÉ

| Élément | Statut | Description |
|---------|--------|-------------|
| **Modèles SQLAlchemy** | ✅ Terminé | 23 tables avec préfixe Lometa, relations corrigées |
| **AuditableMixin** | ✅ Corrigé | Changé de UUID à Integer pour created_by/updated_by |
| **Services** | ✅ Terminé | BaseService, SinistreService, ExpertiseService, EvaluationService, ReglementService, RecoursService, ReferentielService, WorkflowService, AuditService, AutomobileService |
| **Contrôleurs** | ✅ Terminé | BaseController, SinistreController, ExpertiseController, EvaluationController, ReglementController, RecoursController, ReferentielController, AutomobileController |
| **Vue principale** | ✅ Terminé | LometaSinistresMainView avec sidebar et 8 pages |
| **Tableau de bord** | ✅ Terminé | DashboardPage avec statistiques et sinistres récents |
| **Nouveau sinistre** | ✅ Terminé | Formulaire complet avec recherche client, sélection contrat, référentiels |
| **Recherche** | ✅ Terminé | Recherche textuelle, filtres, double-clic pour Dossier 360° |
| **Dossier 360°** | ✅ Terminé | 10 onglets (Général, Client, Dommages, Tiers, Expertises, Évaluations, Règlements, Recours, Documents, Historique) |
| **Création mission** | ✅ Terminé | MissionDialog avec date_mission, date_echeance, expert, montant |
| **Dialogues** | ✅ Terminé | EditSinistreDialog, AddDommageDialog, AddTiersDialog, AddExpertiseDialog, AddEvaluationDialog, AddReglementDialog, AddRecoursDialog |
| **Données initiales** | ✅ Terminé | REFERENTIELS_INITIAUX (50+ entrées dans 7 familles) |
| **Migration base** | ✅ Partiel | Tables créées, types corrigés (UUID→Integer pour audit) |

### ⏳ EN COURS / À FAIRE

| Élément                       | Priorité   |                      Description                            |
|-------------------------------|------------|-------------------------------------------------------------|
| **Affecter expert à mission** | 🔴 Haute   | Dialogue d'affectation avec liste des experts disponibles   |
| **Déposer rapport expertise** | 🔴 Haute   | Dialogue avec upload de fichier et saisie du rapport        |
| **Valider mission expertise** | 🔴 Haute   | Action de validation avec vérification des prérequis        |
| **Création évaluation**       | 🟡 Moyenne | ÉvaluationDialog avec calcul auto du montant net            |
| **Réviser évaluation**        | 🟡 Moyenne | Dialogue de révision avec historisation                     |
| **Valider évaluation**        | 🟡 Moyenne | Action de validation avec changement de statut sinistre     |
| **Création règlement**        | 🟡 Moyenne | ReglementDialog avec sélection bénéficiaire                 |
| **Payer règlement**           | 🟡 Moyenne | PaiementDialog avec chèque/virement/Mobile Money            |
| **Lots de paiement**          | 🟢 Basse   | Création et gestion des lots                                |
| **Création recours**          | 🟡 Moyenne | RecoursDialog                                               |
| **Encaissement recours**      | 🟡 Moyenne | EncaissementDialog                                          |
| **Gestion relances**          | 🟢 Basse   | Relance automatique et suivi                                |
| **GED Documents**             | 🟢 Basse   | Intégration complète de la GED                              |
| **Tests unitaires**           | 🟢 Basse   | Tests des services et contrôleurs                           |

---

## 2. STRUCTURE DU PROJET

```
addons/lometa_sinistres/
├── __init__.py                    # ✅ Export des composants
├── main_ui.py                     # ✅ LometaSinistresModule
├── manifest.json                  # ✅ Configuration
├── controllers/
│   ├── __init__.py
│   ├── controleur_base.py         # ✅ BaseController
│   ├── sinistre_controller.py     # ✅ CRUD, cycle de vie
│   ├── referentiel_controller.py  # ✅ Référentiels
│   ├── expertise_controller.py    # ✅ Missions
│   ├── evaluation_controller.py   # ✅ Évaluations
│   ├── reglement_controller.py    # ✅ Règlements
│   ├── recours_controller.py      # ✅ Recours
│   └── automobile_controller.py   # ✅ Clients, Contrats
├── views/
│   ├── __init__.py
│   ├── view.py                    # ✅ Vue principale
│   ├── dossier_360.py             # ✅ Dossier 360°
│   ├── mission_dialog.py          # ✅ Création mission
│   ├── dialogs.py                 # ✅ Tous les dialogues
│   ├── client_search_widget.py    # ✅ Recherche client
│   └── contract_selector_widget.py # ✅ Sélection contrat
├── models/
│   ├── __init__.py                # ✅ Export modèles
│   ├── base.py                    # ✅ Base SQLAlchemy
│   ├── sinistre.py                # ✅ LometaSinistre, Dommage, Tiers, Commentaire, Historique
│   ├── expertise.py               # ✅ LometaExpertise, Evaluation, Provision
│   ├── reglement.py               # ✅ LometaReglement, Beneficiaire, LotPaiement
│   ├── recours.py                 # ✅ LometaRecours, Encaissement, Reversement
│   ├── referentiel.py             # ✅ LometaReferentiel
│   ├── referentiel_data.py        # ✅ Données initiales
│   └── audit.py                   # ✅ LometaAuditLog
├── services/
│   ├── __init__.py
│   ├── base_service.py            # ✅ Session, audit, génération
│   ├── sinistre_service.py        # ✅ CRUD, cycle de vie
│   ├── expertise_service.py       # ✅ Missions, rapports
│   ├── evaluation_service.py      # ✅ Évaluations, provisions
│   ├── reglement_service.py       # ✅ Règlements, lots
│   ├── recours_service.py         # ✅ Recours, encaissements
│   ├── referentiel_service.py     # ✅ Référentiels
│   ├── workflow_service.py        # ✅ Workflow paramétrable
│   ├── audit_service.py           # ✅ Journal d'audit
│   └── automobile_service.py      # ✅ Clients, Contrats
└── migrations/
    └── versions/
        └── 001_initial_lometa_schema.py  # ✅ Migration initiale
```

---

## 3. BASE DE DONNÉES - CORRECTIONS APPLIQUÉES

### Modifications du modèle

| Fichier | Modification | Statut |
|---------|--------------|--------|
| **core/database.py** | `AuditableMixin` : UUID → Integer | ✅ Fait |
| **expertise.py** | `date_mission` : nullable=False avec valeur par défaut | ✅ Fait |
| **reglement.py** | `lot_paiement_id` : ForeignKey corrigée | ✅ Fait |

### SQL à exécuter pour corriger la base

```sql
-- 1. Rendre date_mission NOT NULL avec valeur par défaut
ALTER TABLE lometa_expertises 
ALTER COLUMN date_mission SET NOT NULL;

-- 2. Si des lignes existent avec NULL
UPDATE lometa_expertises 
SET date_mission = date_echeance 
WHERE date_mission IS NULL;

-- 3. Vérifier les types des colonnes d'audit
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name LIKE 'lometa_%' 
AND column_name IN ('created_by', 'updated_by');
```

---

## 4. FONCTIONNALITÉS À DÉVELOPPER - DÉTAIL

### PRIORITÉ HAUTE 🔴

#### 1. Affecter un expert à une mission

**Fichier :** `views/affecter_expert_dialog.py` (à créer)

**Fonctionnalités :**
- Liste des experts disponibles (depuis `utilisateurs` avec rôle expert)
- Sélection de l'expert
- Affichage des missions en attente de l'expert
- Validation de l'affectation

```python
# Structure du dialogue
class AffecterExpertDialog(QDialog):
    def __init__(self, mission_id, expertise_controller, user, parent=None):
        # Charger la liste des experts
        # Charger les infos de la mission
        # Afficher le formulaire d'affectation
        pass
```

#### 2. Déposer un rapport d'expertise

**Fichier :** `views/deposer_rapport_dialog.py` (à créer)

**Fonctionnalités :**
- Sélection du fichier (PDF, Word, Images)
- Saisie du contenu du rapport
- Saisie du montant estimé
- Upload du fichier

```python
class DeposerRapportDialog(QDialog):
    def __init__(self, mission_id, expertise_controller, user, parent=None):
        # Champ: contenu du rapport (QTextEdit)
        # Champ: montant estimé (QDoubleSpinBox)
        # Bouton: sélection fichier (QFileDialog)
        # Bouton: déposer (QPushButton)
        pass
```

#### 3. Valider une mission d'expertise

**Fichier :** `views/valider_mission_dialog.py` (à créer)

**Fonctionnalités :**
- Vérification que le rapport est déposé
- Affichage du récapitulatif de la mission
- Validation avec confirmation

```python
class ValiderMissionDialog(QDialog):
    def __init__(self, mission_id, expertise_controller, user, parent=None):
        # Afficher les infos de la mission
        # Bouton: Valider
        # Changement de statut du sinistre
        pass
```

---

### PRIORITÉ MOYENNE 🟡

#### 4. Créer une évaluation

**Fichier :** `views/evaluation_dialog.py` (existe déjà, à améliorer)

**Fonctionnalités :**
- Type d'évaluation (auto_materiel, auto_corporel, etc.)
- Montant brut
- Franchise
- Taux de responsabilité (auto-calculé)
- **Calcul automatique** du montant net
- Création de provision automatique

#### 5. Réviser une évaluation

**Fichier :** `views/reviser_evaluation_dialog.py` (à créer)

**Fonctionnalités :**
- Affichage de l'évaluation actuelle
- Nouveaux montants
- Motif de la révision
- Historisation de la révision

#### 6. Valider une évaluation

**Fonctionnalité à ajouter dans `evaluation_controller.py`**

```python
def valider_evaluation(self, evaluation_id: int) -> bool:
    # Vérifier que l'évaluation existe
    # Vérifier que l'utilisateur a les droits
    # Mettre à jour le statut
    # Changer le statut du sinistre → VALIDE
    pass
```

#### 7. Créer un règlement

**Fichier :** `views/reglement_dialog.py` (existe déjà)

**Fonctionnalités :**
- Sélection du bénéficiaire (client, expert, garage, etc.)
- Montant du règlement
- Type de paiement (chèque, virement, Mobile Money)
- Validation

#### 8. Payer un règlement

**Fichier :** `views/paiement_dialog.py` (à créer)

**Fonctionnalités :**
- Référence du paiement
- Date du paiement
- Pièce justificative (optionnel)
- Validation du paiement

#### 9. Créer un recours

**Fichier :** `views/recours_dialog.py` (existe déjà)

**Fonctionnalités :**
- Type de recours (responsable, assureur_adverse, etc.)
- Débiteur
- Montant réclamé
- Observations

#### 10. Encaisser un recours

**Fichier :** `views/encaissement_dialog.py` (à créer)

**Fonctionnalités :**
- Montant encaissé
- Mode d'encaissement
- Référence bancaire
- Date d'encaissement

---

### PRIORITÉ BASSE 🟢

#### 11. Lots de paiement

**Fonctionnalités :**
- Créer un lot
- Ajouter des règlements au lot
- Valider le lot
- Traiter le lot (génération de fichiers bancaires)

#### 12. Gestion des relances

**Fonctionnalités :**
- Relance automatique basée sur la date de prochaine relance
- Suivi des relances
- Historique des relances

#### 13. GED Documents

**Fonctionnalités :**
- Upload de documents
- Versionnement des documents
- Catégorisation (expertise, règlement, recours)
- Téléchargement des documents

#### 14. Tests unitaires

**Fonctionnalités :**
- Tests des services
- Tests des contrôleurs
- Tests d'intégration

---

## 5. DIAGRAMME DES FLUX

### Flux de création d'une mission
```
1. Utilisateur sélectionne un sinistre dans la page Expertises
   ↓
2. Clique sur "Nouvelle mission"
   ↓
3. MissionDialog s'ouvre
   ↓
4. Remplit : Type, Domaine, Expert, Date mission, Échéance, Montant
   ↓
5. Valide → ExpertiseController.creer_mission()
   ↓
6. ExpertiseService.creer_mission()
   ↓
7. Génère numéro (EXP-2026-XXXXXX)
   ↓
8. Crée la mission avec statut "CREEE"
   ↓
9. Met à jour le statut du sinistre → "EN_EXPERTISE"
   ↓
10. Rafraîchit la liste des expertises
```

### Flux complet d'une expertise
```
1. Mission créée (CREEE)
   ↓
2. Affecter un expert → AFFECTEE
   ↓
3. Démarrer la mission → EN_COURS (date_mission = aujourd'hui)
   ↓
4. Déposer le rapport → RAPPORT_REÇU
   ↓
5. Valider la mission → VALIDE
   ↓
6. Statut sinistre → EN_EVALUATION
```

---

## 6. PROCHAINES ÉTAPES RECOMMANDÉES

### Sprint 1 : Finaliser les expertises
1. ✅ Création de mission (déjà fait)
2. ⏳ Affecter un expert à une mission
3. ⏳ Déposer un rapport d'expertise
4. ⏳ Valider une mission

### Sprint 2 : Finaliser les évaluations
5. ⏳ Créer une évaluation (déjà partiellement fait)
6. ⏳ Réviser une évaluation
7. ⏳ Valider une évaluation

### Sprint 3 : Finaliser les règlements
8. ⏳ Créer un règlement (déjà partiellement fait)
9. ⏳ Payer un règlement
10. ⏳ Lots de paiement

### Sprint 4 : Finaliser les recours
11. ⏳ Créer un recours (déjà partiellement fait)
12. ⏳ Encaisser un recours
13. ⏳ Gestion des relances

### Sprint 5 : Finaliser la GED et les rapports
14. ⏳ Intégration GED
15. ⏳ Génération de rapports PDF
16. ⏳ Tests

---

## 7. PROCHAINE ACTION

**Je te propose de commencer par le Sprint 1 : "Affecter un expert à une mission"**

Veux-tu que je crée le dialogue `AffecterExpertDialog` avec :
- Liste des experts disponibles
- Sélection de l'expert
- Validation de l'affectation
- Changement de statut de la mission (CREEE → AFFECTEE)

Ou préfères-tu commencer par un autre module ?
