from addons.Automobiles.controllers.automobile_controller import VehicleController, AuditVehicleLog
from addons.Automobiles.controllers.contacts_controller import ContactController, ContactAuditLog
from addons.Automobiles.controllers.contract_controller import ContractController
from addons.Automobiles.controllers.flotte_controller import FleetController
# from addons.Automobiles.controllers.automobile_tarif_controller import CompagnieController
from addons.Automobiles.controllers.compagnies_controller import CompagnieController
from addons.Automobiles.controllers.automobile_tarif_controller import TarifController
from addons.Automobiles.controllers.paiement_controller import PaymentController
from addons.Automobiles.controllers.reports_controller import ReportsController
from addons.Automobiles.controllers.api_asac_controller import ASACAPIController


class AutomobileMainController:
    def __init__(self, session, current_user_id):
        self.session = session
        self.user_id = current_user_id
        # On centralise tous les sous-contrôleurs ici
        self.vehicles = VehicleController(self.session)
        self.contacts = ContactController(self.session, current_user_id)
        self.fleets = FleetController(self.session, current_user_id)
        self.compagnies = CompagnieController(self.session, current_user_id)
        self.contracts = ContractController(self.session)
        self.tarifs = TarifController(self.session)
        self.paiements = PaymentController(self.session)
        self.reports = ReportsController(self.session, current_user_id)
        self.asac = ASACAPIController(self.session)
        # self.compagnies = FleetController(session, current_user_id)

    def is_asac_available(self):
        """Vérifie si l'API ASAC est disponible"""
        return self.asac_service is not None