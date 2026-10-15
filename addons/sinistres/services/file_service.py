"""
Service de gestion physique des fichiers (photos, documents)
"""
import os
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

# Racine des uploads (à la racine du projet)
UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"

# Sous-dossiers
DOMMAGES_DIR = "dommages"
DOCUMENTS_DIR = "documents"
EXPERTS_DIR = "experts"           # ✅ NOUVEAU
RAPPORTS_DIR = "rapports"         # ✅ NOUVEAU

# Extensions autorisées
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
ALLOWED_DOC_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}

# Taille max (en Mo)
MAX_IMAGE_SIZE_MB = 10
MAX_DOC_SIZE_MB = 20


# ============================================================
# SERVICE
# ============================================================

class FileService:
    """Service centralisé pour la gestion des fichiers physiques"""
    
    def __init__(self):
        self._ensure_directories()
    
    # ============================================================
    # INITIALISATION
    # ============================================================
    
    def _ensure_directories(self):
        """Crée les dossiers de base si nécessaire"""
        (UPLOAD_ROOT / DOMMAGES_DIR).mkdir(parents=True, exist_ok=True)
        (UPLOAD_ROOT / DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)
        (UPLOAD_ROOT / EXPERTS_DIR).mkdir(parents=True, exist_ok=True)     # ✅ NOUVEAU
        (UPLOAD_ROOT / RAPPORTS_DIR).mkdir(parents=True, exist_ok=True)    # ✅ NOUVEAU
    
    # ============================================================
    # PHOTOS DE DOMMAGES
    # ============================================================
    
    def save_dommage_photo(
        self,
        sinistre_id: int,
        source_path: str,
        compress: bool = True,
        max_width: int = 1920
    ) -> Optional[str]:
        """Copie une photo dans uploads/dommages/<sinistre_id>/"""
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Fichier source introuvable: {source_path}")
            
            ext = Path(source_path).suffix.lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValueError(f"Extension non autorisée: {ext}")
            
            size_mb = os.path.getsize(source_path) / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                raise ValueError(f"Fichier trop volumineux ({size_mb:.1f} Mo)")
            
            dest_dir = UPLOAD_ROOT / DOMMAGES_DIR / str(sinistre_id)
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = Path(source_path).stem
            safe_name = self._sanitize_filename(original_name)
            unique_suffix = os.urandom(2).hex()
            dest_filename = f"{timestamp}_{unique_suffix}_{safe_name}{ext}"
            dest_path = dest_dir / dest_filename
            
            if compress and ext in {'.jpg', '.jpeg', '.png', '.webp'}:
                self._compress_and_save(source_path, str(dest_path), max_width)
            else:
                shutil.copy2(source_path, dest_path)
            
            return f"{DOMMAGES_DIR}/{sinistre_id}/{dest_filename}"
        
        except Exception as e:
            print(f"[FileService] Erreur save_dommage_photo: {e}")
            return None
    
    def save_multiple_dommage_photos(
        self,
        sinistre_id: int,
        source_paths: List[str]
    ) -> List[str]:
        """Copie plusieurs photos et retourne les chemins relatifs réussis"""
        saved = []
        for src in source_paths:
            rel = self.save_dommage_photo(sinistre_id, src)
            if rel:
                saved.append(rel)
        return saved
    
    def delete_dommage_photo(self, relative_path: str) -> bool:
        """Supprime une photo physiquement"""
        try:
            if not relative_path:
                return False
            full_path = UPLOAD_ROOT / relative_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"[FileService] Erreur delete_dommage_photo: {e}")
            return False
    
    def delete_dommage_folder(self, sinistre_id: int) -> bool:
        """Supprime tout le dossier d'un sinistre"""
        try:
            folder = UPLOAD_ROOT / DOMMAGES_DIR / str(sinistre_id)
            if folder.exists():
                shutil.rmtree(folder)
                return True
            return False
        except Exception as e:
            print(f"[FileService] Erreur delete_dommage_folder: {e}")
            return False
    
    # ============================================================
    # ✅ PHOTOS D'EXPERTS (NOUVEAU)
    # ============================================================
    
    def save_expert_photo(
        self,
        expert_code: str,
        source_path: str,
        compress: bool = True,
        max_width: int = 800,
    ) -> Optional[str]:
        """
        Copie une photo d'expert dans uploads/experts/<code>/
        
        Args:
            expert_code: code unique de l'expert (ex: 'EXP-2026-000001')
            source_path: chemin absolu du fichier source
            compress: compresser l'image
            max_width: largeur max après compression
        
        Returns:
            Chemin relatif (ex: 'experts/EXP-2026-000001/20260924_143022_photo.jpg')
        """
        try:
            # --- Validation ---
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Fichier source introuvable: {source_path}")
            
            ext = Path(source_path).suffix.lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValueError(f"Extension non autorisée: {ext}")
            
            size_mb = os.path.getsize(source_path) / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                raise ValueError(f"Fichier trop volumineux ({size_mb:.1f} Mo)")
            
            # --- Dossier destination ---
            safe_code = self._sanitize_filename(expert_code or "unknown")
            dest_dir = UPLOAD_ROOT / EXPERTS_DIR / safe_code
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # --- Nom unique ---
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_suffix = os.urandom(2).hex()
            dest_filename = f"{timestamp}_{unique_suffix}_photo{ext}"
            dest_path = dest_dir / dest_filename
            
            # --- Copier + compresser ---
            if compress and ext in {'.jpg', '.jpeg', '.png', '.webp'}:
                self._compress_and_save(source_path, str(dest_path), max_width)
            else:
                shutil.copy2(source_path, dest_path)
            
            # --- Retourner le chemin relatif ---
            return f"{EXPERTS_DIR}/{safe_code}/{dest_filename}"
        
        except Exception as e:
            print(f"[FileService] Erreur save_expert_photo: {e}")
            return None
    
    def delete_expert_photo(self, relative_path: str) -> bool:
        """Supprime la photo d'un expert"""
        try:
            if not relative_path:
                return False
            full_path = UPLOAD_ROOT / relative_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"[FileService] Erreur delete_expert_photo: {e}")
            return False
    
    def delete_expert_folder(self, expert_code: str) -> bool:
        """Supprime tout le dossier photos d'un expert"""
        try:
            safe_code = self._sanitize_filename(expert_code or "unknown")
            folder = UPLOAD_ROOT / EXPERTS_DIR / safe_code
            if folder.exists():
                shutil.rmtree(folder)
                return True
            return False
        except Exception as e:
            print(f"[FileService] Erreur delete_expert_folder: {e}")
            return False
    
    # ============================================================
    # UTILITAIRES
    # ============================================================
    
    def get_absolute_path(self, relative_path: str) -> Optional[str]:
        """Convertit un chemin relatif en chemin absolu"""
        if not relative_path:
            return None
        full_path = UPLOAD_ROOT / relative_path
        if full_path.exists():
            return str(full_path)
        return None
    
    def get_full_url(self, relative_path: str) -> Optional[str]:
        """Retourne une URL utilisable par l'UI (file://)"""
        abs_path = self.get_absolute_path(relative_path)
        if abs_path:
            return f"file://{abs_path}"
        return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Nettoie un nom de fichier"""
        name = name.replace(" ", "_")
        name = re.sub(r'[^\w\-]', '', name)
        return name[:50] or "photo"
    
    def _compress_and_save(self, source: str, dest: str, max_width: int):
        """Compresse et sauvegarde une image"""
        try:
            with Image.open(source) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.LANCZOS)
                
                ext = Path(dest).suffix.lower()
                if ext in {'.jpg', '.jpeg'}:
                    img.save(dest, 'JPEG', quality=85, optimize=True)
                elif ext == '.png':
                    img.save(dest, 'PNG', optimize=True)
                elif ext == '.webp':
                    img.save(dest, 'WEBP', quality=85)
                else:
                    img.save(dest)
        except Exception as e:
            print(f"[FileService] Compression échouée, copie directe: {e}")
            shutil.copy2(source, dest)
    
    # ============================================================
    # NETTOYAGE
    # ============================================================
    
    def cleanup_orphan_files(self, valid_paths: List[str]) -> int:
        """Supprime les fichiers physiques non référencés"""
        deleted = 0
        valid_set = set(valid_paths)
        
        dommages_root = UPLOAD_ROOT / DOMMAGES_DIR
        if not dommages_root.exists():
            return 0
        
        for file_path in dommages_root.rglob("*"):
            if file_path.is_file():
                rel = str(file_path.relative_to(UPLOAD_ROOT))
                if rel not in valid_set:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"[FileService] Impossible de supprimer {rel}: {e}")
        
        return deleted


# ============================================================
# SINGLETON
# ============================================================

_file_service_instance = None


def get_file_service() -> FileService:
    """Retourne l'instance unique du FileService"""
    global _file_service_instance
    if _file_service_instance is None:
        _file_service_instance = FileService()
    return _file_service_instance