from addons.Automobiles.controllers.automobile_controller import VehicleController, AuditVehicleLog
from addons.Automobiles.controllers.contacts_controller import ContactController, ContactAuditLog
from addons.Automobiles.controllers.contract_controller import ContractController
from addons.Automobiles.controllers.flotte_controller import FleetController
# from addons.Automobiles.controllers.automobile_tarif_controller import CompagnieController
from addons.Automobiles.controllers.compagnies_controller import CompagnieController
from addons.Automobiles.controllers


class AutomobileMainController:
    def __init__(self, session, current_user_id):
        # On centralise tous les sous-contrôleurs ici
        self.vehicles = VehicleController(session)
        self.contacts = ContactController(session, current_user_id)
        self.fleets = FleetController(session, current_user_id)
        self.compagnies = CompagnieController(session, current_user_id)
        self.contracts = ContractController()
        # self.compagnies = FleetController(session, current_user_id)
        # On garde la session accessible au cas où
        self.session = session