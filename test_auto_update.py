#!/usr/bin/env python3
"""
Test du système de mise à jour automatique
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton
from PySide6.QtCore import QTimer

# Ajouter les chemins
sys.path.insert(0, '/home/fearless/Documents/Assurance')
sys.path.insert(0, '/home/fearless/Documents/Assurance/dist/LOMETA')

from update_manager import UpdateManager
from server.config import Config

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Mise à Jour Auto")
        self.setGeometry(100, 100, 600, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Zone de logs
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # Boutons
        btn_manual = QPushButton("🔍 Vérification manuelle")
        btn_manual.clicked.connect(self.manual_check)
        layout.addWidget(btn_manual)
        
        # Initialiser
        self.log("📁 Initialisation...")
        self.log(f"   Dossier addons: {Config.get_addons_dir()}")
        self.log(f"   Serveur: {Config.UPDATE_SERVER}")
        
        self.update_manager = UpdateManager(self)
        
        # Vérification auto après 2 secondes
        self.log("⏳ Vérification automatique dans 2 secondes...")
        QTimer.singleShot(2000, self.auto_check)
    
    def log(self, message):
        """Ajoute un message dans la zone de logs"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
        print(message)
    
    def auto_check(self):
        """Vérification automatique"""
        self.log("🔄 Lancement de la vérification AUTOMATIQUE...")
        self.update_manager.check_updates_auto()

        
    
    def manual_check(self):
        """Vérification manuelle"""
        self.log("🔄 Lancement de la vérification MANUELLE...")
        self.update_manager.check_updates_manual()
    
    def show_status_message(self, message):
        """Affiche un message de statut"""
        self.log(f"📢 NOTIFICATION: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())