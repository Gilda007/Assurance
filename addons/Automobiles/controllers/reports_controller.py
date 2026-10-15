# addons/Automobiles/controllers/reports_controller.py
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from addons.Automobiles.models.contact_models import Contact
from addons.Automobiles.models.automobile_models import Vehicle
from addons.Automobiles.models.contract_models import ContractStatus, Contrat
from addons.Automobiles.models.compagnies_models import Compagnie
from addons.Automobiles.models.paiement_models import Paiement
from core.logger import logger
from core.local_db import cache
from typing import Dict, Any, List, Optional


class ReportsController:
    """Contrôleur pour la génération de rapports"""
    
    def __init__(self, session, current_user_id):
        self.session = session
        self.current_user_id = current_user_id
        print(f"✅ ReportsController initialisé avec user_id={current_user_id}")
    
    # ============================================================================
    # RAPPORTS DE CONTACTS
    # ============================================================================
    
    def get_contacts_report(self, date_start=None, date_end=None, type_contact=None, status=None):
        """Génère un rapport des contacts"""
        query = self.session.query(Contact)
        
        if date_start:
            query = query.filter(Contact.created_at >= date_start)
        if date_end:
            query = query.filter(Contact.created_at <= date_end)
        if type_contact and type_contact != "Tous":
            query = query.filter(Contact.type_client == type_contact)
        if status and status != "Tous":
            query = query.filter(Contact.vip_status == status)
        
        contacts = query.all()
        
        return {
            'title': 'Rapport des Contacts',
            'data': contacts,
            'stats': {
                'total': len(contacts),
                'assures': len([c for c in contacts if c.type_client == 'Assuré']),
                'prospects': len([c for c in contacts if c.type_client == 'Prospect']),
                'partenaires': len([c for c in contacts if c.type_client == 'Partenaire']),
                'actifs': len([c for c in contacts if c.vip_status == 'Actif']),
                'inactifs': len([c for c in contacts if c.vip_status == 'Inactif'])
            },
            'generated_at': datetime.now()
        }
    
    def get_contacts_by_location_report(self):
        """Rapport des contacts par ville/région"""
        contacts = self.session.query(Contact).all()
        
        cities = {}
        for c in contacts:
            city = c.ville or "Non spécifié"
            if city not in cities:
                cities[city] = {'count': 0, 'contacts': []}
            cities[city]['count'] += 1
            cities[city]['contacts'].append(c)
        
        return {
            'title': 'Répartition géographique des contacts',
            'data': cities,
            'total_cities': len(cities),
            'total_contacts': len(contacts),
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # RAPPORTS DE VÉHICULES
    # ============================================================================
    
    def get_vehicles_report(self, fleet_id=None, status=None, category=None, date_start=None, date_end=None):
        """Génère un rapport des véhicules"""
        query = self.session.query(Vehicle)
        
        if fleet_id:
            query = query.filter(Vehicle.fleet_id == fleet_id)
        if status and status != "Tous":
            query = query.filter(Vehicle.statut == status)
        if category and category != "Toutes":
            query = query.filter(Vehicle.categorie == category)
        if date_start:
            query = query.filter(Vehicle.created_at >= date_start)
        if date_end:
            query = query.filter(Vehicle.created_at <= date_end)
        
        vehicles = query.all()
        
        # Statistiques
        by_category = {}
        by_energy = {}
        total_prime = 0
        
        for v in vehicles:
            cat = v.categorie or "Non classé"
            by_category[cat] = by_category.get(cat, 0) + 1
            
            energy = v.energie or "Non spécifié"
            by_energy[energy] = by_energy.get(energy, 0) + 1
            
            total_prime += v.prime_nette or 0
        
        return {
            'title': 'Rapport des Véhicules',
            'data': vehicles,
            'stats': {
                'total': len(vehicles),
                'by_category': by_category,
                'by_energy': by_energy,
                'total_prime': total_prime,
                'active_count': len([v for v in vehicles if v.statut == 'ACTIF']),
                'expired_count': len([v for v in vehicles if v.statut == 'EXPIRE'])
            },
            'generated_at': datetime.now()
        }
    
    def get_vehicles_by_brand_report(self):
        """Rapport des véhicules par marque"""
        vehicles = self.session.query(Vehicle).all()
        
        brands = {}
        for v in vehicles:
            brand = v.marque or "Non spécifié"
            if brand not in brands:
                brands[brand] = {'count': 0, 'total_prime': 0}
            brands[brand]['count'] += 1
            brands[brand]['total_prime'] += v.prime_nette or 0
        
        return {
            'title': 'Parc automobile par marque',
            'data': brands,
            'total_brands': len(brands),
            'total_vehicles': len(vehicles),
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # RAPPORTS FINANCIERS
    # ============================================================================
    
    def get_financial_report(self, date_start=None, date_end=None):
        """Rapport financier des primes et paiements"""
        query = self.session.query(Contrat)
        
        if date_start:
            query = query.filter(Contrat.created_at >= date_start)
        if date_end:
            query = query.filter(Contrat.created_at <= date_end)
        
        contrats = query.all()
        
        total_primes = sum(c.prime_totale_ttc or 0 for c in contrats)
        total_commission = sum(c.commission_intermediaire or 0 for c in contrats)
        
        # Paiements
        paiements = self.session.query(Paiement).filter(
            Paiement.created_at >= date_start if date_start else True,
            Paiement.created_at <= date_end if date_end else True
        ).all()
        
        total_paid = sum(p.montant or 0 for p in paiements)
        pending_paid = sum(c.prime_totale_ttc or 0 for c in contrats if c.statut != 'PAYE')
        
        return {
            'title': 'Rapport Financier',
            'data': {
                'contrats': contrats,
                'paiements': paiements
            },
            'stats': {
                'total_primes': total_primes,
                'total_commission': total_commission,
                'total_paid': total_paid,
                'pending_paid': pending_paid,
                'contrats_count': len(contrats),
                'paiements_count': len(paiements)
            },
            'generated_at': datetime.now()
        }
    
    def get_premium_report_by_period(self, period='month'):
        """Rapport des primes par période (jour, mois, année)"""
        from calendar import monthrange
        
        now = datetime.now()
        
        if period == 'day':
            # 30 derniers jours
            dates = [(now - timedelta(days=i)).date() for i in range(30)]
            format_str = "%d/%m"
        elif period == 'month':
            # 12 derniers mois
            dates = [(now.replace(day=1) - timedelta(days=30*i)).replace(day=1).date() 
                     for i in range(12)]
            format_str = "%b %Y"
        else:  # year
            # 5 dernières années
            dates = [now.replace(year=now.year - i).replace(month=1, day=1).date() 
                     for i in range(5)]
            format_str = "%Y"
        
        premiums = []
        for d in dates:
            if period == 'day':
                start_date = datetime.combine(d, datetime.min.time())
                end_date = datetime.combine(d, datetime.max.time())
            elif period == 'month':
                last_day = monthrange(d.year, d.month)[1]
                start_date = datetime(d.year, d.month, 1)
                end_date = datetime(d.year, d.month, last_day, 23, 59, 59)
            else:
                start_date = datetime(d.year, 1, 1)
                end_date = datetime(d.year, 12, 31, 23, 59, 59)
            
            total = self.session.query(func.sum(Contrat.prime_totale_ttc)).filter(
                Contrat.created_at >= start_date,
                Contrat.created_at <= end_date
            ).scalar() or 0
            
            premiums.append({
                'period': d.strftime(format_str),
                'total': total,
                'date': d
            })
        
        return {
            'title': f'Évolution des primes - {period}',
            'data': premiums,
            'period': period,
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # RAPPORTS DE FLOTTES
    # ============================================================================
    
    def get_fleets_report(self):
        """Rapport des flottes et leurs véhicules"""
        from addons.Automobiles.models.flottes_models import Fleet
        
        fleets = self.session.query(Fleet).all()
        
        fleets_data = []
        for fleet in fleets:
            vehicles = [v for v in fleet.vehicles if v.is_active]
            total_prime = sum(v.prime_nette or 0 for v in vehicles)
            
            fleets_data.append({
                'fleet': fleet,
                'vehicle_count': len(vehicles),
                'total_prime': total_prime,
                'active_vehicles': len([v for v in vehicles if v.statut == 'ACTIF'])
            })
        
        return {
            'title': 'Rapport des Flottes',
            'data': fleets_data,
            'stats': {
                'total_fleets': len(fleets),
                'total_vehicles': sum(f['vehicle_count'] for f in fleets_data),
                'total_prime': sum(f['total_prime'] for f in fleets_data)
            },
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # RAPPORTS DE COMPAGNIES
    # ============================================================================
    
    def get_activity_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Génère un rapport d'activité"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Nouveaux contrats
            new_contracts = self.session.query(Contrat).filter(
                and_(
                    Contrat.created_at >= start_date,
                    Contrat.created_at <= end_date
                )
            ).count()
            
            # Nouveaux contacts
            new_contacts = self.session.query(Contact).filter(
                and_(
                    Contact.created_at >= start_date,
                    Contact.created_at <= end_date
                )
            ).count()
            
            # Nouveaux véhicules
            new_vehicles = self.session.query(Vehicle).filter(
                and_(
                    Vehicle.created_at >= start_date,
                    Vehicle.created_at <= end_date
                )
            ).count()
            
            # Contrats actifs
            active_contracts = self.session.query(Contrat).filter(
                Contrat.statut == ContractStatus.ACTIF
            ).count()
            
            # Chiffre d'affaires
            total_premium = self.session.query(func.sum(Contrat.prime_totale_ttc)).scalar() or 0
            
            return {
                'period': {
                    'start': start_date.strftime("%Y-%m-%d"),
                    'end': end_date.strftime("%Y-%m-%d")
                },
                'new_contracts': new_contracts,
                'new_contacts': new_contacts,
                'new_vehicles': new_vehicles,
                'active_contracts': active_contracts,
                'total_premium': float(total_premium)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur dans get_activity_report: {e}")
            raise
    
    def get_monthly_stats(self, year: int = None) -> List[Dict[str, Any]]:
        """Statistiques mensuelles"""
        if not year:
            year = datetime.now().year
        
        stats = []
        for month in range(1, 13):
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)
            
            contracts_count = self.session.query(Contrat).filter(
                and_(
                    Contrat.created_at >= month_start,
                    Contrat.created_at < month_end
                )
            ).count()
            
            premium_total = self.session.query(func.sum(Contrat.prime_totale_ttc)).filter(
                and_(
                    Contrat.created_at >= month_start,
                    Contrat.created_at < month_end
                )
            ).scalar() or 0
            
            stats.append({
                'month': month,
                'month_name': month_start.strftime("%B"),
                'contracts_count': contracts_count,
                'premium_total': float(premium_total)
            })
        
        return stats

    def get_compagnies_report(self):
        """Rapport des compagnies d'assurance"""
        compagnies = self.session.query(Compagnie).all()
        
        compagnies_data = []
        for cie in compagnies:
            vehicles = self.session.query(Vehicle).filter(Vehicle.compagny_id == cie.id).all()
            total_prime = sum(v.prime_nette or 0 for v in vehicles)
            
            compagnies_data.append({
                'compagnie': cie,
                'vehicle_count': len(vehicles),
                'total_prime': total_prime
            })
        
        return {
            'title': 'Rapport des Compagnies',
            'data': compagnies_data,
            'stats': {
                'total_compagnies': len(compagnies),
                'total_vehicles': sum(c['vehicle_count'] for c in compagnies_data),
                'total_prime': sum(c['total_prime'] for c in compagnies_data)
            },
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # RAPPORTS D'ACTIVITÉ
    # ============================================================================
    
    def get_activity_report(self, days=30):
        """Rapport d'activité des 30 derniers jours"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Nouveaux contacts
        new_contacts = self.session.query(Contact).filter(
            Contact.created_at >= start_date
        ).count()
        
        # Nouveaux véhicules
        new_vehicles = self.session.query(Vehicle).filter(
            Vehicle.created_at >= start_date
        ).count()
        
        # Nouveaux contrats
        new_contrats = self.session.query(Contrat).filter(
            Contrat.created_at >= start_date
        ).count()
        
        # Paiements récents
        recent_payments = self.session.query(Paiement).filter(
            Paiement.created_at >= start_date
        ).all()
        total_payments = sum(p.montant or 0 for p in recent_payments)
        
        return {
            'title': f"Rapport d'activité - {days} jours",
            'data': {
                'new_contacts': new_contacts,
                'new_vehicles': new_vehicles,
                'new_contrats': new_contrats,
                'total_payments': total_payments,
                'payments_count': len(recent_payments)
            },
            'generated_at': datetime.now(),
            'period_days': days
        }
    
    def get_top_performers_report(self, limit=10):
        """Rapport des meilleurs clients / contrats"""
        # Top clients par nombre de véhicules
        top_clients = self.session.query(
            Contact.id,
            Contact.nom,
            Contact.prenom,
            func.count(Vehicle.id).label('vehicle_count')
        ).outerjoin(Vehicle).group_by(Contact.id).order_by(
            func.count(Vehicle.id).desc()
        ).limit(limit).all()
        
        # Top contrats par montant
        top_contrats = self.session.query(Contrat).order_by(
            Contrat.prime_totale_ttc.desc()
        ).limit(limit).all()
        
        return {
            'title': 'Top Performers',
            'data': {
                'top_clients': top_clients,
                'top_contrats': top_contrats
            },
            'limit': limit,
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # RAPPORTS D'EXPIRATION
    # ============================================================================
    
    def get_expiring_contracts_report(self, days=30):
        """Rapport des contrats expirant bientôt"""
        today = datetime.now().date()
        expiry_date = today + timedelta(days=days)
        
        expiring_contrats = self.session.query(Contrat).filter(
            Contrat.date_fin >= today,
            Contrat.date_fin <= expiry_date,
            Contrat.statut != 'EXPIRE'
        ).all()
        
        return {
            'title': f'Contrats expirant dans {days} jours',
            'data': expiring_contrats,
            'stats': {
                'total': len(expiring_contrats),
                'next_7_days': len([c for c in expiring_contrats if c.date_fin <= today + timedelta(days=7)]),
                'next_15_days': len([c for c in expiring_contrats if c.date_fin <= today + timedelta(days=15)])
            },
            'generated_at': datetime.now(),
            'days': days
        }
    
    # ============================================================================
    # RAPPORTS D'IMPORTATION (pour l'API)
    # ============================================================================
    
    def get_import_report(self, date_start=None, date_end=None):
        """Rapport des imports effectués"""
        # Cette méthode dépend de votre système d'importation
        # À adapter selon votre structure
        
        return {
            'title': 'Rapport des imports',
            'data': [],
            'generated_at': datetime.now()
        }
    
    # ============================================================================
    # EXPORT DES RAPPORTS
    # ============================================================================
    
    def export_to_csv(self, data, filename):
        """Exporte un rapport au format CSV"""
        import csv
        import os
        from PySide6.QtWidgets import QFileDialog
        
        path, _ = QFileDialog.getSaveFileName(None, "Enregistrer le rapport", filename, "CSV (*.csv)")
        if not path:
            return None
        
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([f"Rapport généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"])
            writer.writerow([])
            writer.writerow(data.get('headers', []))
            for row in data.get('rows', []):
                writer.writerow(row)
        
        return path
    
    def export_to_pdf(self, report_data, output_path):
        """Exporte un rapport au format PDF"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        
        doc = SimpleDocTemplate(output_path, pagesize=landscape(A4))
        story = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=30
        )
        story.append(Paragraph(report_data.get('title', 'Rapport'), title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Date de génération
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=2
        )
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}", date_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des données
        table_data = report_data.get('table_data', [])
        if table_data:
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(table)
        
        doc.build(story)
        return output_path