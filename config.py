# config.py
import os
import sys

class Config:
    """Configuration de l'application"""
    
    UPDATE_SERVER = "http://192.168.100.17:5000/api"
    UPDATE_CHECK_INTERVAL = 3600
    
    @staticmethod
    def get_app_dir():
        """
        Retourne le répertoire de l'application.
        - En développement : dossier du script
        - En compilé : dossier de LOMETA.exe
        """
        if getattr(sys, 'frozen', False):
            # Mode compilé - retourne le dossier de l'exécutable
            return os.path.dirname(sys.executable)
        else:
            # Mode développement
            return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_addons_dir():
        """
        Retourne le répertoire des addons.
        TOUJOURS à côté de l'exécutable, JAMAIS dans _internal
        """
        app_dir = Config.get_app_dir()
        addons_dir = os.path.join(app_dir, 'addons')
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(addons_dir, exist_ok=True)
        
        return addons_dir
    
    @staticmethod
    def get_internal_dir():
        """
        Retourne le répertoire _internal (uniquement pour les ressources)
        """
        if getattr(sys, 'frozen', False):
            # En mode compilé, les ressources système sont dans _internal
            return sys._MEIPASS if hasattr(sys, '_MEIPASS') else app_dir
        return Config.get_app_dir()
    
    @staticmethod
    def get_resource_path(relative_path):
        """
        Retourne le chemin absolu d'une ressource.
        Les ressources sont dans _internal en mode compilé.
        """
        if getattr(sys, 'frozen', False):
            # Mode compilé - chercher dans _internal
            base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else Config.get_app_dir()
        else:
            # Mode développement
            base_path = Config.get_app_dir()
        
        return os.path.join(base_path, relative_path)