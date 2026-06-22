# addons/Automobiles/views/asac_manager.py
"""
Interface ASAC - Export et import des données d'assurance
Design moderne et professionnel avec système de notifications
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QProgressBar, QTabWidget, QTextEdit,
    QLineEdit, QComboBox, QCheckBox, QGridLayout,
    QDialog, QScrollArea, QApplication, QSplitter,
    QGraphicsDropShadowEffect, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime, QSettings, QTimer, QUrl
from PySide6.QtGui import QColor, QFont, QDesktopServices, QIcon
from PySide6.QtTextToSpeech import QTextToSpeech
from PySide6.QtCore import QLocale  # Ajoutez cet import
from datetime import datetime, date
import sys
import subprocess
import platform
import json
import os
import re


# ============================================================================
# STYLE MODERNE
# ============================================================================

MODERN_STYLE = """
    QWidget {
        background-color: #f8fafc;
        font-family: 'Segoe UI', sans-serif;
        color: #1e293b;
    }
    
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    QScrollBar:vertical {
        background: #e2e8f0;
        width: 6px;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical {
        background: #94a3b8;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #64748b;
    }
    
    .HeaderCard {
        background: white;
        border-radius: 24px;
        padding: 20px 24px;
        border: none;
    }
    
    .InfoCard {
        background: white;
        border-radius: 20px;
        padding: 20px;
        border: none;
    }
    
    .SectionTitle {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 16px;
    }
    
    .LabelPrimary {
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .LabelValue {
        color: #1e293b;
        font-size: 14px;
        font-weight: 600;
    }
    
    QTableWidget {
        background: white;
        border: none;
        border-radius: 16px;
        gridline-color: #f1f5f9;
    }
    
    QTableWidget::item {
        padding: 12px 10px;
        border: none;
    }
    
    QTableWidget::item:selected {
        background-color: #eef2ff;
    }
    
    QHeaderView::section {
        background-color: #f8fafc;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        padding: 12px 10px;
        font-weight: 600;
        color: #475569;
        font-size: 12px;
    }
    
    QTabWidget::pane {
        border: none;
        background: transparent;
    }
    
    QTabBar::tab {
        background: #f1f5f9;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        margin: 0 4px;
        font-weight: 600;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background: #3b82f6;
        color: white;
    }
    
    QTabBar::tab:hover {
        background: #e2e8f0;
    }
    
    QLineEdit, QTextEdit {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border-color: #3b82f6;
    }
    
    QPushButton {
        background: #f1f5f9;
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }
    
    QPushButton:hover {
        background: #e2e8f0;
    }
    
    .BtnPrimary {
        background: #3b82f6;
        color: white;
    }
    .BtnPrimary:hover {
        background: #2563eb;
    }
    
    .BtnSuccess {
        background: #10b981;
        color: white;
    }
    .BtnSuccess:hover {
        background: #059669;
    }
    
    .BtnSecondary {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    .BtnSecondary:hover {
        background: #e2e8f0;
    }
    
    QProgressBar {
        border: none;
        border-radius: 10px;
        background-color: #e2e8f0;
        height: 6px;
    }
    
    QProgressBar::chunk {
        background-color: #3b82f6;
        border-radius: 10px;
    }
    
    .StatusBadge {
        background: #eef2ff;
        color: #3b82f6;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .StatusSuccess {
        background: #d1fae5;
        color: #059669;
    }
    
    .StatusError {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .StatusWarning {
        background: #fef3c7;
        color: #d97706;
    }
    
    .NotificationItem {
        background: #f8fafc;
        border-radius: 12px;
        padding: 12px;
        margin: 4px 0;
        border-left: 3px solid #3b82f6;
    }
    
    .NotificationItem:hover {
        background: #f1f5f9;
    }
"""


# ============================================================================
# THREADS API
# ============================================================================


class ExportWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, dict, str)
    token_received = Signal(dict)  # Nouveau signal pour le token
    log_captured = Signal(str)  # Nouveau signal pour les logs

    def __init__(self, vehicle_data, config):
        super().__init__()
        self.vehicle_data = vehicle_data
        self.config = config
        self.logs = []  # ← AJOUTER CETTE LIGNE

    def validate_asac_request(self, request):
        """Valide la requête avant envoi"""
        errors = []
        
        # Vérifier les champs obligatoires
        required_fields = ['office_code', 'organization_code', 'certificate_type', 'channel']
        for field in required_fields:
            if not request.get(field):
                errors.append(f"Champ manquant: {field}")
        
        # Vérifier les productions
        productions = request.get('productions', [])
        if not productions:
            errors.append("Aucune production")
        else:
            prod = productions[0]
            prod_required = ['police_number', 'starts_at', 'ends_at', 'licence_plate', 
                            'customer_name', 'taxpayer_number', 'vehicle_first_registration_date']
            for field in prod_required:
                if not prod.get(field):
                    errors.append(f"Champ production manquant: {field}")
        
        return errors
    
    def run(self):
        try:
            self.progress.emit(10, "📋 Préparation des données...")
            
            request = self.build_asac_request()
            
            self.progress.emit(30, "🔐 Authentification ASAC...")
            
            import requests
            
            # 1. Requête pour obtenir le token
            auth_url = f"{self.config.get('url', '')}/api/v1/auth/tokens"
            
            # En-têtes pour l'authentification
            headers = {
                "X-App-Id": self.config.get("app_key", ""),
                "Content-Type": "application/json"
            }
            
            # Corps de la requête (seul le username est envoyé)
            auth_payload = {
                "username": self.config.get("username", ""),
                "password": self.config.get("password", ""),
                "email": self.config.get("email", "")
            }
            
            # LOG: Afficher la requête d'authentification
            self.log_request(auth_url, headers, auth_payload, "AUTHENTIFICATION REQUEST")
            
            # Envoyer la requête
            auth_response = requests.post(
                auth_url,
                headers=headers,
                json=auth_payload,
                timeout=10
            )
            
            # LOG: Afficher la réponse d'authentification
            self.log_response(auth_response, "AUTHENTIFICATION RESPONSE")
            
            if auth_response.status_code != 200:
                error_msg = f"Authentification échouée: {auth_response.text[:200]}"
                print(f"❌ {error_msg}")
                self.finished.emit(False, {}, error_msg)
                return
            
            auth_data = auth_response.json()
            
            # Extraire les informations de la réponse
            token = auth_data.get("token", "")
            token_name = auth_data.get("token_name", "")
            expires_at = auth_data.get("expires_at", "")
            application_key_name = auth_data.get("application_key_name", "")
            
            print(f"\n✅ TOKEN REÇU AVEC SUCCÈS!")
            print(f"   📛 Nom: {token_name}")
            print(f"   🏢 Application: {application_key_name}")
            print(f"   ⏰ Expire: {expires_at}")
            print(f"   🔑 Token: {token[:30]}...{token[-20:] if len(token) > 50 else token}")
            
            # Émettre le token pour l'affichage
            self.token_received.emit({
                "token": token,
                "token_name": token_name,
                "expires_at": expires_at,
                "application_key_name": application_key_name
            })
            
            self.progress.emit(60, "📤 Envoi à ASAC...")
            
            # 2. Utiliser le token pour l'envoi des données
            prod_url = f"{self.config['url']}/api/v1/productions"
            prod_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # LOG: Afficher la requête d'envoi des données
            self.log_request(prod_url, prod_headers, request, "PRODUCTION REQUEST")
            
            prod_response = requests.post(prod_url, json=request, headers=prod_headers, timeout=30)
            
            # LOG: Afficher la réponse de production
            self.log_response(prod_response, "PRODUCTION RESPONSE")
            
            self.progress.emit(90, "📥 Traitement de la réponse...")
            
            if prod_response.status_code in [200, 201]:
                response_data = prod_response.json()
                self.progress.emit(100, "✅ Export terminé !")
                print(f"\n✅ EXPORT TERMINÉ AVEC SUCCÈS!")
                self.finished.emit(True, response_data, "")
            else:
                error_msg = f"Erreur ASAC: {prod_response.text[:200]}"
                print(f"❌ {error_msg}")
                self.finished.emit(False, {}, error_msg)
                
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout: {str(e)}"
            print(f"❌ {error_msg}")
            self.finished.emit(False, {}, error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erreur de connexion: {str(e)}"
            print(f"❌ {error_msg}")
            self.finished.emit(False, {}, error_msg)
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, {}, error_msg)

    def build_asac_request(self):
        """Construit la requête ASAC selon le format exact exigé"""
        vehicle = self.vehicle_data
        
        # Récupérer les codes valides depuis la configuration
        office_code = self.config.get("office_code", "AG-DLA-001")
        organization_code = self.config.get("org_code", "ACTIVA")
        
        # Pour la date, s'assurer du format YYYY-MM-DD
        # date_debut = vehicle.get("date_debut")
        # if not date_debut:
        #     date_debut = datetime.now().strftime("%Y-%m-%d")
        # elif isinstance(date_debut, datetime):
        #     date_debut = date_debut.strftime("%Y-%m-%d")
        # elif hasattr(date_debut, 'strftime'):
        #     date_debut = date_debut.strftime("%Y-%m-%d")
        
        # date_fin = vehicle.get("date_fin")
        # if not date_fin:
        #     date_fin = (datetime.now().replace(year=datetime.now().year+1)).strftime("%Y-%m-%d")
        # elif isinstance(date_fin, datetime):
        #     date_fin = date_fin.strftime("%Y-%m-%d")
        # elif hasattr(date_fin, 'strftime'):
        #     date_fin = date_fin.strftime("%Y-%m-%d")

        # ✅ CORRECTION: Gérer correctement les dates
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        
        # Récupérer la date de début du véhicule
        vehicle_date_debut = vehicle.get("date_debut")
        
        # Par défaut, utiliser la date du jour
        date_debut = today.strftime("%Y-%m-%d")
        
        # Si une date de début est fournie, essayer de l'utiliser
        if vehicle_date_debut:
            try:
                # Convertir en date si c'est un datetime
                if isinstance(vehicle_date_debut, datetime):
                    vehicle_date = vehicle_date_debut.date()
                # Convertir en date si c'est une chaîne
                elif isinstance(vehicle_date_debut, str):
                    vehicle_date = datetime.strptime(vehicle_date_debut, "%Y-%m-%d").date()
                else:
                    vehicle_date = vehicle_date_debut
                
                # Utiliser la date du véhicule si elle est >= aujourd'hui
                if vehicle_date >= today:
                    date_debut = vehicle_date.strftime("%Y-%m-%d")
            except Exception as e:    from datetime import datetime, timedelta
        
        today = datetime.now().date()
        
        # Récupérer la date de début du véhicule
        vehicle_date_debut = vehicle.get("date_debut")
        
        # Par défaut, utiliser la date du jour
        date_debut = today.strftime("%Y-%m-%d")
        
        # Si une date de début est fournie, essayer de l'utiliser
        if vehicle_date_debut:
            try:
                # Convertir en date si c'est un datetime
                if isinstance(vehicle_date_debut, datetime):
                    vehicle_date = vehicle_date_debut.date()
                # Convertir en date si c'est une chaîne
                elif isinstance(vehicle_date_debut, str):
                    vehicle_date = datetime.strptime(vehicle_date_debut, "%Y-%m-%d").date()
                else:
                    vehicle_date = vehicle_date_debut
                
                # Utiliser la date du véhicule si elle est >= aujourd'hui
                if vehicle_date >= today:
                    date_debut = vehicle_date.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"⚠️ Erreur lors du parsing de la date de début: {e}")
        
        # date_fin = aujourd'hui + 1 an (ou utiliser celle du véhicule si valide)
        date_fin = (today + timedelta(days=365)).strftime("%Y-%m-%d")
        
        vehicle_date_fin = vehicle.get("date_fin")
        if vehicle_date_fin:
            try:
                if isinstance(vehicle_date_fin, datetime):
                    vehicle_date = vehicle_date_fin.date()
                elif isinstance(vehicle_date_fin, str):
                    vehicle_date = datetime.strptime(vehicle_date_fin, "%Y-%m-%d").date()
                else:
                    vehicle_date = vehicle_date_fin
                
                if vehicle_date >= today:
                    date_fin = vehicle_date.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"⚠️ Erreur lors du parsing de la date de fin: {e}")
    
                print(f"⚠️ Erreur lors du parsing de la date de début: {e}")
        
        # date_fin = aujourd'hui + 1 an (ou utiliser celle du véhicule si valide)
        date_fin = (today + timedelta(days=365)).strftime("%Y-%m-%d")
        
        vehicle_date_fin = vehicle.get("date_fin")
        if vehicle_date_fin:
            try:
                if isinstance(vehicle_date_fin, datetime):
                    vehicle_date = vehicle_date_fin.date()
                elif isinstance(vehicle_date_fin, str):
                    vehicle_date = datetime.strptime(vehicle_date_fin, "%Y-%m-%d").date()
                else:
                    vehicle_date = vehicle_date_fin
                
                if vehicle_date >= today:
                    date_fin = vehicle_date.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"⚠️ Erreur lors du parsing de la date de fin: {e}")
        
        
        # ✅ Récupérer la date de première mise en circulation
        first_registration = vehicle.get("date_mise_circulation")
        if not first_registration:
            # Si non fournie, utiliser l'année du véhicule (1er janvier)
            annee = vehicle.get("annee")
            if annee:
                first_registration = f"{annee}-01-01"
            else:
                first_registration = date_debut
        elif isinstance(first_registration, datetime):
            first_registration = first_registration.strftime("%Y-%m-%d")
        elif hasattr(first_registration, 'strftime'):
            first_registration = first_registration.strftime("%Y-%m-%d")
        
        # ✅ Numéro d'immatriculation sans espace
        licence_plate = vehicle.get("immatriculation", "").replace(" ", "").upper()
        
        # ✅ Numéro de police
        police_number = vehicle.get("numero_police", f"POL-{datetime.now().year}-{vehicle.get('id', '00000')}")
        
        # ✅ Code postal
        city = vehicle.get("city", "Douala")
        postal_code = f"BP {city}"
        
        # ✅ Nom du conducteur
        driver_name = vehicle.get("driver_name")
        if not driver_name:
            driver_name = vehicle.get("owner", "")
        
        # ✅ Date de naissance du conducteur
        driver_birthdate = vehicle.get("driver_birth")
        if not driver_birthdate:
            driver_birthdate = "1990-01-01"
        elif isinstance(driver_birthdate, datetime):
            driver_birthdate = driver_birthdate.strftime("%Y-%m-%d")
        elif hasattr(driver_birthdate, 'strftime'):
            driver_birthdate = driver_birthdate.strftime("%Y-%m-%d")
        
        # ✅ Date de délivrance du permis
        licence_issued_at = vehicle.get("driver_licence_date")
        if not licence_issued_at:
            licence_issued_at = "2010-01-01"
        elif isinstance(licence_issued_at, datetime):
            licence_issued_at = licence_issued_at.strftime("%Y-%m-%d")
        elif hasattr(licence_issued_at, 'strftime'):
            licence_issued_at = licence_issued_at.strftime("%Y-%m-%d")
        
        # ✅ Châssis
        chassis = vehicle.get("chassis", f"VF1{vehicle.get('id', '00000')}ABCD123456")
        
        # ✅ Puissance fiscale
        fiscal_power = vehicle.get("puissance_fiscale", 5)
        if fiscal_power:
            try:
                fiscal_power = int(fiscal_power)
            except (ValueError, TypeError):
                fiscal_power = 5
        
        # ✅ Nombre de places
        nb_seats = vehicle.get("places", 5)
        try:
            nb_seats = int(nb_seats)
        except (ValueError, TypeError):
            nb_seats = 5
        
        # ✅ Catégorie ASAC
        vehicle_category = self._get_vehicle_category(vehicle.get("categorie", "01"))
        
        # ✅ Genre ASAC
        vehicle_genre = self._get_vehicle_genre(vehicle.get("genre", "GV04"))
        
        # ✅ Type ASAC
        vehicle_type = self._get_vehicle_type(vehicle.get("type_vehicule", "TV10"))
        
        # ✅ Usage ASAC
        vehicle_usage = self._get_vehicle_usage(vehicle.get("usage", "UV01"))
        
        # ✅ Énergie ASAC
        vehicle_energy = self._get_vehicle_energy(vehicle.get("energie", "SEE"))
        
        # ✅ Zone de circulation
        zone = vehicle.get("zone", "A").upper()
        
        # ✅ Remorque
        has_trailer = vehicle.get("has_remorque", False)
        
        # ✅ Numéro de contribuable (obligatoire)
        taxpayer_number = vehicle.get("num_contribuable", "")
        if not taxpayer_number:
            # Générer un numéro temporaire si absent
            taxpayer_number = f"TMP-{datetime.now().strftime('%Y%m%d')}-{vehicle.get('id', '000')}"
        
        return {
            "office_code": office_code,
            "organization_code": organization_code,
            "certificate_type": "cima",
            "channel": "api",
            "productions": [
                {
                    "certificate_variant_code": "Bleu",
                    "rc": 63784,  # Valeur par défaut si non disponible
                    "police_number": police_number,
                    "starts_at": date_debut,
                    "ends_at": date_fin,
                    "customer_name": vehicle.get("owner", ""),
                    "customer_phone": vehicle.get("phone", ""),
                    "customer_email": vehicle.get("email", ""),
                    "customer_postal_code": postal_code,
                    "customer_type": "TSPM",
                    "insured_name": vehicle.get("owner", ""),
                    "insured_phone": vehicle.get("phone", ""),
                    "insured_email": vehicle.get("email", ""),
                    "insured_postal_code": postal_code,
                    "licence_plate": licence_plate,
                    "vehicle_chassis": chassis,
                    "vehicle_brand": vehicle.get("marque", "").upper(),
                    "vehicle_model": vehicle.get("modele", "").upper(),
                    "vehicle_category": vehicle_category,
                    "vehicle_genre": vehicle_genre,
                    "vehicle_type": vehicle_type,
                    "vehicule_usage": vehicle_usage,
                    "vehicle_energy": vehicle_energy,
                    "nb_of_seats": nb_seats,
                    "fiscal_power": fiscal_power,
                    "circulation_zone": zone,
                    "driver_name": driver_name,
                    "driver_birthdate": driver_birthdate,
                    "driver_licence_issued_at": licence_issued_at,
                    "vehicle_has_trailer": bool(has_trailer),
                    # ✅ CHAMPS OBLIGATOIRES
                    "taxpayer_number": taxpayer_number,
                    "vehicle_first_registration_date": first_registration
                }
            ]
        }

    def _normalize_date(self, value, default=None):
        """Normalise une date en format YYYY-MM-DD"""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                value = default
            else:
                for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%Y%m%d"):
                    try:
                        return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
                    return raw
                value = default

        if isinstance(default, datetime):
            return default.strftime("%Y-%m-%d")
        if isinstance(default, str):
            return default
        return datetime.now().strftime("%Y-%m-%d")

    def _parse_int(self, value, fallback=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    def _get_first_registration_date(self, vehicle):
        """Récupère la date de première mise en circulation"""
        first_reg = vehicle.get("vehicle_first_registration_date")
        if not first_reg:
            first_reg = vehicle.get("first_registration_date")
        
        if first_reg:
            return self._normalize_date(first_reg)

        annee = vehicle.get("annee") or vehicle.get("year")
        if annee:
            try:
                annee_str = str(int(annee))
                return f"{annee_str}-01-01"
            except (TypeError, ValueError):
                pass

        return self._normalize_date(vehicle.get("date_debut"), default=datetime.now())

    # def log_request(self, url, headers, payload, request_type="REQUEST"):
    #     """Affiche les détails de la requête pour le débogage"""
    #     print(f"\n{'='*60}")
    #     print(f"📤 {request_type}")
    #     print(f"{'='*60}")
    #     print(f"📍 URL: {url}")
    #     print(f"\n📋 HEADERS:")
    #     for key, value in headers.items():
    #         # Masquer partiellement les tokens pour la sécurité
    #         if key in ["Authorization", "X-App-Id"] and len(value) > 10:
    #             print(f"   {key}: {value[:10]}...{value[-5:]}")
    #         else:
    #             print(f"   {key}: {value}")
    #     print(f"\n📦 BODY:")
    #     print(json.dumps(payload, indent=2, ensure_ascii=False))
    #     print(f"{'='*60}\n")

    # def log_response(self, response, response_type="RESPONSE"):
    #     """Affiche les détails de la réponse pour le débogage"""
    #     print(f"\n{'='*60}")
    #     print(f"📥 {response_type}")
    #     print(f"{'='*60}")
    #     print(f"📊 Status Code: {response.status_code}")
    #     print(f"📋 Headers: {dict(response.headers)}")
    #     try:
    #         response_json = response.json()
    #         print(f"\n📦 BODYeee:")
    #         # Masquer le token partiellement pour la sécurité
    #         if isinstance(response_json, dict) and "token" in response_json:
    #             token = response_json["token"]
    #             if len(token) > 20:
    #                 response_json["token"] = f"{token[:15]}...{token[-10:]}"
    #         print(json.dumps(response_json, indent=2, ensure_ascii=False))
    #     except:
    #         print(f"\n📦 BODY (texte): {response.text[:500]}")
    #     print(f"{'='*60}\n")

    def log_request(self, url, headers, payload, request_type="REQUEST"):
        """Affiche et capture les détails de la requête"""
        log_text = f"\n{'='*60}\n"
        log_text += f"📤 {request_type}\n"
        log_text += f"{'='*60}\n"
        log_text += f"📍 URL: {url}\n"
        log_text += f"\n📋 HEADERS:\n"
        for key, value in headers.items():
            if key in ["Authorization", "X-App-Id"] and len(value) > 10:
                log_text += f"   {key}: {value[:10]}...{value[-5:]}\n"
            else:
                log_text += f"   {key}: {value}\n"
        log_text += f"\n📦 BODY:\n"
        log_text += json.dumps(payload, indent=2, ensure_ascii=False)
        log_text += f"\n{'='*60}\n"
        
        self.logs.append(log_text)
        self.log_captured.emit(log_text)
        print(log_text)

    def log_response(self, response, response_type="RESPONSE"):
        """Affiche et capture les détails de la réponse"""
        log_text = f"\n{'='*60}\n"
        log_text += f"📥 {response_type}\n"
        log_text += f"{'='*60}\n"
        log_text += f"📊 Status Code: {response.status_code}\n"
        log_text += f"📋 Headers: {dict(response.headers)}\n"
        try:
            response_json = response.json()
            log_text += f"\n📦 BODY:\n"
            # Masquer le token partiellement pour la sécurité
            if isinstance(response_json, dict) and "token" in response_json:
                token = response_json["token"]
                if len(token) > 20:
                    response_json["token"] = f"{token[:15]}...{token[-10:]}"
            log_text += json.dumps(response_json, indent=2, ensure_ascii=False)
        except:
            log_text += f"\n📦 BODY (texte): {response.text[:500]}\n"
        log_text += f"{'='*60}\n"
        
        self.logs.append(log_text)
        self.log_captured.emit(log_text)
        print(log_text)

    def _get_vehicle_category(self, categorie):
        """Convertit la catégorie en code standard ASAC"""
        mapping = {
            "VP01": "01",
            "VP02": "02",
            "VP03": "03",
            "VP04": "04",
            "VP05": "05",
            "VP06": "06",
            "VP07": "07",
            "VP08": "08",
            "VP09": "09",
            "VP10": "10",
            "VP11": "11",
            "VP12": "12",
            "01": "01",
            "02": "02",
            "03": "03",
            "04": "04",
            "05": "05",
            "06": "06",
            "07": "07",
            "08": "08",
            "09": "09",
            "10": "10",
            "11": "11",
            "12": "12"
        }
        return mapping.get(str(categorie).strip(), "01")

    def _get_vehicle_genre(self, genre):
        """Convertit le genre en code standard ASAC"""
        mapping = {
            "GV01": "GV01",
            "GV02": "GV02",
            "GV03": "GV03",
            "GV04": "GV04",
            "GV05": "GV05",
            "GV06": "GV06",
            "GV07": "GV07",
            "GV08": "GV08",
            "GV09": "GV09",
            "GV10": "GV10",
            "GV11": "GV11",
            "GV12": "GV12",
            "CAMION": "GV01",
            "CAMIONNETTE": "GV02",
            "CYCLOMOTEUR": "GV03",
            "VOITURE": "GV04"
        }
        return mapping.get(str(genre).strip(), "GV04")

    def _get_vehicle_usage(self, usage):
        """Convertit l'usage en code standard ASAC"""
        mapping = {
            "UV01": "UV01",
            "UV02": "UV02",
            "UV03": "UV03",
            "UV04": "UV04",
            "UV05": "UV05",
            "UV06": "UV06",
            "UV07": "UV07",
            "UV08": "UV08",
            "UV09": "UV09",
            "UV10": "UV10"
        }
        return mapping.get(str(usage).strip(), "UV01")

    def _get_vehicle_usage(self, usage):
        """Convertit l'usage en code standard"""
        mapping = {"UV01": "UV01", "UV02": "UV02", "UV03": "UV03", "UP01": "UP01", "UP02": "UP02"}
        return mapping.get(str(usage).upper(), "UV01")

    def _get_vehicle_energy(self, energy):
        """Convertit l'énergie en code standard ASAC"""
        mapping = {"Essence": "SEES", "Diesel": "DIESEL", "Electrique": "ELECTRIC", "Hybride": "HYBRID", "SEES": "SEES"}
        return mapping.get(str(energy).capitalize(), "SEES")

    def _get_vehicle_type(self, type_):
        """Convertit le type en code standard ASAC"""
        mapping = {
            "TV01": "TV01",
            "TV02": "TV02",
            "TV03": "TV03",
            "TV04": "TV04",
            "TV05": "TV05",
            "TV06": "TV06",
            "TV07": "TV07",
            "TV08": "TV08",
            "TV09": "TV09",
            "TV10": "TV10",
            "TV11": "TV11",
            "TV12": "TV12",
            "TV13": "TV13"
        }
        return mapping.get(str(type_).strip(), "TV10")

class ReceiveWorker(QThread):
    """Thread pour recevoir les données du serveur ASAC"""
    progress = Signal(int, str)
    finished = Signal(bool, dict, str)
    log_captured = Signal(str)
    
    def __init__(self, config, search_params):
        super().__init__()
        self.config = config
        self.search_params = search_params
        self.search_params = search_params
        self.logs = []

    def log_request(self, url, headers, payload, request_type="REQUEST"):
        log_text = f"\n{'='*60}\n📤 {request_type}\n{'='*60}\n📍 URL: {url}\n📦 BODY: {json.dumps(payload, indent=2)}\n{'='*60}\n"
        self.logs.append(log_text)
        self.log_captured.emit(log_text)
    
    def log_response(self, response, response_type="RESPONSE"):
        log_text = f"\n{'='*60}\n📥 {response_type}\n{'='*60}\n📊 Status Code: {response.status_code}\n"
        try:
            log_text += f"📦 BODY: {json.dumps(response.json(), indent=2)}\n"
        except:
            log_text += f"📦 BODY: {response.text[:500]}\n"
        log_text += f"{'='*60}\n"
        self.logs.append(log_text)
        self.log_captured.emit(log_text)


    def run(self):
        try:
            self.progress.emit(10, "📋 Préparation des données...")
        
            request = self.build_asac_request()
            
            self.progress.emit(30, "🔐 Authentification ASAC...")
            
            import requests
            auth_url = f"{self.config.get('url', '')}/api/v1/auth/tokens"
            auth_response = requests.post(
                auth_url,
                params={
                    "app_key": self.config.get("app_key", ""), 
                    "username": self.config.get("username", ""), 
                    "password": self.config.get("password", "")
                    },
                timeout=10
            )
            
            if auth_response.status_code != 200:
                self.finished.emit(False, {}, f"Authentification échouée: {auth_response.text[:100]}")
                return
            
            token = auth_response.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Construction de la requête de recherche
            search_type = self.search_params.get("type", "police")
            search_value = self.search_params.get("value", "")
            
            self.progress.emit(30, f"🔍 Recherche par {search_type}...")
            
            if search_type == "police":
                url = f"{self.config['url']}/api/v1/attestations/police/{search_value}"
            elif search_type == "immatriculation":
                url = f"{self.config['url']}/api/v1/attestations/immatriculation/{search_value}"
            elif search_type == "periode":
                url = f"{self.config['url']}/api/v1/attestations?date_debut={self.search_params.get('date_debut', '')}&date_fin={self.search_params.get('date_fin', '')}"
            else:
                url = f"{self.config['url']}/api/v1/attestations"
            
            self.progress.emit(60, "📥 Téléchargement des données...")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            self.progress.emit(90, "📋 Traitement des données...")
            
            if response.status_code == 200:
                data = response.json()
                self.progress.emit(100, "✅ Données récupérées !")
                self.finished.emit(True, data, "")
            else:
                self.finished.emit(False, {}, f"Erreur {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.finished.emit(False, {}, str(e))


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration ASAC")
        self.setMinimumSize(550, 500)
        self.setModal(True)
        self.setStyleSheet(MODERN_STYLE)
        
        # Initialiser le synthétiseur vocal avec diagnostic
        self.tts = None
        self.tts_available = self.init_tts()
        
        self.setup_ui()
        self.load_config()
    
    def init_tts(self):
        """Initialise le TTS avec diagnostic détaillé"""
        try:
            print("Tentative d'initialisation de QTextToSpeech...")
            self.tts = QTextToSpeech()
            
            # Vérifier si des voix sont disponibles
            available_voices = self.tts.availableVoices()
            print(f"Voix disponibles: {len(available_voices)}")
            
            if available_voices:
                # Sélectionner la première voix
                self.tts.setVoice(available_voices[0])
                voice_name = available_voices[0].name()
                print(f"Voix sélectionnée: {voice_name}")
                return True
            else:
                print("Aucune voix disponible sur le système")
                self.tts = None
                return False
                
        except Exception as e:
            print(f"Erreur d'initialisation TTS: {e}")
            self.tts = None
            return False
    
    def speak(self, message):
        """Lit un message vocalement avec vérification"""
        if not self.tts_available or self.tts is None:
            print(f"TTS non disponible - Message non lu: {message}")
            return False
        
        try:
            # Arrêter toute lecture en cours
            self.tts.stop()
            # Lire le nouveau message
            self.tts.say(message)
            print(f"Lecture vocale: {message}")
            return True
        except Exception as e:
            print(f"Erreur lors de la lecture vocale: {e}")
            return False
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # En-tête
        header = QFrame()
        header.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1e293b,stop:1 #0f172a); border-radius: 20px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        icon = QLabel("⚙️")
        icon.setStyleSheet("font-size: 32px;")
        title = QLabel("Configuration du serveur ASAC")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: white;")
        
        # Indicateur de statut TTS
        tts_status = QLabel("🔊" if self.tts_available else "🔇")
        tts_status.setStyleSheet("font-size: 20px; background: transparent;")
        tts_status.setToolTip("Synthèse vocale disponible" if self.tts_available else "Synthèse vocale non disponible")
        
        header_layout.addWidget(icon)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(tts_status)
        layout.addWidget(header)
        
        # Zone de défilement
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(16)
        
        # Carte des champs de configuration
        card = QFrame()
        card.setProperty("class", "InfoCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        
        fields = [
            ("🌐 URL API", "url", "https://ppeatt-api.asac.cm"),
            ("🔑 Clé applicative (App Key)", "app_key", ""),
            ("👤 Nom d'utilisateur", "username", ""),
            ("📧 Email", "email", ""),
            ("🔒 Mot de passe", "password", ""),  # Si nécessaire
            ("🏢 Code bureau", "office_code", "AG-DLA-001"),
            ("📋 Organisation", "org_code", "ACTIVA")
        ]
        
        self.inputs = {}
        for label, key, placeholder in fields:
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            if key == "app_key":
                inp.setEchoMode(QLineEdit.Password)
            if key == "password":
                inp.setEchoMode(QLineEdit.Password)

            card_layout.addWidget(lbl)
            card_layout.addWidget(inp)
            self.inputs[key] = inp
        
        form_layout.addWidget(card)
        
        # Bouton de test TTS
        test_tts_btn = QPushButton("🔊 Tester la synthèse vocale")
        test_tts_btn.setProperty("class", "BtnSecondary")
        test_tts_btn.clicked.connect(self.test_tts)
        test_tts_btn.setEnabled(self.tts_available)
        form_layout.addWidget(test_tts_btn)
        
        # Bouton de test de connexion
        test_btn = QPushButton("🔌 Tester la connexion")
        test_btn.setProperty("class", "BtnSecondary")
        test_btn.clicked.connect(self.test_connection)
        form_layout.addWidget(test_btn)
        
        help_text = QLabel("ℹ️ Pour obtenir une clé applicative (App Key) et un nom d'utilisateur valides, veuillez contacter l'administrateur ASAC.")
        help_text.setStyleSheet("color: #f59e0b; font-size: 11px; background: #fef3c7; padding: 8px; border-radius: 8px;")
        help_text.setWordWrap(True)
        form_layout.addWidget(help_text)
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Boutons de bas de page
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("class", "BtnSecondary")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.setProperty("class", "BtnSuccess")
        save_btn.clicked.connect(self.save_config)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
    
    def test_tts(self):
        """Teste la synthèse vocale"""
        if self.tts_available and self.tts:
            test_message = "Test de la synthèse vocale. Si vous entendez ce message, la voix fonctionne correctement."
            self.speak(test_message)
            QMessageBox.information(self, "Test vocal", "Lecture du message de test en cours...")
        else:
            QMessageBox.warning(self, "Test vocal", "La synthèse vocale n'est pas disponible sur ce système.")
    
    def load_config(self):
        settings = QSettings("LOMETA", "ASAC")
        for key, inp in self.inputs.items():
            value = settings.value(key, "")
            if value:
                inp.setText(value)
    
    def test_connection(self):
        import requests
        
        url = self.inputs["url"].text().strip().rstrip('/')  # Nettoyer l'URL
        app_key = self.inputs["app_key"].text().strip()
        username = self.inputs["username"].text().strip()
        
        # Vérifier les champs requis
        if not url or not app_key or not username:
            warning_msg = "Veuillez remplir l'URL, l'App Key et le nom d'utilisateur"
            QMessageBox.warning(self, "Champs manquants", warning_msg)
            self.speak(warning_msg)
            return
        
        # Désactiver le bouton pendant le test
        test_btn = self.sender()
        if test_btn:
            test_btn.setEnabled(False)
            test_btn.setText("⏳ Test en cours...")
        
        try:
            # URL nettoyée
            auth_url = f"{url}/api/v1/auth/tokens"
            
            print(f"\n🔑 Test de connexion ASAC")
            print(f"   URL: {auth_url}")
            print(f"   X-App-Id: {app_key[:10]}... (longueur: {len(app_key)})")
            print(f"   Username: {username[:30]}... (longueur: {len(username)})")
            
            headers = {
                "X-App-Id": app_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "username": username
            }
            
            response = requests.post(
                auth_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            # Afficher la réponse complète du serveur
            try:
                response_data = response.json()
                formatted_response = json.dumps(response_data, indent=2, ensure_ascii=False)
            except:
                formatted_response = response.text
            
            if response.status_code == 200:
                # Extraire les informations importantes
                token = response_data.get("token", "N/A")
                token_name = response_data.get("token_name", "N/A")
                expires_at = response_data.get("expires_at", "N/A")
                print(token)
                
                message = f"""✅ Connexion au serveur ASAC réussie ! (HTTP {response.status_code})

                    📋 RÉPONSE DU SERVEUR :
                    {formatted_response}

                    🔑 Informations du token :
                    • Nom: {token_name}
                    • Expiration: {expires_at}
                    • Token: {token[:50]}...{token[-30:] if len(token) > 80 else token}"""
                
                QMessageBox.information(self, "Succès", message)
                self.speak("Connexion au serveur ASAC réussie")
                
            else:
                message = f"""❌ Échec de la connexion (HTTP {response.status_code})

    📋 RÉPONSE DU SERVEUR :
    {formatted_response}"""
                
                QMessageBox.warning(self, "Erreur", message)
                self.speak(f"Erreur de connexion: {response.status_code}")
                        
        except requests.exceptions.Timeout:
            error_msg = "La requête a expiré. Vérifiez que l'URL est correcte et que le serveur est accessible."
            QMessageBox.warning(self, "Timeout", f"❌ {error_msg}")
            self.speak(error_msg)
                    
        except requests.exceptions.ConnectionError:
            error_msg = "Impossible de se connecter au serveur. Vérifiez l'URL et votre connexion internet."
            QMessageBox.warning(self, "Erreur de connexion", f"❌ {error_msg}")
            self.speak(error_msg)
                    
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            QMessageBox.warning(self, "Erreur", f"❌ {error_msg}")
            self.speak(error_msg)
        
        finally:
            if test_btn:
                test_btn.setEnabled(True)
                test_btn.setText("🔌 Tester la connexion")
            
    def save_config(self):
        # Vérifier que les champs obligatoires sont remplis
        required_fields = ["url", "username", "password", "email"]
        missing_fields = []
        
        for field in required_fields:
            if not self.inputs[field].text().strip():
                missing_fields.append(field)
        
        if missing_fields:
            field_names = {
                "url": "URL API",
                "username": "Nom d'utilisateur",
                "password": "Mot de passe",
                "email": "Email",
            }
            missing_names = [field_names[f] for f in missing_fields]
            error_msg = f"Les champs suivants sont obligatoires: {', '.join(missing_names)}"
            QMessageBox.warning(self, "Champs manquants", error_msg)
            
            # Lecture vocale de l'erreur
            self.speak(error_msg)
            return
        
        # Sauvegarder la configuration
        settings = QSettings("LOMETA", "ASAC")
        for key, inp in self.inputs.items():
            settings.setValue(key, inp.text())
        
        # Message de succès
        success_message = "Configuration sauvegardée avec succès !"
        
        # Afficher la boîte de dialogue
        QMessageBox.information(self, "Succès", success_message)
        
        # Lire le message à voix haute
        self.speak(success_message)
        
        self.accept()
    
    def test_connection(self):
        import requests
        
        url = self.inputs["url"].text().strip()
        email = self.inputs["email"].text().strip()
        password = self.inputs["password"].text().strip()
        username = self.inputs["username"].text().strip()
        
        # Vérifier les champs requis pour le test
        if not url:
            warning_msg = "Veuillez remplir l'URL avant de tester la connexion"
            QMessageBox.warning(self, "Champs manquants", warning_msg)
            self.speak(warning_msg)
            return
        if not email:
            warning_msg = "Veuillez remplir l'email, avant de tester la connexion"
            QMessageBox.warning(self, "Champs manquants", warning_msg)
            self.speak(warning_msg)
            return
        if not password:
            warning_msg = "Veuillez remplir le mot de passe avant de tester la connexion"
            QMessageBox.warning(self, "Champs manquants", warning_msg)
            self.speak(warning_msg)
            return
        if not username:
            warning_msg = "Veuillez remplir le nom d'utilisateur avant de tester la connexion"
            QMessageBox.warning(self, "Champs manquants", warning_msg)
            self.speak(warning_msg)
            return
        
        # Désactiver le bouton pendant le test
        test_btn = self.sender()
        if test_btn:
            test_btn.setEnabled(False)
            test_btn.setText("⏳ Test en cours...")
        
        try:
            # Effectuer la requête d'authentification
            response = requests.post(
                f"{url}/api/v1/auth/tokens",
                params={"email": email, "password": password, "username": username},
                timeout=10
            )
            
            if response.status_code == 200:
                success_msg = "Connexion au serveur ASAC réussie !"
                QMessageBox.information(self, "Succès", f"✅ {success_msg}")
                
                # Lecture vocale du succès
                self.speak(success_msg)
            else:
                error_msg = f"Erreur HTTP {response.status_code}: La connexion a échoué"
                QMessageBox.warning(self, "Erreur", f"❌ {error_msg}\n\nDétails: {response.text[:200]}")
                
                # Lecture vocale de l'erreur
                self.speak(error_msg)
                        
        except requests.exceptions.Timeout:
            error_msg = "La requête a expiré. Vérifiez que l'URL est correcte et que le serveur est accessible."
            QMessageBox.warning(self, "Timeout", f"❌ {error_msg}")
            self.speak(error_msg)
                    
        except requests.exceptions.ConnectionError:
            error_msg = "Impossible de se connecter au serveur. Vérifiez l'URL et votre connexion internet."
            QMessageBox.warning(self, "Erreur de connexion", f"❌ {error_msg}")
            self.speak(error_msg)
                    
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            QMessageBox.warning(self, "Erreur", f"❌ {error_msg}")
            self.speak(error_msg)
        
        finally:
            # Réactiver le bouton
            if test_btn:
                test_btn.setEnabled(True)
                test_btn.setText("🔌 Tester la connexion")
    
    def get_config(self):
        """Retourne la configuration actuelle sous forme de dictionnaire"""
        return {key: inp.text() for key, inp in self.inputs.items()}


class NotificationDialog(QDialog):
    """Dialogue de notification pour les réponses du serveur"""
    def __init__(self, title, message, details=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.setModal(False)
        self.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Icône
        icon_label = QLabel("📨")
        icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        
        # Message principal
        msg_label = QLabel(message)
        msg_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1e293b;")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        # Détails
        if details:
            text_edit = QTextEdit()
            text_edit.setPlainText(json.dumps(details, indent=2, default=str, ensure_ascii=False))
            text_edit.setFont(QFont("Courier New", 10))
            text_edit.setStyleSheet("background: #1e1e2e; color: #cdd6f4; border-radius: 12px; padding: 16px;")
            text_edit.setMinimumHeight(250)
            layout.addWidget(text_edit)
        
        btn = QPushButton("Fermer")
        btn.setProperty("class", "BtnPrimary")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)



# ============================================================================
# VALIDATEUR DE CONFORMITÉ ASAC
# ============================================================================

class AsacDataValidator:
    """Valide la conformité des données selon le format ASAC exigé"""
    
    # Champs obligatoires
    REQUIRED_FIELDS = [
        "office_code", "organization_code", "certificate_type", "channel", "productions"
    ]
    
    # Champs obligatoires dans productions
    REQUIRED_PRODUCTION_FIELDS = [
        "certificate_variant_code", "rc", "police_number", "starts_at", "ends_at",
        "customer_name", "customer_phone", "licence_plate", "vehicle_chassis",
        "vehicle_brand", "vehicle_model", "vehicle_category", "vehicle_genre",
        "vehicle_type", "vehicule_usage", "vehicle_energy", "nb_of_seats",
        "fiscal_power", "circulation_zone"
    ]
    
    # Valeurs autorisées
    VALID_CERTIFICATE_VARIANTS = ["JAUNE", "VERTE", "BLEUE", "ROSE"]
    VALID_CERTIFICATE_TYPES = ["cima", "non_cima"]
    VALID_CHANNELS = ["api", "web", "mobile"]
    VALID_ENERGIES = ["SEES", "DIESEL", "ELECTRIC", "HYBRID"]
    VALID_CATEGORIES = ["01", "02", "03", "04"]
    VALID_GENRES = ["GV04", "GV05", "GV06", "GP01", "GP02"]
    VALID_TYPES = ["TV10", "TV20", "TV30", "TC10", "TC20"]
    VALID_USAGES = ["UV01", "UV02", "UV03", "UP01", "UP02"]
    VALID_ZONES = ["A", "B", "C", "D"]
    
    @classmethod
    def validate_request(cls, data):
        """Valide complètement la requête"""
        errors = []
        warnings = []
        
        # Validation des champs racine
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"❌ Champ obligatoire manquant: '{field}'")
        
        # Validation des valeurs racine
        if data.get("certificate_type") not in cls.VALID_CERTIFICATE_TYPES:
            errors.append(f"❌ certificate_type invalide: '{data.get('certificate_type')}' (attendu: {', '.join(cls.VALID_CERTIFICATE_TYPES)})")
        
        if data.get("channel") not in cls.VALID_CHANNELS:
            errors.append(f"❌ channel invalide: '{data.get('channel')}' (attendu: {', '.join(cls.VALID_CHANNELS)})")
        
        # Validation des productions
        productions = data.get("productions", [])
        if not productions:
            errors.append("❌ La liste 'productions' est vide")
        
        for idx, prod in enumerate(productions):
            prod_errors = cls._validate_production(prod, idx)
            errors.extend(prod_errors)
        
        return errors, warnings
    
    @classmethod
    def _validate_production(cls, prod, idx):
        """Valide une production individuelle"""
        errors = []
        
        # Vérification des champs obligatoires
        for field in cls.REQUIRED_PRODUCTION_FIELDS:
            if field not in prod:
                errors.append(f"❌ Production[{idx}]: Champ obligatoire manquant '{field}'")
            elif prod[field] in [None, "", 0] and field not in ["rc", "fiscal_power"]:
                if field not in ["customer_email", "insured_email", "driver_name", "driver_birthdate", "driver_licence_issued_at", "vehicle_has_trailer"]:
                    errors.append(f"⚠️ Production[{idx}]: Champ '{field}' est vide ou nul")
        
        # Validation des valeurs
        if prod.get("certificate_variant_code") not in cls.VALID_CERTIFICATE_VARIANTS:
            errors.append(f"❌ Production[{idx}]: certificate_variant_code invalide (attendu: {', '.join(cls.VALID_CERTIFICATE_VARIANTS)})")
        
        # Validation des formats
        if prod.get("starts_at"):
            if not cls._validate_date(prod["starts_at"]):
                errors.append(f"❌ Production[{idx}]: starts_at invalide (format YYYY-MM-DD requis)")
        
        if prod.get("ends_at"):
            if not cls._validate_date(prod["ends_at"]):
                errors.append(f"❌ Production[{idx}]: ends_at invalide (format YYYY-MM-DD requis)")
        
        if prod.get("customer_phone"):
            if not cls._validate_phone(prod["customer_phone"]):
                errors.append(f"⚠️ Production[{idx}]: customer_phone format recommandé: +237XXXXXXXXX")
        
        if prod.get("licence_plate"):
            if not cls._validate_licence_plate(prod["licence_plate"]):
                errors.append(f"⚠️ Production[{idx}]: licence_plate format recommandé: XX-XXXX-XX")
        
        if prod.get("vehicle_chassis"):
            if len(prod["vehicle_chassis"]) < 10:
                errors.append(f"⚠️ Production[{idx}]: vehicle_chassis trop court (minimum 10 caractères)")
        
        return errors
    
    @staticmethod
    def _validate_date(date_str):
        """Valide le format de date YYYY-MM-DD"""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, date_str))
    
    @staticmethod
    def _validate_phone(phone):
        """Valide le format de téléphone"""
        pattern = r'^\+237[0-9]{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def _validate_licence_plate(plate):
        """Valide le format de plaque d'immatriculation"""
        pattern = r'^[A-Z]{2}-\d{4}-[A-Z]{2}$'
        return bool(re.match(pattern, plate))
    
    @classmethod
    def get_compliance_report(cls, data):
        """Génère un rapport de conformité détaillé"""
        errors, warnings = cls.validate_request(data)
        
        total_fields = len(cls.REQUIRED_FIELDS) + len(cls.REQUIRED_PRODUCTION_FIELDS)
        valid_fields = total_fields - len(errors)
        
        return {
            "is_compliant": len(errors) == 0,
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "compliance_rate": int((valid_fields / total_fields) * 100) if total_fields > 0 else 0
        }


# ============================================================================
# WIDGET PRINCIPAL
# ============================================================================

class AsacManager(QDialog):
    """Interface ASAC avec onglets Export et Import"""
    
    def __init__(self, controller, vehicle_data, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.vehicle_data = vehicle_data
        self.export_worker = None
        self.receive_worker = None
        self.last_search_params = None
        self.current_attestations = []
        
        self.setWindowTitle(f"ASAC Manager - {vehicle_data.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(1100, 800)
        self.setStyleSheet(MODERN_STYLE)
        
        self.setup_ui()
        self.load_config()
        self.display_vehicle_info()
        self.view_certificate()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # En-tête
        header = self._create_header()
        layout.addWidget(header)
        
        # Onglets principaux
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_export_tab(), "📤 Export (Envoi)")
        self.tab_widget.addTab(self._create_import_tab(), "📥 Import (Réception)")
        
        layout.addWidget(self.tab_widget)
        
        # Barre de statut
        self.status_bar = QFrame()
        self.status_bar.setProperty("class", "InfoCard")
        self.status_bar.setFixedHeight(50)
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(16, 8, 16, 8)
        
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("color: #f59e0b; font-size: 12px;")
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #64748b; font-size: 12px;")
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.setProperty("class", "BtnSecondary")
        close_btn.clicked.connect(self.close)
        status_layout.addWidget(close_btn)
        
        layout.addWidget(self.status_bar)
        self.apply_shadows_to_all_cards()
    
    def _create_header(self):
        header = QFrame()
        header.setProperty("class", "HeaderCard")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)
        
        logo_container = QHBoxLayout()
        logo = QLabel("🔄")
        logo.setStyleSheet("font-size: 32px;")
        logo_container.addWidget(logo)
        logo_container.addSpacing(12)
        
        title_container = QVBoxLayout()
        title = QLabel("Interface ASAC")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #0f172a;")
        subtitle = QLabel("Export et import des données d'assurance")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        logo_container.addLayout(title_container)
        
        layout.addLayout(logo_container)
        layout.addStretch()
        
        # Statut serveur
        status_frame = QFrame()
        status_frame.setProperty("class", "InfoCard")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(16, 8, 16, 8)
        
        self.server_indicator = QLabel("●")
        self.server_indicator.setStyleSheet("font-size: 12px; color: #f59e0b;")
        self.server_status_label = QLabel("Non configuré")
        self.server_status_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #64748b;")
        
        status_layout.addWidget(self.server_indicator)
        status_layout.addWidget(self.server_status_label)
        
        layout.addWidget(status_frame)
        
        config_btn = QPushButton("⚙️")
        config_btn.setFixedSize(44, 44)
        config_btn.setProperty("class", "BtnSecondary")
        config_btn.setToolTip("Configuration du serveur")
        config_btn.clicked.connect(self.open_config)
        layout.addWidget(config_btn)
        
        return header
    
    def _create_export_tab(self):
        """Onglet d'export (envoi vers ASAC)"""
        tab = QWidget()
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau gauche - Informations véhicule
        left_panel = self._create_vehicle_info_panel()
        splitter.addWidget(left_panel)
        
        # Panneau droit - Export
        right_panel = self._create_export_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        
        return tab

    def apply_shadows_to_all_cards(self):
        """Applique une ombre portée à toutes les cartes (InfoCard, HeaderCard)"""
        # Ombre standard pour les cartes
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(15)
        card_shadow.setXOffset(0)
        card_shadow.setYOffset(4)
        card_shadow.setColor(QColor(0, 0, 0, 40))
        
        # Ombre plus légère pour les petites cartes
        light_shadow = QGraphicsDropShadowEffect()
        light_shadow.setBlurRadius(10)
        light_shadow.setXOffset(0)
        light_shadow.setYOffset(2)
        light_shadow.setColor(QColor(0, 0, 0, 30))
        
        # Parcourir tous les enfants du widget principal
        def apply_to_children(widget):
            for child in widget.findChildren(QFrame):
                class_name = child.property("class")
                if class_name in ["InfoCard", "HeaderCard", "MainCard"]:
                    # Vérifier si c'est une grande carte ou une petite
                    if child.minimumHeight() > 100 or child.height() > 150:
                        child.setGraphicsEffect(card_shadow)
                    else:
                        child.setGraphicsEffect(light_shadow)
        
        apply_to_children(self)

    def _create_import_tab(self):
        """Onglet d'import (réception depuis ASAC) avec disposition:
        - Gauche (30%): Panneau de recherche, Filtres avancés
        - Droite (70%): divisée VERTICALEMENT en deux parties
            - Haut (40% de la droite): Aperçu des données reçues + Rapport de conformité
            - Bas (60% de la droite): Rafraîchissement auto, Progression, Export, Statistiques, Recherche, Actions, Tableau
        """
        
        # Widget principal avec disposition horizontale
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)
        
        # ========== PARTIE GAUCHE (30%) ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)
        
        # ---- 1. Panneau de recherche ----
        search_card = QFrame()
        search_card.setProperty("class", "InfoCard")
        search_layout = QVBoxLayout(search_card)
        search_layout.setSpacing(16)
        
        search_title = QLabel("🔍 Rechercher des attestations")
        search_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        search_layout.addWidget(search_title)
        
        # Type de recherche
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)
        
        self.search_type = QComboBox()
        self.search_type.addItems(["Numéro de police", "Immatriculation", "Période"])
        options_layout.addWidget(self.search_type)
        
        self.search_value = QLineEdit()
        self.search_value.setPlaceholderText("Entrez la valeur de recherche...")
        options_layout.addWidget(self.search_value)
        
        self.date_debut = QLineEdit()
        self.date_debut.setPlaceholderText("Date début (YYYY-MM-DD)")
        self.date_debut.setVisible(False)
        options_layout.addWidget(self.date_debut)
        
        self.date_fin = QLineEdit()
        self.date_fin.setPlaceholderText("Date fin (YYYY-MM-DD)")
        self.date_fin.setVisible(False)
        options_layout.addWidget(self.date_fin)
        
        search_layout.addLayout(options_layout)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Rechercher")
        self.search_btn.setProperty("class", "BtnPrimary")
        self.search_btn.clicked.connect(self.start_receive)
        
        self.clear_btn = QPushButton("Effacer")
        self.clear_btn.setProperty("class", "BtnSecondary")
        self.clear_btn.clicked.connect(self.clear_search)
        
        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        search_layout.addLayout(btn_layout)
        
        left_layout.addWidget(search_card)
        
        # ---- 2. Filtres avancés ----
        advanced_filters_card = QFrame()
        advanced_filters_card.setProperty("class", "InfoCard")
        advanced_filters_layout = QVBoxLayout(advanced_filters_card)
        advanced_filters_layout.setSpacing(12)
        
        filters_title = QLabel("🔧 Filtres avancés")
        filters_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #475569;")
        advanced_filters_layout.addWidget(filters_title)
        
        filters_grid = QGridLayout()
        filters_grid.setSpacing(10)
        
        # Statut
        filters_grid.addWidget(QLabel("Statut:"), 0, 0)
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tous", "VALIDE", "EN_ATTENTE", "REJETE", "EXPIRE"])
        self.filter_status.currentTextChanged.connect(self.apply_filters)
        filters_grid.addWidget(self.filter_status, 0, 1)
        
        # Type certificat
        filters_grid.addWidget(QLabel("Type certificat:"), 1, 0)
        self.filter_cert_type = QComboBox()
        self.filter_cert_type.addItems(["Tous", "cima", "non_cima"])
        self.filter_cert_type.currentTextChanged.connect(self.apply_filters)
        filters_grid.addWidget(self.filter_cert_type, 1, 1)
        
        # Variante
        filters_grid.addWidget(QLabel("Variante:"), 2, 0)
        self.filter_variant = QComboBox()
        self.filter_variant.addItems(["Tous", "JAUNE", "VERTE", "BLEUE", "ROSE"])
        self.filter_variant.currentTextChanged.connect(self.apply_filters)
        filters_grid.addWidget(self.filter_variant, 2, 1)
        
        advanced_filters_layout.addLayout(filters_grid)
        left_layout.addWidget(advanced_filters_card)
        left_layout.addStretch()
        
        # ========== PARTIE DROITE (70%) - DIVISION VERTICALE ==========
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)
        
        # ----- PARTIE HAUTE (40% de la droite) : Aperçu + Conformité -----
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(16)
        
        # ---- Aperçu des données reçues ----
        preview_received_card = QFrame()
        preview_received_card.setProperty("class", "InfoCard")
        preview_received_layout = QVBoxLayout(preview_received_card)
        preview_received_layout.setSpacing(12)
        
        preview_received_title = QLabel("👁️ Aperçu des données reçues")
        preview_received_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        preview_received_layout.addWidget(preview_received_title)

        clear_logs_btn = QPushButton("🗑️")
        clear_logs_btn.setProperty("class", "BtnSecondary")
        clear_logs_btn.setFixedSize(100, 30)
        clear_logs_btn.clicked.connect(self.clear_logs)
        preview_received_layout.addWidget(clear_logs_btn)

        
        self.received_preview = QTextEdit()
        self.received_preview.setReadOnly(True)
        self.received_preview.setFont(QFont("Courier New", 10))
        self.received_preview.setMinimumHeight(200)
        self.received_preview.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #cdd6f4;
                border-radius: 12px;
                padding: 16px;
                font-family: monospace;
            }
        """)
        preview_received_layout.addWidget(self.received_preview)
        
        top_layout.addWidget(preview_received_card)
        
        
        # ----- PARTIE BASSE (60% de la droite) : Résultats et actions AVEC SCROLL -----
        bottom_scroll = QScrollArea()
        bottom_scroll.setWidgetResizable(True)
        bottom_scroll.setFrameShape(QFrame.NoFrame)
        bottom_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #e2e8f0;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """)
        
        bottom_content = QWidget()
        bottom_layout = QVBoxLayout(bottom_content)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(16)
        
        # ---- Rafraîchissement automatique ----
        refresh_card = QFrame()
        refresh_card.setProperty("class", "InfoCard")
        refresh_layout = QHBoxLayout(refresh_card)
        refresh_layout.setContentsMargins(20, 12, 20, 12)
        
        self.auto_refresh_cb = QCheckBox("🔄 Rafraîchissement automatique (30s)")
        self.auto_refresh_cb.setStyleSheet("font-size: 12px;")
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        
        refresh_layout.addWidget(self.auto_refresh_cb)
        refresh_layout.addStretch()
        bottom_layout.addWidget(refresh_card)
        
        # ---- Progression ----
        progress_card = QFrame()
        progress_card.setProperty("class", "InfoCard")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(20, 12, 20, 12)
        
        self.receive_progress = QProgressBar()
        self.receive_progress.setVisible(False)
        self.receive_status = QLabel("")
        self.receive_status.setStyleSheet("color: #64748b; font-size: 12px;")
        
        progress_layout.addWidget(self.receive_progress)
        progress_layout.addWidget(self.receive_status)
        bottom_layout.addWidget(progress_card)
        
        # ---- Export des résultats ----
        export_results_card = QFrame()
        export_results_card.setProperty("class", "InfoCard")
        export_results_layout = QHBoxLayout(export_results_card)
        export_results_layout.setContentsMargins(20, 12, 20, 12)
        
        export_csv_btn = QPushButton("📊 Exporter en CSV")
        export_csv_btn.setProperty("class", "BtnSecondary")
        export_csv_btn.clicked.connect(self.export_results_to_csv)
        
        export_json_btn = QPushButton("📋 Exporter en JSON")
        export_json_btn.setProperty("class", "BtnSecondary")
        export_json_btn.clicked.connect(self.export_results_to_json)
        
        export_results_layout.addWidget(export_csv_btn)
        export_results_layout.addWidget(export_json_btn)
        export_results_layout.addStretch()
        bottom_layout.addWidget(export_results_card)
        
        # ---- Statistiques des résultats ----
        stats_card = QFrame()
        stats_card.setProperty("class", "InfoCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 12, 20, 12)
        
        self.stats_total = QLabel("📊 Total: 0")
        self.stats_total.setStyleSheet("font-weight: 700; color: #3b82f6;")
        
        self.stats_valid = QLabel("✅ Valides: 0")
        self.stats_valid.setStyleSheet("color: #10b981;")
        
        self.stats_expired = QLabel("⏰ Expirés: 0")
        self.stats_expired.setStyleSheet("color: #f59e0b;")
        
        stats_layout.addWidget(self.stats_total)
        stats_layout.addWidget(self.stats_valid)
        stats_layout.addWidget(self.stats_expired)
        stats_layout.addStretch()
        bottom_layout.addWidget(stats_card)
        
        # ---- Recherche dans les résultats ----
        search_results_card = QFrame()
        search_results_card.setProperty("class", "InfoCard")
        search_results_layout = QHBoxLayout(search_results_card)
        search_results_layout.setContentsMargins(20, 12, 20, 12)
        
        search_results_label = QLabel("🔎 Filtrer résultats:")
        search_results_label.setStyleSheet("font-size: 12px; font-weight: 600;")
        
        self.results_filter = QLineEdit()
        self.results_filter.setPlaceholderText("Rechercher dans les résultats...")
        self.results_filter.textChanged.connect(self.filter_results)
        
        search_results_layout.addWidget(search_results_label)
        search_results_layout.addWidget(self.results_filter)
        bottom_layout.addWidget(search_results_card)
        
        # ---- Actions en masse ----
        bulk_actions_card = QFrame()
        bulk_actions_card.setProperty("class", "InfoCard")
        bulk_actions_layout = QHBoxLayout(bulk_actions_card)
        bulk_actions_layout.setContentsMargins(20, 12, 20, 12)
        
        self.select_all_cb = QCheckBox("☑️ Tout sélectionner")
        self.select_all_cb.setStyleSheet("font-size: 12px;")
        self.select_all_cb.stateChanged.connect(self.select_all_results)
        
        self.bulk_import_btn = QPushButton("📥 Importer sélection")
        self.bulk_import_btn.setProperty("class", "BtnPrimary")
        self.bulk_import_btn.setEnabled(False)
        self.bulk_import_btn.clicked.connect(self.bulk_import)
        
        bulk_actions_layout.addWidget(self.select_all_cb)
        bulk_actions_layout.addWidget(self.bulk_import_btn)
        bulk_actions_layout.addStretch()
        bottom_layout.addWidget(bulk_actions_card)
        
        # ---- Tableau des résultats ----
        results_card = QFrame()
        results_card.setProperty("class", "InfoCard")
        results_layout = QVBoxLayout(results_card)
        results_layout.setSpacing(12)
        
        results_title = QLabel("📋 Résultats des attestations")
        results_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        results_layout.addWidget(results_title)
        
        self.results_table = QTableWidget(0, 6)
        self.results_table.setHorizontalHeaderLabels(["Police", "Immatriculation", "Propriétaire", "Période", "Statut", "Actions"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setMinimumHeight(250)
        
        results_layout.addWidget(self.results_table)
        bottom_layout.addWidget(results_card)
        
        # Espace flexible
        bottom_layout.addStretch()
        
        bottom_scroll.setWidget(bottom_content)
        
        # Assemblage de la partie droite (top + bottom)
        right_layout.addWidget(top_widget, 40)      # 40% pour la partie haute
        right_layout.addWidget(bottom_scroll, 60)   # 60% pour la partie basse avec scroll
        
        # Assemblage des deux parties principales
        main_layout.addWidget(left_widget, 30)      # 30% pour la gauche
        main_layout.addWidget(right_widget, 70)     # 70% pour la droite
        
        # Widget principal
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 16, 0, 16)
        tab_layout.addWidget(main_widget)
        
        # Connecter les signaux
        self.search_type.currentTextChanged.connect(self._on_search_type_changed)
        
        return tab

    def _create_vehicle_info_panel(self):
        """Panneau des informations véhicule"""
        panel = QScrollArea()
        panel.setWidgetResizable(True)
        panel.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        
        # Carte véhicule
        vehicle_card = QFrame()
        vehicle_card.setProperty("class", "InfoCard")
        vehicle_layout = QVBoxLayout(vehicle_card)
        vehicle_layout.setSpacing(12)
        
        title_layout = QHBoxLayout()
        title_icon = QLabel("🚗")
        title_icon.setStyleSheet("font-size: 24px;")
        title = QLabel("Informations véhicule")
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        vehicle_layout.addLayout(title_layout)
        
        info_fields = [
            ("Immatriculation", "immatriculation"),
            ("Marque / Modèle", "marque_modele"),
            ("Châssis", "chassis"),
            ("Année", "annee"),
            ("Énergie", "energie"),
            ("Catégorie", "categorie"),
            ("Propriétaire", "owner"),
            ("Téléphone", "phone"),
            ("Email", "email"),
            ("Prime nette", "prime_nette")
        ]
        
        self.vehicle_info = {}
        for label, key in info_fields:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            lbl.setFixedWidth(120)
            
            value_lbl = QLabel()
            value_lbl.setProperty("class", "LabelValue")
            value_lbl.setWordWrap(True)
            
            row.addWidget(lbl)
            row.addWidget(value_lbl, 1)
            vehicle_layout.addLayout(row)
            
            self.vehicle_info[key] = value_lbl
        
        layout.addWidget(vehicle_card)
        
        # Carte garanties
        garanties_card = QFrame()
        garanties_card.setProperty("class", "InfoCard")
        garanties_layout = QVBoxLayout(garanties_card)
        garanties_layout.setSpacing(10)
        
        garanties_title = QLabel("🛡️ Garanties souscrites")
        garanties_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        garanties_layout.addWidget(garanties_title)
        
        self.garanties_table = QTableWidget(0, 2)
        self.garanties_table.setHorizontalHeaderLabels(["Garantie", "Montant"])
        self.garanties_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.garanties_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.garanties_table.setAlternatingRowColors(True)
        self.garanties_table.setMaximumHeight(200)
        garanties_layout.addWidget(self.garanties_table)
        
        layout.addWidget(garanties_card)
        
        # Carte configuration
        config_card = QFrame()
        config_card.setProperty("class", "InfoCard")
        config_layout = QVBoxLayout(config_card)
        config_layout.setSpacing(10)
        
        config_header = QHBoxLayout()
        config_title = QLabel("⚙️ Serveur ASAC")
        config_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.config_status = QLabel("Non configuré")
        self.config_status.setProperty("class", "StatusBadge")
        config_header.addWidget(config_title)
        config_header.addStretch()
        config_header.addWidget(self.config_status)
        config_layout.addLayout(config_header)
        
        self.server_info_label = QLabel("Cliquez sur 'Configurer' pour paramétrer le serveur")
        self.server_info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        config_layout.addWidget(self.server_info_label)
        
        config_btn = QPushButton("🔧 Configurer le serveur")
        config_btn.setProperty("class", "BtnSecondary")
        config_btn.clicked.connect(self.open_config)
        config_layout.addWidget(config_btn)
        
        layout.addWidget(config_card)
        layout.addStretch()
        
        panel.setWidget(container)
        return panel
    
    def export_results_to_csv(self):
        """Exporte les résultats de la recherche en CSV"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Aucune donnée", "Il n'y a aucune donnée à exporter.")
            return
        
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", "attestations.csv", "CSV (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # En-têtes
                    headers = ["Police", "Immatriculation", "Propriétaire", "Date début", "Date fin", "Statut"]
                    writer.writerow(headers)
                    
                    # Données
                    for row in range(self.results_table.rowCount()):
                        police = self.results_table.item(row, 0).text()
                        immat = self.results_table.item(row, 1).text()
                        proprietaire = self.results_table.item(row, 2).text()
                        periode = self.results_table.item(row, 3).text()
                        statut = self.results_table.item(row, 4).text()
                        
                        # Séparer les dates
                        dates = periode.split(" → ")
                        date_debut = dates[0] if len(dates) > 0 else ""
                        date_fin = dates[1] if len(dates) > 1 else ""
                        
                        writer.writerow([police, immat, proprietaire, date_debut, date_fin, statut])
                
                self._show_notification("Export réussi", f"✅ {file_path} a été sauvegardé", "success")
            except Exception as e:
                self._show_notification("Erreur", f"❌ Erreur lors de l'export: {str(e)}", "error")

    def export_results_to_json(self):
        """Exporte les résultats de la recherche en JSON"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Aucune donnée", "Il n'y a aucune donnée à exporter.")
            return
        
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en JSON", "attestations.json", "JSON (*.json)"
        )
        
        if file_path:
            try:
                results = []
                for row in range(self.results_table.rowCount()):
                    police = self.results_table.item(row, 0).text()
                    immat = self.results_table.item(row, 1).text()
                    proprietaire = self.results_table.item(row, 2).text()
                    periode = self.results_table.item(row, 3).text()
                    statut = self.results_table.item(row, 4).text()
                    
                    dates = periode.split(" → ")
                    results.append({
                        "police_number": police,
                        "licence_plate": immat,
                        "owner": proprietaire,
                        "start_date": dates[0] if len(dates) > 0 else "",
                        "end_date": dates[1] if len(dates) > 1 else "",
                        "status": statut
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                self._show_notification("Export réussi", f"✅ {file_path} a été sauvegardé", "success")
            except Exception as e:
                self._show_notification("Erreur", f"❌ Erreur lors de l'export: {str(e)}", "error")

    def _create_export_panel(self):
        """Panneau d'export avec disposition horizontale divisée en deux parties"""
        
        # Widget principal
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)
        
        # ========== PARTIE GAUCHE (40%) ==========
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)
        
        # Carte d'aperçu JSON
        preview_card = QFrame()
        preview_card.setProperty("class", "InfoCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setSpacing(12)
        
        preview_header = QHBoxLayout()
        preview_title = QLabel("📋 Aperçu")
        preview_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()

        copy_btn = QPushButton("📋 Copier")
        copy_btn.setProperty("class", "BtnSecondary")
        copy_btn.setFixedSize(80, 30)
        copy_btn.clicked.connect(self.copy_json)

        show_logs_btn = QPushButton("📋")
        show_logs_btn.setProperty("class", "BtnSecondary")
        show_logs_btn.setFixedSize(120, 30)
        show_logs_btn.clicked.connect(self.show_export_logs)
        preview_header.addWidget(show_logs_btn)
        preview_header.addWidget(copy_btn)
        preview_layout.addLayout(preview_header)
        
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Courier New", 10))
        self.json_preview.setMinimumHeight(350)
        self.json_preview.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #cdd6f4;
                border-radius: 12px;
                padding: 16px;
                font-family: monospace;
            }
        """)
        preview_layout.addWidget(self.json_preview)
        
        left_layout.addWidget(preview_card)

        # ========== NOUVEAU : Carte d'affichage du token ==========
        token_card = QFrame()
        token_card.setProperty("class", "InfoCard")
        token_layout = QVBoxLayout(token_card)
        token_layout.setSpacing(8)
        
        token_header = QHBoxLayout()
        token_title = QLabel("🔑 Token d'authentification ASAC")
        token_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        token_header.addWidget(token_title)
        token_header.addStretch()
        
        copy_token_btn = QPushButton("📋 Copier le token")
        copy_token_btn.setProperty("class", "BtnSecondary")
        copy_token_btn.setFixedSize(120, 30)
        copy_token_btn.clicked.connect(self.copy_token)
        token_header.addWidget(copy_token_btn)
        
        token_layout.addLayout(token_header)
        
        self.token_display = QTextEdit()
        self.token_display.setReadOnly(True)
        self.token_display.setFont(QFont("Courier New", 10))
        self.token_display.setMinimumHeight(200)  # Hauteur minimale augmentée
        self.token_display.setMaximumHeight(300)  # Hauteur maximale augmentée
        self.token_display.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e;
                color: #cdd6f4;
                border-radius: 12px;
                padding: 12px;
                font-family: monospace;
            }
        """)
        token_layout.addWidget(self.token_display)
        
        # Informations du token
        token_info_layout = QHBoxLayout()
        self.token_name_label = QLabel("Nom: -")
        self.token_name_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.token_expires_label = QLabel("Expire: -")
        self.token_expires_label.setStyleSheet("color: #64748b; font-size: 11px;")
        token_info_layout.addWidget(self.token_name_label)
        token_info_layout.addWidget(self.token_expires_label)
        token_info_layout.addStretch()
        token_layout.addLayout(token_info_layout)
        
        left_layout.addWidget(token_card)
        
        # Panneau de conformité
        left_layout.addWidget(self._create_compliance_panel())
        
        # ========== PARTIE DROITE (60%) AVEC SCROLL ==========
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #e2e8f0;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """)
        
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)
        
        # Zone d'export
        export_card = QFrame()
        export_card.setProperty("class", "InfoCard")
        export_layout = QVBoxLayout(export_card)
        export_layout.setSpacing(12)
        
        export_title = QLabel("🚀 Export vers ASAC")
        export_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        export_layout.addWidget(export_title)
        
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        export_layout.addWidget(self.export_progress)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.export_btn = QPushButton("📤 Exporter vers ASAC")
        self.export_btn.setProperty("class", "BtnPrimary")
        self.export_btn.setMinimumHeight(45)
        self.export_btn.clicked.connect(self.start_export)
        
        self.view_certificate_btn = QPushButton("📄 Voir l'attestation")
        self.view_certificate_btn.setProperty("class", "BtnSecondary")
        self.view_certificate_btn.setVisible(False)
        self.view_certificate_btn.clicked.connect(self.view_certificate)
        
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.view_certificate_btn)
        export_layout.addLayout(btn_layout)
        
        right_layout.addWidget(export_card)
        
        # Historique
        history_card = QFrame()
        history_card.setProperty("class", "InfoCard")
        history_layout = QVBoxLayout(history_card)
        history_layout.setSpacing(12)
        
        history_title = QLabel("📜 Historique des exports")
        history_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        history_layout.addWidget(history_title)
        
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Référence", "Statut", "Détails"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setMinimumHeight(200)
        
        history_layout.addWidget(self.history_table)
        right_layout.addWidget(history_card)
        
        # Ajouter un espace flexible en bas
        right_layout.addStretch()
        
        right_scroll.setWidget(right_content)
        
        # Assemblage des deux parties
        main_layout.addWidget(left_widget, 40)
        main_layout.addWidget(right_scroll, 60)
        
        return main_widget

    def _on_search_type_changed(self, text):
        """Change les champs de recherche selon le type"""
        is_period = (text == "Période")
        self.search_value.setVisible(not is_period)
        self.date_debut.setVisible(is_period)
        self.date_fin.setVisible(is_period)
    
    def show_export_logs(self):
        """Affiche les logs d'export dans une nouvelle fenêtre"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Logs d'export ASAC")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        text_edit.setStyleSheet("background: #1e1e2e; color: #cdd6f4; border-radius: 12px; padding: 16px;")
        
        # Pour capturer les logs, vous devrez les stocker dans une variable d'instance
        # text_edit.setText(self.export_logs)
        
        layout.addWidget(text_edit)
        
        btn = QPushButton("Fermer")
        btn.setProperty("class", "BtnPrimary")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        
        dialog.exec()

    def display_vehicle_info(self):
        """Affiche les informations du véhicule"""
        self.vehicle_info["immatriculation"].setText(self.vehicle_data.get("immatriculation", "N/A"))
        
        marque_modele = f"{self.vehicle_data.get('marque', '')} {self.vehicle_data.get('modele', '')}".strip()
        self.vehicle_info["marque_modele"].setText(marque_modele or "N/A")
        
        self.vehicle_info["chassis"].setText(self.vehicle_data.get("chassis", "N/A"))
        self.vehicle_info["annee"].setText(str(self.vehicle_data.get("annee", "N/A")))
        self.vehicle_info["energie"].setText(self.vehicle_data.get("energie", "N/A"))
        self.vehicle_info["categorie"].setText(self.vehicle_data.get("categorie", "N/A"))
        self.vehicle_info["owner"].setText(self.vehicle_data.get("owner", "N/A"))
        self.vehicle_info["phone"].setText(self.vehicle_data.get("phone", "N/A"))
        self.vehicle_info["email"].setText(self.vehicle_data.get("email", "N/A"))
        
        prime = self.vehicle_data.get("prime_nette", 0)
        self.vehicle_info["prime_nette"].setText(f"{prime:,.0f} FCFA" if prime else "N/A")
        
        garanties = [
            ("Responsabilité Civile", "amt_rc"),
            ("Défense et Recours", "amt_dr"),
            ("Vol", "amt_vol"),
            ("Vol à main armée", "amt_vb"),
            ("Incendie", "amt_in"),
            ("Bris de glace", "amt_bris"),
            ("Assistance", "amt_ar"),
            ("Dommages Tous Accidents", "amt_dta"),
            ("Individuelle Chauffeur", "amt_ipt")
        ]
        
        self.garanties_table.setRowCount(0)
        for name, key in garanties:
            montant = self.vehicle_data.get(key, 0)
            if montant and float(montant) > 0:
                row = self.garanties_table.rowCount()
                self.garanties_table.insertRow(row)
                self.garanties_table.setItem(row, 0, QTableWidgetItem(name))
                self.garanties_table.setItem(row, 1, QTableWidgetItem(f"{float(montant):,.0f} FCFA"))
        
        self.update_json_preview()
    
    def update_json_preview(self):
        """Met à jour l'aperçu JSON avec validation de conformité"""
        settings = QSettings("LOMETA", "ASAC")
        config = {
            "url": settings.value("url", ""),
            "app_key": settings.value("app_key", ""),
            "username": settings.value("username", ""),
            "office_code": settings.value("office_code", "AG-DLA-001"),
            "org_code": settings.value("org_code", "ACTIVA")
        }
        
        # Valeurs par défaut pour les codes ASAC
        vehicle_category = self.vehicle_data.get("categorie", "01")
        if vehicle_category == "VP":
            vehicle_category = "01"
        elif vehicle_category == "VU":
            vehicle_category = "02"
        elif vehicle_category == "VL":
            vehicle_category = "03"
        elif vehicle_category == "PL":
            vehicle_category = "04"
        
        vehicle_energy = self.vehicle_data.get("energie", "SEES")
        if vehicle_energy == "Essence":
            vehicle_energy = "SEES"
        elif vehicle_energy == "Diesel":
            vehicle_energy = "DIESEL"
        
        vehicle_usage = self.vehicle_data.get("usage", "UV01")
        
        # Construire la requête selon le format exact
        request = {
            "office_code": config.get("office_code", "AG-DLA-001"),
            "organization_code": config.get("org_code", "711"),
            "certificate_type": "cima",
            "channel": "api",
            "productions": [
                {
                    "certificate_variant_code": "BLEUE",
                    "rc": int(self.vehicle_data.get("amt_rc", 0)) or 63784,
                    "police_number": self.vehicle_data.get("numero_police", f"POL-{datetime.now().year}-{self.vehicle_data.get('id', '00000')}"),
                    "starts_at": datetime.now().strftime("%Y-%m-%d"),
                    "ends_at": str(self.vehicle_data.get("date_fin", (datetime.now().replace(year=datetime.now().year+1)).strftime("%Y-%m-%d"))),
                    "customer_name": self.vehicle_data.get("owner", ""),
                    "customer_phone": self.vehicle_data.get("phone", ""),
                    "customer_email": self.vehicle_data.get("email", ""),
                    "customer_postal_code": f"BP {self.vehicle_data.get('city', 'Douala')}",
                    "customer_type": "TSPM",
                    "insured_name": self.vehicle_data.get("owner", ""),
                    "insured_phone": self.vehicle_data.get("phone", ""),
                    "insured_email": self.vehicle_data.get("email", ""),
                    "insured_postal_code": f"BP {self.vehicle_data.get('city', 'Douala')}",
                    "licence_plate": self.vehicle_data.get("immatriculation", "").upper(),
                    "vehicle_chassis": self.vehicle_data.get("chassis", f"VF1{self.vehicle_data.get('id', '00000')}ABCD123456"),
                    "vehicle_brand": self.vehicle_data.get("marque", "").upper(),
                    "vehicle_model": self.vehicle_data.get("modele", "").upper(),
                    "vehicle_category": vehicle_category,
                    "vehicle_genre": self.vehicle_data.get("genre", "GV04"),
                    "vehicle_type": self.vehicle_data.get("type", "TV10"),
                    "vehicule_usage": vehicle_usage,
                    "vehicle_energy": vehicle_energy,
                    "nb_of_seats": int(self.vehicle_data.get("places", 5)),
                    "fiscal_power": int(self.vehicle_data.get("fiscal_power", 5)),
                    "circulation_zone": self.vehicle_data.get("zone", "A").upper(),
                    "driver_name": self.vehicle_data.get("driver_name", self.vehicle_data.get("owner", "")),
                    "driver_birthdate": self.vehicle_data.get("driver_birthdate", "1990-01-01"),
                    "driver_licence_issued_at": self.vehicle_data.get("licence_issued_at", "2010-01-01"),
                    "vehicle_has_trailer": bool(self.vehicle_data.get("has_trailer", False))
                }
            ]
        }
        
        # Validation de conformité
        try:
            compliance = AsacDataValidator.get_compliance_report(request)
        except ImportError:
            # Si le validateur n'existe pas, créer un rapport simple
            compliance = {"is_compliant": True, "errors_count": 0, "warnings_count": 0, "errors": [], "warnings": [], "compliance_rate": 100}
        
        # Ajouter le rapport de conformité à l'affichage
        preview_text = json.dumps(request, indent=2, default=str, ensure_ascii=False)
        
        if not compliance.get("is_compliant", True):
            compliance_text = f"\n\n{'='*60}\n⚠️ RAPPORT DE CONFORMITÉ\n{'='*60}\n"
            compliance_text += f"Taux de conformité: {compliance.get('compliance_rate', 0)}%\n"
            compliance_text += f"❌ Erreurs ({compliance.get('errors_count', 0)}):\n"
            for err in compliance.get("errors", [])[:10]:
                compliance_text += f"  {err}\n"
            if compliance.get("warnings"):
                compliance_text += f"\n⚠️ Avertissements ({compliance.get('warnings_count', 0)}):\n"
                for warn in compliance.get("warnings", [])[:5]:
                    compliance_text += f"  {warn}\n"
            
            preview_text += compliance_text
            
            # Mettre à jour le panneau de conformité
            if hasattr(self, 'compliance_status'):
                self.compliance_status.setText(f"⚠️ Conformité: {compliance.get('compliance_rate', 0)}% - {compliance.get('errors_count', 0)} erreur(s)")
                self.compliance_details.setText(compliance_text)
                self.status_label.setText(f"⚠️ Conformité: {compliance.get('compliance_rate', 0)}%")
                self.status_icon.setStyleSheet("color: #ef4444; font-size: 12px;")
        else:
            if hasattr(self, 'compliance_status'):
                self.compliance_status.setText("✅ Données conformes au format ASAC")
                self.compliance_details.clear()
                self.status_label.setText("✅ Données conformes")
                self.status_icon.setStyleSheet("color: #10b981; font-size: 12px;")
        
        self.json_preview.setText(preview_text)

    def copy_json(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.json_preview.toPlainText())
        self._show_notification("Copie réussie", "✅ JSON copié dans le presse-papier", "info")
    
    def clear_search(self):
        self.search_value.clear()
        self.date_debut.clear()
        self.date_fin.clear()
        self.results_table.setRowCount(0)
        self.receive_status.setText("")
    
    def load_config(self):
        settings = QSettings("LOMETA", "ASAC")
        url = settings.value("url", "")
        app_key = settings.value("app_key", "")
        username = settings.value("username", "")
        password = settings.value("password", "")
        
        if url and app_key and username and password:
            self.config_status.setText("Connecté")
            self.config_status.setProperty("class", "StatusBadge StatusSuccess")
            self.server_info_label.setText(f"Serveur: {url}")
            self.server_status_label.setText("Connecté")
            self.server_indicator.setStyleSheet("font-size: 12px; color: #10b981;")
        else:
            self.config_status.setText("Non configuré")
            self.config_status.setProperty("class", "StatusBadge StatusError")
            self.server_info_label.setText("Configuration requise avant export")
            self.server_status_label.setText("Non configuré")
            self.server_indicator.setStyleSheet("font-size: 12px; color: #f59e0b;")
        
        self.config_status.style().unpolish(self.config_status)
        self.config_status.style().polish(self.config_status)
    
    def open_config(self):
        dialog = ConfigDialog(self)
        if dialog.exec():
            self.load_config()
            self.update_json_preview()
    
    # def start_export(self):
    #     settings = QSettings("LOMETA", "ASAC")
    #     config = {
    #         "url": settings.value("url", ""),
    #         "app_key": settings.value("app_key", ""),
    #         "username": settings.value("username", ""),
    #         "password": settings.value("password", ""),
    #         "email": settings.value("email", ""),
    #         "office_code": settings.value("office_code", "AG-DLA-001"),
    #         "org_code": settings.value("org_code", "ACTIVA")
    #     }
        
    #     if not config["url"] or not config["app_key"] or not config["username"] or not config["password"]:
    #         QMessageBox.warning(self, "Configuration manquante", 
    #             "Veuillez configurer le serveur ASAC avec l'URL, l'App Key, le nom d'utilisateur et le mot de passe avant d'exporter.")
    #         self.open_config()
    #         return
        
    #     self.export_btn.setEnabled(False)
    #     self.export_btn.setText("⏳ Export en cours...")
    #     self.export_progress.setVisible(True)
    #     self.export_progress.setValue(0)
        
    #     # Effacer l'affichage précédent du token
    #     self.token_display.clear()
    #     self.token_name_label.setText("Nom: -")
    #     self.token_expires_label.setText("Expire: -")
        
    #     self.export_worker = ExportWorker(self.vehicle_data, config)
    #     self.export_worker.progress.connect(self.on_export_progress)
    #     self.export_worker.finished.connect(self.on_export_finished)
    #     self.export_worker.token_received.connect(self.on_token_received)  # Nouvelle connexion
    #     self.export_worker.start()

    def start_export(self):
        settings = QSettings("LOMETA", "ASAC")
        config = {
            "url": settings.value("url", ""),
            "app_key": settings.value("app_key", ""),
            "username": settings.value("username", ""),
            "password": settings.value("password", ""),
            "email": settings.value("email", ""),
            "office_code": settings.value("office_code", "AG-DLA-001"),
            "org_code": settings.value("org_code", "ACTIVA")
        }
        
        if not config["url"] or not config["app_key"] or not config["username"] or not config["password"]:
            QMessageBox.warning(self, "Configuration manquante", 
                "Veuillez configurer le serveur ASAC avec l'URL, l'App Key, le nom d'utilisateur et le mot de passe avant d'exporter.")
            self.open_config()
            return
        
        self.export_btn.setEnabled(False)
        self.export_btn.setText("⏳ Export en cours...")
        self.export_progress.setVisible(True)
        self.export_progress.setValue(0)
        
        # Effacer l'affichage précédent
        self.token_display.clear()
        self.token_name_label.setText("Nom: -")
        self.token_expires_label.setText("Expire: -")
        self.received_preview.clear()  # Effacer l'aperçu précédent
        
        self.export_worker = ExportWorker(self.vehicle_data, config)
        self.export_worker.progress.connect(self.on_export_progress)
        self.export_worker.finished.connect(self.on_export_finished)
        self.export_worker.token_received.connect(self.on_token_received)
        self.export_worker.log_captured.connect(self.on_log_captured)  # Nouvelle connexion
        self.export_worker.start()

    def on_log_captured(self, log_text):
        """Affiche les logs dans la zone d'aperçu"""
        current_text = self.received_preview.toPlainText()
        new_text = current_text + log_text
        self.received_preview.setText(new_text)
        # Scroll en bas
        scrollbar = self.received_preview.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_token_received(self, token_data):
        """Affiche le token reçu du serveur"""
        token = token_data.get("token", "")
        token_name = token_data.get("token_name", "")
        expires_at = token_data.get("expires_at", "")
        
        # Afficher le token formaté
        display_text = f"Token: {token}\n\n"
        display_text += f"Nom du token: {token_name}\n"
        display_text += f"Expiration: {expires_at}"
        
        self.token_display.setText(display_text)
        self.token_name_label.setText(f"Nom: {token_name}")
        self.token_expires_label.setText(f"Expire: {expires_at}")
        
        self._show_notification(
            "Token reçu",
            f"✅ Token d'authentification reçu avec succès!\nExpire le: {expires_at}",
            "success"
        )
    
    def on_export_progress(self, value, message):
        self.export_progress.setValue(value)
        self.status_label.setText(message)
    
    def on_export_finished(self, success, response, error):
        """Termine l'export et gère les erreurs"""
        self.export_btn.setEnabled(True)
        self.export_btn.setText("📤 Exporter vers ASAC")
        self.export_progress.setVisible(False)
        
        if success:
            reference = response.get("data", {}).get("reference", response.get("reference", "N/A"))
            self.save_to_history(reference, response)
            self.last_certificate_url = response.get("data", {}).get("download_link", 
                                    response.get("download_link", ""))
            self.view_certificate_btn.setVisible(True)
            
            self._show_notification(
                "Export réussi",
                f"✅ Le véhicule {self.vehicle_data.get('immatriculation', '')} a été exporté avec succès!\nRéférence: {reference}",
                "success",
                response
            )
        else:
            # Analyser l'erreur ASAC
            error_details = ""
            try:
                # Si error est une chaîne JSON
                if isinstance(error, str) and error.startswith('{'):
                    error_data = json.loads(error)
                    if 'errors' in error_data:
                        error_details = "\n".join([e.get('detail', '') for e in error_data['errors']])
                    elif 'detail' in error_data:
                        error_details = error_data['detail']
                elif isinstance(error, dict) and 'errors' in error:
                    error_details = "\n".join([e.get('detail', '') for e in error['errors']])
            except:
                pass
            
            if error_details:
                self._show_notification("Erreur de validation", f"❌ {error_details}", "error")
            else:
                self._show_notification("Erreur d'export", f"❌ L'export a échoué.\n\n{error}", "error")
        
        self.refresh_history()

    
    def start_receive(self):
        """Démarre la réception des données depuis ASAC"""
        settings = QSettings("LOMETA", "ASAC")
        config = {
            "url": settings.value("url", ""),
            "app_key": settings.value("app_key", ""),
            "username": settings.value("username", ""),
            "password": settings.value("password", ""),
            "email": settings.value("email", "")
        }
        
        if not config["url"] or not config["app_key"] or not config["username"] or not config["password"]:
            QMessageBox.warning(self, "Configuration manquante", "Veuillez configurer le serveur ASAC avec l'URL, l'App Key, le nom d'utilisateur et le mot de passe.")
            self.open_config()
            return
        
        search_type = self.search_type.currentText()
        search_params = {"type": "police"}
        
        if search_type == "Numéro de police":
            if not self.search_value.text():
                QMessageBox.warning(self, "Erreur", "Veuillez entrer un numéro de police")
                return
            search_params = {"type": "police", "value": self.search_value.text()}
        elif search_type == "Immatriculation":
            if not self.search_value.text():
                QMessageBox.warning(self, "Erreur", "Veuillez entrer une immatriculation")
                return
            search_params = {"type": "immatriculation", "value": self.search_value.text()}
        elif search_type == "Période":
            if not self.date_debut.text() or not self.date_fin.text():
                QMessageBox.warning(self, "Erreur", "Veuillez entrer une période valide")
                return
            search_params = {
                "type": "periode",
                "date_debut": self.date_debut.text(),
                "date_fin": self.date_fin.text()
            }

        self.last_search_params = search_params
        settings = QSettings("LOMETA", "ASAC")
        settings.setValue("last_search_params", json.dumps(search_params))
        
        self.search_btn.setEnabled(False)
        self.search_btn.setText("⏳ Recherche en cours...")
        self.receive_progress.setVisible(True)
        self.receive_progress.setValue(0)
        
        self.receive_worker = ReceiveWorker(config, search_params)
        self.receive_worker.progress.connect(self.on_receive_progress)
        self.receive_worker.finished.connect(self.on_receive_finished)
        self.receive_worker.log_captured.connect(self.on_log_captured)
        self.receive_worker.start()
    
    def on_receive_progress(self, value, message):
        self.receive_progress.setValue(value)
        self.receive_status.setText(message)
        self.status_label.setText(message)
    

    def on_receive_finished(self, success, data, error):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("🔍 Rechercher")
        self.receive_progress.setVisible(False)
        
        if success:
            # Afficher l'aperçu des données reçues
            self.received_preview.setText(json.dumps(data, indent=2, default=str, ensure_ascii=False))
            
            attestations = data.get("data", []) if isinstance(data, dict) else data
            if isinstance(attestations, dict):
                attestations = [attestations]
            
            # Remplir le tableau
            self._populate_results_table(attestations)
            
            # Mettre à jour les stats
            self.update_results_stats()
            
            # Sauvegarder les paramètres de recherche
            self.last_search_params = self.search_params if hasattr(self, 'search_params') else None
            
            if attestations:
                self._show_notification(
                    "Données reçues",
                    f"✅ {len(attestations)} attestation(s) trouvée(s)",
                    "success",
                    {"count": len(attestations), "data": attestations[:5]}
                )
            else:
                self._show_notification("Aucun résultat", "🔍 Aucune attestation trouvée pour ces critères", "warning")
        else:
            self.received_preview.setText(f"❌ Erreur: {error}")
            self.results_table.setRowCount(0)
            self.update_results_stats()
            self._show_notification("Erreur de réception", f"❌ Échec de la réception: {error}", "error")
    
    def view_attestation_details(self, attestation):
        """Affiche les détails d'une attestation"""
        content = json.dumps(attestation, indent=2, default=str, ensure_ascii=False)
        dialog = NotificationDialog("Détails de l'attestation", "Informations complètes", attestation, self)
        dialog.exec()
    
    def _show_notification(self, title, message, level="info", details=None):
        """Affiche une notification"""
        dialog = NotificationDialog(title, message, details, self)
        dialog.show()
        
        self.status_label.setText(message)
        if level == "success":
            self.status_icon.setStyleSheet("color: #10b981; font-size: 12px;")
        elif level == "error":
            self.status_icon.setStyleSheet("color: #ef4444; font-size: 12px;")
        elif level == "warning":
            self.status_icon.setStyleSheet("color: #f59e0b; font-size: 12px;")
        else:
            self.status_icon.setStyleSheet("color: #3b82f6; font-size: 12px;")
        
        QTimer.singleShot(5000, self.reset_status)
    
    def reset_status(self):
        self.status_label.setText("Prêt")
        self.status_icon.setStyleSheet("color: #f59e0b; font-size: 12px;")
    
    def copy_token(self):
        """Copie le token dans le presse-papier"""
        token_text = self.token_display.toPlainText()
        if token_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(token_text)
            self._show_notification("Copie réussie", "✅ Token copié dans le presse-papier", "info")
        else:
            self._show_notification("Aucun token", "⚠️ Aucun token à copier", "warning")

    def save_to_history(self, reference, response):
        settings = QSettings("LOMETA", "ASAC")
        history = settings.value(f"history_{self.vehicle_data.get('immatriculation', 'unknown')}", [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except:
                history = []
        
        record = {
            "date": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"),
            "reference": reference,
            "status": "success",
            "response": response,
            "timestamp": QDateTime.currentDateTime().toSecsSinceEpoch()
        }
        
        history.insert(0, record)
        history = history[:20]
        settings.setValue(f"history_{self.vehicle_data.get('immatriculation', 'unknown')}", 
                         json.dumps(history, default=str))
    
    def toggle_auto_refresh(self, state):
        """Active/désactive le rafraîchissement automatique"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        if state == Qt.Checked:
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.auto_refresh_search)
            self.refresh_timer.start(30000)

    def apply_filters(self):
        """Applique les filtres aux résultats (statut, type certificat, variante)"""
        if not hasattr(self, 'current_attestations') or not self.current_attestations:
            return
        
        filtered_attestations = []
        
        for att in self.current_attestations:
            # Filtrer par statut
            status_filter = self.filter_status.currentText()
            if status_filter != "Tous":
                att_status = att.get("statut", att.get("status", "INCONNU"))
                if att_status != status_filter:
                    continue
            
            # Filtrer par type certificat
            cert_filter = self.filter_cert_type.currentText()
            if cert_filter != "Tous":
                att_cert = att.get("certificate_type", att.get("type", ""))
                if att_cert != cert_filter:
                    continue
            
            # Filtrer par variante
            variant_filter = self.filter_variant.currentText()
            if variant_filter != "Tous":
                att_variant = att.get("certificate_variant_code", att.get("variant", ""))
                if att_variant != variant_filter:
                    continue
            
            filtered_attestations.append(att)
        
        self._populate_results_table(filtered_attestations)
        self.update_results_stats()
        
        self._show_notification(
            "Filtres appliqués",
            f"🔍 {len(filtered_attestations)}/{len(self.current_attestations)} attestations affichées",
            "info"
        )

    def export_results_to_csv(self):
        """Exporte les résultats en CSV"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Aucune donnée", "Il n'y a aucune donnée à exporter.")
            return
        
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", f"attestations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            "CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # En-têtes
                headers = ["Numéro Police", "Immatriculation", "Propriétaire", "Téléphone", 
                        "Email", "Date Début", "Date Fin", "Statut", "Type Certificat", "Variante"]
                writer.writerow(headers)
                
                # Données
                for row in range(self.results_table.rowCount()):
                    police = self.results_table.item(row, 0).text() if self.results_table.item(row, 0) else ""
                    immat = self.results_table.item(row, 1).text() if self.results_table.item(row, 1) else ""
                    proprietaire = self.results_table.item(row, 2).text() if self.results_table.item(row, 2) else ""
                    
                    periode = self.results_table.item(row, 3).text() if self.results_table.item(row, 3) else ""
                    dates = periode.split(" → ")
                    date_debut = dates[0] if len(dates) > 0 else ""
                    date_fin = dates[1] if len(dates) > 1 else ""
                    
                    statut = self.results_table.item(row, 4).text() if self.results_table.item(row, 4) else ""
                    
                    # Récupérer les données supplémentaires depuis l'attestation source
                    att = self.current_attestations[row] if hasattr(self, 'current_attestations') and row < len(self.current_attestations) else {}
                    telephone = att.get("customer_phone", att.get("phone", ""))
                    email = att.get("customer_email", att.get("email", ""))
                    cert_type = att.get("certificate_type", att.get("type", ""))
                    variant = att.get("certificate_variant_code", att.get("variant", ""))
                    
                    writer.writerow([police, immat, proprietaire, telephone, email, 
                                    date_debut, date_fin, statut, cert_type, variant])
            
            self._show_notification("Export réussi", f"✅ {len(self.results_table.rowCount())} attestations exportées en CSV", "success")
            
        except Exception as e:
            self._show_notification("Erreur", f"❌ Erreur lors de l'export: {str(e)}", "error")

    def export_results_to_json(self):
        """Exporte les résultats en JSON"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Aucune donnée", "Il n'y a aucune donnée à exporter.")
            return
        
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en JSON", f"attestations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            "JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            results = []
            for row in range(self.results_table.rowCount()):
                police = self.results_table.item(row, 0).text() if self.results_table.item(row, 0) else ""
                immat = self.results_table.item(row, 1).text() if self.results_table.item(row, 1) else ""
                proprietaire = self.results_table.item(row, 2).text() if self.results_table.item(row, 2) else ""
                
                periode = self.results_table.item(row, 3).text() if self.results_table.item(row, 3) else ""
                dates = periode.split(" → ")
                date_debut = dates[0] if len(dates) > 0 else ""
                date_fin = dates[1] if len(dates) > 1 else ""
                
                statut = self.results_table.item(row, 4).text() if self.results_table.item(row, 4) else ""
                
                # Récupérer l'attestation source
                att = self.current_attestations[row] if hasattr(self, 'current_attestations') and row < len(self.current_attestations) else {}
                
                results.append({
                    "police_number": police,
                    "licence_plate": immat,
                    "owner": proprietaire,
                    "customer_phone": att.get("customer_phone", att.get("phone", "")),
                    "customer_email": att.get("customer_email", att.get("email", "")),
                    "start_date": date_debut,
                    "end_date": date_fin,
                    "status": statut,
                    "certificate_type": att.get("certificate_type", att.get("type", "")),
                    "certificate_variant_code": att.get("certificate_variant_code", att.get("variant", "")),
                    "full_data": att
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "export_date": datetime.now().isoformat(),
                    "total_count": len(results),
                    "attestations": results
                }, f, indent=2, ensure_ascii=False, default=str)
            
            self._show_notification("Export réussi", f"✅ {len(results)} attestations exportées en JSON", "success")
            
        except Exception as e:
            self._show_notification("Erreur", f"❌ Erreur lors de l'export: {str(e)}", "error")

    def filter_results(self, text):
        """Filtre les résultats dans le tableau en temps réel"""
        if not text or text.strip() == "":
            # Afficher toutes les lignes
            for row in range(self.results_table.rowCount()):
                self.results_table.setRowHidden(row, False)
            # Mettre à jour les stats avec le nombre visible
            self.update_results_stats()
            return
        
        text_lower = text.lower().strip()
        visible_count = 0
        
        for row in range(self.results_table.rowCount()):
            show = False
            # Rechercher dans les colonnes: Police, Immatriculation, Propriétaire
            for col in range(3):
                item = self.results_table.item(row, col)
                if item and text_lower in item.text().lower():
                    show = True
                    break
            
            self.results_table.setRowHidden(row, not show)
            if show:
                visible_count += 1
        
        # Mettre à jour les stats avec le nombre visible
        total = self.results_table.rowCount()
        hidden = total - visible_count
        self.stats_total.setText(f"📊 Total: {visible_count}/{total}")
        
        # Mettre à jour les compteurs de statut sur les lignes visibles uniquement
        valid = 0
        expired = 0
        for row in range(self.results_table.rowCount()):
            if not self.results_table.isRowHidden(row):
                statut = self.results_table.item(row, 4).text() if self.results_table.item(row, 4) else ""
                if "VALIDE" in statut or "Succès" in statut:
                    valid += 1
                elif "EXPIRE" in statut or "Expiré" in statut:
                    expired += 1
        
        self.stats_valid.setText(f"✅ Valides: {valid}")
        self.stats_expired.setText(f"⏰ Expirés: {expired}")

    def _populate_results_table(self, attestations):
        """Remplit le tableau des résultats avec les attestations"""
        self.results_table.setRowCount(0)
        
        for i, att in enumerate(attestations):
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # Police
            police = att.get("numero_police", att.get("police_number", "N/A"))
            self.results_table.setItem(row, 0, QTableWidgetItem(str(police)))
            
            # Immatriculation
            immat = att.get("immatriculation", att.get("licence_plate", "N/A"))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(immat)))
            
            # Propriétaire
            proprietaire = att.get("proprietaire", att.get("customer_name", att.get("owner", "N/A")))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(proprietaire)))
            
            # Période
            date_debut = att.get("date_debut", att.get("starts_at", ""))
            date_fin = att.get("date_fin", att.get("ends_at", ""))
            periode = f"{date_debut} → {date_fin}" if date_debut or date_fin else "N/A"
            self.results_table.setItem(row, 3, QTableWidgetItem(periode))
            
            # Statut avec badge coloré
            statut = att.get("statut", att.get("status", "INCONNU"))
            status_item = QTableWidgetItem()
            
            if statut == "VALIDE" or statut == "SUCCESS":
                status_item.setText("✅ Valide")
                status_item.setForeground(QColor("#10b981"))
            elif statut == "EN_ATTENTE" or statut == "PENDING":
                status_item.setText("⏳ En attente")
                status_item.setForeground(QColor("#f59e0b"))
            elif statut == "REJETE" or statut == "REJECTED":
                status_item.setText("❌ Rejeté")
                status_item.setForeground(QColor("#ef4444"))
            elif statut == "EXPIRE" or statut == "EXPIRED":
                status_item.setText("⚠️ Expiré")
                status_item.setForeground(QColor("#ef4444"))
            else:
                status_item.setText(f"📄 {statut}")
            
            self.results_table.setItem(row, 4, status_item)
            
            # Bouton Voir détails
            view_btn = QPushButton("👁️ Détails")
            view_btn.setProperty("class", "BtnSecondary")
            view_btn.setFixedSize(80, 28)
            view_btn.clicked.connect(lambda checked, a=att: self.view_attestation_details(a))
            self.results_table.setCellWidget(row, 5, view_btn)
        
        # Sauvegarder les attestations pour les filtres
        self.current_attestations = attestations

    def select_all_results(self, state):
        """Sélectionne/désélectionne toutes les lignes"""
        self.results_table.setSelectionMode(QTableWidget.MultiSelection)
        if state == Qt.Checked:
            self.results_table.selectAll()
            self.bulk_import_btn.setEnabled(True)
        else:
            self.results_table.clearSelection()
            self.bulk_import_btn.setEnabled(False)

    def bulk_import(self):
        """Importe les attestations sélectionnées"""
        selected_rows = set()
        for item in self.results_table.selectedItems():
            selected_rows.add(item.row())
        if selected_rows:
            QMessageBox.information(self, "Import en masse", f"{len(selected_rows)} attestation(s) sélectionnée(s)")

    def update_results_stats(self):
        """Met à jour les statistiques"""
        total = self.results_table.rowCount()
        valid = 0
        expired = 0
        for row in range(total):
            statut = self.results_table.item(row, 4).text() if self.results_table.item(row, 4) else ""
            if "VALIDE" in statut:
                valid += 1
            elif "EXPIRE" in statut:
                expired += 1
        self.stats_total.setText(f"📊 Total: {total}")
        self.stats_valid.setText(f"✅ Valides: {valid}")
        self.stats_expired.setText(f"⏰ Expirés: {expired}")

    def refresh_history(self):
        settings = QSettings("LOMETA", "ASAC")
        history = settings.value(f"history_{self.vehicle_data.get('immatriculation', 'unknown')}", [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except:
                history = []
        
        self.history_table.setRowCount(len(history))
        for i, record in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(record.get("date", "")))
            self.history_table.setItem(i, 1, QTableWidgetItem(record.get("reference", "N/A")))
            
            status_item = QTableWidgetItem("✅ Succès")
            status_item.setForeground(QColor("#10b981"))
            self.history_table.setItem(i, 2, status_item)
            
            btn = QPushButton("👁️ Détails")
            btn.setProperty("class", "BtnSecondary")
            btn.setFixedSize(80, 28)
            btn.clicked.connect(lambda checked, r=record: self.show_details(r))
            self.history_table.setCellWidget(i, 3, btn)
    
    def clear_logs(self):
        """Efface les logs affichés"""
        self.received_preview.clear()
        self._show_notification("Logs effacés", "✅ Les logs ont été effacés", "info")

    def show_details(self, record):
        content = json.dumps(record, indent=2, default=str, ensure_ascii=False)
        dialog = QDialog(self)
        dialog.setWindowTitle("Détails de l'export")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(MODERN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text = QTextEdit()
        text.setPlainText(content)
        text.setFont(QFont("Courier New", 10))
        text.setStyleSheet("background: #1e1e2e; color: #cdd6f4; border-radius: 12px; padding: 16px;")
        
        layout.addWidget(text)
        
        btn = QPushButton("Fermer")
        btn.setProperty("class", "BtnPrimary")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        
        dialog.exec()
    
    def _create_compliance_panel(self):
        """Crée le panneau de rapport de conformité"""
        panel = QFrame()
        panel.setProperty("class", "InfoCard")
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        title = QLabel("📋 Rapport de conformité ASAC")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #3b82f6;")
        layout.addWidget(title)
        
        self.compliance_status = QLabel("En attente de validation...")
        self.compliance_status.setWordWrap(True)
        self.compliance_status.setStyleSheet("font-size: 12px; padding: 8px; background: #f8fafc; border-radius: 10px;")
        layout.addWidget(self.compliance_status)
        
        self.compliance_details = QTextEdit()
        self.compliance_details.setReadOnly(True)
        self.compliance_details.setMaximumHeight(150)
        self.compliance_details.setStyleSheet("font-size: 11px; font-family: monospace;")
        self.compliance_details.setVisible(False)
        layout.addWidget(self.compliance_details)
        
        toggle_btn = QPushButton("Afficher les détails")
        toggle_btn.setProperty("class", "BtnSecondary")
        toggle_btn.setFixedSize(120, 30)
        toggle_btn.clicked.connect(lambda: self.compliance_details.setVisible(not self.compliance_details.isVisible()))
        layout.addWidget(toggle_btn, alignment=Qt.AlignRight)
        
        return panel

    def apply_shadow(self, widget, blur_radius=15, offset_x=0, offset_y=4, color=QColor(0, 0, 0, 50)):
        """Applique une ombre portée à un widget"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setXOffset(offset_x)
        shadow.setYOffset(offset_y)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    def view_certificate(self):
        if hasattr(self, 'last_certificate_url') and self.last_certificate_url:
            QDesktopServices.openUrl(QUrl(self.last_certificate_url))
        else:
            QMessageBox.information(self, "Information", "Aucune attestation disponible pour cet export")