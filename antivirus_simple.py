# antivirus_simple.py - Completely Working Windows Version
import sys
import os
import json
import datetime
import threading
from pathlib import Path

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTabWidget,
    QProgressBar, QStatusBar, QMessageBox, QHeaderView, QFrame,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QCheckBox, QGroupBox
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QSize
)
from PySide6.QtGui import (
    QFont, QIcon, QPalette, QColor, QBrush
)

# System monitoring libraries
import psutil
import platform

# ==================== THREAT DETECTION ENGINE ====================
class ThreatDetectionEngine(QThread):
    """Background thread for scanning without freezing UI"""
    threat_found = Signal(dict)
    scan_progress = Signal(int)
    scan_complete = Signal()
    log_message = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.scanning = False
        self.threat_signatures = self.load_signatures()
        
    def load_signatures(self):
        """Load threat signatures"""
        return {
            "malicious_processes": [
                "mimikatz", "nc.exe", "netcat", "wce.exe", "pwdump",
                "fgdump", "hashdump", "keylog", "injector", "rootkit",
                "xmrig", "miner", "cryptonight"
            ],
            "malicious_ports": [4444, 5555, 6666, 7777, 8888, 31337],
        }
    
    def start_quick_scan(self):
        """Start quick system scan"""
        self.scanning = True
        self.start()
    
    def run(self):
        """Main scan thread"""
        self.log_message.emit("🔍 Starting system scan...")
        
        # Scan processes
        self.scan_processes()
        
        # Scan network
        self.scan_network()
        
        self.scan_complete.emit()
        self.log_message.emit("✅ Scan completed!")
        self.scanning = False
    
    def scan_processes(self):
        """Scan running processes"""
        self.log_message.emit("📊 Analyzing processes...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                
                for threat in self.threat_signatures["malicious_processes"]:
                    if threat in proc_name:
                        self.threat_found.emit({
                            "type": "Malicious Process",
                            "severity": "HIGH",
                            "location": f"PID: {proc.info['pid']}",
                            "details": f"Process: {proc_name}",
                            "recommendation": "Terminate process and investigate"
                        })
                        self.log_message.emit(f"⚠️ THREAT: {proc_name}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def scan_network(self):
        """Scan network connections"""
        self.log_message.emit("🌐 Analyzing network connections...")
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                if conn.raddr.port in self.threat_signatures["malicious_ports"]:
                    self.threat_found.emit({
                        "type": "Malicious Connection",
                        "severity": "HIGH",
                        "location": f"Port: {conn.raddr.port}",
                        "details": f"Connected to {conn.raddr.ip}:{conn.raddr.port}",
                        "recommendation": "Investigate network traffic"
                    })


# ==================== REAL-TIME MONITOR ====================
class RealTimeMonitor(QThread):
    """Background thread for real-time protection"""
    process_started = Signal(dict)
    alert = Signal(str, str)
    
    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.known_processes = set()
        
    def start_monitoring(self):
        self.monitoring = True
        self.start()
    
    def stop_monitoring(self):
        self.monitoring = False
    
    def run(self):
        while self.monitoring:
            current_processes = set()
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    current_processes.add((proc.info['pid'], proc.info['name']))
                except:
                    continue
            
            new_processes = current_processes - self.known_processes
            for pid, name in new_processes:
                self.process_started.emit({"pid": pid, "name": name})
                
                suspicious = ['mimikatz', 'nc.exe', 'netcat', 'wce']
                if any(s in name.lower() for s in suspicious):
                    self.alert.emit(name, f"Suspicious process detected: {name}")
            
            self.known_processes = current_processes
            self.msleep(3000)


# ==================== MAIN WINDOW ====================
class AntivirusMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Advanced Antivirus Pro")
        self.setGeometry(100, 100, 1300, 700)
        
        # Initialize engines
        self.scan_engine = ThreatDetectionEngine()
        self.real_time_monitor = RealTimeMonitor()
        
        # Connect signals
        self.connect_signals()
        
        # Setup UI
        self.setup_ui()
        self.apply_style()
        
        # Start status bar updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
    
    def connect_signals(self):
        """Connect all signal/slots"""
        self.scan_engine.threat_found.connect(self.add_threat)
        self.scan_engine.scan_complete.connect(self.scan_finished)
        self.scan_engine.log_message.connect(self.add_log)
        
        self.real_time_monitor.process_started.connect(self.on_process_started)
        self.real_time_monitor.alert.connect(self.show_alert)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🛡️ ADVANCED ANTIVIRUS PRO")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #00ff00; padding: 10px;")
        main_layout.addWidget(header)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        buttons = [
            ("🔍 Quick Scan", self.start_quick_scan, "#007acc"),
            ("⚡ Full Scan", self.start_full_scan, "#6a9955"),
            ("🛡️ Real-time Protection", self.toggle_realtime, "#dcdcaa"),
            ("📊 System Info", self.show_system_info, "#ce9178"),
            ("🗑️ Clear Threats", self.clear_threats, "#d16969"),
            ("📑 Export Report", self.export_report, "#e5c07b")
        ]
        
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(140)
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
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
        """)
        
        # Dashboard tab
        self.dashboard = self.create_dashboard()
        tabs.addTab(self.dashboard, "📊 Dashboard")
        
        # Threats tab
        self.threats_table = self.create_threats_table()
        tabs.addTab(self.threats_table, "⚠️ Threats")
        
        # System Monitor tab
        self.system_monitor = self.create_system_monitor()
        tabs.addTab(self.system_monitor, "📈 System Monitor")
        
        # Log tab
        self.log_area = self.create_log_area()
        tabs.addTab(self.log_area, "📝 Log")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("✅ System Ready | Real-time: OFF")
        self.status_bar.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_dashboard(self):
        """Create dashboard with metrics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Metrics grid
        metrics_layout = QHBoxLayout()
        
        # System health card
        health_card = self.create_card("System Health", "🟢 Good", "No active threats")
        metrics_layout.addWidget(health_card)
        
        # Last scan card
        self.scan_card = self.create_card("Last Scan", "Not run yet", "Click Quick Scan")
        metrics_layout.addWidget(self.scan_card)
        
        # Threats card
        self.threats_card = self.create_card("Total Threats", "0", "No threats detected")
        metrics_layout.addWidget(self.threats_card)
        
        layout.addLayout(metrics_layout)
        
        # Recent threats
        recent_label = QLabel("📋 Recent Threats")
        recent_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(recent_label)
        
        self.recent_threats = QTableWidget()
        self.recent_threats.setColumnCount(4)
        self.recent_threats.setHorizontalHeaderLabels(["Time", "Type", "Severity", "Location"])
        self.recent_threats.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.recent_threats)
        
        layout.addStretch()
        return widget
    
    def create_card(self, title, value, subtitle):
        """Create a metric card"""
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
        
        # Store value label for updates
        if title == "Total Threats":
            self.threats_value_label = value_label
        elif title == "Last Scan":
            self.scan_value_label = value_label
            
        return card
    
    def create_threats_table(self):
        """Create threats table"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Severity", "Type", "Location", "Details", "Recommendation"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #2d2d30;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        return table
    
    def create_system_monitor(self):
        """Create system monitor"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # CPU Group
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout()
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # Memory Group
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout()
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        memory_layout.addWidget(self.memory_bar)
        memory_group.setLayout(memory_layout)
        layout.addWidget(memory_group)
        
        # Process List
        process_label = QLabel("Running Processes")
        process_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(process_label)
        
        self.process_list = QTreeWidget()
        self.process_list.setHeaderLabels(["Process Name", "PID", "CPU %", "Memory %"])
        layout.addWidget(self.process_list)
        
        # Update timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_system_stats)
        self.monitor_timer.start(2000)
        
        return widget
    
    def create_log_area(self):
        """Create log area"""
        log = QTextEdit()
        log.setReadOnly(True)
        log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas';
                font-size: 11px;
            }
        """)
        return log
    
    def apply_style(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #252526;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
    
    def lighten_color(self, color):
        """Lighten a color for hover effect"""
        return "#00aaff" if color == "#007acc" else "#88cc77"
    
    # ==================== SCAN METHODS ====================
    def start_quick_scan(self):
        """Start quick scan"""
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        self.add_log("🚀 Starting quick system scan...")
        self.scan_engine.start_quick_scan()
    
    def start_full_scan(self):
        """Start full system scan"""
        self.add_log("⚡ Full scan feature coming soon...")
        QMessageBox.information(self, "Info", "Full scan will be available in next update")
    
    def toggle_realtime(self):
        """Toggle real-time protection"""
        if self.real_time_monitor.monitoring:
            self.real_time_monitor.stop_monitoring()
            self.status_label.setText("✅ System Ready | Real-time: OFF")
            self.add_log("🛡️ Real-time protection disabled")
        else:
            self.real_time_monitor.start_monitoring()
            self.status_label.setText("🛡️ System Protected | Real-time: ACTIVE")
            self.add_log("🛡️ Real-time protection enabled")
    
    def show_system_info(self):
        """Show system information"""
        info = f"""
        System: {platform.system()} {platform.release()}
        Processor: {platform.processor()}
        RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB
        CPU Cores: {psutil.cpu_count()}
        """
        QMessageBox.information(self, "System Information", info)
        self.add_log("📊 System information displayed")
    
    def add_threat(self, threat_data):
        """Add threat to threats table"""
        row = self.threats_table.rowCount()
        self.threats_table.insertRow(row)
        
        # Set severity color
        severity = threat_data["severity"]
        severity_item = QTableWidgetItem(severity)
        if severity == "HIGH":
            severity_item.setForeground(QColor(255, 0, 0))
        elif severity == "MEDIUM":
            severity_item.setForeground(QColor(255, 165, 0))
        
        self.threats_table.setItem(row, 0, severity_item)
        self.threats_table.setItem(row, 1, QTableWidgetItem(threat_data["type"]))
        self.threats_table.setItem(row, 2, QTableWidgetItem(threat_data["location"]))
        self.threats_table.setItem(row, 3, QTableWidgetItem(threat_data["details"]))
        self.threats_table.setItem(row, 4, QTableWidgetItem(threat_data["recommendation"]))
        
        # Update dashboard
        threat_count = self.threats_table.rowCount()
        if hasattr(self, 'threats_value_label'):
            self.threats_value_label.setText(str(threat_count))
        
        # Add to recent threats
        recent_row = self.recent_threats.rowCount()
        self.recent_threats.insertRow(recent_row)
        self.recent_threats.setItem(recent_row, 0, QTableWidgetItem(
            datetime.datetime.now().strftime("%H:%M:%S")
        ))
        self.recent_threats.setItem(recent_row, 1, QTableWidgetItem(threat_data["type"]))
        self.recent_threats.setItem(recent_row, 2, QTableWidgetItem(severity))
        self.recent_threats.setItem(recent_row, 3, QTableWidgetItem(threat_data["location"]))
    
    def clear_threats(self):
        """Clear all threats from table"""
        self.threats_table.setRowCount(0)
        self.recent_threats.setRowCount(0)
        if hasattr(self, 'threats_value_label'):
            self.threats_value_label.setText("0")
        self.add_log("🗑️ Cleared all threat records")
    
    def export_report(self):
        """Export scan report"""
        filename = f"antivirus_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system": {
                "os": platform.system(),
                "release": platform.release(),
            },
            "threats": []
        }
        
        for row in range(self.threats_table.rowCount()):
            threat = {
                "severity": self.threats_table.item(row, 0).text(),
                "type": self.threats_table.item(row, 1).text(),
                "location": self.threats_table.item(row, 2).text(),
                "details": self.threats_table.item(row, 3).text()
            }
            report["threats"].append(threat)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.add_log(f"📑 Report exported to {filename}")
        QMessageBox.information(self, "Export Complete", f"Report saved as {filename}")
    
    def scan_finished(self):
        """Handle scan completion"""
        self.progress_bar.hide()
        self.add_log("✅ Scan completed successfully!")
        if hasattr(self, 'scan_value_label'):
            self.scan_value_label.setText(datetime.datetime.now().strftime("%H:%M:%S"))
    
    def add_log(self, message):
        """Add message to log area"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
    
    def update_system_stats(self):
        """Update system monitor stats"""
        try:
            # Update CPU
            cpu_percent = psutil.cpu_percent()
            self.cpu_bar.setValue(int(cpu_percent))
            self.cpu_bar.setFormat(f"CPU: {cpu_percent}%")
            
            # Update Memory
            memory = psutil.virtual_memory()
            self.memory_bar.setValue(int(memory.percent))
            self.memory_bar.setFormat(f"Memory: {memory.percent}%")
            
            # Update process list
            self.process_list.clear()
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except:
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
            
            for proc in processes[:30]:  # Show top 30
                if proc['name']:
                    item = QTreeWidgetItem([
                        proc['name'][:50],
                        str(proc['pid']),
                        f"{proc.get('cpu_percent', 0):.1f}",
                        f"{proc.get('memory_percent', 0):.1f}"
                    ])
                    self.process_list.addTopLevelItem(item)
                    
        except Exception as e:
            pass
    
    def update_status(self):
        """Update status bar"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            self.status_bar.showMessage(f"CPU: {cpu}% | Memory: {memory}% | Processes: {len(list(psutil.process_iter()))}")
        except:
            pass
    
    def on_process_started(self, process_info):
        """Handle new process detection"""
        self.add_log(f"🔄 New process: {process_info['name']} (PID: {process_info['pid']})")
    
    def show_alert(self, title, message):
        """Show alert dialog"""
        QMessageBox.warning(self, title, message)


# ==================== MAIN ====================
def main():
    app = QApplication(sys.argv)
    
    # Set app style
    app.setStyle('Fusion')
    
    window = AntivirusMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()