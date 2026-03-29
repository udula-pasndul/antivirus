# antivirus_with_analyzer.py - Full version with Super Analyzer
import sys
import json
import datetime
import threading
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import psutil
import platform

# Import Super Analyzer
from super_analyzer import get_analyzer, SuperAnalyzer

# ==================== THREAT DETECTION ENGINE WITH ANALYZER ====================
class AdvancedThreatEngine(QThread):
    threat_found = Signal(dict)
    scan_progress = Signal(int)
    scan_complete = Signal()
    log_message = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.scanning = False
        self.analyzer = get_analyzer()  # Link super analyzer
        
    def start_scan(self):
        self.scanning = True
        self.start()
    
    def run(self):
        self.log_message.emit("🔍 Starting advanced threat scan with Super Analyzer...")
        self.log_message.emit("📊 Using AI-powered threat detection engine")
        
        # Get all processes
        processes = list(psutil.process_iter(['pid', 'name']))
        total = len(processes)
        
        for i, proc in enumerate(processes):
            if not self.scanning:
                break
                
            try:
                # Deep analyze using super analyzer
                analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                
                if analysis["threat_score"] > 30:
                    self.threat_found.emit({
                        "type": "Advanced Threat Detection",
                        "severity": analysis["severity"],
                        "location": f"PID: {proc.info['pid']}",
                        "details": f"{proc.info['name']} - Score: {analysis['threat_score']}",
                        "recommendation": analysis["recommendations"][0] if analysis["recommendations"] else "Investigate",
                        "threats": analysis["threats"]
                    })
                    
                    # Log detailed threats
                    for threat in analysis["threats"]:
                        self.log_message.emit(f"  ⚠️ {threat['type']}: {threat['details']}")
                
                # Update progress
                progress = int((i + 1) / total * 100)
                self.scan_progress.emit(progress)
                
            except Exception as e:
                continue
        
        self.scan_complete.emit()
        self.log_message.emit("✅ Advanced scan completed!")
        self.scanning = False


# ==================== REAL-TIME MONITOR WITH ANALYZER ====================
class AdvancedRealTimeMonitor(QThread):
    threat_detected = Signal(dict)
    alert = Signal(str, str)
    
    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.known_processes = {}
        self.analyzer = get_analyzer()
        
    def start_monitoring(self):
        self.monitoring = True
        self.start()
    
    def stop_monitoring(self):
        self.monitoring = False
    
    def run(self):
        while self.monitoring:
            current_processes = {}
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    current_processes[proc.info['pid']] = proc.info['name']
                except:
                    continue
            
            # Check for new processes
            for pid, name in current_processes.items():
                if pid not in self.known_processes:
                    # Analyze new process
                    analysis = self.analyzer.deep_analyze_process(pid)
                    
                    if analysis["threat_score"] > 50:
                        self.threat_detected.emit({
                            "pid": pid,
                            "name": name,
                            "analysis": analysis
                        })
                        self.alert.emit(
                            f"⚠️ Threat Detected: {name}",
                            f"Process {name} (PID: {pid}) has threat score {analysis['threat_score']}\n\nThreats:\n" + 
                            "\n".join([f"- {t['type']}: {t['details']}" for t in analysis["threats"][:3]])
                        )
            
            self.known_processes = current_processes
            self.msleep(3000)


# ==================== MAIN WINDOW ====================
class AntivirusMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Advanced Antivirus Pro - Super Analyzer Edition")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize engines with super analyzer
        self.scan_engine = AdvancedThreatEngine()
        self.real_time_monitor = AdvancedRealTimeMonitor()
        self.analyzer = get_analyzer()
        
        # Connect signals
        self.connect_signals()
        
        # Setup UI
        self.setup_ui()
        self.apply_style()
        
        # Start status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
        
        # Show welcome
        self.add_log("🛡️ Advanced Antivirus Pro - Super Analyzer Edition")
        self.add_log("🤖 AI-Powered Threat Detection Engine Active")
    
    def connect_signals(self):
        self.scan_engine.threat_found.connect(self.add_threat)
        self.scan_engine.scan_progress.connect(self.update_progress)
        self.scan_engine.scan_complete.connect(self.scan_finished)
        self.scan_engine.log_message.connect(self.add_log)
        
        self.real_time_monitor.threat_detected.connect(self.on_realtime_threat)
        self.real_time_monitor.alert.connect(self.show_alert)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🛡️ ADVANCED ANTIVIRUS PRO")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #00ff00; padding: 15px; background-color: #1a1a1a;")
        main_layout.addWidget(header)
        
        # Subheader
        subheader = QLabel("Powered by Super Analyzer AI Engine | Real-time Protection | Behavioral Analysis")
        subheader.setAlignment(Qt.AlignCenter)
        subheader.setStyleSheet("color: #888888; padding: 5px;")
        main_layout.addWidget(subheader)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        buttons = [
            ("🔍 Quick Scan", self.start_scan, "#007acc"),
            ("⚡ Deep Scan", self.start_deep_scan, "#6a9955"),
            ("🛡️ Real-time", self.toggle_realtime, "#dcdcaa"),
            ("🔬 Rootkit Check", self.check_rootkits, "#ce9178"),
            ("📊 IOC Report", self.generate_ioc_report, "#e5c07b"),
            ("🗑️ Clear", self.clear_threats, "#d16969"),
            ("📑 Export", self.export_report, "#c586c0")
        ]
        
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(120)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(color)};
                }}
            """)
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3e3e42; background-color: #252526; }
            QTabBar::tab { background-color: #2d2d30; padding: 10px 20px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #007acc; }
        """)
        
        # Dashboard
        self.dashboard = self.create_dashboard()
        tabs.addTab(self.dashboard, "📊 Dashboard")
        
        # Threats
        self.threats_table = self.create_threats_table()
        tabs.addTab(self.threats_table, "⚠️ Threats")
        
        # System Monitor
        self.system_monitor = self.create_system_monitor()
        tabs.addTab(self.system_monitor, "📈 System")
        
        # Analyzer Stats
        self.analyzer_stats = self.create_analyzer_stats()
        tabs.addTab(self.analyzer_stats, "🤖 Analyzer Stats")
        
        # Log
        self.log_area = self.create_log_area()
        tabs.addTab(self.log_area, "📝 Log")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("✅ System Ready | Real-time: OFF | Super Analyzer: ACTIVE")
        self.status_bar.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        # System Health
        health_card = self.create_card("System Health", "🟢 Protected", "Super Analyzer Active")
        metrics_layout.addWidget(health_card)
        
        # Threats Card
        self.threats_card = self.create_card("Total Threats", "0", "Detected by AI")
        metrics_layout.addWidget(self.threats_card)
        
        # Scan Card
        self.scan_card = self.create_card("Last Scan", "Not run", "Click Quick Scan")
        metrics_layout.addWidget(self.scan_card)
        
        layout.addLayout(metrics_layout)
        
        # Recent Threats
        recent_label = QLabel("📋 Recent AI Detections")
        recent_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(recent_label)
        
        self.recent_threats = QTableWidget()
        self.recent_threats.setColumnCount(4)
        self.recent_threats.setHorizontalHeaderLabels(["Time", "Process", "Severity", "Threat Score"])
        self.recent_threats.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.recent_threats)
        
        layout.addStretch()
        return widget
    
    def create_card(self, title, value, subtitle):
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #00ff00; font-size: 22px; font-weight: bold;")
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #666666; font-size: 10px;")
        layout.addWidget(subtitle_label)
        
        if title == "Total Threats":
            self.threats_value_label = value_label
        elif title == "Last Scan":
            self.scan_value_label = value_label
            
        return card
    
    def create_threats_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Severity", "Type", "Process", "Details", "Threat Score", "Recommendation"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget { alternate-background-color: #2d2d30; gridline-color: #3e3e42; }
            QTableWidget::item { padding: 5px; }
        """)
        return table
    
    def create_system_monitor(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # CPU
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout()
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # Memory
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout()
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        memory_layout.addWidget(self.memory_bar)
        memory_group.setLayout(memory_layout)
        layout.addWidget(memory_group)
        
        # Processes
        process_label = QLabel("Running Processes (Top 30 by CPU)")
        process_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(process_label)
        
        self.process_list = QTreeWidget()
        self.process_list.setHeaderLabels(["Process", "PID", "CPU%", "Memory%", "Threat Score"])
        layout.addWidget(self.process_list)
        
        # Update timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_system_stats)
        self.monitor_timer.start(2000)
        
        return widget
    
    def create_analyzer_stats(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats display
        self.analyzer_text = QTextEdit()
        self.analyzer_text.setReadOnly(True)
        self.analyzer_text.setStyleSheet("background-color: #1e1e1e; font-family: Consolas; font-size: 11px;")
        layout.addWidget(self.analyzer_text)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Stats")
        refresh_btn.clicked.connect(self.update_analyzer_stats)
        layout.addWidget(refresh_btn)
        
        self.update_analyzer_stats()
        
        return widget
    
    def create_log_area(self):
        log = QTextEdit()
        log.setReadOnly(True)
        log.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 11px;")
        return log
    
    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { background-color: #252526; color: #ffffff; }
            QGroupBox { border: 1px solid #3e3e42; border-radius: 5px; margin-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QProgressBar { border: 1px solid #3e3e42; border-radius: 3px; text-align: center; }
            QProgressBar::chunk { background-color: #007acc; border-radius: 3px; }
        """)
    
    def lighten_color(self, color):
        return "#00aaff" if color == "#007acc" else "#88cc77"
    
    # ==================== ACTIONS ====================
    def start_scan(self):
        self.progress_bar.show()
        self.progress_bar.setRange(0, 100)
        self.add_log("🚀 Starting AI-powered threat scan...")
        self.scan_engine.start_scan()
    
    def start_deep_scan(self):
        self.add_log("🔬 Running deep analysis with behavioral detection...")
        
        def deep_scan():
            threats = self.analyzer.scan_all_processes()
            for threat in threats:
                self.add_threat({
                    "type": "Deep Scan Detection",
                    "severity": threat['analysis']['severity'],
                    "location": f"PID: {threat['pid']}",
                    "details": f"{threat['name']} - CPU: {threat.get('cpu', 0)}%",
                    "recommendation": threat['analysis']['recommendations'][0] if threat['analysis']['recommendations'] else "Investigate",
                    "threats": threat['analysis']['threats']
                })
            self.add_log(f"✅ Deep scan complete - Found {len(threats)} threats")
        
        threading.Thread(target=deep_scan, daemon=True).start()
    
    def toggle_realtime(self):
        if self.real_time_monitor.monitoring:
            self.real_time_monitor.stop_monitoring()
            self.status_label.setText("✅ System Ready | Real-time: OFF | Super Analyzer: ACTIVE")
            self.add_log("🛡️ Real-time protection disabled")
        else:
            self.real_time_monitor.start_monitoring()
            self.status_label.setText("🛡️ System Protected | Real-time: ACTIVE | Super Analyzer: ACTIVE")
            self.add_log("🛡️ Real-time protection enabled with Super Analyzer")
    
    def check_rootkits(self):
        self.add_log("🔍 Running rootkit detection...")
        
        def check():
            result = self.analyzer.rootkit_detection()
            if result["rootkit_detected"]:
                self.add_log(f"🚨 ROOTKIT DETECTED! Hidden processes: {result['hidden_processes']}")
                self.add_threat({
                    "type": "Rootkit Detection",
                    "severity": "CRITICAL",
                    "location": "System Kernel",
                    "details": f"Hidden processes: {result['hidden_processes']}",
                    "recommendation": "Run specialized rootkit removal tool",
                    "threats": []
                })
            else:
                self.add_log("✅ No rootkits detected")
        
        threading.Thread(target=check, daemon=True).start()
    
    def generate_ioc_report(self):
        self.add_log("📊 Generating IOC report...")
        
        def generate():
            iocs = self.analyzer.generate_ioc_report()
            filename = f"ioc_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(iocs, f, indent=2)
            
            self.add_log(f"📁 IOC Report saved: {filename}")
            self.add_log(f"📊 Summary: {iocs['summary']['suspicious_processes']} suspicious processes, "
                        f"{iocs['summary']['suspicious_connections']} suspicious connections")
            
            QMessageBox.information(self, "IOC Report", 
                f"Report saved to {filename}\n\n"
                f"Suspicious Processes: {iocs['summary']['suspicious_processes']}\n"
                f"Suspicious Connections: {iocs['summary']['suspicious_connections']}\n"
                f"Total Threat Score: {iocs['summary']['total_threat_score']}")
        
        threading.Thread(target=generate, daemon=True).start()
    
    def update_analyzer_stats(self):
        stats = f"""
╔══════════════════════════════════════════════════════════════╗
║                    SUPER ANALYZER STATS                      ║
╠══════════════════════════════════════════════════════════════╣
║  AI Engine Status:  🟢 ACTIVE                                ║
║  Detection Methods: Behavioral, Signature, Heuristic        ║
║                                                              ║
║  Threat Signatures Loaded:                                   ║
║    • APT Groups: 2                                          ║
║    • Ransomware: 3                                          ║
║    • Cryptominers: 5                                        ║
║    • Malicious Ports: 6                                     ║
║                                                              ║
║  Analysis Capabilities:                                      ║
║    • Process Memory Analysis: ✓                             ║
║    • Network Behavior: ✓                                    ║
║    • CPU/Resource Monitoring: ✓                             ║
║    • Rootkit Detection: ✓                                   ║
║    • IOC Generation: ✓                                      ║
║                                                              ║
║  Current System Status:                                      ║
║    • Running Processes: {len(list(psutil.process_iter()))}                              ║
║    • CPU Usage: {psutil.cpu_percent()}%                                        ║
║    • Memory Usage: {psutil.virtual_memory().percent}%                                      ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.analyzer_text.setText(stats)
    
    def add_threat(self, threat_data):
        row = self.threats_table.rowCount()
        self.threats_table.insertRow(row)
        
        severity = threat_data["severity"]
        severity_item = QTableWidgetItem(severity)
        if severity == "CRITICAL":
            severity_item.setForeground(QColor(255, 0, 0))
        elif severity == "HIGH":
            severity_item.setForeground(QColor(255, 100, 0))
        elif severity == "MEDIUM":
            severity_item.setForeground(QColor(255, 200, 0))
        
        threat_score = threat_data.get("threats", [{}])[0].get("risk", "N/A") if threat_data.get("threats") else "N/A"
        
        self.threats_table.setItem(row, 0, severity_item)
        self.threats_table.setItem(row, 1, QTableWidgetItem(threat_data["type"]))
        self.threats_table.setItem(row, 2, QTableWidgetItem(threat_data["details"][:50]))
        self.threats_table.setItem(row, 3, QTableWidgetItem(threat_data["location"]))
        self.threats_table.setItem(row, 4, QTableWidgetItem(str(threat_score)))
        self.threats_table.setItem(row, 5, QTableWidgetItem(threat_data["recommendation"]))
        
        # Update dashboard
        threat_count = self.threats_table.rowCount()
        if hasattr(self, 'threats_value_label'):
            self.threats_value_label.setText(str(threat_count))
        
        # Add to recent
        recent_row = self.recent_threats.rowCount()
        self.recent_threats.insertRow(recent_row)
        self.recent_threats.setItem(recent_row, 0, QTableWidgetItem(datetime.datetime.now().strftime("%H:%M:%S")))
        self.recent_threats.setItem(recent_row, 1, QTableWidgetItem(threat_data["details"][:30]))
        self.recent_threats.setItem(recent_row, 2, QTableWidgetItem(severity))
        self.recent_threats.setItem(recent_row, 3, QTableWidgetItem(str(threat_score)))
    
    def on_realtime_threat(self, threat):
        self.add_log(f"🚨 REAL-TIME THREAT: {threat['name']} (Score: {threat['analysis']['threat_score']})")
        self.add_threat({
            "type": "Real-time Detection",
            "severity": threat['analysis']['severity'],
            "location": f"PID: {threat['pid']}",
            "details": threat['name'],
            "recommendation": "Process detected in real-time - Investigate immediately",
            "threats": threat['analysis']['threats']
        })
    
    def clear_threats(self):
        self.threats_table.setRowCount(0)
        self.recent_threats.setRowCount(0)
        if hasattr(self, 'threats_value_label'):
            self.threats_value_label.setText("0")
        self.add_log("🗑️ Cleared all threats")
    
    def export_report(self):
        filename = f"antivirus_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system": {"os": platform.system(), "release": platform.release()},
            "threats": []
        }
        
        for row in range(self.threats_table.rowCount()):
            threat = {
                "severity": self.threats_table.item(row, 0).text(),
                "type": self.threats_table.item(row, 1).text(),
                "details": self.threats_table.item(row, 2).text(),
                "location": self.threats_table.item(row, 3).text()
            }
            report["threats"].append(threat)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.add_log(f"📑 Report exported: {filename}")
        QMessageBox.information(self, "Export", f"Report saved to {filename}")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def scan_finished(self):
        self.progress_bar.hide()
        self.add_log("✅ Scan completed!")
        if hasattr(self, 'scan_value_label'):
            self.scan_value_label.setText(datetime.datetime.now().strftime("%H:%M:%S"))
    
    def update_system_stats(self):
        try:
            cpu = psutil.cpu_percent()
            self.cpu_bar.setValue(int(cpu))
            self.cpu_bar.setFormat(f"CPU: {cpu}%")
            
            memory = psutil.virtual_memory()
            self.memory_bar.setValue(int(memory.percent))
            self.memory_bar.setFormat(f"Memory: {memory.percent}%")
            
            self.process_list.clear()
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except:
                    continue
            
            processes.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
            
            for proc in processes[:30]:
                if proc.get('name'):
                    # Get threat score
                    threat_score = "N/A"
                    try:
                        analysis = self.analyzer.deep_analyze_process(proc['pid'])
                        threat_score = analysis["threat_score"]
                    except:
                        pass
                    
                    item = QTreeWidgetItem([
                        proc['name'][:40],
                        str(proc['pid']),
                        f"{proc.get('cpu_percent', 0):.1f}",
                        f"{proc.get('memory_percent', 0):.1f}",
                        str(threat_score)
                    ])
                    
                    if isinstance(threat_score, int) and threat_score > 50:
                        item.setForeground(4, QColor(255, 0, 0))
                    
                    self.process_list.addTopLevelItem(item)
        except:
            pass
    
    def update_status(self):
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            self.status_bar.showMessage(f"CPU: {cpu}% | Memory: {memory}% | Super Analyzer: Active")
        except:
            pass
    
    def add_log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
    
    def show_alert(self, title, message):
        QMessageBox.warning(self, title, message)


# ==================== MAIN ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = AntivirusMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()