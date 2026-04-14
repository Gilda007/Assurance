# config.py
import os
import sys

class Config:
    """Configuration de l'application"""
    
    # URL du serveur de mise à jour
    UPDATE_SERVER = "http://192.168.100.17:5000/api"
    
    # Intervalle de vérification (en secondes)
    UPDATE_CHECK_INTERVAL = 86400  # 1 jour
    
    @staticmethod
    def get_app_dir():
        """Retourne le répertoire de l'application"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_addons_dir():
        """Retourne le répertoire des addons (modules)"""
        return os.path.join(Config.get_app_dir(), 'addons')