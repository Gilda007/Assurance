# config.py
import os
import sys

class Config:
    """Configuration de l'application"""
    
    # Serveur de mise à jour
    UPDATE_SERVER = "http://192.168.100.17:5000/api"
    
    @staticmethod
    def get_app_dir():
        """Retourne le dossier de l'application"""
        if getattr(sys, 'frozen', False):
            # Mode compilé (PyInstaller)
            return os.path.dirname(sys.executable)
        else:
            # Mode développement
            return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_addons_dir():
        """Retourne le dossier des addons/modules"""
        app_dir = Config.get_app_dir()
        
        # En mode compilé, les addons sont dans le dossier de l'exe
        if getattr(sys, 'frozen', False):
            addons_dir = os.path.join(app_dir, 'addons')
        else:
            # En développement, chercher dans plusieurs endroits possibles
            possible_paths = [
                os.path.join(app_dir, 'addons'),
                os.path.join(os.path.dirname(app_dir), 'addons'),
                os.path.join(app_dir, '..', 'addons'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            
            # Créer le dossier par défaut
            addons_dir = os.path.join(app_dir, 'addons')
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(addons_dir, exist_ok=True)
        return addons_dir
    
    @staticmethod
    def get_internal_dir():
        """Retourne le dossier _internal (mode compilé)"""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return Config.get_app_dir()
    
    @staticmethod
    def get_temp_dir():
        """Retourne le dossier temporaire"""
        import tempfile
        temp_dir = os.path.join(tempfile.gettempdir(), 'lometa_updates')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir