# Mise à jour en production (VM Windows + macOS + Linux)

## 1) Principe

- Application livrée via releases GitHub (`tag`, `artifact`) : onefile/standalone par OS.
- Les VMs exécutent un agent local (`core/vm_updater.py`) qui interroge la release la plus récente.
- Agent vérifie la version locale (`version.txt`) et remplace le binaire si la release est plus récente.
- Backup et rollback automatique (fichier `.bak.<timestamp>`).

## 2) Préparation Github

1. Dans le repository GitHub (`https://github.com/ORG/REPO`), créer des releases:
   - `v1.0.0`, `v1.0.1`, etc.
   - upload des fichiers:
      - `ams-windows.exe`
      - `ams-macos` (ou `ams-macos.app`)
      - `ams-linux` (onefile)
2. Optionnel : ajouter `SHA256` dans la description ou API pour vérification.

## 3) Configuration locale (VM)

Dans la VM, créer `vm_updater_config.json` :

```json
{
  "update_server_url": "https://api.github.com/repos/ORG/REPO/releases/latest",
  "install_path": "C:/AMS" ,
  "binary_name": "AMS.exe",                 
  "version_file": "version.txt",
  "check_interval_seconds": 3600
}
```
{"immatriculation": "TL 32658 LK", "chas...
- Mac : `install_path`: `/Applications/AMS`
- Linux : `install_path`: `/opt/ams`

## 4) Démarrage

- vérifier la version locale :

```bash
python core/vm_updater.py check
```

- lancer le service (boucle régulière) :

```bash
python core/vm_updater.py run
```

## 5) Processus de build multi-OS

- Windows (sur hôte Windows) :
  `nuitka --standalone --onefile --enable-plugin=pyside6 main.py --output-dir=dist/windows`
- macOS (sur hôte mac) :
  `nuitka --standalone --onefile --enable-plugin=pyside6 main.py --output-dir=dist/mac`
- Linux (déjà) :
  `nuitka --standalone --onefile --enable-plugin=pyside6 main.py --output-dir=dist/linux`

## 6) Déploiement CI/CD (GitHub Actions)

- Steps : checkout → install deps → tests → build OS → upload artifacts → create release.
- Sur chaque VM, tâche planifiée exécute update agent périodiquement.

## 7) Vérification post-update

- `version.txt` contient numéro version.
- `logs/update.log` (à ajouter au module) pour audits.
- `backup` dans le dossier de l’app en cas de reprise.
