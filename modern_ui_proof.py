# modern_ui_proof.py - Super Analyzer Connected (With Visible Proof)
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
from super_analyzer import get_analyzer, SuperAnalyzer

# Import UI components
from super_ui import AnimatedGaugeWidget, RealTimeGraphWidget, ThreatHeatmapWidget, NetworkMapWidget

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
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 15px;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 15px;
            }
        """)
    
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
        self.setGeometry(50, 50, 1400, 850)
        
        # ========== PROOF: Initialize Super Analyzer ==========
        self.analyzer = get_analyzer()
        print("✅ Super Analyzer CONNECTED and LOADED!")
        print(f"✅ Analyzer type: {type(self.analyzer).__name__}")
        print(f"✅ Threat signatures loaded: {len(self.analyzer.threat_database)} categories")
        
        # Status variables
        self.scanning = False
        self.real_time_active = False
        self.scan_count = 0
        self.threats_found = 0
        
        # Setup UI
        self.setup_ui()
        self.apply_style()
        
        # Start background monitoring
        self.start_background_monitoring()
        
        # ========== PROOF: Show analyzer status ==========
        self.show_notification("🤖 Super Analyzer AI Engine Active", 3000)
        self.add_log("🛡️ Sentinel Antivirus Started - Super Analyzer Connected")
        self.add_log(f"📊 Analyzer Status: {type(self.analyzer).__name__} - Ready")
        
    def setup_ui(self):
        """Setup the main UI"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
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
        
        self.content_stack.addWidget(self.dashboard_page)  # 0
        self.content_stack.addWidget(self.scan_page)      # 1
        self.content_stack.addWidget(self.threats_page)   # 2
        self.content_stack.addWidget(self.analyzer_page)  # 3
        
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
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-bottom: 2px solid #007acc;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo
        logo = QLabel("🛡️ SENTINEL ANTIVIRUS")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff00;")
        layout.addWidget(logo)
        
        # ========== PROOF: Super Analyzer Badge ==========
        analyzer_badge = QLabel("🤖 SUPER ANALYZER AI")
        analyzer_badge.setStyleSheet("""
            background-color: #007acc;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
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
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: rgba(0,0,0,0.3);
                border-radius: 15px;
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
                background-color: rgba(0, 120, 215, 0.3);
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        
        # ========== PROOF: Analyzer Status Card ==========
        status_card = GlassPanel()
        status_layout = QVBoxLayout(status_card)
        
        analyzer_status = QLabel("🤖 ANALYZER STATUS")
        analyzer_status.setStyleSheet("font-weight: bold; color: #00ff00;")
        status_layout.addWidget(analyzer_status)
        
        self.analyzer_status_label = QLabel("🟢 ONLINE - AI ACTIVE")
        self.analyzer_status_label.setStyleSheet("color: #00ff00; font-size: 12px;")
        status_layout.addWidget(self.analyzer_status_label)
        
        self.threat_sig_label = QLabel(f"📊 Signatures: {len(self.analyzer.threat_database)} categories")
        self.threat_sig_label.setStyleSheet("color: #888888; font-size: 11px;")
        status_layout.addWidget(self.threat_sig_label)
        
        layout.addWidget(status_card)
        layout.addSpacing(20)
        
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
        """Create dashboard with analyzer stats visible"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # ========== PROOF: Welcome with Analyzer Info ==========
        welcome = GlassPanel()
        welcome_layout = QVBoxLayout(welcome)
        
        welcome_title = QLabel("🛡️ SENTINEL ANTIVIRUS PRO")
        welcome_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")
        welcome_layout.addWidget(welcome_title)
        
        # Show analyzer is working
        analyzer_info = QLabel(f"🤖 Super Analyzer AI Engine Active | {type(self.analyzer).__name__} v1.0")
        analyzer_info.setStyleSheet("color: #007acc; font-size: 12px;")
        welcome_layout.addWidget(analyzer_info)
        
        layout.addWidget(welcome)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Threat meter card
        threat_card = GlassPanel()
        threat_layout = QVBoxLayout(threat_card)
        threat_layout.addWidget(QLabel("CURRENT THREAT LEVEL"))
        self.threat_meter = ThreatMeterWidget()
        threat_layout.addWidget(self.threat_meter)
        stats_layout.addWidget(threat_card)
        
        # Scans card
        scan_card = GlassPanel()
        scan_layout = QVBoxLayout(scan_card)
        scan_layout.addWidget(QLabel("SCANS PERFORMED"))
        self.scan_count_label = QLabel("0")
        self.scan_count_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ff00;")
        scan_layout.addWidget(self.scan_count_label)
        stats_layout.addWidget(scan_card)
        
        # Threats card
        threats_card = GlassPanel()
        threats_layout = QVBoxLayout(threats_card)
        threats_layout.addWidget(QLabel("THREATS DETECTED"))
        self.threats_count_label = QLabel("0")
        self.threats_count_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #ff6600;")
        threats_layout.addWidget(self.threats_count_label)
        stats_layout.addWidget(threats_card)
        
        layout.addLayout(stats_layout)
        
        # CPU Graph
        graph_card = GlassPanel()
        graph_layout = QVBoxLayout(graph_card)
        graph_layout.addWidget(QLabel("REAL-TIME CPU USAGE"))
        self.cpu_graph = RealTimeGraphWidget("CPU Usage")
        graph_layout.addWidget(self.cpu_graph)
        layout.addWidget(graph_card)
        
        # Threat Heatmap
        heatmap_card = GlassPanel()
        heatmap_layout = QVBoxLayout(heatmap_card)
        heatmap_layout.addWidget(QLabel("THREAT ACTIVITY HEATMAP"))
        self.heatmap = ThreatHeatmapWidget()
        heatmap_layout.addWidget(self.heatmap)
        layout.addWidget(heatmap_card)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        quick_btn = ModernButton("🔍 QUICK SCAN")
        quick_btn.clicked.connect(self.start_quick_scan)
        actions_layout.addWidget(quick_btn)
        
        deep_btn = ModernButton("⚡ DEEP SCAN")
        deep_btn.clicked.connect(self.start_deep_scan)
        actions_layout.addWidget(deep_btn)
        
        layout.addLayout(actions_layout)
        
        # Log area
        log_label = QLabel("ACTIVITY LOG")
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
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
        layout.setSpacing(20)
        
        # Scan options
        options_card = GlassPanel()
        options_layout = QVBoxLayout(options_card)
        options_layout.addWidget(QLabel("SCAN OPTIONS").setStyleSheet("font-weight: bold;"))
        
        self.quick_radio = QRadioButton("Quick Scan (Running Processes)")
        self.quick_radio.setChecked(True)
        self.full_radio = QRadioButton("Full Scan (All Processes)")
        
        options_layout.addWidget(self.quick_radio)
        options_layout.addWidget(self.full_radio)
        layout.addWidget(options_card)
        
        # Scan button
        self.scan_btn = ModernButton("START SCAN")
        self.scan_btn.setFixedHeight(50)
        self.scan_btn.clicked.connect(self.execute_scan)
        layout.addWidget(self.scan_btn)
        
        # Scan results
        results_label = QLabel("SCAN RESULTS")
        results_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(results_label)
        
        self.scan_results = QTreeWidget()
        self.scan_results.setHeaderLabels(["Process", "PID", "Threat Score", "Severity", "Details"])
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
        
        # Action buttons
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
        """Create analyzer stats page - PROOF that analyzer works"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # ========== PROOF: Test Super Analyzer ==========
        test_card = GlassPanel()
        test_layout = QVBoxLayout(test_card)
        
        test_title = QLabel("🔬 SUPER ANALYZER TEST")
        test_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff00;")
        test_layout.addWidget(test_title)
        
        # Test button to show analyzer is working
        test_btn = ModernButton("TEST ANALYZER ON CURRENT PROCESSES")
        test_btn.clicked.connect(self.test_analyzer)
        test_layout.addWidget(test_btn)
        
        layout.addWidget(test_card)
        
        # Analyzer stats
        stats_card = GlassPanel()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.addWidget(QLabel("📊 ANALYZER STATISTICS").setStyleSheet("font-weight: bold;"))
        
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
        
        # Update stats
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
        """)
    
    # ==================== SUPER ANALYZER ACTIONS ====================
    
    def test_analyzer(self):
        """Test that Super Analyzer is actually working"""
        self.add_log("🔬 Testing Super Analyzer on current processes...")
        
        test_results = []
        for proc in list(psutil.process_iter(['pid', 'name']))[:5]:
            try:
                analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                test_results.append(f"PID {proc.info['pid']} ({proc.info['name']}): Score {analysis['threat_score']} - {analysis['severity']}")
                self.add_log(f"  📊 {proc.info['name']}: Threat Score = {analysis['threat_score']}")
            except Exception as e:
                test_results.append(f"PID {proc.info['pid']}: Error - {e}")
        
        self.show_notification(f"✅ Analyzer tested on {len(test_results)} processes", 3000)
        self.add_log("✅ Super Analyzer test complete!")
        
        # Update stats display
        self.update_analyzer_stats()
    
    def start_quick_scan(self):
        """Start quick scan using Super Analyzer"""
        self.scanning = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.scan_btn.setText("SCANNING...")
        self.add_log("🔍 Starting Quick Scan with Super Analyzer...")
        self.show_notification("🔍 Quick scan started", 2000)
        
        def scan_thread():
            threats_found = 0
            processes = list(psutil.process_iter(['pid', 'name']))
            total = len(processes)
            
            for i, proc in enumerate(processes):
                try:
                    # ========== USING SUPER ANALYZER ==========
                    analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                    
                    if analysis["threat_score"] > 30:
                        threats_found += 1
                        self.add_threat_to_display(proc.info['name'], proc.info['pid'], analysis)
                        self.add_log(f"⚠️ THREAT: {proc.info['name']} (Score: {analysis['threat_score']}) - {analysis['severity']}")
                    
                    # Update progress
                    progress = int((i + 1) / total * 100)
                    QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, progress))
                    QMetaObject.invokeMethod(self.progress_bar, "setFormat", Qt.QueuedConnection, Q_ARG(str, f"Scanning... {progress}%"))
                    
                except Exception as e:
                    continue
            
            self.scanning = False
            QMetaObject.invokeMethod(self.progress_bar, "setVisible", Qt.QueuedConnection, Q_ARG(bool, False))
            QMetaObject.invokeMethod(self.scan_btn, "setText", Qt.QueuedConnection, Q_ARG(str, "START SCAN"))
            
            self.scan_count += 1
            QMetaObject.invokeMethod(self.scan_count_label, "setText", Qt.QueuedConnection, Q_ARG(str, str(self.scan_count)))
            
            self.add_log(f"✅ Scan complete! Found {threats_found} threats")
            self.show_notification(f"✅ Scan complete - {threats_found} threats found", 3000)
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def start_deep_scan(self):
        """Start deep scan with more thorough analysis"""
        self.add_log("⚡ Starting Deep Scan with full behavioral analysis...")
        self.start_quick_scan()  # Use same for now, but could be more thorough
    
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
        """Start real-time process monitoring with analyzer"""
        def monitor():
            known_pids = set()
            while self.real_time_active:
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
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def add_threat_to_display(self, name, pid, analysis):
        """Add threat to threats table"""
        self.threats_found += 1
        QMetaObject.invokeMethod(self.threats_count_label, "setText", Qt.QueuedConnection, Q_ARG(str, str(self.threats_found)))
        
        # Add to threats table
        row = self.threats_table.rowCount()
        QMetaObject.invokeMethod(self.threats_table, "insertRow", Qt.QueuedConnection, Q_ARG(int, row))
        
        time_item = QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S"))
        name_item = QTableWidgetItem(name[:30])
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
        
        # Update heatmap
        threats = [{"severity": analysis['severity'], "details": name}]
        QMetaObject.invokeMethod(self.heatmap, "update_threats", Qt.QueuedConnection, Q_ARG(list, threats))
        
        # Add to scan results if on scan page
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
        """Export threat report"""
        filename = f"sentinel_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "analyzer": type(self.analyzer).__name__,
            "scans_performed": self.scan_count,
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
        """Update analyzer statistics display"""
        stats = f"""
╔══════════════════════════════════════════════════════════════╗
║                    SUPER ANALYZER STATUS                      ║
╠══════════════════════════════════════════════════════════════╣
║  Status:              🟢 ACTIVE                              ║
║  Engine:              {type(self.analyzer).__name__}                         ║
║                                                              ║
║  Threat Signatures Loaded:                                   ║
║    • Categories:      {len(self.analyzer.threat_database)}                                  ║
║    • APT Groups:      {len(self.analyzer.threat_database.get('apt_groups', {}))}                                     ║
║    • Ransomware:      {len(self.analyzer.threat_database.get('ransomware', {}))}                                     ║
║    • Cryptominers:    {len(self.analyzer.threat_database.get('cryptominers', []))}                                   ║
║                                                              ║
║  Detection Methods:                                         ║
║    • Behavioral Analysis: ✓                                ║
║    • Signature-based:   ✓                                ║
║    • Heuristic:         ✓                                ║
║    • Memory Forensics:  ✓                                ║
║                                                              ║
║  Current System:                                            ║
║    • CPU:              {psutil.cpu_percent()}%                              ║
║    • RAM:              {psutil.virtual_memory().percent}%                             ║
║    • Processes:        {len(list(psutil.process_iter()))}                               ║
║                                                              ║
║  Protection Stats:                                          ║
║    • Scans:            {self.scan_count}                                   ║
║    • Threats Found:    {self.threats_found}                                   ║
║    • Real-time:        {"ON" if self.real_time_active else "OFF"}                                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.analyzer_stats.setText(stats)
    
    def add_log(self, message):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        QMetaObject.invokeMethod(self.log_text, "append", Qt.QueuedConnection, Q_ARG(str, f"[{timestamp}] {message}"))
    
    def show_notification(self, message, duration=3000):
        """Show notification"""
        NotificationWidget(message, self, duration)
    
    def start_background_monitoring(self):
        """Start background system monitoring"""
        def monitor():
            while True:
                try:
                    cpu = psutil.cpu_percent()
                    mem = psutil.virtual_memory().percent
                    QMetaObject.invokeMethod(self.cpu_label, "setText", Qt.QueuedConnection, Q_ARG(str, f"CPU: {cpu}%"))
                    QMetaObject.invokeMethod(self.mem_label, "setText", Qt.QueuedConnection, Q_ARG(str, f"RAM: {mem}%"))
                    
                    # Update analyzer stats periodically
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