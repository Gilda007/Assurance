import csv
import os
from datetime import datetime

class AuditReporter:
    @staticmethod
    def export_to_csv(logs):
        """Exporte les logs d'audit vers le dossier Documents de l'utilisateur"""
        # Chemin par défaut : /home/user/Documents/audit_export_date.csv
        home = os.path.expanduser("~")
        filename = os.path.join(home, f"Audit_AMS_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Utilisateur ID", "Action", "Détails", "Adresse IP"])
                for log in logs:
                    writer.writerow([
                        log.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                        log.user_id,
                        log.action,
                        log.details,
                        log.ip_address
                    ])
            return True, filename
        except Exception as e:
            return False, str(e)