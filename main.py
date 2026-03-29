# main.py - Fixed Integrated Antivirus System
import sys
import threading
import psutil
import json
import os
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Import our modules
from professional_antivirus import AntivirusMainWindow
from super_analyzer import get_analyzer
from super_ui import RealTimeGraphWidget, ThreatHeatmapWidget, NetworkMapWidget, ModernButton

class EnhancedAntivirusWindow(AntivirusMainWindow):
    """Enhanced main window with super analyzer integration"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Advanced Antivirus Pro - Enterprise Edition")
        
        # Initialize super analyzer
        self.analyzer = get_analyzer()
        
        # Start background analysis thread
        self.analysis_running = True
        self.analysis_thread = threading.Thread(target=self.continuous_analysis, daemon=True)
        self.analysis_thread.start()
        
        # Add enhanced UI components
        self.add_enhanced_components()
        
        # Start periodic IOC collection
        self.ioc_timer = QTimer()
        self.ioc_timer.timeout.connect(self.collect_iocs)
        self.ioc_timer.start(30000)  # Every 30 seconds
        
        self.add_log("🛡️ Enhanced Antivirus Pro - Ready")
        self.add_log("📊 Super Analyzer Engine Active")
        
    def add_enhanced_components(self):
        """Add enhanced UI components to existing tabs"""
        
        # Find dashboard layout
        dashboard_layout = self.dashboard.layout()
        
        # Add threat heatmap to dashboard
        heatmap_label = QLabel("Threat Activity Heatmap")
        heatmap_label.setFont(QFont("Arial", 12, QFont.Bold))
        dashboard_layout.addWidget(heatmap_label)
        
        self.heatmap = ThreatHeatmapWidget()
        dashboard_layout.addWidget(self.heatmap)
        
        # Add real-time graph to system monitor
        graph_label = QLabel("CPU Usage History")
        graph_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.system_monitor.layout().addWidget(graph_label)
        
        self.cpu_graph = RealTimeGraphWidget("Real-time CPU Usage")
        self.system_monitor.layout().addWidget(self.cpu_graph)
        
        # Add network map to system monitor
        network_label = QLabel("Active Network Connections")
        network_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.system_monitor.layout().addWidget(network_label)
        
        self.network_map = NetworkMapWidget()
        self.system_monitor.layout().addWidget(self.network_map)
        
        # Add deep scan button to control bar
        self.deep_scan_btn = ModernButton("🔬 Deep Analysis Scan")
        self.deep_scan_btn.clicked.connect(self.start_deep_analysis)
        
        # Find control bar layout and add button
        control_layout = self.findChild(QHBoxLayout)
        if control_layout:
            control_layout.insertWidget(3, self.deep_scan_btn)
        
        # Add threat gauge to dashboard
        gauge_label = QLabel("Current Threat Level")
        gauge_label.setFont(QFont("Arial", 12, QFont.Bold))
        dashboard_layout.addWidget(gauge_label)
        
        self.threat_gauge = AnimatedGaugeWidget()
        dashboard_layout.addWidget(self.threat_gauge)
        
        from super_ui import AnimatedGaugeWidget
        
    def start_deep_analysis(self):
        """Start deep process analysis"""
        self.add_log("🔬 Starting deep behavioral analysis...")
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        
        def analyze():
            try:
                # Get all running processes
                processes = list(psutil.process_iter(['pid', 'name', 'exe']))
                total = len(processes)
                
                for i, proc in enumerate(processes[:50]):  # Limit for performance
                    try:
                        # Deep analyze each process
                        analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                        
                        if analysis["threat_score"] > 50:
                            self.add_threat({
                                "type": "Deep Analysis Finding",
                                "severity": analysis["severity"],
                                "location": f"PID: {proc.info['pid']}",
                                "details": f"{proc.info['name']} - Score: {analysis['threat_score']}",
                                "recommendation": analysis["recommendations"][0] if analysis["recommendations"] else "Review"
                            })
                            
                            for threat in analysis["threats"]:
                                self.add_log(f"  ⚠️ {threat['type']}: {threat['details']}")
                    
                    except Exception as e:
                        continue
                    
                    # Update progress
                    if i % 10 == 0:
                        self.progress_bar.setValue(int((i + 1) / total * 100))
                
                self.add_log("✅ Deep analysis completed")
                
            except Exception as e:
                self.add_log(f"❌ Deep analysis error: {e}")
            finally:
                self.progress_bar.hide()
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def continuous_analysis(self):
        """Continuous background analysis thread"""
        last_rootkit_check = 0
        
        while self.analysis_running:
            try:
                import time
                
                # Check for rootkits every 30 seconds
                current_time = time.time()
                if current_time - last_rootkit_check > 30:
                    rootkit_detection = self.analyzer.rootkit_detection()
                    if rootkit_detection["rootkit_detected"]:
                        self.add_log(f"🚨 ROOTKIT DETECTED! Hidden processes: {rootkit_detection['hidden_processes']}")
                        
                        # Add as critical threat
                        self.add_threat({
                            "type": "Rootkit Detection",
                            "severity": "CRITICAL",
                            "location": "System Kernel",
                            "details": f"Hidden processes detected: {rootkit_detection['hidden_processes']}",
                            "recommendation": "Run specialized rootkit removal tool"
                        })
                    last_rootkit_check = current_time
                
                # Analyze high-risk processes
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        if proc.info['cpu_percent'] and proc.info['cpu_percent'] > 80:
                            analysis = self.analyzer.deep_analyze_process(proc.info['pid'])
                            
                            if analysis["threat_score"] > 100:
                                self.add_log(f"🚨 HIGH RISK PROCESS: {proc.info['name']} (Score: {analysis['threat_score']})")
                                
                                self.add_threat({
                                    "type": "Active Threat",
                                    "severity": analysis["severity"],
                                    "location": f"PID: {proc.info['pid']}",
                                    "details": f"Process: {proc.info['name']} - CPU: {proc.info['cpu_percent']}%",
                                    "recommendation": "Immediate investigation required"
                                })
                    except:
                        continue
                
                # Update network map with suspicious connections
                suspicious_connections = []
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        suspicious_connections.append({
                            "port": conn.raddr.port,
                            "ip": conn.raddr.ip,
                            "suspicious": conn.raddr.port in [4444, 5555, 6666, 7777, 8888, 31337]
                        })
                
                # Update UI (use QTimer to avoid thread issues)
                QMetaObject.invokeMethod(self.network_map, "update_connections", 
                                        Qt.QueuedConnection, 
                                        Q_ARG(list, suspicious_connections[:20]))
                
                # Update threat heatmap
                threats = []
                for row in range(self.threats_table.rowCount()):
                    threats.append({
                        "severity": self.threats_table.item(row, 0).text(),
                        "details": self.threats_table.item(row, 3).text()
                    })
                QMetaObject.invokeMethod(self.heatmap, "update_threats", 
                                        Qt.QueuedConnection, 
                                        Q_ARG(list, threats))
                
                # Update threat gauge
                threat_score = min(100, len(threats) * 5)
                QMetaObject.invokeMethod(self.threat_gauge, "setValue", 
                                        Qt.QueuedConnection, 
                                        Q_ARG(int, threat_score))
                
                time.sleep(10)  # Wait 10 seconds
                
            except Exception as e:
                print(f"Analysis error: {e}")
                import time
                time.sleep(30)
    
    def collect_iocs(self):
        """Collect Indicators of Compromise"""
        try:
            iocs = self.analyzer.generate_ioc_report()
            
            if iocs["processes"] or iocs["network"]:
                self.add_log(f"📊 IOC Report: {len(iocs['processes'])} suspicious processes, {len(iocs['network'])} suspicious connections")
                
                # Save to file
                filename = f"ioc_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(iocs, f, indent=2)
                
                self.add_log(f"📁 IOC report saved to {filename}")
        except Exception as e:
            self.add_log(f"⚠️ IOC collection error: {e}")
    
    def closeEvent(self, event):
        """Handle application close"""
        self.analysis_running = False
        self.add_log("🛡️ Antivirus shutting down...")
        event.accept()


# Splash screen
class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(500, 300)
        pixmap.fill(QColor(30, 30, 40))
        
        super().__init__(pixmap)
        
        # Draw text on splash screen
        painter = QPainter(self.pixmap())
        painter.setPen(QColor(0, 255, 0))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "🛡️ Advanced Antivirus Pro\n\nLoading security modules...")
        painter.end()
        
        self.show()
        
        # Add progress bar
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 250, 400, 20)
        self.progress.setStyleSheet("""
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
        self.progress.show()


def main():
    app = QApplication(sys.argv)
    
    # Show splash screen
    splash = SplashScreen()
    
    # Simulate loading
    for i in range(100):
        splash.progress.setValue(i + 1)
        QApplication.processEvents()
        QTimer.singleShot(10, lambda: None)
    
    # Create and show main window
    window = EnhancedAntivirusWindow()
    window.show()
    
    splash.finish(window)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()