import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from addons.Automobiles.models.tarif_models import AutomobileTarif  # Assurez-vous du chemin d'import
from core.alerts import AlertManager

class TarifController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_tarifs(self):
        """Récupère tous les tarifs actifs."""
        return self.db.query(AutomobileTarif).filter(AutomobileTarif.is_active == True).all()

    def get_tarifs_by_compagnie(self, cie_id):
        """Récupère les tarifs d'une compagnie spécifique."""
        return self.db.query(AutomobileTarif).filter(
            AutomobileTarif.cie_id == cie_id,
            AutomobileTarif.is_active == True
        ).all()

    def delete_tarif(self, tarif_id):
        """Suppression logique d'un tarif."""
        tarif = self.db.query(AutomobileTarif).filter(AutomobileTarif.id == tarif_id).first()
        if tarif:
            tarif.is_active = False
            self.db.commit()
            return True, "Tarif supprimé"
        return False, "Tarif non trouvé"

    d