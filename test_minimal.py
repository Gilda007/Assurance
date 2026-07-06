"""
╔══════════════════════════════════════════════════════════════════╗
║         🚀 HOLLYWOOD MONITOR - Cyberpunk Dashboard             ║
║     Tableau de bord système style néon avec données réelles    ║
╚══════════════════════════════════════════════════════════════════╝
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Placeholder, Log, Label, Static, Button
from textual.containers import Grid, Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import events
from textual.binding import Binding
import asyncio
import random
from datetime import datetime
import sys

# ============================================================================
# WIDGETS AVANCÉS
# ============================================================================

class GlitchText(Static):
    """Texte avec effet glitch cyberpunk"""
    text = reactive("")
    
    def render(self) -> str:
        import time
        t = int(time.time() * 2) % 20
        if t < 2:
            return f"[bold magenta]💀 {self.text}[/bold magenta]"
        elif t < 4:
            return f"[bold cyan]☠️ {self.text}[/bold cyan]"
        else:
            return f"[bold green]▶ {self.text}[/bold green]"

class NeonMetric(Static):
    """Widget métrique avec effet néon"""
    value = reactive("0")
    label = reactive("")
    icon = reactive("📊")
    unit = reactive("")
    trend = reactive("stable")
    color = reactive("#00ff88")
    
    def render(self) -> str:
        colors = {
            "up": "#00ff88",
            "down": "#ff0055",
            "stable": "#ffaa00"
        }
        arrows = {
            "up": "▲",
            "down": "▼",
            "stable": "◆"
        }
        color = colors.get(self.trend, "#00ff88")
        arrow = arrows.get(self.trend, "•")
        
        return (
            f"{self.icon} [bold]{self.label}[/bold]\n"
            f"[bold {color}]{self.value} {self.unit}[/bold {color}]\n"
            f"[dim]{arrow} {self.trend.upper()}[/dim]"
        )

class AnimatedProgress(Static):
    """Barre de progression animée"""
    value = reactive(0)
    label = reactive("")
    color = reactive("#00ff88")
    
    def render(self) -> str:
        bar_length = 30
        filled = int(self.value / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"{self.label}\n[{bar}] {self.value:.1f}%"

class Sparkline(Static):
    """Graphique ASCII en temps réel"""
    data = reactive([])
    label = reactive("")
    
    def render(self) -> str:
        if not self.data:
            return f"{self.label}\n[dim]En attente de données...[/dim]"
        
        levels = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        max_val = max(self.data) if self.data else 1
        
        points = ""
        for val in self.data[-30:]:
            idx = min(7, int(7 * val / max_val)) if max_val > 0 else 0
            points += levels[idx]
        
        return f"{self.label}\n[bold cyan]{points}[/bold cyan]"

class PulseText(Static):
    """Texte avec effet de pulsation"""
    text = reactive("")
    
    def render(self) -> str:
        import time
        intensity = abs((int(time.time() * 2) % 8) - 4)
        colors = ["#00ff88", "#00ffaa", "#00ffcc", "#88ff88", "#00ffcc", "#00ffaa", "#00ff88"]
        return f"[bold {colors[intensity]}]{self.text}[/bold {colors[intensity]}]"

# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

class HollywoodRealDataApp(App):
    """Application de monitoring cyberpunk"""
    
    CSS = """
    /* === Layout Principal === */
    Grid {
        grid-size: 3 2;
        grid-gutter: 1;
    }
    
    /* === Panneaux Néon === */
    .panel {
        border: solid #00ff88 50%;
        background: #0a0a0a;
        color: #00ff88;
        padding: 1;
        height: 100%;
    }
    
    .panel-neon {
        border: solid #ff00ff 50%;
        background: #0a0a0a;
        color: #ff00ff;
        padding: 1;
        height: 100%;
    }
    
    .panel-cyber {
        border: solid #00ffff 50%;
        background: #0a0a0a;
        color: #00ffff;
        padding: 1;
        height: 100%;
    }
    
    .panel:hover {
        border: solid #00ffcc;
        background: #111111;
    }
    
    /* === Titres === */
    .panel-title {
        text-style: bold;
        color: #00ff88;
        border-bottom: solid #00ff00 50%;
        padding-bottom: 1;
        margin-bottom: 1;
    }
    
    .panel-title-cyber {
        text-style: bold;
        color: #00ffff;
        border-bottom: solid #00ffff 50%;
        padding-bottom: 1;
        margin-bottom: 1;
    }
    
    .panel-title-neon {
        text-style: bold;
        color: #ff00ff;
        border-bottom: solid #ff00ff 50%;
        padding-bottom: 1;
        margin-bottom: 1;
    }
    
    /* === En-tête et Pied de page === */
    Header {
        background: #0a0a0a;
        color: #00ff88;
        border-bottom: solid #00ff88 50%;
    }
    
    Footer {
        background: #0a0a0a;
        color: #00ff88;
        border-top: solid #00ff88 50%;
    }
    
    /* === Boutons === */
    Button {
        background: #1a1a1a;
        color: #00ff88;
        border: solid #00ff88 50%;
        padding: 1;
    }
    
    Button:hover {
        background: #00ff88;
        color: #0a0a0a;
    }
    
    /* === Statuts === */
    .status-ok { color: #00ff00; }
    .status-warning { color: #ffaa00; }
    .status-error { color: #ff0000; }
    
    /* === Grille des métriques === */
    #metrics_container {
        grid-size: 2 3;
        grid-gutter: 1;
    }
    
    /* === Animations === */
    .glitch {
        text-style: bold;
        color: #ff00ff;
    }
    
    .pulse {
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quitter"),
        Binding("c", "clear", "Effacer logs"),
        Binding("r", "refresh", "Rafraîchir"),
        Binding("d", "dark_mode", "Dark/Light"),
        Binding("f", "fullscreen", "Plein écran"),
        Binding("?", "help", "Aide"),
    ]

    def __init__(self):
        super().__init__()
        self._is_running = True
        self.alert_count = 0
        self.trend_data = []
        self.connection_history = []
        self.start_time = datetime.now()
        
        self.log_widget = None
        self.cpu_metric = None
        self.ram_metric = None
        self.disk_metric = None
        self.network_in_metric = None
        self.network_out_metric = None
        self.connections_metric = None
        self.bandwidth_progress = None
        self.sparkline = None
        self.uptime_label = None
        self.system_status = None
        self.server_status = None
        self.network_status = None
        self.security_status = None

    def compose(self) -> ComposeResult:
        """Composition de l'interface"""
        yield Header(show_clock=True)
        
        with Container():
            # ===== BARRE DE STATUT =====
            with Horizontal():
                yield PulseText("⚡ SYSTEM READY", id="system_status")
                yield PulseText("🖥️ SERVER ONLINE", id="server_status")
                yield PulseText("🌐 NETWORK ACTIVE", id="network_status")
                yield PulseText("🔒 SECURE", id="security_status")
                yield PulseText(f"⏱️ UPTIME: 0s", id="uptime_label")
            
            # ===== GRILLE PRINCIPALE =====
            with Grid():
                # Panel 1: Logs
                with Vertical(classes="panel"):
                    yield Label("📋 LOGS EN TEMPS RÉEL", classes="panel-title-cyber")
                    yield Log(id="logs_nginx")
                
                # Panel 2: Docker
                with Vertical(classes="panel-neon"):
                    yield Label("🐳 CONTENEURS DOCKER", classes="panel-title-neon")
                    yield Placeholder(id="docker_placeholder")
                
                # Panel 3: Métriques
                # Panel 3: Métriques
            with Vertical(classes="panel-cyber"):
                yield Label("💻 MÉTRIQUES SYSTÈME", classes="panel-title-cyber")
                with Grid(id="metrics_container"):
                    cpu_metric = NeonMetric(id="cpu_metric")
                    cpu_metric.label = "CPU"
                    cpu_metric.icon = "⚡"
                    cpu_metric.value = "0%"
                    yield cpu_metric
                    
                    ram_metric = NeonMetric(id="ram_metric")
                    ram_metric.label = "RAM"
                    ram_metric.icon = "🧠"
                    ram_metric.value = "0%"
                    yield ram_metric
                    
                    disk_metric = NeonMetric(id="disk_metric")
                    disk_metric.label = "DISK"
                    disk_metric.icon = "💾"
                    disk_metric.value = "0%"
                    yield disk_metric
                    
                    network_in_metric = NeonMetric(id="network_in_metric")
                    network_in_metric.label = "RÉSEAU IN"
                    network_in_metric.icon = "📥"
                    network_in_metric.value = "0 KB/s"
                    yield network_in_metric
                    
                    network_out_metric = NeonMetric(id="network_out_metric")
                    network_out_metric.label = "RÉSEAU OUT"
                    network_out_metric.icon = "📤"
                    network_out_metric.value = "0 KB/s"
                    yield network_out_metric
                    
                    connections_metric = NeonMetric(id="connections_metric")
                    connections_metric.label = "CONNEXIONS"
                    connections_metric.icon = "🔗"
                    connections_metric.value = "0"
                    yield connections_metric
                
                # Panel 4: SSL
                with Vertical(classes="panel"):
                    yield Label("🔒 SÉCURITÉ SSL", classes="panel-title")
                    yield Placeholder(id="ssl_placeholder")
                
                # Panel 5: Réseau
                with Vertical(classes="panel-cyber"):
                    yield Label("🌐 FLUX RÉSEAU", classes="panel-title-cyber")
                    bandwidth_progress = AnimatedProgress(id="bandwidth_progress")
                    bandwidth_progress.label = "Bandwidth"
                    bandwidth_progress.value = 0
                    yield bandwidth_progress

                    sparkline = Sparkline(id="sparkline")
                    sparkline.label = "📈 Débit"
                    yield sparkline
                
                # Panel 6: Alertes
                with Vertical(classes="panel-neon"):
                    yield GlitchText("🚨 ALERTES", classes="panel-title-neon")
                    yield Placeholder(id="alerts_placeholder")
        
        yield Footer()

    async def on_mount(self):
        """Initialisation au démarrage"""
        self.log_widget = self.query_one("#logs_nginx", Log)
        self.cpu_metric = self.query_one("#cpu_metric", NeonMetric)
        self.ram_metric = self.query_one("#ram_metric", NeonMetric)
        self.disk_metric = self.query_one("#disk_metric", NeonMetric)
        self.network_in_metric = self.query_one("#network_in_metric", NeonMetric)
        self.network_out_metric = self.query_one("#network_out_metric", NeonMetric)
        self.connections_metric = self.query_one("#connections_metric", NeonMetric)
        self.bandwidth_progress = self.query_one("#bandwidth_progress", AnimatedProgress)
        self.sparkline = self.query_one("#sparkline", Sparkline)
        self.alerts_placeholder = self.query_one("#alerts_placeholder", Placeholder)
        self.docker_placeholder = self.query_one("#docker_placeholder", Placeholder)
        self.ssl_placeholder = self.query_one("#ssl_placeholder", Placeholder)
        self.uptime_label = self.query_one("#uptime_label", PulseText)
        self.system_status = self.query_one("#system_status", PulseText)
        self.server_status = self.query_one("#server_status", PulseText)
        self.network_status = self.query_one("#network_status", PulseText)
        self.security_status = self.query_one("#security_status", PulseText)
        
        tasks = [
            self.update_uptime(),
            self.simuler_logs(),
            self.simuler_metriques(),
            self.simuler_docker(),
            self.simuler_ssl(),
            self.simuler_flux_reseau(),
            self.simuler_alertes(),
            self.simuler_statuts(),
        ]
        
        for task in tasks:
            asyncio.create_task(task)

    # ============================================================================
    # TÂCHES DE FOND
    # ============================================================================

    async def update_uptime(self):
        """Met à jour l'uptime en temps réel"""
        while self._is_running:
            elapsed = int((datetime.now() - self.start_time).total_seconds())
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.uptime_label.text = f"⏱️ UPTIME: {hours:02d}:{minutes:02d}:{seconds:02d}"
            await asyncio.sleep(1)

    async def simuler_logs(self):
        """Simulation de logs avec différents niveaux"""
        patterns = [
            ("[INFO]", "Connexion depuis 192.168.1.{}:443"),
            ("[INFO]", "Requête GET /api/v1/users - 200 OK"),
            ("[INFO]", "Requête POST /api/v1/auth - 200 OK"),
            ("[INFO]", "Cache hit pour /static/app.css"),
            ("[WARNING]", "Tentative d'accès à /admin depuis 10.0.0.{}"),
            ("[WARNING]", "Temps de réponse: {}ms (seuil: 500ms)"),
            ("[ERROR]", "Timeout sur la base de données: connexion lente"),
            ("[ERROR]", "Erreur 500 sur /api/v1/products"),
            ("[SUCCESS]", "Sauvegarde automatique effectuée: {} éléments"),
            ("[SUCCESS]", "Certificat SSL renouvelé avec succès"),
        ]
        
        while self._is_running:
            try:
                idx = random.randint(0, len(patterns) - 1)
                level, pattern = patterns[idx]
                
                if "{}" in pattern:
                    value = random.randint(1, 999)
                    line = f"{level} {pattern.format(value)}"
                else:
                    line = f"{level} {pattern}"
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_widget.write_line(f"[{timestamp}] {line}")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            except Exception:
                await asyncio.sleep(1)

    async def simuler_metriques(self):
        """Simulation des métriques système"""
        while self._is_running:
            cpu = max(0, min(100, random.gauss(50, 20)))
            ram = max(0, min(100, random.gauss(60, 15)))
            disk = max(0, min(100, random.gauss(50, 25)))
            
            self.cpu_metric.value = f"{cpu:.1f}"
            self.cpu_metric.trend = "up" if cpu > 70 else "down" if cpu < 30 else "stable"
            self.cpu_metric.color = "#ff0044" if cpu > 80 else "#00ff88" if cpu < 50 else "#ffaa00"
            
            self.ram_metric.value = f"{ram:.1f}"
            self.ram_metric.trend = "up" if ram > 80 else "down" if ram < 50 else "stable"
            self.ram_metric.color = "#ff0044" if ram > 90 else "#00ff88" if ram < 60 else "#ffaa00"
            
            self.disk_metric.value = f"{disk:.1f}"
            self.disk_metric.trend = "up" if disk > 75 else "down" if disk < 40 else "stable"
            self.disk_metric.color = "#ff0044" if disk > 85 else "#00ff88" if disk < 50 else "#ffaa00"
            
            net_in = random.uniform(10, 800)
            net_out = random.uniform(5, 300)
            self.network_in_metric.value = f"{net_in:.0f}"
            self.network_in_metric.trend = "up" if net_in > 500 else "down" if net_in < 100 else "stable"
            
            self.network_out_metric.value = f"{net_out:.0f}"
            self.network_out_metric.trend = "up" if net_out > 200 else "down" if net_out < 50 else "stable"
            
            conn = random.randint(10, 350)
            self.connections_metric.value = str(conn)
            self.connections_metric.trend = "up" if conn > 250 else "down" if conn < 50 else "stable"
            
            await asyncio.sleep(2)

    async def simuler_docker(self):
        """Simulation des conteneurs Docker"""
        containers = [
            ("nginx-proxy", "running", "2h", "🟢"),
            ("postgres-15", "running", "5d", "🟢"),
            ("redis-cache", "running", "12h", "🟢"),
            ("app-web", "running", "3h", "🟢"),
            ("app-worker", "running", "1d", "🟢"),
            ("monitoring", "running", "7d", "🟢"),
            ("backup", "exited", "0s", "🔴"),
        ]
        
        while self._is_running:
            text = "📦 CONTENEURS DOCKER\n\n"
            
            active = sum(1 for c in containers if c[1] == "running")
            text += f"🚀 Actifs: {active}/{len(containers)}\n\n"
            
            for name, status, uptime, icon in containers:
                if random.random() < 0.03:
                    new_status = "exited" if status == "running" else "running"
                    containers[containers.index((name, status, uptime, icon))] = \
                        (name, new_status, uptime, "🔴" if new_status == "exited" else "🟢")
                
                color = "#00ff88" if status == "running" else "#ff0044"
                text += f"[bold {color}]{icon}[/bold {color}] {name}\n  {status} ({uptime})\n"
            
            self.docker_placeholder.update(text)
            await asyncio.sleep(3)

    async def simuler_ssl(self):
        """Simulation SSL"""
        while self._is_running:
            days_left = random.randint(15, 365)
            status = "✅ VALIDE" if days_left > 30 else "⚠️ EXPIRATION"
            color = "#00ff88" if days_left > 30 else "#ffaa00"
            
            text = f"""
            [{status}]({color})
            📅 Expire: {datetime.now().year + 1}-12-31
            ⏳ Jours restants: {days_left}
            🔑 SHA-256: 3A:4B:5C:{random.randint(10,99):02X}:{random.randint(10,99):02X}...
            🛡️ Protocole: TLS 1.3
            🔐 Cipher: AES-256-GCM
            """
            self.ssl_placeholder.update(text)
            self.security_status.text = f"🔒 {status}" if days_left > 30 else f"🔒 {status}"
            await asyncio.sleep(8)

    async def simuler_flux_reseau(self):
        """Simulation du flux réseau"""
        data_points = []
        while self._is_running:
            bandwidth = random.uniform(10, 95)
            self.bandwidth_progress.value = bandwidth
            data_points.append(bandwidth)
            if len(data_points) > 40:
                data_points.pop(0)
            self.sparkline.data = data_points
            
            await asyncio.sleep(1.5)

    async def simuler_alertes(self):
        """Simulation d'alertes"""
        messages = [
            ("🟢", "Système stable - Aucune alerte", "ok"),
            ("🟡", "CPU élevé: 85% - Surveillance active", "warning"),
            ("🔴", "Erreur 500 sur /api/v1/payment - Investigation", "error"),
            ("🟢", "Attaque DDOS détectée et bloquée", "ok"),
            ("🟡", "Espace disque: 75% utilisé - Nettoyage recommandé", "warning"),
            ("🔴", "Timeout base de données - Connexion rétablie", "error"),
            ("🟢", "Mise à jour de sécurité installée avec succès", "ok"),
            ("🟡", "Tentatives de connexion suspectes: 3", "warning"),
        ]
        
        while self._is_running:
            self.alert_count += 1
            icon, msg, severity = random.choice(messages)
            
            alerts_text = f"🚨 DERNIÈRES ALERTES\n\n"
            alerts_text += f"📊 Total: {self.alert_count}\n"
            alerts_text += f"📋 {icon} {msg}\n"
            alerts_text += f"🕐 {datetime.now().strftime('%H:%M:%S')}"
            
            self.alerts_placeholder.update(alerts_text)
            
            if severity in ("warning", "error"):
                self.notify(
                    f"{icon} {msg}",
                    title="🚨 ALERTE",
                    severity=severity,
                    timeout=4
                )
            
            await asyncio.sleep(random.uniform(4, 8))

    async def simuler_statuts(self):
        """Simulation des statuts avec transitions réalistes"""
        while self._is_running:
            self.system_status.text = "⚡ SYSTEM READY" if random.random() > 0.15 else "⚡ SYSTEM WARNING"
            self.server_status.text = "🖥️ SERVER ONLINE" if random.random() > 0.2 else "🖥️ SERVER LOADED"
            self.network_status.text = "🌐 NETWORK ACTIVE" if random.random() > 0.1 else "🌐 NETWORK SLOW"
            await asyncio.sleep(4)

    # ============================================================================
    # INTERACTIVITÉ
    # ============================================================================

    def action_quit(self):
        """Quitte l'application"""
        self._is_running = False
        self.exit()

    def action_clear(self):
        """Efface les logs"""
        if self.log_widget:
            self.log_widget.clear()
            self.log_widget.write_line("[SUCCESS] 🧹 Logs effacés avec succès!")
            self.notify("🧹 Logs effacés", severity="information")

    def action_refresh(self):
        """Rafraîchit les données"""
        self.notify("🔄 Rafraîchissement en cours...", severity="information")
        self.log_widget.write_line("[INFO] 🔄 Rafraîchissement demandé par l'utilisateur")

    def action_dark_mode(self):
        """Bascule le thème sombre/clair"""
        self.dark = not self.dark
        self.notify(f"🌓 Mode {'sombre' if self.dark else 'clair'}", severity="information")

    def action_fullscreen(self):
        """Bascule le mode plein écran"""
        self.full_screen = not self.full_screen
        self.notify(f"🖥️ {'Plein écran' if self.full_screen else 'Fenêtré'}", severity="information")

    def action_help(self):
        """Affiche l'aide"""
        help_text = """
╔═══════════════════════════════════════════════╗
║              RACCOURCIS CLAVIER              ║
╠═══════════════════════════════════════════════╣
║  q  │ Quitter l'application                  ║
║  c  │ Effacer les logs                      ║
║  r  │ Rafraîchir les données                ║
║  d  │ Basculer mode sombre/clair            ║
║  f  │ Basculer plein écran                  ║
║  ?  │ Afficher cette aide                   ║
╚═══════════════════════════════════════════════╝
"""
        self.notify(help_text, title="📖 Aide", severity="information", timeout=8)

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = HollywoodRealDataApp()
    app.run()