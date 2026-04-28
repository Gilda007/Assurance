# vignette_printer.py

from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt, QCoreApplication
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
import os
from datetime import datetime
import qrcode
from io import BytesIO

class VignettePrinter:
    def __init__(self, vehicle_data, export_dir=None):
        """
        Initialise l'imprimeur de vignette professionnel.
        
        Args:
            vehicle_data (dict): Données du véhicule
            export_dir (str, optional): Dossier d'export par défaut
        """
        self.data = vehicle_data
        self.width, self.height = A4
        self.export_dir = export_dir or os.path.join(os.path.expanduser("~"), "Documents", "Attestations_Assurance")
        
        # Déterminer si le paiement est effectué
        self.is_paid = self._check_payment_status()
        
        # Couleurs de l'entreprise
        self.colors = {
            'primary': colors.HexColor('#1a56db'),      # Bleu principal
            'secondary': colors.HexColor('#0e9f6e'),    # Vert succès
            'accent': colors.HexColor('#ff6b35'),       # Orange accent
            'dark': colors.HexColor('#1f2937'),         # Gris foncé
            'gray': colors.HexColor('#6b7280'),         # Gris moyen
            'light': colors.HexColor('#f3f4f6'),        # Gris clair
            'white': colors.HexColor('#ffffff'),
            'border': colors.HexColor('#e5e7eb'),
            'success': colors.HexColor('#10b981'),
            'warning': colors.HexColor('#f59e0b'),
            'danger': colors.HexColor('#ef4444'),       # Rouge pour impayé
        }
        
    def _check_payment_status(self):
        """
        Vérifie le statut de paiement du contrat.
        
        Returns:
            bool: True si payé, False sinon
        """
        # Vérifier le statut de paiement dans les données
        statut_paiement = self.data.get('statut_paiement', '')
        print(statut_paiement)
        montant_paye = int(self.data.get('montant_paye', '0'))
        print(f"montant_paye: {montant_paye}")
        prime_totale = self.data.get('prime_totale_ttc', self.data.get('prime_nette', 0))
        
        # Si le statut est explicitement PAYE ou si le montant payé >= prime totale
        if statut_paiement == 'PAYE':
            return True
        elif statut_paiement == 'NON_PAYE':
            return False
        elif statut_paiement == 'PARTIEL':
            return False
        elif montant_paye and prime_totale and montant_paye >= prime_totale:
            return True
        
        # Par défaut, considérer comme non payé si aucune information
        return False
    
    def _add_watermark(self, canvas_obj, doc):
        """
        Ajoute un filigrane sur le document si le contrat n'est pas payé.
        
        Args:
            canvas_obj: L'objet canvas ReportLab
            doc: Le document courant
        """
        if not self.is_paid:
            canvas_obj.saveState()
            
            # Rotation et position
            canvas_obj.translate(self.width / 2, self.height / 2)
            canvas_obj.rotate(45)
            
            # Style du filigrane
            canvas_obj.setFont('Helvetica-Bold', 60)
            canvas_obj.setFillColor(colors.Color(0.9, 0.2, 0.2, alpha=0.15))  # Rouge transparent
            
            # Ajouter un deuxième filigrane décalé
            canvas_obj.setFont('Helvetica-Bold', 40)
            canvas_obj.setFillColor(colors.Color(0.9, 0.2, 0.2, alpha=0.1))
            
            canvas_obj.restoreState()
    
    def _add_stamp(self, canvas_obj, doc):
        """
        Ajoute un tampon "IMPAYÉ" sur le document si nécessaire.
        """
        if not self.is_paid:
            canvas_obj.saveState()
            
            # Position en bas à droite
            canvas_obj.setFont('Helvetica-Bold', 14)
            canvas_obj.setFillColor(colors.Color(0.9, 0.2, 0.2, alpha=0.8))
            
            # Dessiner un rectangle autour du tampon
            canvas_obj.setStrokeColor(colors.Color(0.9, 0.2, 0.2, alpha=0.8))
            canvas_obj.setLineWidth(2)
            canvas_obj.rect(self.width - 60*mm, 20*mm, 50*mm, 15*mm)
            
            # Texte du tampon
            canvas_obj.drawCentredString(self.width - 35*mm, 25*mm, "IMPAYÉ")
            
            canvas_obj.restoreState()
    
    def print(self, parent_widget=None):
        """Affiche la boîte de dialogue pour sauvegarder le PDF"""
        
        # Avertir si le contrat n'est pas payé
        if not self.is_paid:
            msg = QMessageBox(parent_widget)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Attention - Contrat non payé")
            msg.setText("Le contrat d'assurance n'a pas été entièrement payé.")
            msg.setInformativeText(
                "L'attestation générée comportera un filigrane 'NON PAYÉ'.\n\n"
                "Voulez-vous continuer ?"
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            
            if msg.exec() != QMessageBox.Yes:
                return
        
        # Créer le nom de fichier par défaut
        immat = self.data.get('immatriculation', 'vehicule').replace(' ', '_')
        status_suffix = "impaye" if not self.is_paid else "paye"
        default_filename = f"attestation_timbre_{immat}_{status_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        default_path = os.path.join(self.export_dir, default_filename)
        
        # Assurer que le dossier existe
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Boîte de dialogue pour choisir l'emplacement
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Enregistrer l'attestation de timbre",
            default_path,
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            # Afficher une progression
            progress = QProgressDialog("Génération du document...", "Annuler", 0, 100, parent_widget)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(500)
            progress.setValue(10)
            QCoreApplication.processEvents()
            
            # Générer le PDF
            self.generate_pdf(file_path, progress)
            
            progress.setValue(100)
            progress.close()
            
            # Message de confirmation avec statut
            if not self.is_paid:
                msg = QMessageBox(parent_widget)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Document généré avec avertissement")
                msg.setText("L'attestation a été générée avec un filigrane 'NON PAYÉ'.")
                msg.setInformativeText(
                    f"Fichier : {os.path.basename(file_path)}\n"
                    f"Emplacement : {os.path.dirname(file_path)}\n\n"
                    "Ce document n'a pas de valeur légale tant que le paiement n'est pas effectué."
                )
                msg.exec()
            else:
                msg = QMessageBox(parent_widget)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Succès")
                msg.setText("L'attestation de timbre a été générée avec succès !")
                msg.setInformativeText(f"Fichier : {os.path.basename(file_path)}\nEmplacement : {os.path.dirname(file_path)}")
                msg.exec()
            
            # Option pour ouvrir le dossier
            reply = QMessageBox.question(
                parent_widget,
                "Ouvrir le dossier ?",
                "Voulez-vous ouvrir le dossier contenant le fichier ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                import subprocess
                import platform
                
                file_dir = os.path.dirname(file_path)
                if platform.system() == 'Windows':
                    os.startfile(file_dir)
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', file_dir])
                else:
                    subprocess.Popen(['xdg-open', file_dir])
                    
        except Exception as e:
            if progress:
                progress.close()
            QMessageBox.critical(
                parent_widget,
                "Erreur de génération",
                f"Erreur lors de la génération du PDF :\n\n{str(e)}"
            )
            raise
    
    def generate_pdf(self, file_path, progress=None):
        """Génère le PDF avec un design professionnel"""
        
        # Créer le document avec des marges réduites pour plus d'espace
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            topMargin=12*mm,
            bottomMargin=12*mm,
            leftMargin=15*mm,
            rightMargin=15*mm,
            title="Attestation de paiement du Droit de Timbre",
            author="AMS ASSURANCES",
            subject="Attestation de timbre automobile"
        )
        
        if progress:
            progress.setValue(20)
            QCoreApplication.processEvents()
        
        # Styles personnalisés
        styles = self.create_styles()
        
        # Construction du document
        story = []
        
        # === HEADER AVEC LOGO ET INFOS ===
        story.append(self.create_header(styles))
        story.append(Spacer(1, 8))
        
        # === LIGNE DE SÉPARATION ===
        line_color = self.colors['danger'] if not self.is_paid else self.colors['primary']
        story.append(HRFlowable(width="100%", thickness=1.5, color=line_color, spaceAfter=10, spaceBefore=5))
        
        if progress:
            progress.setValue(30)
            QCoreApplication.processEvents()
        
        # === TITRE PRINCIPAL ===
        story.append(Paragraph("Attestation de paiement du Droit de Timbre Automobile", styles['MainTitle']))
        story.append(Spacer(1, 4))
        
        story.append(Paragraph("Document officiel - Valeur légale", styles['SubTitle']))
        story.append(Spacer(1, 4))
        
        # === CADRE DE VALIDITÉ ===
        story.append(self.create_validity_box(styles))
        story.append(Spacer(1, 12))
        
        if progress:
            progress.setValue(40)
            QCoreApplication.processEvents()
        
        # # === STATUT DE PAIEMENT ===
        # story.append(self.create_payment_status_section(styles))
        # story.append(Spacer(1, 16))
        
        # === INFORMATIONS VÉHICULE ===
        story.append(Paragraph("Détails du véhicule assuré", styles['SectionTitle']))
        story.append(Spacer(1, 8))
        
        # Tableau des informations
        story.append(self.create_vehicle_table(styles))
        story.append(Spacer(1, 16))
        
        if progress:
            progress.setValue(60)
            QCoreApplication.processEvents()
        
        # === QR CODE ===
        story.append(self.create_qr_code_section(styles))
        story.append(Spacer(1, 16))
        
        if progress:
            progress.setValue(75)
            QCoreApplication.processEvents()
        
        # === SIGNATURE ET CACHET ===
        story.append(self.create_signature_section(styles))
        
        # === PIED DE PAGE ===
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.colors['border'], spaceAfter=6))
        # story.append(self.create_footer(styles))
        
        if progress:
            progress.setValue(90)
            QCoreApplication.processEvents()
        
        # Génération du PDF avec filigrane
        def on_page(canvas_obj, doc):
            # Ajouter le filigrane sur chaque page
            self._add_watermark(canvas_obj, doc)
            self._add_stamp(canvas_obj, doc)
        
        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
        
        if progress:
            progress.setValue(100)
            QCoreApplication.processEvents()

    def create_header(self, styles):
        """Crée l'en-tête du document avec logo et informations"""
        
        # 1. Préparation du logo
        # Remplacez 'logo_ams.png' par le chemin réel de l'image sur votre machine
        logo_path = "addons/Automobiles/static/logo.png" 
        try:
            # Ajustez la largeur (width) et la hauteur (height) selon vos besoins
            logo = Image(logo_path, width=20*mm, height=15*mm)
            logo.hAlign = 'LEFT'
        except:
            logo = "LOGO NON TROUVÉ" # Sécurité si l'image est manquante

        # Ajouter un indicateur de statut dans l'en-tête
        status_indicator = "🔴" if not self.is_paid else "🟢"
        status_text = "PAYÉ" if self.is_paid else "IMPAYÉ"
        
        # 2. Structure des données (On insère l'objet logo dans la cellule sous le titre)
        header_data = [
            ["AMS ASSURANCES", f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
            [logo, f"N° Police: {self.data.get('numero_police', 'N/A')}"],
            ["Assureur agréé", f"{status_indicator} Statut: {status_text}"],
        ]
        
        header_table = Table(header_data, colWidths=[90*mm, 70*mm])
        header_table.setStyle(TableStyle([
            # Style du titre principal
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('TEXTCOLOR', (0, 0), (0, 0), self.colors['primary']),
            
            # Alignement du logo (cellule 0, 1)
            ('LEFTPADDING', (0, 1), (0, 1), 0),
            ('TOPPADDING', (0, 1), (0, 1), 5),
            ('BOTTOMPADDING', (0, 1), (0, 1), 5),

            # Style du texte de droite
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), self.colors['gray']),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            
            # Style du statut
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (1, 2), (1, 2), self.colors['success'] if self.is_paid else self.colors['danger']),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ]))
        
        return header_table
        
        # Les autres méthodes (create_validity_box, create_amount_section, etc.)
        # restent identiques à la version précédente...
    
    def format_date(self, date):
        """Formate une date au format JJ/MM/AAAA"""
        if date and date != 'N/A' and date != '':
            try:
                if hasattr(date, 'strftime'):
                    return date.strftime("%d/%m/%Y")
                return str(date)
            except:
                return str(date)
        return datetime.now().strftime("%d/%m/%Y")
    
    def create_styles(self):
        """Crée les styles personnalisés pour le document"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'MainTitle': ParagraphStyle(
                'MainTitle',
                parent=styles['Heading1'],
                fontSize=16,
                fontName='Helvetica-Bold',
                textColor=self.colors['primary'],
                alignment=TA_CENTER,
                spaceAfter=6,
                leading=20
            ),
            'SubTitle': ParagraphStyle(
                'SubTitle',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica',
                textColor=self.colors['gray'],
                alignment=TA_CENTER,
                spaceAfter=12
            ),
            'WarningTitle': ParagraphStyle(
                'WarningTitle',
                parent=styles['Normal'],
                fontSize=14,
                fontName='Helvetica-Bold',
                textColor=self.colors['danger'],
                alignment=TA_CENTER,
                spaceAfter=8,
                leading=18
            ),
            'SectionTitle': ParagraphStyle(
                'SectionTitle',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=self.colors['dark'],
                alignment=TA_LEFT,
                spaceAfter=8,
                spaceBefore=4
            ),
            'TableLabel': ParagraphStyle(
                'TableLabel',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=self.colors['gray'],
                alignment=TA_LEFT,
                leading=12
            ),
            'TableValue': ParagraphStyle(
                'TableValue',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                textColor=self.colors['dark'],
                alignment=TA_LEFT,
                leading=12
            ),
            'QrText': ParagraphStyle(
                'QrText',
                parent=styles['Normal'],
                fontSize=8,
                fontName='Helvetica',
                textColor=self.colors['gray'],
                alignment=TA_LEFT,
                leading=10
            ),
            'Footer': ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=7,
                fontName='Helvetica',
                textColor=self.colors['gray'],
                alignment=TA_CENTER,
                leading=9
            ),
        }
        
        return custom_styles
    
    def create_validity_box(self, styles):
        """Crée un cadre élégant pour la période de validité"""
        
        date_debut = self.format_date(self.data.get('date_debut', ''))
        date_fin = self.format_date(self.data.get('date_fin', ''))
        
        # Données du cadre
        validity_data = [
            ["📅 PÉRIODE DE VALIDITÉ", ""],
            ["Du", date_debut, "Au", date_fin],
        ]
        
        validity_table = Table(validity_data, colWidths=[40*mm, 45*mm, 20*mm, 45*mm])
        validity_table.setStyle(TableStyle([
            # Style du titre
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Style des lignes de données
            ('BACKGROUND', (0, 1), (-1, 1), self.colors['light']),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('ALIGN', (1, 1), (1, 1), 'CENTER'),
            ('ALIGN', (3, 1), (3, 1), 'CENTER'),
            ('TEXTCOLOR', (0, 1), (0, 1), self.colors['gray']),
            ('TEXTCOLOR', (2, 1), (2, 1), self.colors['gray']),
            ('TEXTCOLOR', (1, 1), (1, 1), self.colors['success'] if self.is_paid else self.colors['danger']),
            ('TEXTCOLOR', (3, 1), (3, 1), self.colors['success'] if self.is_paid else self.colors['danger']),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold'),
            # Bordures
            ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 8),
        ]))
        
        return validity_table

    def create_vehicle_table(self, styles):
        """Crée un tableau élégant pour les informations du véhicule"""
        
        # Récupérer les données
        vehicle_info = [
            ("Marque", self.data.get('marque', '').upper()),
            ("Modèle", self.data.get('modele', '').upper()),
            ("Immatriculation", self.data.get('immatriculation', '').upper()),
            ("Châssis", self.data.get('chassis', 'N/A').upper()),
            ("Énergie", self.data.get('energy', self.data.get('energie', '')).upper()),
            ("Puissance", f"{self.data.get('usage', '')} CV"),
            ("Places", str(self.data.get('places', '5'))),
            ("Zone", self.data.get('zone', 'N/A')),
            ("Catégorie", self.data.get('categorie', 'Particulier')),
        ]
        
        # Créer le tableau
        table_data = []
        for i, (label, value) in enumerate(vehicle_info):
            if i % 2 == 0:
                # Nouvelle ligne, deux colonnes
                if i + 1 < len(vehicle_info):
                    label2, value2 = vehicle_info[i + 1]
                    table_data.append([
                        Paragraph(f"<b>{label}</b>", styles['TableLabel']),
                        Paragraph(value, styles['TableValue']),
                        Paragraph(f"<b>{label2}</b>", styles['TableLabel']),
                        Paragraph(value2, styles['TableValue'])
                    ])
        
        vehicle_table = Table(table_data, colWidths=[35*mm, 40*mm, 35*mm, 40*mm])
        vehicle_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (0, -1), self.colors['light']),
            ('BACKGROUND', (2, 0), (2, -1), self.colors['light']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
        ]))
        
        return vehicle_table

    def create_qr_code_section(self, styles):
        """Crée un QR code pour validation en ligne"""
        
        # Générer les données pour le QR code
        vehicle_id = self.data.get('id', '')
        qr_data = f"https://amsassurances.cm/verify/{vehicle_id}/{datetime.now().strftime('%Y%m%d')}"
        
        # Créer le QR code
        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1a56db", back_color="white")
        
        # Convertir en BytesIO pour ReportLab
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Créer l'image ReportLab
        qr_image = Image(buffer, width=40*mm, height=40*mm)
        
        # Créer le tableau avec QR code et texte
        qr_text = """
        <font size="8" color="#6b7280">
        Scannez ce QR code pour vérifier<br/>
        l'authenticité de cette attestation<br/>
        sur notre plateforme sécurisée.
        </font>
        """
        
        qr_table_data = [
            [qr_image, Paragraph(qr_text, styles['QrText'])]
        ]
        
        qr_table = Table(qr_table_data, colWidths=[45*mm, 105*mm])
        qr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return qr_table

    def create_signature_section(self, styles):
        """Crée la section de signature avec cachet"""
        
        today = datetime.now().strftime("%d/%m/%Y")
        
        signature_data = [
            ["", ""],
            [f"Fait à Yaoundé, le {today}", "Pour AMS ASSURANCES"],
            ["", "Le Directeur Général"],
            ["", "_________________________"],
            ["", "Cachet de l'assureur"],
        ]
        
        signature_table = Table(signature_data, colWidths=[80*mm, 70*mm])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
            ('ALIGN', (1, 2), (1, 2), 'RIGHT'),
            ('ALIGN', (1, 3), (1, 3), 'RIGHT'),
            ('ALIGN', (1, 4), (1, 4), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return signature_table

    # def create_footer(self, styles):
    #     """Crée le pied de page professionnel"""
        
    #     footer_text = """
    #     <font size="7" color="#6b7280">
    #     AMS ASSURANCES - Agrément n° 2025/001/MINFI<br/>
    #     Siège social : Douala - Cameroun | Tél : (+237) 233 42 42 42 | Email : contact@amsassurances.cm<br/>
    #     Document authentifié par signature électronique - Toute reproduction est interdite
    #     </font>
    #     """
        
    #     return Paragraph(footer_text, styles['Footer'])