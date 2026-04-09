# addons/Automobiles/controllers/payment_controller.py
import socket
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from core.database import SessionLocal
from core.logger import logger
from addons.Automobiles.models.paiement_models import AuditPaiementLog, Paiement
from addons.Automobiles.models.contract_models import Contrat


class PaymentController:
    """Contrôleur dédié à la gestion des paiements"""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session or SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    # ==================== CRUD PAIEMENTS ====================

# addons/Automobiles/controllers/payment_controller.py

    def create_payment(self, data: Dict, user_id: int, ip: str = None) -> Tuple[bool, Optional[Paiement], str]:
        """
        Crée un nouveau paiement pour un contrat
        """
        try:
            # Nettoyer la session
            # self.db.rollback()
            
            # Vérifier que le contrat existe
            contrat = self.db.query(Contrat).filter(Contrat.id == data.get('contrat_id')).first()
            print(contrat.id)
            if not contrat:
                return False, None, "Contrat non trouvé"
            
            # Vérifier que le montant ne dépasse pas le dû
            reste_a_payer = contrat.prime_totale_ttc - contrat.montant_paye
            if data.get('montant', 0) > reste_a_payer + 0.01:
                return False, None, f"Le montant dépasse le solde restant ({reste_a_payer:,.0f} FCFA)"
            
            # === CORRECTION: Mapping des modes de paiement ===
            mode_saisi = data.get('mode_paiement', 'CASH').upper().strip()
            
            # Mapping des valeurs françaises vers les valeurs PostgreSQL
            mode_mapping = {
                'ESPECES': 'CASH',
                'CASH': 'CASH',
                'ESPECE': 'CASH',
                'CARTE_BANCAIRE': 'CARD',
                'CARTE': 'CARD',
                'CARD': 'CARD',
                'VIREMENT': 'TRANSFER',
                'TRANSFER': 'TRANSFER',
                'CHEQUE': 'CHECK',
                'CHECK': 'CHECK',
                'ORANGE_MONEY': 'ORANGE_MONEY',
                'ORANGE': 'ORANGE_MONEY',
                'MTN_MONEY': 'MTN_MONEY',
                'MTN': 'MTN_MONEY',
                'WAVE': 'WAVE',
                'BANK_DEPOSIT': 'BANK_DEPOSIT',
                'DEPOT_BANCAIRE': 'BANK_DEPOSIT',
            }
            
            mode_paiement = mode_mapping.get(mode_saisi, 'CASH')
            print(f"Mode de paiement: {mode_saisi} -> {mode_paiement}")
            
            # Générer un numéro de reçu unique
            from datetime import datetime
            annee = datetime.now().strftime('%Y')
            mois = datetime.now().strftime('%m')
            jour = datetime.now().strftime('%d')
            count = self.db.query(Paiement).count() + 1
            numero_recu = f"REC-{annee}{mois}{jour}-{count:04d}"
            
            # Créer le paiement avec la bonne valeur enum
            nouveau_paiement = Paiement(
                contrat_id=data.get('contrat_id'),
                numero_recu=numero_recu,
                montant=data.get('montant'),
                mode_paiement=mode_paiement,  # Maintenant avec 'CASH', 'CARD', etc.
                reference_externe=data.get('reference_externe'),
                transaction_id=data.get('transaction_id'),
                numero_cheque=data.get('numero_cheque'),
                banque=data.get('banque'),
                statut='COMPLETED',  # Valeur en majuscules
                is_annule=False,
                notes=data.get('notes'),
                date_paiement=datetime.now(),
                caissier_id=user_id,
                terminal_name=socket.gethostname(),
                created_ip=ip,
                created_at=datetime.now(),
                created_by=user_id,
                updated_at=datetime.now(),
                updated_by=user_id
            )
            
            self.db.add(nouveau_paiement)
            self.db.flush()
            
            # Mettre à jour le contrat
            contrat.montant_paye += data.get('montant')
            contrat.updated_at = datetime.now()
            
            if contrat.montant_paye >= contrat.prime_totale_ttc:
                contrat.statut_paiement = "PAYE"
            elif contrat.montant_paye > 0:
                contrat.statut_paiement = "PARTIEL"
            
            # Journaliser l'audit
            audit = AuditPaiementLog(
                user_id=user_id,
                action='CREATE',
                payment_id=nouveau_paiement.id,
                contrat_id=contrat.id,
                new_values=str({
                    'numero_recu': numero_recu,
                    'montant': data.get('montant'),
                    'mode_paiement': mode_paiement
                }),
                ip_local=ip,
                timestamp=datetime.now()
            )
            self.db.add(audit)
            
            self.db.commit()
            self.db.refresh(nouveau_paiement)
            
            logger.info(f"Paiement créé: {numero_recu} pour contrat {contrat.numero_police}")
            return True, nouveau_paiement, "Paiement enregistré avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création paiement: {e}")
            import traceback
            traceback.print_exc()
            return False, None, str(e)        
        
    def update_payment(self, payment_id: int, data: Dict, user_id: int) -> Tuple[bool, Optional[Paiement], str]:
        """Met à jour un paiement existant"""
        try:
            paiement = self.get_payment_by_id(payment_id)
            if not paiement:
                return False, None, "Paiement non trouvé"
            
            # Sauvegarder les anciennes valeurs
            old_values = self._payment_to_dict(paiement)
            
            # Champs modifiables
            updatable_fields = ['statut', 'notes', 'numero_cheque', 'banque', 'transaction_id']
            
            for field in updatable_fields:
                if field in data:
                    setattr(paiement, field, data[field])
            
            ip_local, ip_public = self._get_ips()
            paiement.updated_by = user_id
            paiement.updated_ip = ip_local
            
            # Journaliser l'audit
            self._log_audit(
                user_id=user_id,
                action='UPDATE_PAYMENT',
                payment_id=payment_id,
                contrat_id=paiement.contrat_id,
                old_values=old_values,
                new_values=self._payment_to_dict(paiement),
                ip_local=ip_local,
                ip_public=ip_public
            )
            
            self.db.commit()
            self.db.refresh(paiement)
            
            logger.info(f"Paiement mis à jour: {paiement.numero_recu}")
            return True, paiement, "Paiement mis à jour avec succès"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour paiement: {e}")
            return False, None, str(e)
    
    def cancel_payment(self, payment_id: int, user_id: int, motif: str = "") -> Tuple[bool, str]:
        """Annule un paiement et ajuste le contrat"""
        try:
            paiement = self.get_payment_by_id(payment_id)
            if not paiement:
                return False, "Paiement non trouvé"
            
            if paiement.statut == 'CANCELLED':
                return False, "Ce paiement est déjà annulé"
            
            # Sauvegarder l'état
            old_values = self._payment_to_dict(paiement)
            
            # Mettre à jour le statut
            paiement.statut = 'CANCELLED'
            paiement.notes = f"{paiement.notes or ''}\nAnnulé le {datetime.now()}: {motif}".strip()
            
            ip_local, ip_public = self._get_ips()
            paiement.updated_by = user_id
            paiement.updated_ip = ip_local
            
            # Ajuster le contrat (déduire le montant annulé)
            contrat = self.db.query(Contrat).filter(Contrat.id == paiement.contrat_id).first()
            if contrat:
                nouveau_montant_paye = contrat.montant_paye - paiement.montant
                contrat.montant_paye = max(0, nouveau_montant_paye)
                
                # Mettre à jour le statut du contrat
                if contrat.montant_paye >= contrat.prime_totale_ttc:
                    contrat.statut_paiement = "PAYE"
                elif contrat.montant_paye > 0:
                    contrat.statut_paiement = "PARTIEL"
                else:
                    contrat.statut_paiement = "NON_PAYE"
                
                contrat.updated_by = user_id
                contrat.last_ip = ip_local
            
            # Journaliser l'audit
            self._log_audit(
                user_id=user_id,
                action='CANCEL_PAYMENT',
                payment_id=payment_id,
                contrat_id=paiement.contrat_id,
                old_values=old_values,
                new_values=self._payment_to_dict(paiement),
                ip_local=ip_local,
                ip_public=ip_public,
                notes=motif
            )
            
            self.db.commit()
            
            logger.info(f"Paiement annulé: {paiement.numero_recu} par user {user_id}")
            return True, f"Paiement annulé avec succès. Motif: {motif if motif else 'Non spécifié'}"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur annulation paiement: {e}")
            return False, str(e)
    
    # ==================== RECHERCHE PAIEMENTS ====================
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Paiement]:
        """Récupère un paiement par son ID"""
        return self.db.query(Paiement).filter(Paiement.is_annule == True).filter(Paiement.id == payment_id).first()
    
    def get_payment(self) -> Optional[Paiement]:
        """Récupère un paiement par son ID"""
        return self.db.query(Paiement).filter(Paiement.is_annule == True).first()
    
    def get_payment_by_receipt(self, numero_recu: str) -> Optional[Paiement]:
        """Récupère un paiement par son numéro de reçu"""
        return self.db.query(Paiement).filter(Paiement.is_annule == True).filter(Paiement.numero_recu == numero_recu).first()
    
    def get_payments_by_contract(self, contrat_id: int, limit: int = 100) -> List[Paiement]:
        """Récupère tous les paiements d'un contrat"""
        return self.db.query(Paiement).filter(Paiement.is_annule == True).filter(
            Paiement.contrat_id == contrat_id
        ).order_by(Paiement.date_operation.desc()).limit(limit).all()
    
    def get_payments_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Paiement]:
        """Récupère les paiements sur une période"""
        return self.db.query(Paiement).filter(Paiement.is_annule == True).filter(
            and_(
                Paiement.date_paiement >= start_date,
                Paiement.date_paiement <= end_date,
                Paiement.statut == 'COMPLETED'
            )
        ).order_by(Paiement.date_paiement.desc()).all()
    
    def get_payments_by_mode(self, mode_paiement: str, limit: int = 100) -> List[Paiement]:
        """Récupère les paiements par mode de paiement"""
        return self.db.query(Paiement).filter(Paiement.is_annule == True).filter(
            Paiement.mode_paiement == mode_paiement,
            Paiement.statut == 'COMPLETED'
        ).order_by(Paiement.date_paiement.desc()).limit(limit).all()
    
    def search_payments(self, filters: Dict) -> List[Paiement]:
        """
        Recherche avancée de paiements
        
        Args:
            filters: Dictionnaire de filtres
                - contrat_id: ID du contrat
                - mode_paiement: Mode de paiement
                - statut: Statut du paiement
                - date_min: Date minimum
                - date_max: Date maximum
                - montant_min: Montant minimum
                - montant_max: Montant maximum
                - numero_recu: Numéro de reçu
        """
        query = self.db.query(Paiement)
        
        if filters.get('contrat_id'):
            query = query.filter(Paiement.contrat_id == filters['contrat_id'])
        
        if filters.get('mode_paiement'):
            query = query.filter(Paiement.mode_paiement == filters['mode_paiement'])
        
        if filters.get('statut'):
            query = query.filter(Paiement.is_annule == filters['statut'])
        
        if filters.get('date_min'):
            query = query.filter(Paiement.date_operation >= filters['date_min'])
        
        if filters.get('date_max'):
            query = query.filter(Paiement.date_operation <= filters['date_max'])
        
        if filters.get('montant_min'):
            query = query.filter(Paiement.montant >= filters['montant_min'])
        
        if filters.get('montant_max'):
            query = query.filter(Paiement.montant <= filters['montant_max'])
        
        return query.order_by(Paiement.date_operation .desc()).all()
    
    # ==================== STATISTIQUES ET RAPPORTS ====================
    
    def get_payment_statistics(self, contrat_id: int = None, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """
        Génère des statistiques sur les paiements
        
        Args:
            contrat_id: Filtrer par contrat (optionnel)
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
        """
        query = self.db.query(Paiement).filter(Paiement.is_annule == 'COMPLETED')
        
        if contrat_id:
            query = query.filter(Paiement.contrat_id == contrat_id)
        
        if start_date:
            query = query.filter(Paiement.date_operation >= start_date)
        
        if end_date:
            query = query.filter(Paiement.date_operation <= end_date)
        
        # Statistiques générales
        total_paiements = query.count()
        montant_total = query.with_entities(func.sum(Paiement.montant)).scalar() or 0
        
        # Statistiques par mode de paiement
        stats_par_mode = {}
        modes = ['ESPECES', 'CARTE_BANCAIRE', 'VIREMENT', 'CHEQUE', 'ORANGE_MONEY', 'MTN_MONEY']
        
        for mode in modes:
            count = query.filter(Paiement.mode_paiement == mode).count()
            montant = query.filter(Paiement.mode_paiement == mode).with_entities(
                func.sum(Paiement.montant)
            ).scalar() or 0
            
            stats_par_mode[mode] = {
                'count': count,
                'montant': montant,
                'pourcentage': (count / total_paiements * 100) if total_paiements > 0 else 0
            }
        
        # Paiements par jour (pour les 30 derniers jours)
        from datetime import timedelta
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        paiements_recents = query.filter(Paiement.date_paiement >= thirty_days_ago).all()
        
        paiements_par_jour = {}
        for paiement in paiements_recents:
            jour = paiement.date_paiement.strftime('%Y-%m-%d')
            if jour not in paiements_par_jour:
                paiements_par_jour[jour] = {'count': 0, 'montant': 0}
            paiements_par_jour[jour]['count'] += 1
            paiements_par_jour[jour]['montant'] += paiement.montant
        
        return {
            'total_paiements': total_paiements,
            'montant_total': montant_total,
            'montant_moyen': montant_total / total_paiements if total_paiements > 0 else 0,
            'stats_par_mode': stats_par_mode,
            'paiements_par_jour': paiements_par_jour,
            'periode': {
                'debut': start_date.strftime('%Y-%m-%d') if start_date else 'Début',
                'fin': end_date.strftime('%Y-%m-%d') if end_date else 'Aujourd\'hui'
            }
        }
    
    def get_payment_schedule(self, contrat_id: int) -> List[Dict]:
        """
        Calcule l'échéancier des paiements pour un contrat mensualisé
        
        Args:
            contrat_id: ID du contrat
            
        Returns:
            Liste des échéances à venir
        """
        from addons.Automobiles.controllers.contract_controller import ContractController
        
        with ContractController(self.db) as contract_ctrl:
            contrat = contract_ctrl.get_contract_by_id(contrat_id)
            if not contrat or not contrat.commission_intermediaire:
                return []
            
            # Récupérer les paiements existants
            paiements = self.get_payments_by_contract(contrat_id)
            montant_total_paye = sum(p.montant for p in paiements if p.is_annule == False)
            
            mensualite = contrat.prime_totale_ttc / contrat.montant_paye
            paiements_effectues = int(montant_total_paye / mensualite) if mensualite > 0 else 0
            
            echeances = []
            date_prochaine = contrat.date_debut
            
            for i in range(paiements_effectues, contrat.montant_paye):
                if i > 0:
                    # Ajouter un mois à la date
                    if date_prochaine.month == 12:
                        date_prochaine = date_prochaine.replace(year=date_prochaine.year + 1, month=1)
                    else:
                        date_prochaine = date_prochaine.replace(month=date_prochaine.month + 1)
                
                echeances.append({
                    'numero': i + 1,
                    'date_echeance': date_prochaine.strftime('%d/%m/%Y'),
                    'montant': mensualite,
                    'statut': 'paye' if i < paiements_effectues else 'a_venir'
                })
            
            return echeances
    
    def generate_receipt_pdf(self, payment_id: int) -> Optional[str]:
        """
        Génère un PDF de reçu de paiement
        
        Args:
            payment_id: ID du paiement
            
        Returns:
            Chemin du fichier PDF généré ou None
        """
        try:
            paiement = self.get_payment_by_id(payment_id)
            if not paiement:
                return None
            
            # Ici, implémentez la génération PDF avec reportlab ou autre
            # Exemple avec reportlab:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            import os
            
            # Créer le répertoire s'il n'existe pas
            receipt_dir = "data/receipts"
            os.makedirs(receipt_dir, exist_ok=True)
            
            # Chemin du fichier
            filepath = f"{receipt_dir}/recu_{paiement.numero_recu}.pdf"
            
            # Générer le PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # En-tête
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "REÇU DE PAIEMENT")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"N° Reçu: {paiement.numero_recu}")
            c.drawString(50, height - 100, f"Date: {paiement.date_paiement.strftime('%d/%m/%Y %H:%M')}")
            
            # Détails
            y = height - 150
            c.drawString(50, y, "Détails du paiement:")
            y -= 30
            c.drawString(70, y, f"Montant: {paiement.montant:,.0f} FCFA")
            y -= 25
            c.drawString(70, y, f"Mode: {paiement.mode_paiement}")
            y -= 25
            if paiement.reference_externe:
                c.drawString(70, y, f"Référence: {paiement.reference_externe}")
                y -= 25
            
            c.save()
            
            # Mettre à jour le chemin dans la base
            paiement.recu_pdf_path = filepath
            self.db.commit()
            
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur génération PDF reçu: {e}")
            return None
    
    # ==================== MÉTHODES UTILITAIRES PRIVÉES ====================
    
    def _generate_receipt_number(self) -> str:
        """Génère un numéro de reçu unique"""
        from datetime import datetime
        annee = datetime.now().strftime('%Y')
        mois = datetime.now().strftime('%m')
        jour = datetime.now().strftime('%d')
        
        # Compter les reçus du jour
        count = self.db.query(Paiement).filter(
            Paiement.numero_recu.like(f'REC-{annee}{mois}{jour}%')
        ).count() + 1
        
        return f"REC-{annee}{mois}{jour}-{count:04d}"
    
    def _get_ips(self) -> Tuple[str, str]:
        """Récupère l'IP locale et publique"""
        ip_local = self._get_local_ip()
        ip_public = self._get_public_ip()
        return ip_local, ip_public
    
    def _get_local_ip(self) -> str:
        """Récupère l'IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_public_ip(self) -> str:
        """Récupère l'IP publique"""
        try:
            response = requests.get('https://api.ipify.org', timeout=3)
            return response.text
        except:
            return ""
    
    def _update_contract_after_payment(self, contrat: Contrat, montant: float, user_id: int, ip_local: str):
        """Met à jour le contrat après un paiement"""
        contrat.montant_paye += montant
        contrat.last_payment_date = datetime.now()
        
        # Mettre à jour le statut
        if contrat.montant_paye >= contrat.prime_totale_ttc:
            contrat.statut_paiement = "PAYE"
        elif contrat.montant_paye > 0:
            contrat.statut_paiement = "PARTIEL"
        
        contrat.updated_by = user_id
        contrat.last_ip = ip_local
    
    def _log_audit(self, user_id: int, action: str, payment_id: int, contrat_id: int,
                   old_values: Dict, new_values: Dict, ip_local: str, ip_public: str,
                   notes: str = None):
        """Journalise une action dans les logs d'audit"""
        try:
            # Vérifier si la table d'audit existe
            from addons.Automobiles.models.paiement_models import AuditPaiementLog
            
            audit_log = AuditPaiementLog(
                user_id=user_id,
                action=action,
                payment_id=payment_id,
                contrat_id=contrat_id,
                old_values=json.dumps(old_values, default=str) if old_values else None,
                new_values=json.dumps(new_values, default=str) if new_values else None,
                ip_local=ip_local,
                ip_public=ip_public,
                notes=notes
            )
            self.db.add(audit_log)
        except Exception as e:
            logger.error(f"Erreur journalisation audit paiement: {e}")
    
    def _payment_to_dict(self, paiement: Paiement) -> Dict:
        """Convertit un paiement en dictionnaire pour l'audit"""
        if not paiement:
            return {}
        
        return {
            'id': paiement.id,
            'contrat_id': paiement.contrat_id,
            'montant': paiement.montant,
            'mode_paiement': paiement.mode_paiement,
            'date_paiement': paiement.date_paiement.isoformat() if paiement.date_paiement else None,
            'reference_externe': paiement.reference_externe,
            'numero_recu': paiement.numero_recu,
            'statut': paiement.statut
        }