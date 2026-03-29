# super_analyzer.py - Advanced Threat Analysis Engine
import psutil
import hashlib
import os
import re
import json
import subprocess
import platform
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class SuperAnalyzer:
    """Advanced threat analysis engine with multiple detection layers"""
    
    def __init__(self):
        self.threat_database = self.load_threat_intelligence()
        self.scan_results = []
        
    def load_threat_intelligence(self) -> Dict:
        """Load comprehensive threat intelligence database"""
        return {
            "apt_groups": {
                "Lazarus": ["ccleaner", "malicious_update"],
                "APT28": ["xagent", "sednit"],
            },
            "ransomware": {
                "WannaCry": ["wcry", ".wncry"],
                "Locky": ["locky", ".locky"],
                "Ryuk": ["ryuk"],
            },
            "cryptominers": ["xmrig", "cpuminer", "cgminer", "minerd", "stratum"],
            "malicious_processes": [
                "mimikatz", "nc.exe", "netcat", "wce.exe", "pwdump",
                "fgdump", "hashdump", "keylog", "injector", "rootkit",
                "xmrig", "miner", "cryptonight", "ransomware"
            ],
            "malicious_ports": [4444, 5555, 6666, 7777, 8888, 31337],
        }
    
    def deep_analyze_process(self, pid: int) -> Dict:
        """Perform deep analysis on a specific process"""
        analysis = {
            "pid": pid,
            "threat_score": 0,
            "threats": [],
            "behavior": [],
            "recommendations": [],
            "severity": "LOW"
        }
        
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name().lower() if proc.name() else ''
            
            # Check against threat database
            for category, threats in self.threat_database.items():
                if isinstance(threats, dict):
                    for threat_name, patterns in threats.items():
                        for pattern in patterns:
                            if pattern in proc_name:
                                analysis["threats"].append({
                                    "type": f"{category.upper()}: {threat_name}",
                                    "details": f"Process matches known threat pattern: {pattern}",
                                    "risk": "HIGH"
                                })
                                analysis["threat_score"] += 80
                elif isinstance(threats, list):
                    for threat in threats:
                        if threat in proc_name:
                            analysis["threats"].append({
                                "type": f"Malicious {category.upper()}",
                                "details": f"Process matches: {threat}",
                                "risk": "HIGH"
                            })
                            analysis["threat_score"] += 70
            
            # Check CPU usage
            cpu_percent = proc.cpu_percent(interval=0.1)
            if cpu_percent > 80:
                analysis["threats"].append({
                    "type": "High CPU Usage",
                    "details": f"CPU at {cpu_percent}% - Possible miner",
                    "risk": "MEDIUM"
                })
                analysis["threat_score"] += 40
            
            # Check memory usage
            memory_mb = proc.memory_info().rss / 1024 / 1024
            if memory_mb > 500:
                analysis["threats"].append({
                    "type": "High Memory Usage",
                    "details": f"Using {memory_mb:.2f} MB RAM",
                    "risk": "MEDIUM"
                })
                analysis["threat_score"] += 30
            
            # Check network connections
            connections = proc.connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    if conn.raddr.port in self.threat_database["malicious_ports"]:
                        analysis["threats"].append({
                            "type": "Suspicious Connection",
                            "details": f"Connected to port {conn.raddr.port}",
                            "risk": "HIGH"
                        })
                        analysis["threat_score"] += 60
            
            # Set severity
            if analysis["threat_score"] >= 150:
                analysis["severity"] = "CRITICAL"
                analysis["recommendations"].append("IMMEDIATE ACTION REQUIRED - Terminate process")
            elif analysis["threat_score"] >= 80:
                analysis["severity"] = "HIGH"
                analysis["recommendations"].append("Investigate this process immediately")
            elif analysis["threat_score"] >= 40:
                analysis["severity"] = "MEDIUM"
                analysis["recommendations"].append("Monitor this process for unusual behavior")
            else:
                analysis["severity"] = "LOW"
                analysis["recommendations"].append("No immediate action needed")
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def scan_all_processes(self) -> List[Dict]:
        """Scan all running processes and return threats"""
        threats = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                analysis = self.deep_analyze_process(proc.info['pid'])
                if analysis["threat_score"] > 30:
                    threats.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent'],
                        "analysis": analysis
                    })
            except:
                continue
        
        return threats
    
    def rootkit_detection(self) -> Dict:
        """Detect rootkits and hidden processes"""
        detection = {
            "rootkit_detected": False,
            "hidden_processes": [],
            "suspicious_drivers": []
        }
        
        if platform.system() == "Windows":
            try:
                # Get processes from tasklist
                result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                                      capture_output=True, text=True, timeout=10, shell=True)
                tasklist_processes = set()
                
                for line in result.stdout.split('\n')[1:]:
                    if line:
                        parts = line.split(',')
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1].strip('"'))
                                tasklist_processes.add(pid)
                            except:
                                pass
                
                # Get processes from psutil
                psutil_processes = set()
                for proc in psutil.process_iter(['pid']):
                    try:
                        psutil_processes.add(proc.info['pid'])
                    except:
                        pass
                
                # Check for hidden processes
                hidden = tasklist_processes - psutil_processes
                if hidden:
                    detection["rootkit_detected"] = True
                    detection["hidden_processes"] = list(hidden)[:10]
                    
            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                pass
        
        return detection
    
    def generate_ioc_report(self) -> Dict:
        """Generate Indicators of Compromise (IOC) report"""
        iocs = {
            "timestamp": datetime.now().isoformat(),
            "processes": [],
            "network": [],
            "summary": {}
        }
        
        # Collect suspicious processes
        suspicious_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                analysis = self.deep_analyze_process(proc.info['pid'])
                if analysis["threat_score"] > 40:
                    iocs["processes"].append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "threat_score": analysis["threat_score"],
                        "severity": analysis["severity"],
                        "threats": analysis["threats"][:3]
                    })
                    suspicious_count += 1
            except:
                continue
        
        # Collect suspicious network connections
        network_count = 0
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                if conn.raddr.port in self.threat_database["malicious_ports"]:
                    iocs["network"].append({
                        "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                        "pid": conn.pid
                    })
                    network_count += 1
        
        iocs["summary"] = {
            "suspicious_processes": suspicious_count,
            "suspicious_connections": network_count,
            "total_threat_score": sum(p.get("threat_score", 0) for p in iocs["processes"])
        }
        
        return iocs


# Singleton instance
_analyzer_instance = None

def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SuperAnalyzer()
    return _analyzer_instance