

# devis_printer.py - Version Premium avec fonctionnalités avancées
import os
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PySide6.QtCore import Qt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import math
import qrcode
from io import BytesIO

try:
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from reportlab.graphics import renderPDF
    HAS_GRAPHICS = True
except ImportError:
    HAS_GRAPHICS = False


class DevisPrinter:
    """Générateur et imprimeur de devis d'assurance - Version Premium"""
    
    # Constantes de mise en page
    MARGIN_TOP = 100
    MARGIN_BOTTOM = 60
    MARGIN_LEFT = 40
    MARGIN_RIGHT = 40
    
    def __init__(self, vehicle_data, export_dir=None, company_name="AMS ASSURANCES"):
        """
        Initialise l'imprimeur de devis
        
        Args:
            vehicle_data (dict): Données du véhicule et du devis
            export_dir (str): Dossier d'export des PDF
            company_name (str): Nom de la compagnie
        """
        self.vehicle_data = vehicle_data
        self.company_name = company_name
        self.export_dir = export_dir or os.path.expanduser("~/Documents/Devis_Assurance")
        print(f"voici les données du véhicule: {self.vehicle_data}")
        
        # Créer le dossier d'export
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Chemin du logo
        self.logo_path = self._find_logo()
        
        # Couleurs personnalisées
        self.colors = {
            'primary': colors.HexColor("#1e293b"),
            'secondary': colors.HexColor("#2563eb"),
            'accent': colors.HexColor("#f59e0b"),
            'success': colors.HexColor("#10b981"),
            'danger': colors.HexColor("#ef4444"),
            'warning': colors.HexColor("#f59e0b"),
            'info': colors.HexColor("#3b82f6"),
            'text': colors.HexColor("#1e293b"),
            'text_light': colors.HexColor("#64748b"),
            'text_muted': colors.HexColor("#94a3b8"),
            'border': colors.HexColor("#e2e8f0"),
            'background': colors.HexColor("#f8fafc"),
            'white': colors.white,
            'black': colors.black,
        }
        
        # Styles de police
        self.fonts = {
            'title': 'Helvetica-Bold',
            'subtitle': 'Helvetica-Bold',
            'body': 'Helvetica',
            'body_bold': 'Helvetica-Bold',
            'small': 'Helvetica',
            'small_bold': 'Helvetica-Bold',
        }
    
    def _find_logo(self):
        """Trouve le chemin du logo"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "static", "logo.png"),
            os.path.join(os.getcwd(), "addons", "Automobiles", "static", "logo.png"),
            os.path.join(os.getcwd(), "static", "logo.png"),
            os.path.join(os.path.expanduser("~"), "Documents", "AMS", "logo.png"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def draw_header(self, c, width, height):
        """Dessine l'en-tête du devis avec design amélioré"""
        # Rectangle de fond d'en-tête
        c.setFillColor(self.colors['background'])
        c.rect(0, height - 110, width, 110, fill=1, stroke=0)
        
        # Ligne décorative en haut
        c.setFillColor(self.colors['secondary'])
        c.rect(0, height - 3, width, 3, fill=1, stroke=0)
        
        # Logo
        logo_size = 55
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = ImageReader(self.logo_path)
                c.drawImage(logo, 35, height - 95, width=logo_size, height=logo_size, mask='auto')
            except Exception as e:
                print(f"Erreur chargement logo: {e}")
                self._draw_fallback_logo(c, 35, height - 95, logo_size)
        else:
            self._draw_fallback_logo(c, 35, height - 95, logo_size)
        
        # Titre de l'entreprise
        c.setFillColor(self.colors['primary'])
        c.setFont("Helvetica-Bold", 24)
        c.drawString(105, height - 65, self.company_name)
        
        # Slogan
        c.setFont("Helvetica", 9)
        c.setFillColor(self.colors['text_light'])
        c.drawString(105, height - 80, "Assurance de confiance depuis 2020")
        
        # Ligne décorative sous le titre
        c.setStrokeColor(self.colors['secondary'])
        c.setLineWidth(2)
        c.line(105, height - 85, 280, height - 85)
        
        # Informations du document (alignées à droite)
        c.setFont("Helvetica", 8)
        c.setFillColor(self.colors['text_light'])
        
        # Numéro de devis
        vehicle_id = self.vehicle_data.get('id', '001')
        devis_num = f"DEV-{datetime.now().strftime('%Y%m%d')}-{str(vehicle_id).zfill(3)}"
        c.drawRightString(width - 35, height - 55, f"N° DEVIS : {devis_num}")
        
        # Date
        date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        c.drawRightString(width - 35, height - 68, f"Date d'émission : {date_str}")
        
        # Validité
        validite = self.vehicle_data.get('validite_jours', 30)
        c.drawRightString(width - 35, height - 81, f"Validité : {validite} jours")
        
        # Version du document
        c.drawRightString(width - 35, height - 94, "Version 1.0")
        
        # Ligne de séparation
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(1)
        c.line(35, height - 102, width - 35, height - 102)
    
    def _draw_fallback_logo(self, c, x, y, size):
        """Dessine un logo de fallback"""
        c.setFillColor(self.colors['secondary'])
        c.roundRect(x, y, size, size, 12, fill=1, stroke=0)
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica-Bold", 24)
        c.drawString(x + size/2 - 12, y + size/2 - 8, "A")
    
    def draw_info_card(self, c, x, y, width, height, title, items, icon="📄", bg_color=None):
        """Dessine une carte d'information stylisée"""
        if bg_color is None:
            bg_color = self.colors['white']
        
        # Ombre portée (simulée)
        c.setFillColor(colors.HexColor("#00000010"))
        c.roundRect(x + 2, y - 2, width, height, 12, fill=1, stroke=0)
        
        # Fond de la carte
        c.setFillColor(bg_color)
        c.roundRect(x, y, width, height, 12, fill=1, stroke=0)
        
        # Bordure
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(1)
        c.roundRect(x, y, width, height, 12, fill=0, stroke=1)
        
        # En-tête de la carte
        c.setFillColor(self.colors['secondary'])
        c.roundRect(x, y + height - 38, width, 38, 12, fill=1, stroke=0)
        c.roundRect(x, y + height - 38, width, 20, 12, fill=1, stroke=0)
        
        # Titre avec icône
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 15, y + height - 24, f"{icon} {title}")
        
        # Lignes d'information
        c.setFillColor(self.colors['text'])
        c.setFont("Helvetica", 9)
        y_pos = y + height - 55
        line_height = 20
        
        for i, (label, value) in enumerate(items):
            if i >= 6:
                break
            # Label
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 8)
            c.drawString(x + 15, y_pos - i * line_height, label)
            # Valeur
            c.setFillColor(self.colors['text'])
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x + 130, y_pos - i * line_height, str(value))
    
    def draw_garanties_table(self, c, x, y, width):
        """Dessine le tableau des garanties avec design amélioré"""
        # Titre avec icône
        c.setFillColor(self.colors['primary'])
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x, y, "🛡️ GARANTIES SOUSCRITES")
        
        # Ligne décorative sous le titre
        c.setStrokeColor(self.colors['secondary'])
        c.setLineWidth(2)
        c.line(x, y - 6, x + 80, y - 6)
        
        # En-têtes du tableau
        table_y = y - 28
        c.setFillColor(self.colors['secondary'])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 10, table_y, "Garantie")
        c.drawString(x + 180, table_y, "Montant (FCFA)")
        c.drawRightString(x + width - 10, table_y, "Statut")
        
        # Ligne de séparation
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(0.5)
        c.line(x, table_y - 5, x + width, table_y - 5)
        
        # Remplir le tableau
        c.setFont("Helvetica", 9)
        y_pos = table_y - 22
        row_height = 20
        
        total_brut = 0
        garanties_active = 0
        
        # Mapping des garanties
        garanties_mapping = [
            ("Responsabilité Civile", 'amt_rc', 'check_rc'),
            ("Défense et Recours", 'amt_dr', 'check_dr'),
            ("Vol du véhicule", 'amt_vol', 'check_vol'),
            ("Vol à Main Armée", 'amt_vb', 'check_vb'),
            ("Incendie", 'amt_ipt', 'check_ipt'),
            ("Bris de Glaces", 'amt_bris', 'check_bris'),
            ("Assistance Panne", 'amt_ar', 'check_ar'),
            ("Dommages Tous Accidents", 'amt_dta', 'check_dta'),
            ("Individuelle Chauffeur", 'amt_in_garantie', 'check_in_garantie'),
        ]
        
        for name, amount_key, check_key in garanties_mapping:
            amount = self.vehicle_data.get(amount_key, 0)
            checked = self.vehicle_data.get(check_key, False)
            
            if amount > 0 or checked:
                # Alternance des couleurs de fond
                if garanties_active % 2 == 0:
                    c.setFillColor(self.colors['background'])
                    c.rect(x, y_pos - 12, width, row_height + 2, fill=1, stroke=0)
                
                # Nom de la garantie
                c.setFillColor(self.colors['text'])
                c.setFont("Helvetica", 9)
                c.drawString(x + 10, y_pos, name)
                
                # Montant
                c.drawString(x + 180, y_pos, f"{int(amount):,}".replace(",", " "))
                
                # Statut
                if checked and amount > 0:
                    c.setFillColor(self.colors['success'])
                    c.setFont("Helvetica-Bold", 8)
                    c.drawRightString(x + width - 10, y_pos, "✅ Actif")
                elif amount > 0 and not checked:
                    c.setFillColor(self.colors['warning'])
                    c.drawRightString(x + width - 10, y_pos, "⚠️ Non actif")
                else:
                    c.setFillColor(self.colors['text_muted'])
                    c.drawRightString(x + width - 10, y_pos, "❌ Non souscrit")
                
                y_pos -= row_height
                total_brut += amount
                garanties_active += 1
        
        # Si aucune garantie active
        if garanties_active == 0:
            c.setFillColor(self.colors['text_muted'])
            c.setFont("Helvetica", 9)
            c.drawString(x + 10, y_pos - 5, "Aucune garantie souscrite pour ce véhicule")
            y_pos -= 25
        
        # Total
        y_pos -= 10
        c.setStrokeColor(self.colors['border'])
        c.line(x, y_pos + 8, x + width, y_pos + 8)
        
        # Récupérer les valeurs
        reduction = self.vehicle_data.get('reduction', 0)
        prime_nette = self.vehicle_data.get('prime_nette', 0)
        
        # Total Brut
        c.setFillColor(self.colors['text'])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 10, y_pos - 2, "Total Brut")
        c.drawString(x + 180, y_pos - 2, f"{int(total_brut):,}".replace(",", " "))
        y_pos -= 18

        # Réduction
        if reduction > 0:
            c.setFillColor(self.colors['success'])
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x + 10, y_pos, "Réduction")
            c.drawString(x + 180, y_pos, f"- {int(reduction):,}".replace(",", " "))
            y_pos -= 18

        # Total Net (Prime nette)
        c.setFillColor(self.colors['secondary'])
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 10, y_pos + 2, "TOTAL NET (Prime nette)")
        c.drawString(x + 180, y_pos + 2, f"{int(prime_nette):,}".replace(",", " ") + " FCFA")
        
        return y_pos - 15
    
    def draw_footer(self, c, width, height):
        """Dessine le pied de page avec mentions légales"""
        # Rectangle de fond
        c.setFillColor(self.colors['background'])
        c.rect(0, 0, width, 70, fill=1, stroke=0)
        
        # Ligne décorative
        c.setStrokeColor(self.colors['secondary'])
        c.setLineWidth(2)
        c.line(35, 62, width - 35, 62)
        
        # Informations de contact
        c.setFillColor(self.colors['text_light'])
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, 48, "AMS ASSURANCES - Siège social : Yaoundé, Cameroun")
        c.drawCentredString(width / 2, 36, "📞 +237 6XX XX XX XX | 📧 contact@amsassurance.com | 🌐 www.amsassurance.com")
        
        # Mentions légales
        c.setFont("Helvetica", 7)
        c.setFillColor(self.colors['text_muted'])
        c.drawCentredString(width / 2, 24, "Ce devis est valable 30 jours à compter de sa date d'émission")
        c.drawCentredString(width / 2, 14, "Les montants sont indicatifs et peuvent être modifiés après validation définitive")
        
        # Numéro de page
        c.drawRightString(width - 35, 8, "Page 1/1")
    
    def generate_pdf(self, output_path, show_progress=True):
        """Génère le PDF du devis avec toutes les améliorations"""
        if show_progress:
            progress = QProgressDialog("Génération du devis...", "Annuler", 0, 100, None)
            progress.setWindowTitle("Génération PDF")
            progress.show()
        
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        try:
            # ========== EN-TÊTE ==========
            if show_progress:
                progress.setValue(10)
            self.draw_header(c, width, height)
            
            # ========== INFORMATIONS VÉHICULE ==========
            if show_progress:
                progress.setValue(25)

            # ✅ Récupérer la puissance fiscale avec plusieurs clés possibles
            puissance_fiscale = self.vehicle_data.get('puissance_fiscale')
            if not puissance_fiscale:
                puissance_fiscale = self.vehicle_data.get('puissance')
            if not puissance_fiscale:
                puissance_fiscale = self.vehicle_data.get('puissance_fiscale_saisie')
            if not puissance_fiscale:
                puissance_fiscale = 'N/A'

            # ✅ Ajouter " CV" si ce n'est pas déjà fait
            if puissance_fiscale != 'N/A' and not str(puissance_fiscale).endswith('CV'):
                puissance_fiscale = f"{puissance_fiscale} CV"

            # ✅ Récupérer l'énergie avec plusieurs clés possibles
            energie = self.vehicle_data.get('energie')
            if not energie:
                energie = self.vehicle_data.get('type_energie')
            if not energie:
                energie = self.vehicle_data.get('energy')
            if not energie:
                energie = 'N/A'

            vehicle_items = [
                ("Immatriculation", self.vehicle_data.get('immatriculation', 'N/A')),
                ("Marque / Modèle", f"{self.vehicle_data.get('marque', 'N/A')} {self.vehicle_data.get('modele', 'N/A')}"),
                ("Châssis (VIN)", self.vehicle_data.get('chassis', 'N/A')),
                ("Année", self.vehicle_data.get('annee', 'N/A')),
                ("Puissance fiscale", puissance_fiscale),
                ("Énergie", energie),
                ("Places", self.vehicle_data.get('places', 'N/A')),
                ("Zone", self.vehicle_data.get('zone', 'N/A')),
            ]
            self.draw_info_card(c, 35, height - 280, 230, 155, "INFORMATIONS VÉHICULE", vehicle_items, "🚗")
            # ========== INFORMATIONS PROPRIÉTAIRE ==========
            if show_progress:
                progress.setValue(40)
            owner_items = [
                ("Nom complet", self.vehicle_data.get('owner', 'N/A')),
                ("Téléphone", self.vehicle_data.get('phone', 'N/A')),
                ("Email", self.vehicle_data.get('email', 'N/A')),
                ("Adresse", self.vehicle_data.get('city', 'N/A')),
            ]
            self.draw_info_card(c, 285, height - 280, 280, 155, "PROPRIÉTAIRE", owner_items, "👤")
            
            # ========== DÉTAILS CONTRAT ==========
            if show_progress:
                progress.setValue(55)
            # Ligne de séparation
            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(1)
            c.line(35, height - 295, width - 35, height - 295)
            
            # ========== TABLEAU DES GARANTIES ==========
            if show_progress:
                progress.setValue(70)
            y = self.draw_garanties_table(c, 35, height - 320, width - 70)
            
            # ========== DÉTAIL DES FRAIS ==========
            if show_progress:
                progress.setValue(85)

            # Récupérer les valeurs
            prime_brute = self.vehicle_data.get('prime_brute', 0)  # ✅ Ajout
            reduction = self.vehicle_data.get('reduction', 0)      # ✅ Ajout
            prime_nette = self.vehicle_data.get('prime_nette', 0)
            carte_rose = self.vehicle_data.get('carte_rose', 0)
            accessoires = self.vehicle_data.get('accessoires', 0)  # ✅ Accessoires
            tva = self.vehicle_data.get('tva', 0)
            asac = self.vehicle_data.get('fichier_asac', 0)
            vignette = self.vehicle_data.get('vignette', 0)
            pttc = self.vehicle_data.get('pttc', 0)

            # Filtrer les frais > 0
            frais_items = [
                ("Prime brute", prime_brute, "💰"),  # ✅ Prime brute (avant réduction)
                ("Réduction", reduction, "📉"),      # ✅ Réduction appliquée
                ("Prime nette", prime_nette, "💳"),  # ✅ Prime nette (après réduction)
                ("Carte rose", carte_rose, "📄"),
                ("Accessoires", accessoires, "🔧"),
                ("TVA (19.25%)", tva, "📊"),
                ("Fichier ASAC", asac, "📁"),
                ("Vignette", vignette, "🏷️"),
            ]
            frais_actifs = [(label, value, icon) for label, value, icon in frais_items if value > 0]

            if frais_actifs:
                # Titre
                c.setFillColor(self.colors['primary'])
                c.setFont("Helvetica-Bold", 13)
                c.drawString(35, y - 15, "💰 DÉTAIL DES FRAIS")
                
                # Ligne décorative
                c.setStrokeColor(self.colors['secondary'])
                c.setLineWidth(2)
                c.line(35, y - 21, 150, y - 21)
                
                # Tableau des frais
                c.setFont("Helvetica", 9)
                y_pos = y - 45
                total_frais = 0
                
                for label, value, icon in frais_actifs:
                    # Alternance de fond
                    if (frais_actifs.index((label, value, icon)) % 2) == 0:
                        c.setFillColor(self.colors['background'])
                        c.rect(35, y_pos - 12, width - 70, 18, fill=1, stroke=0)
                    
                    c.setFillColor(self.colors['text'])
                    c.drawString(50, y_pos, f"{icon} {label}")
                    
                    c.setFillColor(self.colors['text'])
                    c.setFont("Helvetica-Bold", 9)
                    c.drawRightString(width - 50, y_pos, f"{int(value):,}".replace(",", " ") + " FCFA")
                    
                    y_pos -= 18
                    total_frais += value
                
                # Total
                y_pos -= 10
                c.setStrokeColor(self.colors['border'])
                c.line(35, y_pos + 10, width - 35, y_pos + 10)
                
                # Ligne de total - ✅ Utiliser pttc pour le TOTAL TTC
                y_pos -= 5
                c.setFillColor(self.colors['secondary'])
                c.setFont("Helvetica-Bold", 14)
                c.drawString(35, y_pos, "🟢 TOTAL TTC (À payer)")
                c.drawRightString(width - 35, y_pos, f"{int(pttc):,}".replace(",", " ") + " FCFA")
                
                # Mention TVA
                y_pos -= 18
                c.setFillColor(self.colors['text_muted'])
                c.setFont("Helvetica", 7)
                c.drawString(35, y_pos, "* TVA incluse au taux de 19.25%")
        
        except Exception as e:
            print(f"Erreur lors de la génération du PDF: {e}")
            raise
        
        finally:
            if show_progress:
                progress.setValue(100)
            c.save()
    
    def print(self, parent_widget=None):
        """Génère le PDF et propose l'impression ou la sauvegarde"""
        try:
            # Générer un nom de fichier
            immat = self.vehicle_data.get('immatriculation', 'vehicule')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"devis_{immat}_{timestamp}.pdf"
            pdf_path = os.path.join(self.export_dir, filename)
            
            # Générer le PDF
            self.generate_pdf(pdf_path)
            
            # Demander à l'utilisateur
            reply = QMessageBox.question(
                parent_widget,
                "Devis généré",
                f"✅ Le devis a été généré avec succès !\n\n"
                f"📄 Fichier : {filename}\n"
                f"📁 Dossier : {self.export_dir}\n"
                f"💰 Montant : {self.vehicle_data.get('pttc', 0):,} FCFA\n\n"
                f"Que souhaitez-vous faire ?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Save | QMessageBox.Open,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Imprimer
                self._print_pdf(pdf_path, parent_widget)
                
            elif reply == QMessageBox.Save:
                # Sauvegarder ailleurs
                save_path, _ = QFileDialog.getSaveFileName(
                    parent_widget,
                    "Sauvegarder le devis",
                    filename,
                    "PDF Files (*.pdf)"
                )
                if save_path:
                    import shutil
                    shutil.copy(pdf_path, save_path)
                    QMessageBox.information(parent_widget, "Succès", "💾 Devis sauvegardé avec succès!")
                    
            elif reply == QMessageBox.Open:
                # Ouvrir le PDF
                import subprocess
                import sys
                if sys.platform == "win32":
                    os.startfile(pdf_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", pdf_path])
                else:
                    subprocess.run(["xdg-open", pdf_path])
            else:
                QMessageBox.information(
                    parent_widget, 
                    "Devis généré", 
                    f"📄 Le devis a été sauvegardé dans :\n{self.export_dir}"
                )
            
        except Exception as e:
            print(f"Erreur lors de la génération du devis : {str(e)}")
            import traceback
            traceback.print_exc()
            
            if parent_widget:
                QMessageBox.critical(
                    parent_widget,
                    "Erreur",
                    f"❌ Une erreur est survenue lors de la génération du devis :\n\n{str(e)}"
                )
    
    def _print_pdf(self, pdf_path, parent_widget):
        """Imprime le PDF"""
        import subprocess
        import sys
        
        try:
            if sys.platform == "win32":
                os.startfile(pdf_path, "print")
            elif sys.platform == "darwin":
                subprocess.run(["lp", pdf_path])
            else:
                subprocess.run(["lp", pdf_path])
            
            QMessageBox.information(parent_widget, "Impression", "🖨️ Le devis a été envoyé à l'imprimante.")
        except Exception as e:
            QMessageBox.warning(
                parent_widget,
                "Erreur d'impression",
                f"Impossible d'imprimer le document :\n{str(e)}\n\n"
                f"Vous pouvez ouvrir le PDF manuellement."
            )
    
    def preview(self, parent_widget=None):
        """Affiche un aperçu avant impression"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        
        dialog = QDialog(parent_widget)
        dialog.setWindowTitle("Aperçu du devis")
        dialog.setMinimumSize(600, 400)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Informations de l'aperçu
        info = QLabel("📄 Aperçu du devis\n\n")
        info.setStyleSheet("font-size: 14px; font-weight: bold;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Résumé
        summary = QLabel(
            f"Véhicule : {self.vehicle_data.get('marque', 'N/A')} {self.vehicle_data.get('modele', 'N/A')}\n"
            f"Immatriculation : {self.vehicle_data.get('immatriculation', 'N/A')}\n"
            f"Propriétaire : {self.vehicle_data.get('owner', 'N/A')}\n"
            f"Montant total : {self.vehicle_data.get('pttc', 0):,} FCFA"
        )
        summary.setStyleSheet("font-size: 12px; padding: 20px; background: #f8fafc; border-radius: 8px;")
        summary.setAlignment(Qt.AlignCenter)
        layout.addWidget(summary)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        btn_print = QPushButton("🖨️ Imprimer")
        btn_print.setStyleSheet("background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px;")
        btn_print.clicked.connect(lambda: self.print(parent_widget) and dialog.accept())
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_print)
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()

