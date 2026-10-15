# 📋 CONTEXTE LOMETA - MISE À JOUR COMPLÈTE
## Version : 2.2 | Date : 7 Septembre 2026

---

## 1. ÉTAT D'AVANCEMENT GÉNÉRAL

### ✅ SPRINT 1 COMPLÉTÉ : FINALISER LES EXPERTISES

| Tâche | Statut | Description |
|-------|--------|-------------|
| **1.1 Créer une mission** | ✅ Terminé | MissionDialog avec date_mission, date_echeance, expert, montant |
| **1.2 Affecter un expert** | ✅ Terminé | AffecterExpertDialog avec liste des experts, recherche, sélection |
| **1.3 Déposer un rapport** | ✅ Terminé | DeposerRapportDialog avec contenu, montant, fichiers multiples |
| **1.4 Valider une mission** | ⏳ À faire | Validation avec vérification des prérequis |

### ✅ COMPLÉTÉ (GLOBAL)

| Élément | Statut | Description |
|---------|--------|-------------|
| **Modèles SQLAlchemy** | ✅ Terminé | 23 tables avec préfixe Lometa, relations corrigées |
| **AuditableMixin** | ✅ Corrigé | Changé de UUID à Integer pour created_by/updated_by |
| **Services** | ✅ Terminé | 10 services (Base, Sinistre, Expertise, Evaluation, Reglement, Recours, Referentiel, Workflow, Audit, Automobile) |
| **Contrôleurs** | ✅ Terminé | 8 contrôleurs avec gestion utilisateur et signaux |
| **Vue principale** | ✅ Terminé | LometaSinistresMainView avec sidebar et 8 pages |
| **Tableau de bord** | ✅ Terminé | DashboardPage avec statistiques et sinistres récents |
| **Nouveau sinistre** | ✅ Terminé | Formulaire complet avec recherche client, sélection contrat, référentiels |
| **Recherche** | ✅ Terminé | Recherche textuelle, filtres, double-clic pour Dossier 360° |
| **Dossier 360°** | ✅ Terminé | 10 onglets (Général, Client, Dommages, Tiers, Expertises, Évaluations, Règlements, Recours, Documents, Historique) |
| **Dialogues** | ✅ Terminé | EditSinistreDialog, AddDommageDialog, AddTiersDialog, AddExpertiseDialog, AddEvaluationDialog, AddReglementDialog, AddRecoursDialog, MissionDialog, AffecterExpertDialog, DeposerRapportDialog |
| **Données initiales** | ✅ Terminé | REFERENTIELS_INITIAUX (50+ entrées dans 7 familles) |
| **Client/Contrat recherche** | ✅ Terminé | ClientSearchWidget, ContractSelectorWidget |

### ⏳ EN COURS / À FAIRE

| Élément | Priorité | Description |
|---------|----------|-------------|
| **Valider mission expertise** | 🔴 Haute | Validation avec vérification des prérequis |
| **Création évaluation** | 🟡 Moyenne | ÉvaluationDialog avec calcul auto du montant net |
| **Réviser évaluation** | 🟡 Moyenne | Dialogue de révision avec historisation |
| **Valider évaluation** | 🟡 Moyenne | Action de validation avec changement de statut sinistre |
| **Création règlement** | 🟡 Moyenne | ReglementDialog avec sélection bénéficiaire |
| **Payer règlement** | 🟡 Moyenne | PaiementDialog avec chèque/virement/Mobile Money |
| **Lots de paiement** | 🟢 Basse | Création et gestion des lots |
| **Création recours** | 🟡 Moyenne | RecoursDialog |
| **Encaissement recours** | 🟡 Moyenne | EncaissementDialog |
| **Gestion relances** | 🟢 Basse | Relance automatique et suivi |
| **GED Documents** | 🟢 Basse | Intégration complète de la GED |
| **Tests unitaires** | 🟢 Basse | Tests des services et contrôleurs |

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
│   ├── affecter_expert_dialog.py  # ✅ Affectation expert
│   ├── deposer_rapport_dialog.py  # ✅ Dépôt rapport (fichiers multiples)
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

## 3. DIALOGUES DISPONIBLES

| Dialogue | Fichier | Description |
|----------|---------|-------------|
| MissionDialog | `mission_dialog.py` | Création de mission d'expertise |
| AffecterExpertDialog | `affecter_expert_dialog.py` | Affectation d'un expert à une mission |
| DeposerRapportDialog | `deposer_rapport_dialog.py` | Dépôt de rapport avec fichiers multiples |
| EditSinistreDialog | `dialogs.py` | Modification d'un sinistre |
| AddDommageDialog | `dialogs.py` | Ajout d'un dommage |
| AddTiersDialog | `dialogs.py` | Ajout d'un tiers |
| AddExpertiseDialog | `dialogs.py` | Création d'expertise (ancienne version) |
| AddEvaluationDialog | `dialogs.py` | Création d'évaluation |
| AddReglementDialog | `dialogs.py` | Création de règlement |
| AddRecoursDialog | `dialogs.py` | Création de recours |

---

## 4. FLUX DE TRAVAIL EXPERTISE (COMPLET)

```
1. Créer la mission → statut: CREEE
   │   - MissionDialog
   │   - Type, Domaine, Expert, Date mission, Échéance, Montant
   ↓
2. Affecter un expert → statut: AFFECTEE
   │   - AffecterExpertDialog
   │   - Liste des experts disponibles
   │   - Recherche par nom/spécialité
   ↓
3. Démarrer la mission → statut: EN_COURS
   │   - date_mission = aujourd'hui
   │   - Bouton "Démarrer" dans ExpertisesPage
   ↓
4. Déposer le rapport → statut: RAPPORT_REÇU
   │   - DeposerRapportDialog
   │   - Contenu du rapport
   │   - Montant estimé
   │   - Fichiers multiples (PDF, DOCX, JPG, PNG, ZIP)
   ↓
5. Valider la mission → statut: VALIDE
   │   - Vérification prérequis
   │   - Sinistre passe en EN_EVALUATION
```

---

## 5. CORRECTIONS APPLIQUÉES

| Problème | Solution | Statut |
|----------|----------|--------|
| `date_mission` NOT NULL | Ajouté comme champ dans MissionDialog | ✅ |
| Statut "Créée" vs "CREEE" | Utilisation de la valeur réelle via `get_mission_by_numero()` | ✅ |
| `file_path_display` inexistant | Supprimé, remplacé par `QListWidget` | ✅ |
| `_format_size` en double | Supprimé la deuxième définition | ✅ |
| Fichiers multiples | Ajout de `ajouter_fichiers()`, `supprimer_fichier()`, `QListWidget` | ✅ |

---

## 6. PROCHAINES ÉTAPES RECOMMANDÉES

### Sprint 1 (suite)
1. ⏳ **Valider une mission d'expertise** (Tâche 1.4)

### Sprint 2 : Finaliser les évaluations
2. ⏳ Créer une évaluation (dialogue amélioré avec calcul auto)
3. ⏳ Réviser une évaluation
4. ⏳ Valider une évaluation

### Sprint 3 : Finaliser les règlements
5. ⏳ Créer un règlement
6. ⏳ Payer un règlement
7. ⏳ Lots de paiement

### Sprint 4 : Finaliser les recours
8. ⏳ Créer un recours
9. ⏳ Encaisser un recours
10. ⏳ Gestion des relances

---

## 7. COMMANDE POUR LA PROCHAINE TÂCHE

**Tâche 1.4 : Valider une mission d'expertise**

Créer un dialogue `ValiderMissionDialog` qui :
- Affiche le récapitulatif de la mission
- Vérifie qu'un rapport est déposé
- Permet de valider la mission
- Change le statut de la mission en "VALIDE"
- Change le statut du sinistre en "EN_EVALUATION"

---

## 8. NOTE SUR LES FICHIERS MODIFIÉS

| Fichier | Modifications récentes |
|---------|----------------------|
| `deposer_rapport_dialog.py` | ✅ Ajout fichiers multiples, suppression `file_path_display` |
| `affecter_expert_dialog.py` | ✅ Nouveau fichier |
| `view.py` | ✅ Méthodes `affecter_expert()`, `deposer_rapport()`, `demarrer_mission()` |
| `expertise_controller.py` | ✅ `get_mission_by_numero()` |
| `expertise_service.py` | ✅ Gestion fichiers multiples |

---

**Fin du contexte LOMETA v2.2**

Prêt pour la tâche suivante !


# 📋 CONTEXTE LOMETA - MISE À JOUR COMPLÈTE
## Version : 2.3 | Date : 7 Septembre 2026

---

## 1. ÉTAT D'AVANCEMENT GÉNÉRAL

### ✅ SPRINT 1 COMPLÉTÉ : FINALISER LES EXPERTISES

| Tâche | Statut | Description |
|-------|--------|-------------|
| **1.1 Créer une mission** | ✅ Terminé | MissionDialog avec date_mission, date_echeance, expert, montant |
| **1.2 Affecter un expert** | ✅ Terminé | AffecterExpertDialog avec liste des experts, recherche, sélection |
| **1.3 Déposer un rapport** | ✅ Terminé | DeposerRapportDialog avec contenu, montant, fichiers multiples |
| **1.4 Valider une mission** | ✅ Terminé | Validation avec vérification des prérequis |

### ✅ SPRINT 2 COMPLÉTÉ : FINALISER LES ÉVALUATIONS

| Tâche | Statut | Description |
|-------|--------|-------------|
| **2.1 Créer une évaluation** | ✅ Terminé | EvaluationDialog avec calcul automatique du montant net |
| **2.2 Réviser une évaluation** | ✅ Terminé | ReviserEvaluationDialog avec historisation et comparaison |
| **2.3 Valider une évaluation** | ✅ Terminé | Validation avec changement de statut du sinistre |

### ✅ SPRINT 3 COMPLÉTÉ : FINALISER LES RÈGLEMENTS

| Tâche | Statut | Description |
|-------|--------|-------------|
| **3.1 Créer un règlement** | ✅ Terminé | ReglementDialog avec sélection bénéficiaire, évaluation, type paiement |
| **3.2 Payer un règlement** | ✅ Terminé | PaiementDialog avec référence, date, informations complémentaires |
| **3.3 Lots de paiement** | ✅ Terminé | LotPaiementDialog avec sélection de règlements, validation, traitement |

### ✅ SPRINT 4 COMPLÉTÉ : FINALISER LES RECOURS

| Tâche | Statut | Description |
|-------|--------|-------------|
| **4.1 Créer un recours** | ✅ Terminé | RecoursDialog avec type, débiteur, montant réclamé |
| **4.2 Encaisser un recours** | ✅ Terminé | EncaissementDialog avec montant, mode, référence |
| **4.3 Gestion des relances** | ✅ Terminé | RelanceDialog avec types, planification automatique, suivi |
| **4.4 Planification auto** | ✅ Terminé | Planification automatique des relances pour tous les recours |

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
│   ├── expertise_controller.py    # ✅ Missions, rapports
│   ├── evaluation_controller.py   # ✅ Évaluations, provisions
│   ├── reglement_controller.py    # ✅ Règlements, lots
│   ├── recours_controller.py      # ✅ Recours, encaissements, relances
│   └── automobile_controller.py   # ✅ Clients, Contrats
├── views/
│   ├── __init__.py
│   ├── view.py                    # ✅ Vue principale (toutes les pages)
│   ├── dossier_360.py             # ✅ Dossier 360°
│   ├── mission_dialog.py          # ✅ Création mission
│   ├── affecter_expert_dialog.py  # ✅ Affectation expert
│   ├── deposer_rapport_dialog.py  # ✅ Dépôt rapport (fichiers multiples)
│   ├── evaluation_dialog.py       # ✅ Création évaluation
│   ├── reviser_evaluation_dialog.py # ✅ Révision évaluation
│   ├── reglement_dialog.py        # ✅ Création règlement
│   ├── paiement_dialog.py         # ✅ Paiement règlement
│   ├── lot_paiement_dialog.py     # ✅ Création lot
│   ├── recours_dialog.py          # ✅ Création recours
│   ├── encaissement_dialog.py     # ✅ Encaissement recours
│   ├── relance_dialog.py          # ✅ Ajout relance
│   ├── dialogs.py                 # ✅ Dialogues génériques
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
│   ├── recours_service.py         # ✅ Recours, encaissements, relances
│   ├── referentiel_service.py     # ✅ Référentiels
│   ├── workflow_service.py        # ✅ Workflow paramétrable
│   ├── audit_service.py           # ✅ Journal d'audit
│   └── automobile_service.py      # ✅ Clients, Contrats
└── migrations/
    └── versions/
        └── 001_initial_lometa_schema.py  # ✅ Migration initiale
```

---

## 3. DIALOGUES DISPONIBLES

| Dialogue | Fichier | Description |
|----------|---------|-------------|
| MissionDialog | `mission_dialog.py` | Création de mission d'expertise |
| AffecterExpertDialog | `affecter_expert_dialog.py` | Affectation d'un expert à une mission |
| DeposerRapportDialog | `deposer_rapport_dialog.py` | Dépôt de rapport avec fichiers multiples |
| EvaluationDialog | `evaluation_dialog.py` | Création d'évaluation avec calcul auto |
| ReviserEvaluationDialog | `reviser_evaluation_dialog.py` | Révision d'évaluation avec historisation |
| ReglementDialog | `reglement_dialog.py` | Création de règlement |
| PaiementDialog | `paiement_dialog.py` | Paiement d'un règlement |
| LotPaiementDialog | `lot_paiement_dialog.py` | Création de lot de paiement |
| RecoursDialog | `recours_dialog.py` | Création de recours |
| EncaissementDialog | `encaissement_dialog.py` | Encaissement de recours |
| RelanceDialog | `relance_dialog.py` | Ajout de relance |
| EditSinistreDialog | `dialogs.py` | Modification d'un sinistre |
| AddDommageDialog | `dialogs.py` | Ajout d'un dommage |
| AddTiersDialog | `dialogs.py` | Ajout d'un tiers |

---

## 4. FLUX DE TRAVAIL COMPLETS

### Flux Expertise
```
1. Créer la mission → CREEE
   ↓ (MissionDialog)
2. Affecter un expert → AFFECTEE
   ↓ (AffecterExpertDialog)
3. Démarrer la mission → EN_COURS (date_mission = aujourd'hui)
   ↓
4. Déposer le rapport → RAPPORT_REÇU
   ↓ (DeposerRapportDialog - fichiers multiples)
5. Valider la mission → VALIDE
   ↓ (Sinistre passe en EN_EVALUATION)
```

### Flux Évaluation
```
1. Créer l'évaluation → non validée
   ↓ (EvaluationDialog - calcul auto)
2. Réviser l'évaluation → historisation
   ↓ (ReviserEvaluationDialog - comparaison)
3. Valider l'évaluation → validée
   ↓ (Sinistre passe en VALIDE)
```

### Flux Règlement
```
1. Créer le règlement → CRÉÉ
   ↓ (ReglementDialog)
2. Valider le règlement → VALIDE
   ↓
3. Payer le règlement → PAYÉ
   ↓ (PaiementDialog - comptabilisation auto)
4. (Optionnel) Lot de paiement → OUVERT → VALIDE → TRAITE → COMPTABILISE
```

### Flux Recours
```
1. Créer le recours → OUVERT
   ↓ (RecoursDialog)
2. Instruction → EN_INSTRUCTION
   ↓
3. Abouti → ABOUTI → EN_ATTENTE_ENCAISSEMENT
   ↓
4. Encaisser → PARTIELLEMENT_ENCAISSE ou ENCAISSE
   ↓ (EncaissementDialog)
5. Reversement → REVERSEMENT_EN_COURS → PAYE → COMPTABILISE → CLOTURE
   ↓
6. Relances automatiques (RELANCE) si besoin
   ↓ (RelanceDialog / Planification auto)
```

---

## 5. CORRECTIONS APPLIQUÉES

| Problème | Solution | Statut |
|----------|----------|--------|
| `date_mission` NOT NULL | Ajouté comme champ dans MissionDialog | ✅ |
| Statut "Créée" vs "CREEE" | Utilisation de la valeur réelle via `get_mission_by_numero()` | ✅ |
| `file_path_display` inexistant | Supprimé, remplacé par `QListWidget` | ✅ |
| `_format_size` en double | Supprimé la deuxième définition | ✅ |
| Fichiers multiples | Ajout de `ajouter_fichiers()`, `supprimer_fichier()`, `QListWidget` | ✅ |
| `created_by` UUID vs Integer | Modification du type dans la base de données | ✅ |
| `reglement_numero` non défini | Correction avec `self.reglement_numero` | ✅ |

---

## 6. PROCHAINES ÉTAPES RECOMMANDÉES

### Sprint 5 : Finaliser la GED et les rapports
1. ⏳ Intégration GED (documents)
2. ⏳ Génération de rapports PDF
3. ⏳ Exports Excel

### Sprint 6 : Tests et optimisation
4. ⏳ Tests unitaires
5. ⏳ Tests d'intégration
6. ⏳ Optimisation des performances

### Fonctionnalités avancées
7. ⏳ Notifications (email, SMS)
8. ⏳ Dashboard avancé (graphiques)
9. ⏳ Workflow personnalisé par branche

---

## 7. COMMANDES UTILES

### Pour corriger la base de données (UUID → Integer)
```sql
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN 
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_name LIKE 'lometa_%' 
        AND column_name IN ('created_by', 'updated_by')
        AND data_type = 'uuid'
    LOOP
        EXECUTE format('ALTER TABLE %I ALTER COLUMN %I DROP NOT NULL', 
                      rec.table_name, rec.column_name);
        EXECUTE format('ALTER TABLE %I ALTER COLUMN %I TYPE INTEGER USING NULL', 
                      rec.table_name, rec.column_name);
    END LOOP;
END $$;
```

### Pour exécuter les migrations
```bash
alembic upgrade head
```

---

## 8. STATISTIQUES DU PROJET

| Élément | Nombre |
|---------|--------|
| **Modèles SQLAlchemy** | 23 tables |
| **Services** | 10 services |
| **Contrôleurs** | 8 contrôleurs |
| **Vues** | 8 pages principales + 12 dialogues |
| **Référentiels** | 50+ entrées dans 7 familles |
| **Fichiers** | 30+ fichiers Python |

---

**Fin du contexte LOMETA v2.3**

Prêt pour les prochaines étapes !