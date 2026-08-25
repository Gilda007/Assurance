# addons/Automobiles/views/icons.py
"""
Fichier de configuration des icônes QtAwesome pour LOMETA
Utilise le préfixe 'mdi.' pour Material Design Icons
"""

import qtawesome as qta
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


# ============================================================================
# DICTIONNAIRE DES ICÔNES
# ============================================================================

ICONS = {
    # ============================================================
    # NAVIGATION & MENU
    # ============================================================
    'dashboard': 'mdi.view-dashboard',
    'vehicles': 'mdi.car',
    'clients': 'mdi.account-group',
    'companies': 'mdi.bank',
    'contracts': 'mdi.file-document',
    'claims': 'mdi.alert-circle',
    'expertise': 'mdi.account-tie',
    'garages': 'mdi.garage',
    'import': 'mdi.file-import',
    'reports': 'mdi.chart-bar',
    'settings': 'mdi.cog',
    'logout': 'mdi.logout',
    'menu': 'mdi.menu',
    'home': 'mdi.home',
    'help': 'mdi.help-circle',
    'fullscreen': 'mdi.fullscreen',
    'close': 'mdi.close',
    'minimize': 'mdi.minus',
    'maximize': 'mdi.square',
    
    # ============================================================
    # ACTIONS CRUD
    # ============================================================
    'add': 'mdi.plus',
    'edit': 'mdi.pencil',
    'delete': 'mdi.delete',
    'pen': 'mdi.pencil',
    'copy': 'mdi.content-copy',
    'save': 'mdi.content-save',
    'cancel': 'mdi.cancel',
    'search': 'mdi.magnify',
    'filter': 'mdi.filter',
    'refresh': 'mdi.sync',
    'export': 'mdi.export',
    'import': 'mdi.import',
    'print': 'mdi.printer',
    'view': 'mdi.eye',
    'eye': 'mdi.eye',  
    'hide': 'mdi.eye-off',
    'lock': 'mdi.lock',
    'unlock': 'mdi.lock-open',
    
    # ============================================================
    # PERSONNES & UTILISATEURS
    # ============================================================
    'user': 'mdi.account',
    'users': 'mdi.account-multiple',
    'user_check': 'mdi.account-check',
    'user_tie': 'mdi.account-tie',
    'user_astronaut': 'mdi.account-astronaut',
    'user_plus': 'mdi.account-plus',
    'user_minus': 'mdi.account-minus',
    'user_remove': 'mdi.account-remove',
    'user_clock': 'mdi.account-clock',
    'user_edit': 'mdi.account-edit',
    'user_key': 'mdi.account-key',
    'user_lock': 'mdi.account-lock',
    'user_voice': 'mdi.account-voice',
    'user_badge': 'mdi.account-badge',
    'user_card': 'mdi.account-card',
    'user_circle': 'mdi.account-circle',
    'user_convert': 'mdi.account-convert',
    'user_details': 'mdi.account-details',
    'user_off': 'mdi.account-off',
    'user_outline': 'mdi.account-outline',
    'user_supervisor': 'mdi.account-supervisor',
    'user_switch': 'mdi.account-switch',
    
    # ============================================================
    # VÉHICULES
    # ============================================================
    'car': 'mdi.car',
    'car_sports': 'mdi.car-sports',
    'car_hatchback': 'mdi.car-hatchback',
    'car_pickup': 'mdi.car-pickup',
    'car_estate': 'mdi.car-estate',
    'car_convertible': 'mdi.car-convertible',
    'car_limousine': 'mdi.car-limousine',
    'caravan': 'mdi.caravan',
    'bus': 'mdi.bus',
    'truck': 'mdi.truck',
    'tractor': 'mdi.tractor',
    'motorcycle': 'mdi.motorcycle',
    'bicycle': 'mdi.bicycle',
    'ambulance': 'mdi.ambulance',
    'police': 'mdi.car-police',
    'taxi': 'mdi.taxi',
    'tire': 'mdi.car-tire',
    'garage': 'mdi.garage',
    'garage_open': 'mdi.garage-open',
    'garage_variant': 'mdi.garage-variant',
    'car_wash': 'mdi.car-wash',
    'car_brake': 'mdi.car-brake',
    'car_light': 'mdi.car-light',
    'car_seat': 'mdi.car-seat',
    'car_shift': 'mdi.car-shift',
    'car_door': 'mdi.car-door',
    'car_engine': 'mdi.car-engine',
    'car_heater': 'mdi.car-heater',
    'car_side': 'mdi.car-side',
    'car_back': 'mdi.car-back',
    'car_brake_abs': 'mdi.car-brake-abs',
    'car_brake_fluid': 'mdi.car-brake-fluid',
    'car_brake_warning': 'mdi.car-brake-warning',
    'car_emergency': 'mdi.car-emergency',
    'car_esp': 'mdi.car-esp',
    'car_heated_seat': 'mdi.car-heated-seat',
    'car_horn': 'mdi.car-horn',
    'car_parking': 'mdi.car-parking',
    'car_seat_cooler': 'mdi.car-seat-cooler',
    'car_seat_heater': 'mdi.car-seat-heater',
    'car_speed': 'mdi.car-speed',
    'car_steering': 'mdi.car-steering',
    'car_suspension': 'mdi.car-suspension',
    'car_turbo': 'mdi.car-turbo',
    'car_wheel': 'mdi.car-wheel',
    'car_windshield': 'mdi.car-windshield',
    
    # ============================================================
    # DOCUMENTS & FICHIERS
    # ============================================================
    'file': 'mdi.file',
    'file_document': 'mdi.file-document',
    'file_pdf': 'mdi.file-pdf-box',
    'file_csv': 'mdi.file-delimited',
    'file_excel': 'mdi.file-excel',
    'file_word': 'mdi.file-word',
    'file_image': 'mdi.file-image',
    'file_import': 'mdi.file-import',
    'file_export': 'mdi.file-export',
    'file_upload': 'mdi.file-upload',
    'file_download': 'mdi.file-download',
    'file_edit': 'mdi.file-edit',
    'file_remove': 'mdi.file-remove',
    'file_restore': 'mdi.file-restore',
    'file_search': 'mdi.file-search',
    'file_send': 'mdi.file-send',
    'file_swap': 'mdi.file-swap',
    'file_compare': 'mdi.file-compare',
    'file_cloud': 'mdi.file-cloud',
    'file_lock': 'mdi.file-lock',
    'file_outline': 'mdi.file-outline',
    'file_plus': 'mdi.file-plus',
    'file_minus': 'mdi.file-minus',
    
    # ============================================================
    # CONTRATS & ASSURANCE
    # ============================================================
    'contract': 'mdi.file-document',
    'policy': 'mdi.shield-check',
    'insurance': 'mdi.shield',
    'claim': 'mdi.alert-circle',
    'payment': 'mdi.credit-card',
    'premium': 'mdi.coins',
    'renewal': 'mdi.reload',
    'endorsement': 'mdi.file-edit',
    'cancellation': 'mdi.cancel',
    'guarantee': 'mdi.shield-check',
    'coverage': 'mdi.umbrella',
    'franchise': 'mdi.percent',
    'deductible': 'mdi.cash-multiple',
    'indemnity': 'mdi.cash',
    'compensation': 'mdi.bank-transfer',
    
    # ============================================================
    # FINANCES & MONTANTS
    # ============================================================
    'money': 'mdi.cash',
    'money_multiple': 'mdi.cash-multiple',
    'credit_card': 'mdi.credit-card',
    'wallet': 'mdi.wallet',
    'bank': 'mdi.bank',
    'coins': 'mdi.coins',
    'currency_usd': 'mdi.currency-usd',
    'currency_eur': 'mdi.currency-eur',
    'currency_xaf': 'mdi.currency-cfa',
    'percent': 'mdi.percent',
    'invoice': 'mdi.receipt',
    'receipt': 'mdi.receipt',
    'chart_line': 'mdi.chart-line',
    'chart_bar': 'mdi.chart-bar',
    'chart_pie': 'mdi.chart-pie',
    'chart_scatter': 'mdi.chart-scatter',
    'chart_timeline': 'mdi.chart-timeline',
    'chart_waterfall': 'mdi.chart-waterfall',
    'chart_box': 'mdi.chart-box',
    'chart_bell': 'mdi.chart-bell',
    'chart_bubble': 'mdi.chart-bubble',
    'chart_donut': 'mdi.chart-donut',
    'chart_gantt': 'mdi.chart-gantt',
    'chart_sankey': 'mdi.chart-sankey',
    'chart_scatter_plot': 'mdi.chart-scatter-plot',
    'chart_stacked': 'mdi.chart-stacked',
    
    # ============================================================
    # STATUTS & INDICATEURS
    # ============================================================
    'check': 'mdi.check',
    'check_circle': 'mdi.check-circle',
    'check_box': 'mdi.checkbox-marked',
    'close_circle': 'mdi.close-circle',
    'close_box': 'mdi.close-box',
    'information': 'mdi.information',
    'information_outline': 'mdi.information-outline',
    'alert': 'mdi.alert',
    'alert_circle': 'mdi.alert-circle',
    'alert_octagon': 'mdi.alert-octagon',
    'warning': 'mdi.alert',
    'error': 'mdi.alert-circle',
    'success': 'mdi.check-circle',
    'pending': 'mdi.clock',
    'progress': 'mdi.progress-clock',
    'spinner': 'mdi.loading',
    'sync': 'mdi.sync',
    'sync_alert': 'mdi.sync-alert',
    'sync_off': 'mdi.sync-off',
    'check_decagram': 'mdi.check-decagram',
    'check_network': 'mdi.check-network',
    'check_network_outline': 'mdi.check-network-outline',
    'check_undetermined': 'mdi.check-undetermined',
    
    # ============================================================
    # COMMUNICATION
    # ============================================================
    'email': 'mdi.email',
    'email_open': 'mdi.email-open',
    'phone': 'mdi.phone',
    'phone_incoming': 'mdi.phone-incoming',
    'phone_outgoing': 'mdi.phone-outgoing',
    'phone_missed': 'mdi.phone-missed',
    'message': 'mdi.message',
    'message_text': 'mdi.message-text',
    'chat': 'mdi.chat',
    'chat_processing': 'mdi.chat-processing',
    'chat_sleep': 'mdi.chat-sleep',
    'bell': 'mdi.bell',
    'bell_ring': 'mdi.bell-ring',
    'bell_outline': 'mdi.bell-outline',
    'notification': 'mdi.notification-clear-all',
    'sms': 'mdi.sms',
    'whatsapp': 'mdi.whatsapp',
    'telegram': 'mdi.telegram',
    'wechat': 'mdi.wechat',
    
    # ============================================================
    # CALENDRIER & TEMPS
    # ============================================================
    'calendar': 'mdi.calendar',
    'calendar_month': 'mdi.calendar-month',
    'calendar_week': 'mdi.calendar-week',
    'calendar_today': 'mdi.calendar-today',
    'clock': 'mdi.clock',
    'clock_outline': 'mdi.clock-outline',
    'timer': 'mdi.timer',
    'timer_sand': 'mdi.timer-sand',
    'alarm': 'mdi.alarm',
    'schedule': 'mdi.schedule',
    'history': 'mdi.history',
    'update': 'mdi.update',
    
    # ============================================================
    # LOCALISATION & ADRESSE
    # ============================================================
    'map': 'mdi.map',
    'map_marker': 'mdi.map-marker',
    'map_marker_multiple': 'mdi.map-marker-multiple',
    'location': 'mdi.map-marker',
    'address': 'mdi.map-marker',
    'city': 'mdi.city',
    'city_variant': 'mdi.city-variant',
    'country': 'mdi.country',
    'globe': 'mdi.globe',
    'earth': 'mdi.earth',
    'navigation': 'mdi.navigation',
    'compass': 'mdi.compass',
    
    # ============================================================
    # CERTIFICATS & SÉCURITÉ
    # ============================================================
    'certificate': 'mdi.certificate',
    'shield': 'mdi.shield',
    'shield_check': 'mdi.shield-check',
    'shield_lock': 'mdi.shield-lock',
    'shield_key': 'mdi.shield-key',
    'key': 'mdi.key',
    'key_variant': 'mdi.key-variant',
    'lock': 'mdi.lock',
    'lock_open': 'mdi.lock-open',
    'lock_check': 'mdi.lock-check',
    'lock_question': 'mdi.lock-question',
    'security': 'mdi.security',
    'security_network': 'mdi.security-network',
    'badge': 'mdi.badge',
    'badge_account': 'mdi.badge-account',
    'badge_alert': 'mdi.badge-alert',
    'badge_check': 'mdi.badge-check',
    'fingerprint': 'mdi.fingerprint',
    'qrcode': 'mdi.qrcode',
    'barcode': 'mdi.barcode',
    
    # ============================================================
    # IMPRESSION & DOCUMENTS
    # ============================================================
    'printer': 'mdi.printer',
    'printer_3d': 'mdi.printer-3d',
    'scanner': 'mdi.scanner',
    'fax': 'mdi.fax',
    'stamp': 'mdi.stamp',
    'book': 'mdi.book',
    'book_open': 'mdi.book-open',
    'notebook': 'mdi.notebook',
    'notebook_plus': 'mdi.notebook-plus',
    'clipboard': 'mdi.clipboard',
    'clipboard_list': 'mdi.clipboard-list',
    'clipboard_check': 'mdi.clipboard-check',
    'clipboard_edit': 'mdi.clipboard-edit',
    
    # ============================================================
    # ICÔNES MÉTIERS
    # ============================================================
    'agent': 'mdi.account-tie',
    'broker': 'mdi.account-tie',
    'customer': 'mdi.account',
    'prospect': 'mdi.account-search',
    'supplier': 'mdi.account',
    'partner': 'mdi.handshake',
    'expert': 'mdi.account-tie',
    'consultant': 'mdi.account-tie',
    'manager': 'mdi.account-tie',
    'director': 'mdi.account-tie',
    'ceo': 'mdi.account-tie',
    
    # ============================================================
    # DIVERS
    # ============================================================
    'star': 'mdi.star',
    'star_outline': 'mdi.star-outline',
    'heart': 'mdi.heart',
    'heart_outline': 'mdi.heart-outline',
    'flag': 'mdi.flag',
    'flag_outline': 'mdi.flag-outline',
    'tag': 'mdi.tag',
    'tag_multiple': 'mdi.tag-multiple',
    'label': 'mdi.label',
    'label_outline': 'mdi.label-outline',
    'folder': 'mdi.folder',
    'folder_open': 'mdi.folder-open',
    'folder_plus': 'mdi.folder-plus',
    'folder_edit': 'mdi.folder-edit',
    'note': 'mdi.note',
    'note_plus': 'mdi.note-plus',
    'note_edit': 'mdi.note-edit',
    'note_remove': 'mdi.note-remove',
    'text': 'mdi.text',
    'text_box': 'mdi.text-box',
    'text_box_edit': 'mdi.text-box-edit',
    'list': 'mdi.format-list-bulleted',
    'list_numbered': 'mdi.format-list-numbered',
    'sort': 'mdi.sort',
    'sort_ascending': 'mdi.sort-ascending',
    'sort_descending': 'mdi.sort-descending',
    'grid': 'mdi.view-grid',
    'grid_plus': 'mdi.view-grid-plus',
    'list_view': 'mdi.view-list',
    'carousel': 'mdi.view-carousel',
    'dashboard': 'mdi.view-dashboard',
    'card': 'mdi.card',
    'card_plus': 'mdi.card-plus',
    'card_edit': 'mdi.card-edit',
    'card_account': 'mdi.card-account',
    'card_alert': 'mdi.card-alert',
    'card_check': 'mdi.card-check',
    'card_clock': 'mdi.card-clock',

    # ============================================================
    # MÉTÉO & THÈMES
    # ============================================================
    'sun': 'mdi.weather-sunny',
    'moon': 'mdi.weather-night',
    'cloud': 'mdi.weather-cloudy',
    'rain': 'mdi.weather-rainy',
    'storm': 'mdi.weather-storm',
    'snow': 'mdi.weather-snowy',
    'wind': 'mdi.weather-windy',
    'sunset': 'mdi.weather-sunset',
    'sunrise': 'mdi.weather-sunrise',
    'temperature': 'mdi.thermometer',
    
    # ============================================================
    # THÈMES & APPARENCE
    # ============================================================
    'theme_light': 'mdi.white-balance-sunny',
    'theme_dark': 'mdi.weather-night',
    'palette': 'mdi.palette',
    'contrast': 'mdi.contrast',
    'brightness': 'mdi.brightness-5',
    
    # ============================================================
    # NOTIFICATIONS & ALERTES (COMPLÉMENT)
    # ============================================================
    'notification': 'mdi.bell',
    'notification_clear': 'mdi.notification-clear-all',
    'alert_box': 'mdi.alert-box',
    'alert_rhombus': 'mdi.alert-rhombus',
    'bell_badge': 'mdi.bell-badge',
    'bell_cancel': 'mdi.bell-cancel',
    'bell_check': 'mdi.bell-check',
    'bell_plus': 'mdi.bell-plus',
    'bell_remove': 'mdi.bell-remove',
    'bell_sleep': 'mdi.bell-sleep',
    
    # ============================================================
    # CERTIFICATS (COMPLÉMENT)
    # ============================================================
    'certificate_outline': 'mdi.certificate-outline',
    'shield_crown': 'mdi.shield-crown',
    'shield_half': 'mdi.shield-half',
    'shield_plus': 'mdi.shield-plus',
    'shield_remove': 'mdi.shield-remove',
    'shield_star': 'mdi.shield-star',
    
    # ============================================================
    # UTILITAIRES DASHBOARD
    # ============================================================
    'widgets': 'mdi.widgets',
    'view_dashboard_edit': 'mdi.view-dashboard-edit',
    'view_dashboard_variant': 'mdi.view-dashboard-variant',
    'card_bulleted': 'mdi.card-bulleted',
    'card_bulleted_off': 'mdi.card-bulleted-off',
    'card_bulleted_settings': 'mdi.card-bulleted-settings',

    # ============================================================
    # AJOUTER DANS LA SECTION DIVERS
    # ============================================================
    'upload': 'mdi.upload',
    'download': 'mdi.download',
    'template': 'mdi.file-template',
    'file_upload': 'mdi.file-upload',
    'file_download': 'mdi.file-download',
    'data_matrix': 'mdi.data-matrix',
    'account_convert': 'mdi.account-convert',
    'calendar_edit': 'mdi.calendar-edit',
    'calendar_clock': 'mdi.calendar-clock',
    'calculator': 'mdi.calculator',
    'percent_outline': 'mdi.percent-outline',
    'cash': 'mdi.cash',
    'cash_multiple': 'mdi.cash-multiple',
    'bank_transfer': 'mdi.bank-transfer',
    'credit_card': 'mdi.credit-card',
    'wallet': 'mdi.wallet',
    'coins': 'mdi.coins',
    'currency_usd': 'mdi.currency-usd',
    'currency_eur': 'mdi.currency-eur',
    'currency_cfa': 'mdi.currency-cfa',

    # ============================================================
    # ICÔNES SUPPLÉMENTAIRES POUR L'IMPORT
    # ============================================================
    'file_excel_box': 'mdi.file-excel-box',
    'file_delimited': 'mdi.file-delimited',
    'spreadsheet': 'mdi.spreadsheet',
    'view_list': 'mdi.view-list',
    'view_grid': 'mdi.view-grid',
    'view_module': 'mdi.view-module',
    'sort_variant': 'mdi.sort-variant',
    'filter_variant': 'mdi.filter-variant',
    'play': 'mdi.play',
    'stop': 'mdi.stop',
    'pause': 'mdi.pause',
    'fast_forward': 'mdi.fast-forward',
    'rewind': 'mdi.rewind',
    'skip_next': 'mdi.skip-next',
    'skip_previous': 'mdi.skip-previous',

    # ============================================================
    # GARANTIES
    # ============================================================
    'shield_car': 'mdi.shield-car',
    'shield_airplane': 'mdi.shield-airplane',
    'shield_home': 'mdi.shield-home',
    'shield_health': 'mdi.shield-health',
    'umbrella': 'mdi.umbrella',
    'umbrella_outline': 'mdi.umbrella-outline',
    'security': 'mdi.security',
    'security_network': 'mdi.security-network',
    'fire': 'mdi.fire',
    'fire_extinguisher': 'mdi.fire-extinguisher',
    'water': 'mdi.water',
    'weather_lightning': 'mdi.weather-lightning',
    'weather_rainy': 'mdi.weather-rainy',
    'weather_snowy': 'mdi.weather-snowy',
    'weather_windy': 'mdi.weather-windy',
    'weather_cloudy': 'mdi.weather-cloudy',
    'weather_sunny': 'mdi.weather-sunny',
    'weather_night': 'mdi.weather-night',
    'glass': 'mdi.glass',
    'glass_fragile': 'mdi.glass-fragile',
    'car_wrench': 'mdi.car-wrench',
    'car_repair': 'mdi.car-repair',
    'wrench': 'mdi.wrench',
    'screwdriver': 'mdi.screwdriver',
    'hammer': 'mdi.hammer',
    'tools': 'mdi.tools',
    'engine': 'mdi.engine',
    'engine_off': 'mdi.engine-off',
    'gas_station': 'mdi.gas-station',
    'fuel': 'mdi.fuel',
    'battery': 'mdi.battery',
    'battery_charging': 'mdi.battery-charging',
    'lightbulb': 'mdi.lightbulb',
    'lightbulb_off': 'mdi.lightbulb-off',
    'flashlight': 'mdi.flashlight',
    'flashlight_off': 'mdi.flashlight-off',
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_icon(icon_name: str, color: str = None, size: int = 24) -> QIcon:
    """
    Récupère une icône QtAwesome par son nom
    
    Args:
        icon_name: Nom de l'icône dans le dictionnaire ICONS
        color: Couleur de l'icône (format hex ou nom)
        size: Taille de l'icône
    
    Returns:
        QIcon: Icône QtAwesome
    """
    if icon_name not in ICONS:
        print(f"⚠️ Icône inconnue: {icon_name}")
        return qta.icon('mdi.help-circle', color=color)
    
    icon_path = ICONS[icon_name]
    if color:
        return qta.icon(icon_path, color=color)
    return qta.icon(icon_path)


def get_icon_pixmap(icon_name: str, color: str = None, size: int = 24):
    """
    Récupère un pixmap d'icône QtAwesome
    
    Args:
        icon_name: Nom de l'icône dans le dictionnaire ICONS
        color: Couleur de l'icône (format hex ou nom)
        size: Taille de l'icône
    
    Returns:
        QPixmap: Pixmap de l'icône
    """
    icon = get_icon(icon_name, color)
    return icon.pixmap(QSize(size, size))


def get_icon_names(category: str = None) -> list:
    """
    Récupère la liste des noms d'icônes
    
    Args:
        category: Catégorie d'icônes (optionnel)
    
    Returns:
        list: Liste des noms d'icônes
    """
    if category:
        # Filtrer par catégorie (basé sur le nom)
        return [name for name in ICONS.keys() if category in name]
    return list(ICONS.keys())


def get_icon_by_category(category: str) -> dict:
    """
    Récupère les icônes par catégorie
    
    Args:
        category: Catégorie d'icônes
    
    Returns:
        dict: Dictionnaire des icônes de la catégorie
    """
    return {name: path for name, path in ICONS.items() if category in name or category in path}


# ============================================================================
# CONSTANTES POUR LES COULEURS
# ============================================================================

ICON_COLORS = {
    'primary': '#2563eb',
    'primary_dark': '#1e40af',
    'success': '#16a34a',
    'warning': '#f59e0b',
    'danger': '#dc2626',
    'info': '#7c3aed',
    'gray': '#64748b',
    'gray_dark': '#475569',
    'white': '#ffffff',
    'black': '#000000',
}


# ============================================================================
# CATÉGORIES D'ICÔNES
# ============================================================================

ICON_CATEGORIES = {
    'Navigation': [
        'dashboard', 'vehicles', 'clients', 'companies', 'contracts',
        'claims', 'expertise', 'garages', 'import', 'reports', 'settings'
    ],
    'Actions': [
        'add', 'edit', 'delete', 'copy', 'save', 'cancel', 'search',
        'filter', 'refresh', 'export', 'import', 'print', 'view'
    ],
    'Users': [
        'user', 'users', 'user_check', 'user_tie', 'user_plus',
        'user_minus', 'user_edit', 'user_key', 'user_lock'
    ],
    'Vehicles': [
        'car', 'car_sports', 'bus', 'truck', 'motorcycle', 'bicycle',
        'ambulance', 'police', 'taxi', 'garage'
    ],
    'Documents': [
        'file', 'file_document', 'file_pdf', 'file_csv', 'file_excel',
        'file_import', 'file_export', 'file_upload', 'file_download'
    ],
    'Finance': [
        'money', 'credit_card', 'wallet', 'bank', 'coins',
        'chart_line', 'chart_bar', 'chart_pie'
    ],
    'Status': [
        'check', 'check_circle', 'close_circle', 'information',
        'alert', 'warning', 'success', 'pending', 'spinner'
    ],
    'Communication': [
        'email', 'phone', 'message', 'chat', 'bell', 'notification'
    ],
    'Calendar': [
        'calendar', 'calendar_month', 'clock', 'timer', 'alarm', 'history'
    ],
    'Security': [
        'certificate', 'shield', 'shield_check', 'key', 'lock',
        'fingerprint', 'qrcode'
    ],
}


# ============================================================================
# EXPORT DES COULEURS
# ============================================================================

COLORS = ICON_COLORS