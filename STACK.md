# Stack technique — Assurance

Résumé de la stack utilisée par ce projet.

- Langage principal: Python 3.10/3.11 (tests en matrix)
- GUI Desktop: PySide6 (Qt6) — application native desktop
- Backend léger / API: Flask + Flask-CORS
- ORM / DB: SQLAlchemy
  - PostgreSQL adapter: psycopg2-binary
  - MySQL adapters: PyMySQL, mysqlclient
- Packaging / Distribution: PyInstaller (fichiers `.spec`, scripts `build_secure.sh`, `build_windows.sh`)
- Data & reporting: pandas, numpy, openpyxl, reportlab, qrcode
- Graphs / widgets: pyqtgraph
- Sécurité: bcrypt, cryptography
- Utilities: python-dotenv, Pillow, requests
- Tests & CI: pytest, GitHub Actions (CI/CD workflow)
- Scripts & automation: shell scripts (Linux) et batch (Windows), systemd service for backups

Fichiers-clés:
- `requirements.txt` — dépendances Python
- `.github/workflows/ci-cd.yml` — workflow CI/CD
- `LOMETA_DEBUG.spec`, `LOMETA.spec` — PyInstaller specs
- `build_secure.sh`, `build_windows.sh` — scripts de build
- `server/api.py` — point d'entrée API Flask

Recommandations rapides:
- Installer un runner avec accès graphique si vous voulez packager PySide6 avec certaines dépendances natives.
- Pour builds reproducibles, pinnez les versions dans `requirements.txt` (ex: `package==1.2.3`).
- Considérer l'ajout d'un job `release` pour créer des artefacts signés et des releases GitHub.
