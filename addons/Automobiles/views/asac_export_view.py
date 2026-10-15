# addons/Automobiles/views/asac_export_view.py
"""
Vue d'export ASAC - Export en masse de véhicules
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QGridLayout, QCheckBox, QComboBox, QLineEdit,
    QTextEdit, QTabWidget, QScrollArea, QSplitter,
    QDialog, QDateEdit, QFormLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime, QSettings
from PySide6.QtGui import QColor, QFont, QTextCursor, QPalette

from datetime import datetime
from typing import List, Dict, Any
import json
import time
import requests

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard


class ASACExportView(QWidget):
    """Vue d'export ASAC en masse"""
    
    def __init__(self, controller, user=None, selected_vehicles=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.selected_vehicles = selected_vehicles or []
        self.export_results = []
        self.export_worker = None
        self.settings = QSettings("LOMETA", "ASAC")
        
        self.setup_ui()
        self.load_config()
        self.populate_vehicles_table()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.LG)
        
        # En-tête
        header = self._create_header()
        layout.addWidget(header)
        
        # Barre d'outils
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # Tableau des véhicules
        self._create_vehicles_table()
        layout.addWidget(self.vehicles_table_container, 1)
        
        # Barre de progression
        self.progress_card = self._create_progress_card()
        layout.addWidget(self.progress_card)
        
        # Pied de page
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self):
        """Crée l'en-tête"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 16px;
                padding: 20px 28px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        
        # Titre
        title_container = QVBoxLayout()
        title = QLabel("📤 Export ASAC en masse")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 800;")
        
        subtitle = QLabel(f"Export de {len(self.selected_vehicles)} véhicules vers le serveur ASAC")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px;")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        # Statistiques
        stats_container = QHBoxLayout()
        stats_container.setSpacing(20)
        
        self.stats_total = self._create_stat_item("📊", str(len(self.selected_vehicles)), "Total")
        self.stats_pending = self._create_stat_item("⏳", str(len(self.selected_vehicles)), "En attente")
        self.stats_success = self._create_stat_item("✅", "0", "Exportés")
        self.stats_error = self._create_stat_item("❌", "0", "Erreurs")
        
        stats_container.addWidget(self.stats_total)
        stats_container.addWidget(self.stats_pending)
        stats_container.addWidget(self.stats_success)
        stats_container.addWidget(self.stats_error)
        
        layout.addLayout(title_container)
        layout.addStretch()
        layout.addLayout(stats_container)
        
        return header
    
    def _create_stat_item(self, icon, value, label):
        """Crée un élément de statistique"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 8px 16px;
                border: 1px solid rgba(255,255,255,0.05);
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)
        
        value_lbl = QLabel(f"{icon} {value}")
        value_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: 700;")
        value_lbl.setObjectName("value")
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        
        layout.addWidget(value_lbl)
        layout.addWidget(label_lbl)
        
        widget.value_label = value_lbl
        
        return widget
    
    def _create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = QFrame()
        toolbar.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px 16px;
            }}
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(10)
        
        # Boutons d'action
        self.btn_export = self._create_action_button("📤 Exporter tout", "#2563eb")
        self.btn_export.clicked.connect(self.start_export)
        
        self.btn_config = self._create_action_button("⚙️ Configuration", "#64748b")
        self.btn_config.clicked.connect(self.open_config)
        
        self.btn_refresh = self._create_action_button("🔄 Rafraîchir", "#64748b")
        self.btn_refresh.clicked.connect(self.populate_vehicles_table)
        
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_config)
        layout.addWidget(self.btn_refresh)
        
        layout.addStretch()
        
        # Filtres
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_vehicles)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        layout.addWidget(self.search_input)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "À exporter", "Exporté", "Erreur"])
        self.status_filter.setFixedWidth(120)
        self.status_filter.currentTextChanged.connect(self.filter_vehicles)
        self.status_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.status_filter)
        
        return toolbar
    
    def _create_action_button(self, text, color):
        """Crée un bouton d'action"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:disabled {{
                background-color: #cbd5e1;
                color: #94a3b8;
            }}
        """)
        return btn
    
    def _create_vehicles_table(self):
        """Crée le tableau des véhicules"""
        self.vehicles_table_container = QFrame()
        self.vehicles_table_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(self.vehicles_table_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête du tableau
        header = QFrame()
        header.setStyleSheet("background: transparent; border-bottom: 1px solid #e2e8f0; padding: 12px 20px;")
        
        header_layout = QHBoxLayout(header)
        title = QLabel("📋 Véhicules à exporter")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b;")
        
        self.table_info = QLabel(f"{len(self.selected_vehicles)} véhicule(s)")
        self.table_info.setStyleSheet("color: #64748b; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.table_info)
        
        layout.addWidget(header)
        
        # Tableau
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(7)
        self.vehicles_table.setHorizontalHeaderLabels([
            "Immatriculation", "Marque", "Modèle", "Catégorie", 
            "Statut", "Date export", "Actions"
        ])
        
        self.vehicles_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background: #eef2ff;
            }
            QHeaderView::section {
                background: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                color: #64748b;
                font-size: 11px;
                text-transform: uppercase;
            }
        """)
        
        self.vehicles_table.horizontalHeader().setStretchLastSection(True)
        self.vehicles_table.verticalHeader().setVisible(False)
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicles_table.setMinimumHeight(300)
        
        # Largeurs des colonnes
        self.vehicles_table.setColumnWidth(0, 150)
        self.vehicles_table.setColumnWidth(1, 120)
        self.vehicles_table.setColumnWidth(2, 120)
        self.vehicles_table.setColumnWidth(3, 100)
        self.vehicles_table.setColumnWidth(4, 130)
        self.vehicles_table.setColumnWidth(5, 120)
        self.vehicles_table.setColumnWidth(6, 100)
        
        layout.addWidget(self.vehicles_table)
        
        # Pied du tableau
        footer = QFrame()
        footer.setStyleSheet("background: transparent; border-top: 1px solid #e2e8f0; padding: 8px 20px;")
        
        footer_layout = QHBoxLayout(footer)
        
        # Légende
        legend_items = [
            ("🟢", "Exporté", "#10b981"),
            ("🟡", "En attente", "#f59e0b"),
            ("🔴", "Erreur", "#ef4444"),
            ("🔄", "En cours", "#3b82f6")
        ]
        
        for dot, label, color in legend_items:
            item = QLabel(f"{dot} {label}")
            item.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 500;")
            footer_layout.addWidget(item)
        
        footer_layout.addStretch()
        
        # Temps estimé
        self.est_time_label = QLabel(f"Temps estimé: ~{len(self.selected_vehicles)}s")
        self.est_time_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        footer_layout.addWidget(self.est_time_label)
        
        layout.addWidget(footer)
    
    def _create_progress_card(self):
        """Crée la carte de progression"""
        card = ModernCard(title="⏳ Progression de l'export", icon="📊")
        card.setVisible(False)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #f1f5f9;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #8b5cf6);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        status_layout = QHBoxLayout()
        self.progress_status = QLabel("Prêt")
        self.progress_status.setStyleSheet("color: #64748b; font-size: 13px;")
        status_layout.addWidget(self.progress_status)
        status_layout.addStretch()
        self.progress_count = QLabel("0 / 0")
        self.progress_count.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 600;")
        status_layout.addWidget(self.progress_count)
        
        layout.addLayout(status_layout)
        
        # Logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(120)
        self.logs_text.setFont(QFont("Courier New", 10))
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background: #0f172a;
                color: #e2e8f0;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.logs_text)
        
        card.add_layout(layout)
        
        return card
    
    def _create_footer(self):
        """Crée le pied de page"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px 16px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        
        # Statut
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("color: #10b981; font-size: 10px;")
        layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Quota
        quota_label = QLabel("⏱️ Quota: 60 requêtes/minute")
        quota_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(quota_label)
        
        return footer
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def populate_vehicles_table(self):
        """Remplit le tableau des véhicules"""
        self.vehicles_table.setRowCount(0)
        
        for row, vehicle in enumerate(self.selected_vehicles):
            self.vehicles_table.insertRow(row)
            
            # Immatriculation
            immat_item = QTableWidgetItem(vehicle.get('immatriculation', '-'))
            immat_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            immat_item.setForeground(QColor("#2563eb"))
            self.vehicles_table.setItem(row, 0, immat_item)
            
            # Marque
            self.vehicles_table.setItem(row, 1, QTableWidgetItem(vehicle.get('marque', '-')))
            
            # Modèle
            self.vehicles_table.setItem(row, 2, QTableWidgetItem(vehicle.get('modele', '-')))
            
            # Catégorie
            cat_item = QTableWidgetItem(vehicle.get('categorie', '-'))
            cat_item.setForeground(QColor("#64748b"))
            self.vehicles_table.setItem(row, 3, cat_item)
            
            # Statut
            status = vehicle.get('asac_status', 'pending')
            status_text, status_color = self._get_status_config(status)
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(status_color))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.vehicles_table.setItem(row, 4, status_item)
            
            # Date export
            date_item = QTableWidgetItem(vehicle.get('export_date', '-'))
            date_item.setForeground(QColor("#64748b"))
            self.vehicles_table.setItem(row, 5, date_item)
            
            # Actions
            actions_widget = self._create_actions_widget(row)
            self.vehicles_table.setCellWidget(row, 6, actions_widget)
        
        self.vehicles_table.resizeColumnsToContents()
        self.table_info.setText(f"{len(self.selected_vehicles)} véhicule(s)")
        self.est_time_label.setText(f"Temps estimé: ~{len(self.selected_vehicles)}s")
    
    def _get_status_config(self, status):
        """Retourne la configuration du statut"""
        status_map = {
            'pending': ('⏳ À exporter', '#f59e0b'),
            'success': ('✅ Exporté', '#10b981'),
            'error': ('❌ Erreur', '#ef4444'),
            'in_progress': ('🔄 En cours', '#3b82f6'),
            'skipped': ('⏭️ Ignoré', '#64748b')
        }
        return status_map.get(status, ('⏳ À exporter', '#f59e0b'))
    
    def _create_actions_widget(self, row):
        """Crée les boutons d'action"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        # Bouton Exporter
        export_btn = QPushButton("📤")
        export_btn.setFixedSize(30, 30)
        export_btn.setToolTip("Exporter ce véhicule")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #d1fae5;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #a7f3d0;
            }
        """)
        export_btn.clicked.connect(lambda: self.export_single_vehicle(row))
        
        # Bouton Détails
        details_btn = QPushButton("👁️")
        details_btn.setFixedSize(30, 30)
        details_btn.setToolTip("Voir les détails")
        details_btn.setStyleSheet("""
            QPushButton {
                background: #e0f2fe;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #bae6fd;
            }
        """)
        details_btn.clicked.connect(lambda: self.view_vehicle_details(row))
        
        layout.addWidget(export_btn)
        layout.addWidget(details_btn)
        
        return widget
    
    def view_vehicle_details(self, row):
        """Affiche les détails d'un véhicule"""
        if row < len(self.selected_vehicles):
            vehicle = self.selected_vehicles[row]
            details = json.dumps(vehicle, indent=2, default=str)
            QMessageBox.information(self, "Détails du véhicule", details)
    
    # ============================================================
    # FILTRES
    # ============================================================
    
    def filter_vehicles(self):
        """Filtre les véhicules"""
        search = self.search_input.text().lower()
        status = self.status_filter.currentText()
        
        for row in range(self.vehicles_table.rowCount()):
            visible = True
            
            if search:
                immat = self.vehicles_table.item(row, 0)
                if immat:
                    visible = search in immat.text().lower()
            
            if visible and status != "Tous":
                status_item = self.vehicles_table.item(row, 4)
                if status_item:
                    visible = status in status_item.text()
            
            self.vehicles_table.setRowHidden(row, not visible)
    
    # ============================================================
    # EXPORT
    # ============================================================
    
    def start_export(self):
        """Démarre l'export en masse"""
        if not self.selected_vehicles:
            QMessageBox.warning(self, "Aucun véhicule", "Aucun véhicule à exporter.")
            return
        
        config = self.load_config()
        if not config["url"] or not config["app_key"]:
            QMessageBox.warning(self, "Configuration manquante", "Veuillez configurer le serveur ASAC.")
            self.open_config()
            return
        
        reply = QMessageBox.question(
            self, "Confirmation d'export",
            f"Voulez-vous exporter {len(self.selected_vehicles)} véhicules vers ASAC ?\n\n"
            f"⚠️ Limite: 60 requêtes par minute.\n"
            f"Temps estimé: ~{len(self.selected_vehicles)} secondes",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._start_bulk_export(config)
    
    def export_single_vehicle(self, row):
        """Exporte un seul véhicule"""
        if row < len(self.selected_vehicles):
            vehicle = self.selected_vehicles[row]
            config = self.load_config()
            
            if not config["url"] or not config["app_key"]:
                QMessageBox.warning(self, "Configuration manquante", "Veuillez configurer le serveur ASAC.")
                self.open_config()
                return
            
            self._start_single_export(vehicle, config)
    
    def _start_bulk_export(self, config):
        """Démarre l'export en masse"""
        self.progress_card.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_status.setText("Export en cours...")
        self.progress_count.setText(f"0 / {len(self.selected_vehicles)}")
        self.set_status("⏳ Export en cours...", "info")
        self.logs_text.clear()
        self.logs_text.append("🚀 Démarrage de l'export en masse...\n")
        
        self.btn_export.setEnabled(False)
        
        self.export_worker = BulkExportWorker(self.selected_vehicles, config)
        self.export_worker.progress_updated.connect(self._update_export_progress)
        self.export_worker.log_updated.connect(self._add_log)
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.error.connect(self._on_export_error)
        self.export_worker.vehicle_result.connect(self._on_vehicle_result)
        self.export_worker.start()
    
    def _start_single_export(self, vehicle, config):
        """Démarre l'export d'un seul véhicule"""
        self.progress_card.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_status.setText("Export en cours...")
        self.progress_count.setText(f"1 / 1")
        self.set_status("⏳ Export en cours...", "info")
        self.logs_text.clear()
        self.logs_text.append(f"🚀 Export du véhicule {vehicle.get('immatriculation', 'N/A')}...\n")
        
        self.btn_export.setEnabled(False)
        
        self.export_worker = BulkExportWorker([vehicle], config)
        self.export_worker.progress_updated.connect(self._update_export_progress)
        self.export_worker.log_updated.connect(self._add_log)
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.error.connect(self._on_export_error)
        self.export_worker.vehicle_result.connect(self._on_vehicle_result)
        self.export_worker.start()
    
    def _update_export_progress(self, current, total, status):
        """Met à jour la progression"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_status.setText(status)
        self.progress_count.setText(f"{current} / {total}")
        self.set_status(f"⏳ {status}", "info")
    
    def _on_vehicle_result(self, vehicle_data, result):
        """Traite le résultat d'un véhicule exporté"""
        immat = vehicle_data.get('immatriculation', 'N/A')
        
        # Mettre à jour le statut dans la liste
        for v in self.selected_vehicles:
            if v.get('immatriculation') == immat:
                if result.get('success'):
                    v['asac_status'] = 'success'
                    v['export_date'] = datetime.now().strftime("%d/%m/%Y")
                    v['error_message'] = ''
                else:
                    v['asac_status'] = 'error'
                    v['error_message'] = result.get('error', 'Erreur inconnue')
                break
        
        # Mettre à jour le tableau
        self.populate_vehicles_table()
        
        # Mettre à jour les stats
        self._update_stats()
    
    def _on_export_finished(self, results):
        """Appelé à la fin de l'export"""
        self.btn_export.setEnabled(True)
        self.progress_card.setVisible(False)
        
        self._save_export_history(results)
        
        summary = (
            f"📊 Export ASAC terminé!\n\n"
            f"✅ Réussis: {results['success']}\n"
            f"⏭️ Ignorés: {results['skipped']}\n"
            f"❌ Échecs: {results['failed']}\n"
            f"📦 Total: {results['total']}"
        )
        
        self._add_log("=" * 50)
        self._add_log(summary)
        self._add_log("=" * 50)
        self.set_status("✅ Export terminé", "success")
        
        if results['failed'] > 0:
            errors = "\n".join(results['errors'][:5])
            QMessageBox.warning(self, "Export terminé avec erreurs", f"{summary}\n\n❌ Erreurs:\n{errors}")
        else:
            QMessageBox.information(self, "Export réussi", summary)
    
    def _on_export_error(self, error_msg):
        """Appelé en cas d'erreur d'export"""
        self.btn_export.setEnabled(True)
        self.progress_card.setVisible(False)
        self._add_log(f"❌ Erreur d'export: {error_msg}")
        self.set_status(f"❌ Erreur: {error_msg}", "error")
        QMessageBox.critical(self, "Erreur", f"Erreur d'export: {error_msg}")
    
    def _add_log(self, message):
        """Ajoute un message dans les logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.logs_text.append(formatted)
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)
    
    def _update_stats(self):
        """Met à jour les statistiques"""
        total = len(self.selected_vehicles)
        success = sum(1 for v in self.selected_vehicles if v.get('asac_status') == 'success')
        error = sum(1 for v in self.selected_vehicles if v.get('asac_status') == 'error')
        pending = total - success - error
        
        self.stats_total.value_label.setText(f"📊 {total}")
        self.stats_pending.value_label.setText(f"⏳ {pending}")
        self.stats_success.value_label.setText(f"✅ {success}")
        self.stats_error.value_label.setText(f"❌ {error}")
    
    def _save_export_history(self, results):
        """Sauvegarde l'historique d'export"""
        for detail in results.get('details', []):
            vehicle = detail.get('vehicle', {})
            vehicle_id = vehicle.get('id')
            if vehicle_id:
                history = self.settings.value(f"asac_history_{vehicle_id}", [])
                if isinstance(history, str):
                    try:
                        history = json.loads(history)
                    except:
                        history = []
                
                history.insert(0, {
                    'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'status': detail.get('status', 'pending').lower(),
                    'message': detail.get('message', ''),
                    'reference': detail.get('reference', '')
                })
                
                history = history[:20]
                self.settings.setValue(f"asac_history_{vehicle_id}", json.dumps(history))
    
    # ============================================================
    # CONFIGURATION
    # ============================================================
    
    def load_config(self):
        """Charge la configuration ASAC"""
        config = {
            "url": self.settings.value("asac_url", ""),
            "app_key": self.settings.value("asac_app_key", ""),
            "username": self.settings.value("asac_username", ""),
            "password": self.settings.value("asac_password", ""),
            "email": self.settings.value("asac_email", ""),
            "office_code": self.settings.value("asac_office_code", "AG-DLA-001"),
            "org_code": self.settings.value("asac_org_code", "ACTIVA")
        }
        return config
    
    def open_config(self):
        """Ouvre la configuration ASAC"""
        dialog = ConfigDialog(self)
        if dialog.exec():
            self.load_config()
            self._add_log("✅ Configuration mise à jour")
    
    def set_status(self, message, level="info"):
        """Met à jour le statut"""
        colors = {
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b",
            "info": "#3b82f6"
        }
        color = colors.get(level, "#64748b")
        self.status_icon.setStyleSheet(f"color: {color}; font-size: 10px;")
        self.status_label.setText(message)


# ============================================================
# BULK EXPORT WORKER
# ============================================================

class BulkExportWorker(QThread):
    """Thread pour l'export en masse vers ASAC"""
    
    progress_updated = Signal(int, int, str)
    log_updated = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    vehicle_result = Signal(dict, dict)
    
    def __init__(self, vehicles_data: List[Dict], config: Dict, options: Dict = None):
        super().__init__()
        self.vehicles_data = vehicles_data
        self.config = config
        self.options = options or {}
        self._running = True
    
    def run(self):
        try:
            total = len(self.vehicles_data)
            results = {
                'total': total,
                'success': 0,
                'failed': 0,
                'skipped': 0,
                'errors': [],
                'details': []
            }
            
            for i, vehicle_data in enumerate(self.vehicles_data):
                if not self._running:
                    break
                
                self.progress_updated.emit(i + 1, total, 
                    f"Traitement {i+1}/{total}: {vehicle_data.get('immatriculation', 'N/A')}")
                
                try:
                    result = self._export_vehicle(vehicle_data)
                    self.vehicle_result.emit(vehicle_data, result)
                    
                    if result.get('success'):
                        results['success'] += 1
                        results['details'].append({
                            'vehicle': vehicle_data,
                            'status': 'SUCCESS',
                            'message': result.get('message', 'Exporté'),
                            'reference': result.get('reference', '')
                        })
                        self.log_updated.emit(f"✅ {vehicle_data.get('immatriculation', 'N/A')}: Exporté")
                    else:
                        results['failed'] += 1
                        error_msg = result.get('error', 'Erreur inconnue')
                        results['errors'].append(f"{vehicle_data.get('immatriculation', 'N/A')}: {error_msg}")
                        results['details'].append({
                            'vehicle': vehicle_data,
                            'status': 'ERROR',
                            'message': error_msg
                        })
                        self.log_updated.emit(f"❌ {vehicle_data.get('immatriculation', 'N/A')}: {error_msg}")
                    
                    # Attendre entre les requêtes (limite de 60/min)
                    if i < total - 1:
                        time.sleep(1)
                    
                except Exception as e:
                    results['failed'] += 1
                    error_msg = str(e)
                    results['errors'].append(f"{vehicle_data.get('immatriculation', 'N/A')}: {error_msg}")
                    results['details'].append({
                        'vehicle': vehicle_data,
                        'status': 'ERROR',
                        'message': error_msg
                    })
                    self.log_updated.emit(f"❌ {vehicle_data.get('immatriculation', 'N/A')}: {error_msg}")
            
            results['completed'] = True
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _export_vehicle(self, vehicle_data: Dict) -> Dict:
        """Exporte un véhicule vers ASAC"""
        try:
            # Construire la requête pour le véhicule
            request = self._build_vehicle_request(vehicle_data)
            
            # Authentification
            auth_url = f"{self.config.get('url', '')}/api/v1/auth/tokens"
            headers = {
                "X-App-Id": self.config.get("app_key", ""),
                "Content-Type": "application/json"
            }
            auth_payload = {
                "username": self.config.get("username", ""),
                "password": self.config.get("password", ""),
                "email": self.config.get("email", "")
            }
            
            import requests
            auth_response = requests.post(auth_url, headers=headers, json=auth_payload, timeout=10)
            
            if auth_response.status_code != 200:
                return {'success': False, 'error': f"Authentification échouée: {auth_response.text[:100]}"}
            
            auth_data = auth_response.json()
            token = auth_data.get("token", "")
            
            # Envoyer la production
            prod_url = f"{self.config['url']}/api/v1/productions"
            prod_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            prod_response = requests.post(prod_url, json=request, headers=prod_headers, timeout=30)
            
            if prod_response.status_code in [200, 201]:
                response_data = prod_response.json()
                return {
                    'success': True,
                    'message': 'Exporté avec succès',
                    'reference': response_data.get('data', {}).get('reference', 'N/A')
                }
            else:
                return {'success': False, 'error': f"Erreur ASAC: {prod_response.text[:200]}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _build_vehicle_request(self, vehicle: Dict) -> Dict:
        """Construit la requête ASAC pour un véhicule"""
        return {
            "immatriculation": vehicle.get('immatriculation', ''),
            "marque": vehicle.get('marque', ''),
            "modele": vehicle.get('modele', ''),
            "categorie": vehicle.get('categorie', ''),
            "energie": vehicle.get('energie', ''),
            "puissance": vehicle.get('puissance', 0),
            "date_mise_circulation": vehicle.get('date_mise_circulation', ''),
            "valeur_neuf": vehicle.get('valeur_neuf', 0),
            "valeur_venale": vehicle.get('valeur_venale', 0),
            "prime_nette": vehicle.get('prime_nette', 0),
            "prime_brute": vehicle.get('prime_brute', 0),
            "owner": {
                "nom": vehicle.get('owner_nom', ''),
                "prenom": vehicle.get('owner_prenom', ''),
                "telephone": vehicle.get('owner_telephone', ''),
                "email": vehicle.get('owner_email', ''),
                "adresse": vehicle.get('owner_adresse', '')
            }
        }


class ConfigDialog(QDialog):
    """Dialogue de configuration ASAC"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuration ASAC")
        self.setMinimumSize(500, 450)
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.LG)
        
        # Titre
        title = QLabel("Configuration du serveur ASAC")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)
        
        # Formulaire
        form_layout = QFormLayout()
        form_layout.setSpacing(Spacing.MD)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.asac.cm")
        form_layout.addRow("URL du serveur:", self.url_input)
        
        # App Key
        self.app_key_input = QLineEdit()
        self.app_key_input.setPlaceholderText("Clé d'application ASAC")
        form_layout.addRow("Clé d'application:", self.app_key_input)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur ASAC")
        form_layout.addRow("Nom d'utilisateur:", self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Mot de passe:", self.password_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@exemple.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Office Code
        self.office_input = QLineEdit()
        self.office_input.setPlaceholderText("AG-DLA-001")
        form_layout.addRow("Code agence:", self.office_input)
        
        # Org Code
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("ACTIVA")
        form_layout.addRow("Code organisation:", self.org_input)
        
        layout.addLayout(form_layout)
        
        # Test
        test_btn = QPushButton("🔌 Tester la connexion")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        test_btn.clicked.connect(self.test_connection)
        layout.addWidget(test_btn)
        
        # Resultat du test
        self.test_result = QLabel("")
        self.test_result.setStyleSheet("font-size: 12px; padding: 4px;")
        layout.addWidget(self.test_result)
        
        # Boutons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
    
    def load_config(self):
        """Charge la configuration actuelle"""
        settings = QSettings("LOMETA", "ASAC")
        self.url_input.setText(settings.value("asac_url", ""))
        self.app_key_input.setText(settings.value("asac_app_key", ""))
        self.username_input.setText(settings.value("asac_username", ""))
        self.password_input.setText(settings.value("asac_password", ""))
        self.email_input.setText(settings.value("asac_email", ""))
        self.office_input.setText(settings.value("asac_office_code", "AG-DLA-001"))
        self.org_input.setText(settings.value("asac_org_code", "ACTIVA"))
    
    def save_config(self):
        """Sauvegarde la configuration"""
        settings = QSettings("LOMETA", "ASAC")
        settings.setValue("asac_url", self.url_input.text())
        settings.setValue("asac_app_key", self.app_key_input.text())
        settings.setValue("asac_username", self.username_input.text())
        settings.setValue("asac_password", self.password_input.text())
        settings.setValue("asac_email", self.email_input.text())
        settings.setValue("asac_office_code", self.office_input.text())
        settings.setValue("asac_org_code", self.org_input.text())
        
        QMessageBox.information(self, "Succès", "Configuration sauvegardée avec succès.")
        self.accept()
    
    def test_connection(self):
        """Teste la connexion au serveur ASAC"""
        import requests
        
        url = self.url_input.text().strip()
        app_key = self.app_key_input.text().strip()
        
        if not url or not app_key:
            self.test_result.setText("❌ Veuillez remplir l'URL et la clé d'application")
            self.test_result.setStyleSheet("color: #ef4444; font-size: 12px; padding: 4px;")
            return
        
        try:
            auth_url = f"{url}/api/v1/auth/tokens"
            headers = {
                "X-App-Id": app_key,
                "Content-Type": "application/json"
            }
            auth_payload = {
                "username": self.username_input.text(),
                "password": self.password_input.text(),
                "email": self.email_input.text()
            }
            
            response = requests.post(auth_url, headers=headers, json=auth_payload, timeout=10)
            
            if response.status_code == 200:
                self.test_result.setText("✅ Connexion réussie !")
                self.test_result.setStyleSheet("color: #10b981; font-size: 12px; padding: 4px;")
                QMessageBox.information(self, "Succès", "Connexion au serveur ASAC réussie.")
            else:
                self.test_result.setText(f"❌ Erreur: {response.status_code} - {response.text[:100]}")
                self.test_result.setStyleSheet("color: #ef4444; font-size: 12px; padding: 4px;")
                
        except Exception as e:
            self.test_result.setText(f"❌ Erreur: {str(e)}")
            self.test_result.setStyleSheet("color: #ef4444; font-size: 12px; padding: 4px;")