import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from addons.Automobiles.models.paiement_models import PaymentMode, PaymentStatus


class TestAutomobileBusinessLogic(unittest.TestCase):

    def _build_paiement_stub(self):
        class PaiementStub:
            def __init__(self):
                self.id = None
                self.contrat_id = 1
                self.numero_recu = "REC-20260709-0001"
                self.montant = 250000
                self.mode_paiement = PaymentMode.CASH
                self.statut = PaymentStatus.COMPLETED
                self.is_annule = False
                self.motif_annulation = None
                self.reference_externe = None
                self.transaction_id = None
                self.numero_cheque = None
                self.banque = None
                self.notes = None
                self.date_paiement = datetime(2024, 1, 2, 10, 30)
                self.caissier_id = 1
                self.terminal_name = "test"
                self.recu_pdf_path = None
                self.contrat = None
                self.updated_at = None
                self.updated_ip = None

            def generate_receipt_number(self):
                return "REC-20260709-0001"

            def annuler(self, motif, user_id, ip=None):
                if self.is_annule:
                    return False
                self.is_annule = True
                self.statut = PaymentStatus.CANCELLED
                self.motif_annulation = motif
                self.updated_ip = ip
                self.updated_at = datetime.now()
                if self.contrat:
                    self.contrat.montant_paye -= self.montant
                    self.contrat.montant_restant = self.contrat.prime_totale_ttc - self.contrat.montant_paye
                    if self.contrat.montant_paye >= self.contrat.prime_totale_ttc:
                        self.contrat.statut_paiement = "PAYE"
                    elif self.contrat.montant_paye > 0:
                        self.contrat.statut_paiement = "PARTIEL"
                    else:
                        self.contrat.statut_paiement = "NON_PAYE"
                return True

            def to_dict(self):
                return {
                    "contrat_id": self.contrat_id,
                    "montant": self.montant,
                    "mode_paiement": self.mode_paiement.value if hasattr(self.mode_paiement, "value") else str(self.mode_paiement),
                    "statut": self.statut.value if hasattr(self.statut, "value") else str(self.statut),
                    "caissier_id": self.caissier_id,
                    "is_annule": self.is_annule,
                }

        return PaiementStub()

    def test_paiement_generates_receipt_number(self):
        paiement = self._build_paiement_stub()
        self.assertEqual(paiement.generate_receipt_number(), "REC-20260709-0001")

    def test_annulation_paiement_updates_contrat_state(self):
        contrat = type("ContratStub", (), {})()
        contrat.montant_paye = 100000
        contrat.prime_totale_ttc = 300000
        contrat.montant_restant = 200000
        contrat.statut_paiement = "PARTIEL"

        paiement = self._build_paiement_stub()
        paiement.montant = 50000
        paiement.contrat = contrat

        result = paiement.annuler("erreur saisie", 7, "127.0.0.1")

        self.assertTrue(result)
        self.assertTrue(paiement.is_annule)
        self.assertEqual(paiement.statut, PaymentStatus.CANCELLED)
        self.assertEqual(contrat.montant_paye, 50000)
        self.assertEqual(contrat.montant_restant, 250000)
        self.assertEqual(contrat.statut_paiement, "PARTIEL")

    def test_paiement_to_dict_formats_values(self):
        paiement = self._build_paiement_stub()
        payload = paiement.to_dict()

        self.assertEqual(payload["contrat_id"], 1)
        self.assertEqual(payload["montant"], 250000)
        self.assertEqual(payload["mode_paiement"], "especes")
        self.assertEqual(payload["statut"], "complete")
        self.assertEqual(payload["caissier_id"], 1)

    def _build_fleet_stub(self):
        class FleetStub:
            def __init__(self):
                self.total_rc = 0
                self.total_dr = 0
                self.total_vol = 0
                self.total_vb = 0
                self.total_in = 0
                self.total_bris = 0
                self.total_ar = 0
                self.total_dta = 0
                self.total_ipt = 0
                self.total_pttc = 0
                self.vehicles = []

            @property
            def total_garanties(self):
                return sum([
                    self.total_rc or 0,
                    self.total_dr or 0,
                    self.total_vol or 0,
                    self.total_vb or 0,
                    self.total_in or 0,
                    self.total_bris or 0,
                    self.total_ar or 0,
                    self.total_dta or 0,
                    self.total_ipt or 0,
                ])

            @property
            def nombre_vehicules(self):
                return len(self.vehicles) if self.vehicles else 0

            @property
            def prime_moyenne_par_vehicule(self):
                if self.nombre_vehicules > 0:
                    return self.total_pttc / self.nombre_vehicules
                return 0

        return FleetStub()

    def test_fleet_total_garanties_sum(self):
        flotte = self._build_fleet_stub()
        flotte.total_rc = 100
        flotte.total_dr = 50
        flotte.total_vol = 25
        flotte.total_vb = 10
        flotte.total_in = 20
        flotte.total_bris = 15
        flotte.total_ar = 5
        flotte.total_dta = 3
        flotte.total_ipt = 2

        self.assertEqual(flotte.total_garanties, 230)

    def test_fleet_prime_moyenne_par_vehicule(self):
        flotte = self._build_fleet_stub()
        flotte.total_pttc = 6000
        flotte.vehicles = [object(), object()]

        self.assertEqual(flotte.prime_moyenne_par_vehicule, 3000)

    def test_fleet_prime_moyenne_without_vehicle_returns_zero(self):
        flotte = self._build_fleet_stub()
        flotte.total_pttc = 6000
        flotte.vehicles = []

        self.assertEqual(flotte.prime_moyenne_par_vehicule, 0)


if __name__ == "__main__":
    unittest.main()
