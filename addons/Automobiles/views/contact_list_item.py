# addons/Automobiles/views/contact_list_item.py
class ContactListItem:
    """Wrapper pour afficher des contacts et des chauffeurs dans la même liste"""
    
    def __init__(self, source_type, data):
        """
        Args:
            source_type: 'contact' ou 'driver'
            data: Objet Contact ou Driver
        """
        self.source_type = source_type
        self.data = data
        
    @property
    def id(self):
        return getattr(self.data, 'id', None)
    
    @property
    def nom(self):
        return getattr(self.data, 'nom', '')
    
    @property
    def prenom(self):
        return getattr(self.data, 'prenom', '')
    
    @property
    def telephone(self):
        return getattr(self.data, 'telephone', '')
    
    @property
    def email(self):
        return getattr(self.data, 'email', '')
    
    @property
    def display_type(self):
        return "Souscripteur" if self.source_type == 'contact' else "Chauffeur"
    
    @property
    def nature(self):
        if self.source_type == 'contact':
            return getattr(self.data, 'nature', '')
        return ''
    
    @property
    def statut(self):
        return getattr(self.data, 'statut', 'Actif')
    
    @property
    def code_client(self):
        if self.source_type == 'contact':
            return getattr(self.data, 'code_client', '')
        return ''
    
    @property
    def code_chauffeur(self):
        if self.source_type == 'driver':
            return getattr(self.data, 'code_chauffeur', '')
        return ''
    
    @property
    def specialite(self):
        if self.source_type == 'driver':
            return getattr(self.data, 'specialite', '')
        return ''