# modern_ui_fixed.py - Ultra-Modern Windows Native UI (No QtCharts needed)
import sys
import json
import datetime
import threading
import psutil
import platform
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Import your existing components
from super_ui import AnimatedGaugeWidget, RealTimeGraphWidget, ThreatHeatmapWidget, NetworkMapWidget, ModernButton
from super_analyzer import get_analyzer

# ==================== CUSTOM STYLED WIDGETS ====================

class GradientWidget(QWidget):
    """Widget with gradient background"""
    def __init__(self, parent=None, color1=QColor(30, 30, 40), color2=QColor(20, 20, 30)):
        super().__init__(parent)
        self.color1 = color1
        self.color2 = color2
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, self.color1)
        gradient.setColorAt(1, self.color2)
        painter.fillRect(self.rect(), gradient)

class GlassPanel(QFrame):
    """Glass morphism effect panel"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 40, 0.7);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

class ThreatMeterWidget(QProgressBar):
    """Custom threat meter with gradient"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setTextVisible(False)
        self.setFixedHeight(30)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        rect = self.rect()
        painter.setBrush(QBrush(QColor(40, 40, 45)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 15, 15)
        
        # Draw value
        value = self.value()
        if value > 0:
            width = int(rect.width() * value / 100)
            value_rect = QRect(0, 0, width, rect.height())
            
            # Gradient based on threat level
            if value < 30:
                gradient = QLinearGradient(0, 0, width, 0)
                gradient.setColorAt(0, QColor(0, 255, 0))
                gradient.setColorAt(1, QColor(100, 255, 0))
            elif value < 70:
                gradient = QLinearGradient(0, 0, width, 0)
                gradient.setColorAt(0, QColor(255, 165, 0))
                gradient.setColorAt(1, QColor(255, 200, 0))
            else:
                gradient = QLinearGradient(0, 0, width, 0)
                gradient.setColorAt(0, QColor(255, 0, 0))
                gradient.setColorAt(1, QColor(200, 0, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(value_rect, 15, 15)

class AnimatedSidebar(QWidget):
    """Animated sliding sidebar"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(0)
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.is_expanded = False
        
    def toggle(self):
        self.is_expanded = not self.is_expanded
        self.animation.setEndValue(250 if self.is_expanded else 0)
        self.animation.start()

class NotificationWidget(QWidget):
    """Floating notification"""
    def __init__(self, message, parent=None, duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        icon_label = QLabel("🛡️")
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(msg_label)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 120, 215, 0.9);
                border-radius: 10px;
            }
        """)
        
        self.adjustSize()
        
        # Position at bottom right
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.right() - self.width() - 20, 
                     parent_geo.bottom() - self.height() - 50)
        
        # Auto close
        QTimer.singleShot(duration, self.close)
        
        # Fade animation
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(500)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()

# ==================== MAIN WINDOW ====================

class UltraModernAntivirus(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Sentinel Antivirus Pro - Ultimate Protection")
        self.setGeometry(50, 50, 1500, 900)
        
        # Set window icon (optional)
        self.setWindowIcon(self.create_window_icon())
        
        # Initialize analyzer
        self.analyzer = get_analyzer()
        self.scanning = False
        self.real_time_active = False
        self.scan_count = 0
        
        # Setup UI
        self.setup_ui()
        self.apply_global_style()
        
        # Start background tasks
        self.start_background_monitoring()
        
        # Show welcome notification
        self.show_notification("🛡️ Sentinel Antivirus Activated", 3000)
        
    def create_window_icon(self):
        """Create window icon"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(0, 120, 215), 3))
        painter.setBrush(QBrush(QColor(0, 120, 215, 100)))
        painter.drawEllipse(10, 10, 44, 44)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(QRect(10, 10, 44, 44), Qt.AlignCenter, "S")
        painter.end()
        return QIcon(pixmap)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #1a1a1a;")
        
        # Create pages
        self.dashboard_page = self.create_dashboard_page()
        self.scan_page = self.create_scan_page()
        self.threats_page = self.create_threats_page()
        self.monitor_page = self.create_monitor_page()
        self.analyzer_page = self.create_analyzer_page()
        self.settings_page = self.create_settings_page()
        
        self.content_stack.addWidget(self.dashboard_page)  # 0
        self.content_stack.addWidget(self.scan_page)      # 1
        self.content_stack.addWidget(self.threats_page)   # 2
        self.content_stack.addWidget(self.monitor_page)   # 3
        self.content_stack.addWidget(self.analyzer_page)  # 4
        self.content_stack.addWidget(self.settings_page)  # 5
        
        main_layout.addWidget(self.content_stack, 1)
        
        # Header bar
        self.header = self.create_header()
        # Add header as a widget that stays on top
        self.header.setParent(self.content_stack)
        self.header.raise_()
        
    def create_sidebar(self):
        """Create modern sidebar"""
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-right: 1px solid rgba(255,255,255,0.05);
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 215, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(0, 120, 215, 0.4);
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 30, 0, 30)
        layout.setSpacing(10)
        
        # Logo
        logo_label = QLabel("🛡️ SENTINEL")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard", 0),
            ("🔍", "Threat Scan", 1),
            ("⚠️", "Threats", 2),
            ("📈", "System Monitor", 3),
            ("🤖", "AI Analyzer", 4),
            ("⚙️", "Settings", 5)
        ]
        
        self.nav_buttons = []
        for icon, text, index in nav_items:
            btn = QPushButton(f"  {icon}  {text}")
            btn.clicked.connect(lambda checked, i=index: self.content_stack.setCurrentIndex(i))
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        layout.addStretch()
        
        # Status indicator
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
                margin: 10px;
                padding: 10px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        
        self.status_indicator = QLabel("🟢 SYSTEM PROTECTED")
        self.status_indicator.setStyleSheet("color: #00ff00; font-weight: bold;")
        status_layout.addWidget(self.status_indicator)
        
        self.realtime_indicator = QLabel("⚪ Real-time: OFF")
        self.realtime_indicator.setStyleSheet("color: #888888;")
        status_layout.addWidget(self.realtime_indicator)
        
        layout.addWidget(status_frame)
        
        return sidebar
    
    def create_header(self):
        """Create modern header bar"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: rgba(0,0,0,0.5);
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Menu button
        menu_btn = ModernButton("☰")
        menu_btn.setFixedSize(40, 40)
        menu_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(menu_btn)
        
        layout.addStretch()
        
        # System stats
        self.cpu_label = QLabel("CPU: --%")
        self.cpu_label.setStyleSheet("color: #888888; font-weight: bold;")
        layout.addWidget(self.cpu_label)
        
        self.mem_label = QLabel("RAM: --%")
        self.mem_label.setStyleSheet("color: #888888; font-weight: bold;")
        layout.addWidget(self.mem_label)
        
        return header
    
    def create_dashboard_page(self):
        """Create main dashboard"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Welcome banner
        welcome = GlassPanel()
        welcome_layout = QHBoxLayout(welcome)
        
        welcome_text = QLabel("Welcome back! Your system is protected by Sentinel AI")
        welcome_text.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff00;")
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome)
        
        # Stats grid
        stats_layout = QHBoxLayout()
        
        # Threat meter card
        threat_card = GlassPanel()
        threat_layout = QVBoxLayout(threat_card)
        threat_title = QLabel("THREAT LEVEL")
        threat_title.setStyleSheet("font-weight: bold;")
        threat_layout.addWidget(threat_title)
        self.threat_meter = ThreatMeterWidget()
        threat_layout.addWidget(self.threat_meter)
        stats_layout.addWidget(threat_card)
        
        # Scan count card
        scan_card = GlassPanel()
        scan_layout = QVBoxLayout(scan_card)
        scan_title = QLabel("SCANS TODAY")
        scan_title.setStyleSheet("font-weight: bold;")
        scan_layout.addWidget(scan_title)
        self.scan_count_label = QLabel("0")
        self.scan_count_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ff00;")
        scan_layout.addWidget(self.scan_count_label)
        stats_layout.addWidget(scan_card)
        
        # Threats blocked card
        blocked_card = GlassPanel()
        blocked_layout = QVBoxLayout(blocked_card)
        blocked_title = QLabel("THREATS BLOCKED")
        blocked_title.setStyleSheet("font-weight: bold;")
        blocked_layout.addWidget(blocked_title)
        self.blocked_label = QLabel("0")
        self.blocked_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #ff6600;")
        blocked_layout.addWidget(self.blocked_label)
        stats_layout.addWidget(blocked_card)
        
        layout.addLayout(stats_layout)
        
        # Real-time graphs
        graphs_layout = QHBoxLayout()
        
        # CPU Graph
        cpu_graph_card = GlassPanel()
        cpu_graph_layout = QVBoxLayout(cpu_graph_card)
        cpu_graph_title = QLabel("CPU USAGE HISTORY")
        cpu_graph_title.setStyleSheet("font-weight: bold;")
        cpu_graph_layout.addWidget(cpu_graph_title)
        self.cpu_graph = RealTimeGraphWidget("CPU Usage")
        cpu_graph_layout.addWidget(self.cpu_graph)
        graphs_layout.addWidget(cpu_graph_card)
        
        # Threat Heatmap
        heatmap_card = GlassPanel()
        heatmap_layout = QVBoxLayout(heatmap_card)
        heatmap_title = QLabel("THREAT HEATMAP")
        heatmap_title.setStyleSheet("font-weight: bold;")
        heatmap_layout.addWidget(heatmap_title)
        self.heatmap = ThreatHeatmapWidget()
        heatmap_layout.addWidget(self.heatmap)
        graphs_layout.addWidget(heatmap_card)
        
        layout.addLayout(graphs_layout)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        quick_scan_btn = ModernButton("🔍 QUICK SCAN")
        quick_scan_btn.setFixedHeight(50)
        quick_scan_btn.clicked.connect(self.start_quick_scan)
        actions_layout.addWidget(quick_scan_btn)
        
        deep_scan_btn = ModernButton("⚡ DEEP SCAN")
        deep_scan_btn.setFixedHeight(50)
        deep_scan_btn.clicked.connect(self.start_deep_scan)
        actions_layout.addWidget(deep_scan_btn)
        
        realtime_btn = ModernButton("🛡️ REAL-TIME")
        realtime_btn.setFixedHeight(50)
        realtime_btn.clicked.connect(self.toggle_realtime)
        actions_layout.addWidget(realtime_btn)
        
        layout.addLayout(actions_layout)
        
        # Recent threats table
        recent_label = QLabel("RECENT THREATS")
        recent_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(recent_label)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Time", "Type", "Severity", "Status"])
        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30,30,40,0.5);
                border-radius: 10px;
                alternate-background-color: rgba(40,40,50,0.5);
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 8px;
                border: none;
            }
        """)
        self.recent_table.setAlternatingRowColors(True)
        layout.addWidget(self.recent_table)
        
        return widget
    
    def create_scan_page(self):
        """Create advanced scan page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Scan options
        options_card = GlassPanel()
        options_layout = QVBoxLayout(options_card)
        options_title = QLabel("SCAN OPTIONS")
        options_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        options_layout.addWidget(options_title)
        
        scan_types = QHBoxLayout()
        
        self.quick_radio = QRadioButton("Quick Scan")
        self.quick_radio.setChecked(True)
        self.full_radio = QRadioButton("Full Scan")
        self.custom_radio = QRadioButton("Custom Scan")
        
        scan_types.addWidget(self.quick_radio)
        scan_types.addWidget(self.full_radio)
        scan_types.addWidget(self.custom_radio)
        options_layout.addLayout(scan_types)
        
        layout.addWidget(options_card)
        
        # Scan button
        self.scan_btn = ModernButton("START SCAN")
        self.scan_btn.setFixedHeight(60)
        self.scan_btn.clicked.connect(self.execute_scan)
        layout.addWidget(self.scan_btn)
        
        # Scan progress
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        self.scan_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 5px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.scan_progress)
        
        # Scan results
        results_label = QLabel("SCAN RESULTS")
        results_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(results_label)
        
        self.scan_results_tree = QTreeWidget()
        self.scan_results_tree.setHeaderLabels(["Item", "Type", "Severity", "Location"])
        self.scan_results_tree.setStyleSheet("""
            QTreeWidget {
                background-color: rgba(30,30,40,0.5);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.scan_results_tree)
        
        return widget
    
    def create_threats_page(self):
        """Create threats management page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Threat table
        self.threats_table = QTableWidget()
        self.threats_table.setColumnCount(6)
        self.threats_table.setHorizontalHeaderLabels(["Severity", "Type", "Process", "Location", "Score", "Action"])
        self.threats_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30,30,40,0.5);
                border-radius: 10px;
                alternate-background-color: rgba(40,40,50,0.5);
            }
        """)
        self.threats_table.setAlternatingRowColors(True)
        layout.addWidget(self.threats_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        clear_btn = ModernButton("Clear All")
        clear_btn.clicked.connect(self.clear_threats)
        action_layout.addWidget(clear_btn)
        
        export_btn = ModernButton("Export Report")
        export_btn.clicked.connect(self.export_threat_report)
        action_layout.addWidget(export_btn)
        
        layout.addLayout(action_layout)
        
        return widget
    
    def create_monitor_page(self):
        """Create system monitor page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Network map
        network_label = QLabel("NETWORK ACTIVITY MAP")
        network_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(network_label)
        
        self.network_map = NetworkMapWidget()
        self.network_map.setMinimumHeight(300)
        layout.addWidget(self.network_map)
        
        # Process list
        process_label = QLabel("RUNNING PROCESSES")
        process_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(process_label)
        
        self.process_tree = QTreeWidget()
        self.process_tree.setHeaderLabels(["Process Name", "PID", "CPU %", "Memory %", "Threat Score"])
        self.process_tree.setStyleSheet("""
            QTreeWidget {
                background-color: rgba(30,30,40,0.5);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.process_tree)
        
        return widget
    
    def create_analyzer_page(self):
        """Create AI analyzer stats page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Analyzer info
        info_card = GlassPanel()
        info_layout = QVBoxLayout(info_card)
        
        info_title = QLabel("🤖 SENTINEL AI ANALYZER")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff00;")
        info_layout.addWidget(info_title)
        
        self.analyzer_stats = QTextEdit()
        self.analyzer_stats.setReadOnly(True)
        self.analyzer_stats.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
                font-family: Consolas;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(self.analyzer_stats)
        
        layout.addWidget(info_card)
        
        refresh_btn = ModernButton("Refresh Stats")
        refresh_btn.clicked.connect(self.update_analyzer_display)
        layout.addWidget(refresh_btn)
        
        self.update_analyzer_display()
        
        return widget
    
    def create_settings_page(self):
        """Create settings page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Protection settings
        protection_card = GlassPanel()
        protection_layout = QVBoxLayout(protection_card)
        protection_title = QLabel("PROTECTION SETTINGS")
        protection_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        protection_layout.addWidget(protection_title)
        
        self.realtime_check = QCheckBox("Enable Real-time Protection")
        self.realtime_check.setChecked(False)
        protection_layout.addWidget(self.realtime_check)
        
        self.startup_check = QCheckBox("Start with Windows")
        protection_layout.addWidget(self.startup_check)
        
        self.notify_check = QCheckBox("Show Threat Notifications")
        self.notify_check.setChecked(True)
        protection_layout.addWidget(self.notify_check)
        
        layout.addWidget(protection_card)
        
        # Scan settings
        scan_card = GlassPanel()
        scan_layout = QVBoxLayout(scan_card)
        scan_title = QLabel("SCAN SETTINGS")
        scan_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        scan_layout.addWidget(scan_title)
        
        self.scan_processes_check = QCheckBox("Scan Running Processes")
        self.scan_processes_check.setChecked(True)
        scan_layout.addWidget(self.scan_processes_check)
        
        self.scan_network_check = QCheckBox("Scan Network Connections")
        self.scan_network_check.setChecked(True)
        scan_layout.addWidget(self.scan_network_check)
        
        self.scan_files_check = QCheckBox("Scan Temporary Files")
        self.scan_files_check.setChecked(True)
        scan_layout.addWidget(self.scan_files_check)
        
        layout.addWidget(scan_card)
        
        layout.addStretch()
        
        save_btn = ModernButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        return widget
    
    def apply_global_style(self):
        """Apply global dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0f;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 8px;
            }
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #007acc;
                border-radius: 5px;
                min-height: 20px;
            }
        """)
    
    # ==================== ACTIONS ====================
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar.width() > 0:
            self.sidebar.setFixedWidth(0)
        else:
            self.sidebar.setFixedWidth(280)
    
    def show_notification(self, message, duration=3000):
        """Show floating notification"""
        NotificationWidget(message, self, duration)
    
    def start_quick_scan(self):
        """Start quick scan"""
        self.show_notification("🔍 Quick scan started...")
        self.scan_btn.setText("SCANNING...")
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 0)
        
        def scan():
            threats = self.analyzer.scan_all_processes()
            for threat in threats[:10]:
                self.add_threat_to_table(threat)
            QMetaObject.invokeMethod(self.scan_progress, "setVisible", Q_ARG(bool, False))
            QMetaObject.invokeMethod(self.scan_btn, "setText", Q_ARG(str, "START SCAN"))
            self.show_notification(f"✅ Scan complete! Found {len(threats)} threats")
            
            # Update scan count
            self.scan_count += 1
            QMetaObject.invokeMethod(self.scan_count_label, "setText", Q_ARG(str, str(self.scan_count)))
        
        threading.Thread(target=scan, daemon=True).start()
    
    def start_deep_scan(self):
        """Start deep system scan"""
        self.show_notification("⚡ Deep scan initiated...")
        # Similar implementation but more thorough
        self.start_quick_scan()  # For now, reuse quick scan
    
    def execute_scan(self):
        """Execute selected scan type"""
        if self.quick_radio.isChecked():
            self.start_quick_scan()
        elif self.full_radio.isChecked():
            self.start_deep_scan()
    
    def toggle_realtime(self):
        """Toggle real-time protection"""
        self.real_time_active = not self.real_time_active
        status = "ACTIVE" if self.real_time_active else "OFF"
        color = "#00ff00" if self.real_time_active else "#888888"
        self.realtime_indicator.setText(f"🛡️ Real-time: {status}")
        self.realtime_indicator.setStyleSheet(f"color: {color};")
        self.show_notification(f"Real-time protection {status}")
    
    def add_threat_to_table(self, threat):
        """Add threat to threats table"""
        row = self.threats_table.rowCount()
        self.threats_table.insertRow(row)
        
        severity = threat['analysis']['severity']
        severity_item = QTableWidgetItem(severity)
        
        if severity == "CRITICAL":
            severity_item.setForeground(QColor(255, 0, 0))
        elif severity == "HIGH":
            severity_item.setForeground(QColor(255, 100, 0))
        elif severity == "MEDIUM":
            severity_item.setForeground(QColor(255, 200, 0))
        else:
            severity_item.setForeground(QColor(0, 255, 0))
        
        self.threats_table.setItem(row, 0, severity_item)
        self.threats_table.setItem(row, 1, QTableWidgetItem(threat['analysis']['threats'][0]['type'] if threat['analysis']['threats'] else "Unknown"))
        self.threats_table.setItem(row, 2, QTableWidgetItem(threat['name']))
        self.threats_table.setItem(row, 3, QTableWidgetItem(f"PID: {threat['pid']}"))
        self.threats_table.setItem(row, 4, QTableWidgetItem(str(threat['analysis']['threat_score'])))
        
        action_btn = QPushButton("Ignore")
        action_btn.setStyleSheet("background-color: #444; border-radius: 3px; padding: 3px;")
        self.threats_table.setCellWidget(row, 5, action_btn)
        
        # Add to recent table
        recent_row = self.recent_table.rowCount()
        self.recent_table.insertRow(recent_row)
        self.recent_table.setItem(recent_row, 0, QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S")))
        self.recent_table.setItem(recent_row, 1, QTableWidgetItem(threat['analysis']['threats'][0]['type'] if threat['analysis']['threats'] else "Unknown"))
        self.recent_table.setItem(recent_row, 2, QTableWidgetItem(severity))
        self.recent_table.setItem(recent_row, 3, QTableWidgetItem("Detected"))
        
        # Update blocked count
        blocked = int(self.blocked_label.text()) + 1
        self.blocked_label.setText(str(blocked))
    
    def clear_threats(self):
        """Clear all threats"""
        self.threats_table.setRowCount(0)
        self.recent_table.setRowCount(0)
        self.show_notification("🗑️ All threats cleared")
    
    def export_threat_report(self):
        """Export threat report"""
        filename = f"threat_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {"timestamp": datetime.datetime.now().isoformat(), "threats": []}
        
        for row in range(self.threats_table.rowCount()):
            threat = {
                "severity": self.threats_table.item(row, 0).text(),
                "type": self.threats_table.item(row, 1).text(),
                "process": self.threats_table.item(row, 2).text(),
                "location": self.threats_table.item(row, 3).text(),
                "score": self.threats_table.item(row, 4).text()
            }
            report["threats"].append(threat)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.show_notification(f"📄 Report saved: {filename}")
    
    def update_analyzer_display(self):
        """Update analyzer stats display"""
        stats = f"""
╔══════════════════════════════════════════════════════════════╗
║                    SENTINEL AI ANALYZER                       ║
╠══════════════════════════════════════════════════════════════╣
║  Status:              🟢 ACTIVE                              ║
║  Detection Methods:   Behavioral, Signature, Heuristic       ║
║                                                              ║
║  Threat Signatures:                                          ║
║    • APT Groups:      Active                                ║
║    • Ransomware:      Monitored                             ║
║    • Cryptominers:    Detected                              ║
║    • Rootkits:        Scanning                              ║
║                                                              ║
║  System Status:                                             ║
║    • CPU:             {psutil.cpu_percent()}%                              ║
║    • RAM:             {psutil.virtual_memory().percent}%                             ║
║    • Processes:       {len(list(psutil.process_iter()))}                               ║
║    • Connections:     {len(psutil.net_connections())}                               ║
║                                                              ║
║  Protection Stats:                                          ║
║    • Scans Today:     {self.scan_count}                                   ║
║    • Threats Found:   {self.threats_table.rowCount()}                                   ║
║    • Real-time:       {"ON" if self.real_time_active else "OFF"}                                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.analyzer_stats.setText(stats)
    
    def save_settings(self):
        """Save user settings"""
        settings = {
            "realtime": self.realtime_check.isChecked(),
            "startup": self.startup_check.isChecked(),
            "notifications": self.notify_check.isChecked(),
            "scan_processes": self.scan_processes_check.isChecked(),
            "scan_network": self.scan_network_check.isChecked(),
            "scan_files": self.scan_files_check.isChecked()
        }
        
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=2)
        
        self.show_notification("⚙️ Settings saved!")
    
    def start_background_monitoring(self):
        """Start background system monitoring"""
        def monitor():
            while True:
                try:
                    # Update CPU and memory labels
                    cpu = psutil.cpu_percent()
                    mem = psutil.virtual_memory().percent
                    QMetaObject.invokeMethod(self.cpu_label, "setText", 
                                            Qt.QueuedConnection,
                                            Q_ARG(str, f"CPU: {cpu}%"))
                    QMetaObject.invokeMethod(self.mem_label, "setText", 
                                            Qt.QueuedConnection,
                                            Q_ARG(str, f"RAM: {mem}%"))
                    
                    # Update threat meter
                    threat_level = min(100, self.threats_table.rowCount() * 5)
                    QMetaObject.invokeMethod(self.threat_meter, "setValue", 
                                            Qt.QueuedConnection,
                                            Q_ARG(int, threat_level))
                    
                    # Update process list
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                        try:
                            processes.append(proc.info)
                        except:
                            continue
                    
                    processes.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
                    
                    QMetaObject.invokeMethod(self.process_tree, "clear", Qt.QueuedConnection)
                    for proc in processes[:30]:
                        if proc.get('name'):
                            item = QTreeWidgetItem([
                                proc['name'][:40],
                                str(proc['pid']),
                                f"{proc.get('cpu_percent', 0):.1f}",
                                f"{proc.get('memory_percent', 0):.1f}",
                                "N/A"
                            ])
                            QMetaObject.invokeMethod(self.process_tree, "addTopLevelItem", 
                                                    Qt.QueuedConnection,
                                                    Q_ARG(QTreeWidgetItem, item))
                    
                    # Update network map
                    connections = []
                    for conn in psutil.net_connections(kind='inet'):
                        if conn.status == 'ESTABLISHED' and conn.raddr:
                            connections.append({
                                "port": conn.raddr.port,
                                "ip": conn.raddr.ip,
                                "suspicious": conn.raddr.port in [4444, 5555, 6666, 7777, 8888]
                            })
                    QMetaObject.invokeMethod(self.network_map, "update_connections", 
                                            Qt.QueuedConnection,
                                            Q_ARG(list, connections[:20]))
                    
                    # Update threat heatmap
                    threats = []
                    for row in range(self.recent_table.rowCount()):
                        severity_item = self.recent_table.item(row, 2)
                        type_item = self.recent_table.item(row, 1)
                        threats.append({
                            "severity": severity_item.text() if severity_item else "LOW",
                            "details": type_item.text() if type_item else ""
                        })
                    QMetaObject.invokeMethod(self.heatmap, "update_threats", 
                                            Qt.QueuedConnection,
                                            Q_ARG(list, threats))
                    
                    import time
                    time.sleep(2)
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(5)
        
        threading.Thread(target=monitor, daemon=True).start()


# ==================== MAIN ====================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = UltraModernAntivirus()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()