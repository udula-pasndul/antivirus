# sentinel_antivirus_final.py - Fully Working Version
import sys
import json
import datetime
import threading
import psutil
import platform
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Import Super Analyzer
from super_analyzer import get_analyzer

# Import UI components
from super_ui import RealTimeGraphWidget, ThreatHeatmapWidget, NetworkMapWidget

class ModernButton(QPushButton):
    """Fixed modern button"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(35)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00aaff;
            }
        """)

class GlassPanel(QFrame):
    """Glass morphism effect panel"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 40, 0.7);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

class ThreatMeterWidget(QProgressBar):
    """Custom threat meter"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setTextVisible(False)
        self.setFixedHeight(30)
        
    def setValue(self, value):
        super().setValue(value)
        if value < 30:
            self.setStyleSheet("""
                QProgressBar { border: 1px solid #3e3e42; border-radius: 15px; }
                QProgressBar::chunk { background-color: #00ff00; border-radius: 15px; }
            """)
        elif value < 70:
            self.setStyleSheet("""
                QProgressBar { border: 1px solid #3e3e42; border-radius: 15px; }
                QProgressBar::chunk { background-color: #ffa500; border-radius: 15px; }
            """)
        else:
            self.setStyleSheet("""
                QProgressBar { border: 1px solid #3e3e42; border-radius: 15px; }
                QProgressBar::chunk { background-color: #ff0000; border-radius: 15px; }
            """)

class NotificationWidget(QWidget):
    """Floating notification"""
    def __init__(self, message, parent=None, duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        icon_label = QLabel("🛡️")
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(msg_label)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 120, 215, 0.9);
                border-radius: 10px;
            }
        """)
        
        self.adjustSize()
        
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.right() - self.width() - 20, 
                     parent_geo.bottom() - self.height() - 50)
        
        QTimer.singleShot(duration, self.close)

# ==================== MAIN WINDOW ====================

class SentinelAntivirus(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ SENTINEL ANTIVIRUS - Super Analyzer Powered")
        self.setGeometry(100, 100, 1300, 800)
        
        # Initialize Super Analyzer
        self.analyzer = get_analyzer()
        print("✅ Super Analyzer CONNECTED and LOADED!")
        print(f"✅ Analyzer type: {type(self.analyzer).__name__}")
        
        # Status variables
        self.scanning = False
        self.real_time_active = False
        self.scan_count = 0
        self.threats_found = 0
        self.monitoring_thread = None
        
        # Setup UI
        self.setup_ui()
        self.apply_style()
        
        # Show welcome
        self.add_log("🛡️ Sentinel Antivirus Started - Super Analyzer Connected")
        self.show_notification("🤖 Super Analyzer AI Engine Active", 3000)
        
        # Start background monitoring
        self.start_background_monitoring()
        
    def setup_ui(self):
        """Setup the main UI"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # Sidebar
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Main content stack
        self.content_stack = QStackedWidget()
        
        # Create pages
        self.dashboard_page = self.create_dashboard_page()
        self.scan_page = self.create_scan_page()
        self.threats_page = self.create_threats_page()
        self.analyzer_page = self.create_analyzer_page()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.scan_page)
        self.content_stack.addWidget(self.threats_page)
        self.content_stack.addWidget(self.analyzer_page)
        
        content_layout.addWidget(self.content_stack, 1)
        main_layout.addWidget(content)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("🟢 Super Analyzer Active | Real-time: OFF")
        self.status_bar.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_header(self):
        """Create header with analyzer badge"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-bottom: 2px solid #007acc;
                border-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo
        logo = QLabel("🛡️ SENTINEL ANTIVIRUS")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff00;")
        layout.addWidget(logo)
        
        # Super Analyzer Badge
        analyzer_badge = QLabel("🤖 SUPER ANALYZER AI")
        analyzer_badge.setStyleSheet("""
            background-color: #007acc;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 11px;
        """)
        layout.addWidget(analyzer_badge)
        
        layout.addStretch()
        
        # Stats
        self.cpu_label = QLabel("CPU: --%")
        self.cpu_label.setStyleSheet("color: #888888; font-weight: bold;")
        layout.addWidget(self.cpu_label)
        
        self.mem_label = QLabel("RAM: --%")
        self.mem_label.setStyleSheet("color: #888888; font-weight: bold;")
        layout.addWidget(self.mem_label)
        
        return header
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Analyzer Status Card
        status_card = QFrame()
        status_card.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 215, 0.2);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        status_layout = QVBoxLayout(status_card)
        
        analyzer_status = QLabel("🤖 ANALYZER STATUS")
        analyzer_status.setStyleSheet("font-weight: bold; color: #00ff00;")
        status_layout.addWidget(analyzer_status)
        
        self.analyzer_status_label = QLabel("🟢 ONLINE")
        self.analyzer_status_label.setStyleSheet("color: #00ff00; font-size: 12px;")
        status_layout.addWidget(self.analyzer_status_label)
        
        layout.addWidget(status_card)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard", 0),
            ("🔍", "Threat Scan", 1),
            ("⚠️", "Threats", 2),
            ("🤖", "AI Analyzer", 3)
        ]
        
        for icon, text, index in nav_items:
            btn = ModernButton(f"{icon}  {text}")
            btn.clicked.connect(lambda checked, i=index: self.content_stack.setCurrentIndex(i))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Real-time toggle
        self.realtime_btn = ModernButton("🛡️ REAL-TIME OFF")
        self.realtime_btn.clicked.connect(self.toggle_realtime)
        layout.addWidget(self.realtime_btn)
        
        return sidebar
    
    def create_dashboard_page(self):
        """Create dashboard page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Welcome Card
        welcome = QFrame()
        welcome.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 215, 0.2);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        welcome_layout = QVBoxLayout(welcome)
        
        welcome_title = QLabel("🛡️ SENTINEL ANTIVIRUS PRO")
        welcome_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff00;")
        welcome_layout.addWidget(welcome_title)
        
        analyzer_info = QLabel(f"🤖 Super Analyzer AI Engine Active | {type(self.analyzer).__name__}")
        analyzer_info.setStyleSheet("color: #007acc; font-size: 11px;")
        welcome_layout.addWidget(analyzer_info)
        
        layout.addWidget(welcome)
        
        # Stats Row
        stats_layout = QHBoxLayout()
        
        # Threat Meter Card
        threat_card = QFrame()
        threat_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 10px; }")
        threat_layout = QVBoxLayout(threat_card)
        threat_layout.addWidget(QLabel("THREAT LEVEL"))
        self.threat_meter = ThreatMeterWidget()
        threat_layout.addWidget(self.threat_meter)
        stats_layout.addWidget(threat_card)
        
        # Scans Card
        scan_card = QFrame()
        scan_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 10px; }")
        scan_layout = QVBoxLayout(scan_card)
        scan_layout.addWidget(QLabel("SCANS"))
        self.scan_count_label = QLabel("0")
        self.scan_count_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #00ff00;")
        scan_layout.addWidget(self.scan_count_label)
        stats_layout.addWidget(scan_card)
        
        # Threats Card
        threats_card = QFrame()
        threats_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 10px; }")
        threats_layout = QVBoxLayout(threats_card)
        threats_layout.addWidget(QLabel("THREATS"))
        self.threats_count_label = QLabel("0")
        self.threats_count_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #ff6600;")
        threats_layout.addWidget(self.threats_count_label)
        stats_layout.addWidget(threats_card)
        
        layout.addLayout(stats_layout)
        
        # CPU Graph
        graph_card = QFrame()
        graph_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 10px; }")
        graph_layout = QVBoxLayout(graph_card)
        graph_layout.addWidget(QLabel("CPU USAGE"))
        self.cpu_graph = RealTimeGraphWidget("CPU Usage")
        graph_layout.addWidget(self.cpu_graph)
        layout.addWidget(graph_card)
        
        # Action Buttons
        actions_layout = QHBoxLayout()
        
        quick_btn = ModernButton("🔍 QUICK SCAN")
        quick_btn.clicked.connect(self.start_quick_scan)
        actions_layout.addWidget(quick_btn)
        
        deep_btn = ModernButton("⚡ DEEP SCAN")
        deep_btn.clicked.connect(self.start_deep_scan)
        actions_layout.addWidget(deep_btn)
        
        layout.addLayout(actions_layout)
        
        # Log Area
        log_label = QLabel("ACTIVITY LOG")
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
                font-family: Consolas;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_text)
        
        return widget
    
    def create_scan_page(self):
        """Create scan page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Scan Options Card
        options_card = QFrame()
        options_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; }")
        options_layout = QVBoxLayout(options_card)
        
        options_title = QLabel("SCAN OPTIONS")
        options_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        options_layout.addWidget(options_title)
        
        self.quick_radio = QRadioButton("Quick Scan (Running Processes)")
        self.quick_radio.setChecked(True)
        self.full_radio = QRadioButton("Full Scan (All Processes)")
        
        options_layout.addWidget(self.quick_radio)
        options_layout.addWidget(self.full_radio)
        layout.addWidget(options_card)
        
        # Scan Button
        self.scan_btn = ModernButton("START SCAN")
        self.scan_btn.setFixedHeight(50)
        self.scan_btn.clicked.connect(self.execute_scan)
        layout.addWidget(self.scan_btn)
        
        # Results Label
        results_label = QLabel("SCAN RESULTS")
        results_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(results_label)
        
        # Results Tree
        self.scan_results = QTreeWidget()
        self.scan_results.setHeaderLabels(["Process", "PID", "Score", "Severity", "Details"])
        self.scan_results.setStyleSheet("""
            QTreeWidget {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.scan_results)
        
        return widget
    
    def create_threats_page(self):
        """Create threats page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.threats_table = QTableWidget()
        self.threats_table.setColumnCount(5)
        self.threats_table.setHorizontalHeaderLabels(["Time", "Process", "Threat Type", "Severity", "Score"])
        self.threats_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
                alternate-background-color: rgba(40,40,50,0.5);
            }
        """)
        self.threats_table.setAlternatingRowColors(True)
        layout.addWidget(self.threats_table)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        clear_btn = ModernButton("Clear All")
        clear_btn.clicked.connect(self.clear_threats)
        btn_layout.addWidget(clear_btn)
        
        export_btn = ModernButton("Export Report")
        export_btn.clicked.connect(self.export_report)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_analyzer_page(self):
        """Create analyzer stats page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Test Card
        test_card = QFrame()
        test_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; }")
        test_layout = QVBoxLayout(test_card)
        
        test_title = QLabel("🔬 SUPER ANALYZER TEST")
        test_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff00;")
        test_layout.addWidget(test_title)
        
        test_btn = ModernButton("TEST ANALYZER ON CURRENT PROCESSES")
        test_btn.clicked.connect(self.test_analyzer)
        test_layout.addWidget(test_btn)
        
        layout.addWidget(test_card)
        
        # Stats Card
        stats_card = QFrame()
        stats_card.setStyleSheet("QFrame { background-color: rgba(0,0,0,0.3); border-radius: 10px; padding: 15px; }")
        stats_layout = QVBoxLayout(stats_card)
        
        stats_title = QLabel("📊 ANALYZER STATISTICS")
        stats_title.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(stats_title)
        
        self.analyzer_stats = QTextEdit()
        self.analyzer_stats.setReadOnly(True)
        self.analyzer_stats.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
                font-family: Consolas;
                font-size: 11px;
            }
        """)
        stats_layout.addWidget(self.analyzer_stats)
        
        layout.addWidget(stats_card)
        
        self.update_analyzer_stats()
        
        return widget
    
    def apply_style(self):
        """Apply global style"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0f;
            }
            QLabel {
                color: #ffffff;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 8px;
            }
            QTableWidget {
                gridline-color: #3e3e42;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 8px;
                border: none;
                color: white;
            }
            QTreeWidget {
                color: white;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 8px;
                border: none;
                color: white;
            }
        """)
    
    # ==================== ACTIONS ====================
    
    def test_analyzer(self):
        """Test Super Analyzer"""
        self.add_log("🔬 Testing Super Analyzer on current processes...")
        
        test_results = []
        count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if count >= 5:
                    break
                analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                test_results.append(f"PID {proc.info['pid']} ({proc.info['name']}): Score {analysis['threat_score']} - {analysis['severity']}")
                self.add_log(f"  📊 {proc.info['name']}: Score = {analysis['threat_score']}")
                count += 1
            except:
                pass
        
        self.show_notification(f"✅ Analyzer tested on {count} processes", 3000)
        self.add_log("✅ Super Analyzer test complete!")
        self.update_analyzer_stats()
    
    def start_quick_scan(self):
        """Start quick scan"""
        if self.scanning:
            return
        
        self.scanning = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.scan_btn.setText("SCANNING...")
        self.add_log("🔍 Starting Quick Scan with Super Analyzer...")
        
        def scan_thread():
            threats = []
            processes = list(psutil.process_iter(['pid', 'name']))
            total = len(processes)
            
            for i, proc in enumerate(processes):
                try:
                    analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                    
                    if analysis["threat_score"] > 30:
                        threats.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'analysis': analysis
                        })
                        self.add_log(f"⚠️ THREAT: {proc.info['name']} (Score: {analysis['threat_score']})")
                    
                    if i % 10 == 0:
                        progress = int((i + 1) / total * 100)
                        QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, progress))
                        QMetaObject.invokeMethod(self.progress_bar, "setFormat", Qt.QueuedConnection, Q_ARG(str, f"Scanning... {progress}%"))
                        
                except:
                    continue
            
            # Update UI
            for threat in threats:
                self.add_threat_to_display(threat['name'], threat['pid'], threat['analysis'])
            
            self.scanning = False
            self.scan_count += 1
            
            QMetaObject.invokeMethod(self.progress_bar, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
            QMetaObject.invokeMethod(self.scan_btn, "setText", Qt.QueuedConnection, Q_ARG(str, "START SCAN"))
            QMetaObject.invokeMethod(self.scan_count_label, "setText", Qt.QueuedConnection, Q_ARG(str, str(self.scan_count)))
            
            self.add_log(f"✅ Scan complete! Found {len(threats)} threats")
            self.show_notification(f"✅ Scan complete - {len(threats)} threats found", 3000)
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def start_deep_scan(self):
        """Start deep scan"""
        self.add_log("⚡ Starting Deep Scan...")
        self.start_quick_scan()
    
    def execute_scan(self):
        """Execute selected scan"""
        if self.scanning:
            return
        if self.quick_radio.isChecked():
            self.start_quick_scan()
        else:
            self.start_deep_scan()
    
    def toggle_realtime(self):
        """Toggle real-time monitoring"""
        self.real_time_active = not self.real_time_active
        status = "ON" if self.real_time_active else "OFF"
        self.realtime_btn.setText(f"🛡️ REAL-TIME {status}")
        self.status_label.setText(f"🟢 Super Analyzer Active | Real-time: {status}")
        self.add_log(f"🛡️ Real-time protection {status}")
        
        if self.real_time_active:
            self.start_realtime_monitoring()
    
    def start_realtime_monitoring(self):
        """Start real-time monitoring"""
        def monitor():
            known_pids = set(psutil.pids())
            while self.real_time_active:
                try:
                    current_pids = set(psutil.pids())
                    new_pids = current_pids - known_pids
                    
                    for pid in new_pids:
                        try:
                            proc = psutil.Process(pid)
                            analysis = self.analyzer.deep_analyze_process(pid)
                            
                            if analysis["threat_score"] > 50:
                                self.add_log(f"🚨 REAL-TIME THREAT: {proc.name()} (Score: {analysis['threat_score']})")
                                self.add_threat_to_display(proc.name(), pid, analysis)
                                self.show_notification(f"⚠️ Threat detected: {proc.name()}", 5000)
                        except:
                            pass
                    
                    known_pids = current_pids
                    threading.Event().wait(3)
                except:
                    threading.Event().wait(3)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def add_threat_to_display(self, name, pid, analysis):
        """Add threat to display"""
        self.threats_found += 1
        
        # Update counter
        QMetaObject.invokeMethod(self.threats_count_label, "setText", Qt.QueuedConnection, Q_ARG(str, str(self.threats_found)))
        
        # Add to threats table
        row = self.threats_table.rowCount()
        QMetaObject.invokeMethod(self.threats_table, "insertRow", Qt.QueuedConnection, Q_ARG(int, row))
        
        time_item = QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S"))
        name_item = QTableWidgetItem(name[:40])
        type_item = QTableWidgetItem(analysis['threats'][0]['type'] if analysis['threats'] else "Unknown")
        severity_item = QTableWidgetItem(analysis['severity'])
        score_item = QTableWidgetItem(str(analysis['threat_score']))
        
        if analysis['severity'] == "CRITICAL":
            severity_item.setForeground(QColor(255, 0, 0))
        elif analysis['severity'] == "HIGH":
            severity_item.setForeground(QColor(255, 100, 0))
        elif analysis['severity'] == "MEDIUM":
            severity_item.setForeground(QColor(255, 200, 0))
        
        QMetaObject.invokeMethod(self.threats_table, "setItem", Qt.QueuedConnection, Q_ARG(int, row), Q_ARG(int, 0), Q_ARG(QTableWidgetItem, time_item))
        QMetaObject.invokeMethod(self.threats_table, "setItem", Qt.QueuedConnection, Q_ARG(int, row), Q_ARG(int, 1), Q_ARG(QTableWidgetItem, name_item))
        QMetaObject.invokeMethod(self.threats_table, "setItem", Qt.QueuedConnection, Q_ARG(int, row), Q_ARG(int, 2), Q_ARG(QTableWidgetItem, type_item))
        QMetaObject.invokeMethod(self.threats_table, "setItem", Qt.QueuedConnection, Q_ARG(int, row), Q_ARG(int, 3), Q_ARG(QTableWidgetItem, severity_item))
        QMetaObject.invokeMethod(self.threats_table, "setItem", Qt.QueuedConnection, Q_ARG(int, row), Q_ARG(int, 4), Q_ARG(QTableWidgetItem, score_item))
        
        # Update threat meter
        threat_level = min(100, self.threats_found * 10)
        QMetaObject.invokeMethod(self.threat_meter, "setValue", Qt.QueuedConnection, Q_ARG(int, threat_level))
        
        # Add to scan results
        item = QTreeWidgetItem([name[:40], str(pid), str(analysis['threat_score']), analysis['severity'], analysis['threats'][0]['details'][:50] if analysis['threats'] else ""])
        QMetaObject.invokeMethod(self.scan_results, "addTopLevelItem", Qt.QueuedConnection, Q_ARG(QTreeWidgetItem, item))
    
    def clear_threats(self):
        """Clear all threats"""
        self.threats_table.setRowCount(0)
        self.scan_results.clear()
        self.threats_found = 0
        self.threats_count_label.setText("0")
        self.threat_meter.setValue(0)
        self.add_log("🗑️ All threats cleared")
    
    def export_report(self):
        """Export report"""
        filename = f"sentinel_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "analyzer": type(self.analyzer).__name__,
            "scans": self.scan_count,
            "threats_found": self.threats_found,
            "threats": []
        }
        
        for row in range(self.threats_table.rowCount()):
            threat = {
                "time": self.threats_table.item(row, 0).text(),
                "process": self.threats_table.item(row, 1).text(),
                "type": self.threats_table.item(row, 2).text(),
                "severity": self.threats_table.item(row, 3).text(),
                "score": self.threats_table.item(row, 4).text()
            }
            report["threats"].append(threat)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.add_log(f"📄 Report exported: {filename}")
        self.show_notification(f"Report saved: {filename}", 3000)
    
    def update_analyzer_stats(self):
        """Update analyzer stats"""
        stats = f"""
╔════════════════════════════════════════════════════╗
║              SUPER ANALYZER STATUS                 ║
╠════════════════════════════════════════════════════╣
║  Status:              🟢 ACTIVE                    ║
║  Engine:              {type(self.analyzer).__name__:<20}║
║                                                     ║
║  Signatures Loaded:                                ║
║    • Categories:      {len(self.analyzer.threat_database):<20}║
║    • APT Groups:      {len(self.analyzer.threat_database.get('apt_groups', {})):<20}║
║    • Ransomware:      {len(self.analyzer.threat_database.get('ransomware', {})):<20}║
║    • Cryptominers:    {len(self.analyzer.threat_database.get('cryptominers', [])):<20}║
║                                                     ║
║  Current System:                                   ║
║    • CPU:             {psutil.cpu_percent()}%                      ║
║    • RAM:             {psutil.virtual_memory().percent}%                      ║
║    • Processes:       {len(list(psutil.process_iter())):<20}║
║                                                     ║
║  Protection Stats:                                 ║
║    • Scans:           {self.scan_count:<20}║
║    • Threats:         {self.threats_found:<20}║
║    • Real-time:       {"ON" if self.real_time_active else "OFF":<20}║
╚════════════════════════════════════════════════════╝
"""
        self.analyzer_stats.setText(stats)
    
    def add_log(self, message):
        """Add log message"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        QMetaObject.invokeMethod(self.log_text, "append", Qt.QueuedConnection, Q_ARG(str, f"[{timestamp}] {message}"))
    
    def show_notification(self, message, duration=3000):
        """Show notification"""
        NotificationWidget(message, self, duration)
    
    def start_background_monitoring(self):
        """Start background monitoring"""
        def monitor():
            while True:
                try:
                    cpu = psutil.cpu_percent()
                    mem = psutil.virtual_memory().percent
                    QMetaObject.invokeMethod(self.cpu_label, "setText", Qt.QueuedConnection, Q_ARG(str, f"CPU: {cpu}%"))
                    QMetaObject.invokeMethod(self.mem_label, "setText", Qt.QueuedConnection, Q_ARG(str, f"RAM: {mem}%"))
                    self.update_analyzer_stats()
                    threading.Event().wait(5)
                except:
                    threading.Event().wait(5)
        
        threading.Thread(target=monitor, daemon=True).start()


# ==================== MAIN ====================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SentinelAntivirus()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()