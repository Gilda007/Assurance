from addons.Automobiles.views.audit_auto_view import AuditLogDialog
from addons.Automobiles.views.automobile_form_view import VehicleForm
from addons.Automobiles.views.automobile_view import VehiculeModuleView
from addons.Automobiles.views.contact_card_view import ContactCard
from addons.Automobiles.views.contact_form_view import ContactForm
from addons.Automobiles.views.contacts_view import ContactListView
from addons.Automobiles.views.compagnies_view import CompanyTariffView
from addons.Automobiles.views.flotte_form_view import FleetForm
# import addons.Automobiles.views.flottes_view
from addons.Automobiles.views.view import VehicleMainView
from addons.Automobiles.views.vehicle_detail_view import VehicleDetailView

class AutomobileMainView:
    def __init__(self, session, current_user_id):
        self.session = session
        self.user_id = current_user_id
        # On centralise tous les sous-contrôleurs ici
        self.auditlogdialog = AuditLogDialog(self.session)
        self.vehicle_form = VehicleForm(self.session, current_user_id)
        self.vehicule_mod = VehiculeModuleView(self.session, current_user_id)
        self.card_contact = ContactCard(self.session, current_user_id)
        self.contact_form = ContactForm()
        self.contact_list = ContactListView(self.session)
        self.compagny_tarif = CompanyTariffView(self.session, current_user_id)
        self.fleet_form = FleetForm(self.session, current_user_id)
        self.vehicle_main_view = VehicleMainView(self.session, current_user_id)
        self.vehicle_detail = VehicleDetailView()