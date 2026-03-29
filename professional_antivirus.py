# professional_antivirus.py
import sys
import os
import json
import datetime
import threading
import queue
from pathlib import Path
from typing import List, Dict, Optional

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTabWidget,
    QProgressBar, QStatusBar, QMessageBox, QHeaderView, QFrame,
    QTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem, QCheckBox
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QSize, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QFont, QIcon, QPalette, QColor, QLinearGradient,
    QBrush, QFontDatabase
)

# System monitoring libraries
import psutil
import hashlib
import platform
import subprocess
import re

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
        self.scan_paths = []
        self.threat_signatures = self.load_signatures()
        
    def load_signatures(self):
        """Load threat signatures"""
        return {
            "malicious_processes": [
                "mimikatz", "nc.exe", "netcat", "wce.exe", "pwdump",
                "fgdump", "hashdump", "keylog", "injector", "rootkit"
            ],
            "suspicious_paths": [
                r".*\\Temp\\.*\.exe$",
                r".*\\AppData\\Local\\Temp\\.*\.exe$",
                r".*\\Downloads\\.*\.exe$"
            ],
            "malicious_ports": [4444, 5555, 6666, 7777, 8888, 31337],
            "suspicious_registry": [
                r".*\\Run.*\\\\.*malware.*",
                r".*\\RunOnce.*\\\\.*exploit.*"
            ]
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
        
        # Scan temp files
        self.scan_temp_files()
        
        self.scan_complete.emit()
        self.log_message.emit("✅ Scan completed!")
        self.scanning = False
    
    def scan_processes(self):
        """Scan running processes"""
        self.log_message.emit("📊 Analyzing processes...")
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent']):
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
                        self.log_message.emit(f"⚠️ THREAT: {proc_name} (PID: {proc.info['pid']})")
                        
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
    
    def scan_temp_files(self):
        """Scan temporary directories"""
        self.log_message.emit("📁 Scanning temporary files...")
        
        temp_paths = []
        if platform.system() == 'Windows':
            temp_paths = [os.environ.get('TEMP', '')]
        else:
            temp_paths = ['/tmp', '/var/tmp']
        
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    for file in os.listdir(temp_path)[:100]:
                        if file.endswith('.exe'):
                            self.threat_found.emit({
                                "type": "Suspicious Executable",
                                "severity": "MEDIUM",
                                "location": temp_path,
                                "details": f"File: {file}",
                                "recommendation": "Review file in Temp directory"
                            })
                except PermissionError:
                    pass


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
            
            # Check for new processes
            new_processes = current_processes - self.known_processes
            for pid, name in new_processes:
                self.process_started.emit({"pid": pid, "name": name})
                
                # Quick threat check
                suspicious = ['mimikatz', 'nc.exe', 'netcat', 'wce']
                if any(s in name.lower() for s in suspicious):
                    self.alert.emit(name, f"Suspicious process detected: {name}")
            
            self.known_processes = current_processes
            self.msleep(3000)  # Check every 3 seconds


# ==================== MAIN WINDOW ====================
class AntivirusMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Advanced Antivirus Pro")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize engines
        self.scan_engine = ThreatDetectionEngine()
        self.real_time_monitor = RealTimeMonitor()
        
        # Connect signals
        self.connect_signals()
        
        # Setup UI
        self.setup_ui()
        self.apply_dark_theme()
        
        # Start status bar updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
    
    def connect_signals(self):
        """Connect all signal/slots"""
        self.scan_engine.threat_found.connect(self.add_threat)
        self.scan_engine.scan_progress.connect(self.update_progress)
        self.scan_engine.scan_complete.connect(self.scan_finished)
        self.scan_engine.log_message.connect(self.add_log)
        
        self.real_time_monitor.process_started.connect(self.on_process_started)
        self.real_time_monitor.alert.connect(self.show_alert)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header with gradient
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Control buttons
        control_bar = self.create_control_bar()
        main_layout.addLayout(control_bar)
        
        # Main content (tabbed interface)
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        # Dashboard tab
        self.dashboard = self.create_dashboard()
        tabs.addTab(self.dashboard, "📊 Dashboard")
        
        # Threats tab
        self.threats_table = self.create_threats_table()
        tabs.addTab(self.threats_table, "⚠️ Detected Threats")
        
        # System monitor tab
        self.system_monitor = self.create_system_monitor()
        tabs.addTab(self.system_monitor, "📈 System Monitor")
        
        # Log tab
        self.log_area = self.create_log_area()
        tabs.addTab(self.log_area, "📝 Scan Log")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "⚙️ Settings")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("System Protected | Real-time: OFF")
        self.status_bar.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_header(self):
        """Create gradient header"""
        header = QFrame()
        header.setFixedHeight(80)
        
        # Gradient background
        palette = header.palette()
        gradient = QLinearGradient(0, 0, 1000, 0)
        gradient.setColorAt(0, QColor(30, 30, 40))
        gradient.setColorAt(1, QColor(20, 20, 30))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        header.setPalette(palette)
        header.setAutoFillBackground(True)
        
        layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("🛡️ ADVANCED ANTIVIRUS PRO")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ff00;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Stats
        self.stats_label = QLabel("Threats Blocked: 0 | Scans: 0")
        self.stats_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.stats_label)
        
        return header
    
    def create_control_bar(self):
        """Create control buttons"""
        layout = QHBoxLayout()
        
        buttons = [
            ("🔍 Quick Scan", self.start_quick_scan, "#007acc"),
            ("⚡ Full Scan", self.start_full_scan, "#6a9955"),
            ("🛡️ Real-time Protection", self.toggle_realtime, "#dcdcaa"),
            ("📊 System Analysis", self.analyze_system, "#ce9178"),
            ("🗑️ Clear Threats", self.clear_threats, "#d16969"),
            ("📑 Export Report", self.export_report, "#e5c07b")
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
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(color)};
                    transform: scale(1.05);
                }}
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        return layout
    
    def create_dashboard(self):
        """Create dashboard with metrics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Metrics grid
        metrics_frame = QFrame()
        metrics_layout = QHBoxLayout(metrics_frame)
        
        # System health card
        self.health_card = self.create_metric_card(
            "System Health", 
            "🟢 Good", 
            "No active threats"
        )
        metrics_layout.addWidget(self.health_card)
        
        # Last scan card
        self.scan_card = self.create_metric_card(
            "Last Scan",
            "Not run yet",
            "Click Quick Scan to start"
        )
        metrics_layout.addWidget(self.scan_card)
        
        # Threats card
        self.threats_card = self.create_metric_card(
            "Total Threats",
            "0",
            "No threats detected"
        )
        metrics_layout.addWidget(self.threats_card)
        
        layout.addWidget(metrics_frame)
        
        # Recent threats
        recent_label = QLabel("📋 Recent Threats")
        recent_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(recent_label)
        
        self.recent_threats = QTableWidget()
        self.recent_threats.setColumnCount(4)
        self.recent_threats.setHorizontalHeaderLabels(["Time", "Type", "Severity", "Location"])
        self.recent_threats.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.recent_threats)
        
        return widget
    
    def create_metric_card(self, title, value, subtitle):
        """Create a metric card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #00ff00; font-size: 24px; font-weight: bold;")
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #666666; font-size: 10px;")
        layout.addWidget(subtitle_label)
        
        return card
    
    def create_threats_table(self):
        """Create threats table"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Severity", "Type", "Location", "Details", 
            "Recommendation", "Status"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        
        # Set column widths
        table.setColumnWidth(0, 100)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 250)
        table.setColumnWidth(3, 300)
        table.setColumnWidth(4, 250)
        
        self.threats_table = table
        return table
    
    def create_system_monitor(self):
        """Create system monitor with real-time graphs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # CPU usage
        cpu_frame = QFrame()
        cpu_layout = QVBoxLayout(cpu_frame)
        cpu_label = QLabel("CPU Usage")
        cpu_label.setFont(QFont("Arial", 12, QFont.Bold))
        cpu_layout.addWidget(cpu_label)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_bar)
        layout.addWidget(cpu_frame)
        
        # Memory usage
        memory_frame = QFrame()
        memory_layout = QVBoxLayout(memory_frame)
        memory_label = QLabel("Memory Usage")
        memory_label.setFont(QFont("Arial", 12, QFont.Bold))
        memory_layout.addWidget(memory_label)
        
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        memory_layout.addWidget(self.memory_bar)
        layout.addWidget(memory_frame)
        
        # Process list
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
    
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scan settings
        scan_group = QFrame()
        scan_layout = QVBoxLayout(scan_group)
        
        scan_title = QLabel("Scan Settings")
        scan_title.setFont(QFont("Arial", 14, QFont.Bold))
        scan_layout.addWidget(scan_title)
        
        # Checkboxes for scan options
        self.scan_processes_cb = QCheckBox("Scan running processes")
        self.scan_processes_cb.setChecked(True)
        scan_layout.addWidget(self.scan_processes_cb)
        
        self.scan_network_cb = QCheckBox("Scan network connections")
        self.scan_network_cb.setChecked(True)
        scan_layout.addWidget(self.scan_network_cb)
        
        self.scan_files_cb = QCheckBox("Scan temporary files")
        self.scan_files_cb.setChecked(True)
        scan_layout.addWidget(self.scan_files_cb)
        
        layout.addWidget(scan_group)
        
        # Protection settings
        protection_group = QFrame()
        protection_layout = QVBoxLayout(protection_group)
        
        protection_title = QLabel("Real-time Protection")
        protection_title.setFont(QFont("Arial", 14, QFont.Bold))
        protection_layout.addWidget(protection_title)
        
        self.auto_start_cb = QCheckBox("Start protection on system boot")
        protection_layout.addWidget(self.auto_start_cb)
        
        self.alert_notifications_cb = QCheckBox("Show alert notifications")
        self.alert_notifications_cb.setChecked(True)
        protection_layout.addWidget(self.alert_notifications_cb)
        
        layout.addWidget(protection_group)
        
        layout.addStretch()
        
        return widget
    
    def apply_dark_theme(self):
        """Apply dark theme to entire application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #252526;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #2d2d30;
                gridline-color: #3e3e42;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 5px;
                border: 1px solid #3e3e42;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
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
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #007acc;
                min-height: 20px;
            }
        """)
    
    def lighten_color(self, color):
        """Lighten a color for hover effect"""
        # Simple approximation
        return "#00aaff" if color == "#007acc" else "#88cc77"
    
    # ==================== SCAN METHODS ====================
    def start_quick_scan(self):
        """Start quick scan"""
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.add_log("🚀 Starting quick system scan...")
        self.scan_engine.start_quick_scan()
    
    def start_full_scan(self):
        """Start full system scan"""
        self.progress_bar.show()
        self.progress_bar.setRange(0, 100)
        self.add_log("⚡ Starting full system scan...")
        # Implement full scan logic
    
    def toggle_realtime(self):
        """Toggle real-time protection"""
        if self.real_time_monitor.monitoring:
            self.real_time_monitor.stop_monitoring()
            self.status_label.setText("System Protected | Real-time: OFF")
            self.add_log("🛡️ Real-time protection disabled")
        else:
            self.real_time_monitor.start_monitoring()
            self.status_label.setText("System Protected | Real-time: ACTIVE")
            self.add_log("🛡️ Real-time protection enabled")
    
    def analyze_system(self):
        """Perform system analysis"""
        self.add_log("📊 Running comprehensive system analysis...")
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        self.add_log(f"CPU Usage: {cpu_percent}%")
        self.add_log(f"Memory Usage: {memory.percent}%")
        self.add_log(f"Running Processes: {len(list(psutil.process_iter()))}")
    
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
        self.threats_table.setItem(row, 5, QTableWidgetItem("Pending"))
        
        # Update dashboard
        threat_count = self.threats_table.rowCount()
        self.threats_card.findChild(QLabel).setText(str(threat_count))
        
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
        self.add_log("🗑️ Cleared all threat records")
    
    def export_report(self):
        """Export scan report"""
        filename = f"antivirus_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system": {
                "os": platform.system(),
                "release": platform.release(),
                "processor": platform.processor()
            },
            "threats": []
        }
        
        # Collect threats
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
    
    def update_progress(self, value):
        """Update scan progress"""
        self.progress_bar.setValue(value)
    
    def scan_finished(self):
        """Handle scan completion"""
        self.progress_bar.hide()
        self.add_log("✅ Scan completed successfully!")
        self.scan_card.findChild(QLabel).setText(
            datetime.datetime.now().strftime("%H:%M:%S")
        )
    
    def add_log(self, message):
        """Add message to log area"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
    
    def update_system_stats(self):
        """Update system monitor stats"""
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
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])[:50]:
            try:
                item = QTreeWidgetItem([
                    proc.info['name'] or "Unknown",
                    str(proc.info['pid']),
                    f"{proc.info['cpu_percent']:.1f}",
                    f"{proc.info['memory_percent']:.1f}"
                ])
                self.process_list.addTopLevelItem(item)
            except:
                continue
    
    def update_status(self):
        """Update status bar"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        self.status_bar.showMessage(f"CPU: {cpu}% | Memory: {memory}%")
    
    def on_process_started(self, process_info):
        """Handle new process detection"""
        self.add_log(f"🔄 New process started: {process_info['name']} (PID: {process_info['pid']})")
    
    def show_alert(self, title, message):
        """Show alert dialog"""
        if self.alert_notifications_cb.isChecked():
            QMessageBox.warning(self, title, message)


# ==================== APPLICATION ENTRY POINT ====================
def main():
    app = QApplication(sys.argv)
    
    # Set application icon (optional)
    app.setApplicationName("Advanced Antivirus Pro")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = AntivirusMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()