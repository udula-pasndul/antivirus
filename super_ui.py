# super_ui.py - Simplified UI Components (No external dependencies)
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import random

class AnimatedGaugeWidget(QWidget):
    """Animated threat level gauge"""
    
    valueChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.target_value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setMinimumHeight(150)
        
    def setValue(self, value):
        self.target_value = min(100, max(0, value))
        self.animation.setEndValue(self.target_value)
        self.animation.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw gauge background
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 20
        
        # Draw arc background
        painter.setPen(QPen(QColor(60, 60, 60), 15))
        painter.drawArc(center.x() - radius, center.y() - radius,
                       radius * 2, radius * 2, 0, 360 * 16)
        
        # Draw value arc
        angle = int((self.value / 100) * 360 * 16)
        painter.setPen(QPen(self.getColor(), 15))
        painter.drawArc(center.x() - radius, center.y() - radius,
                       radius * 2, radius * 2, 90 * 16, angle)
        
        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{self.value}%")
        
    def getColor(self):
        if self.value < 30:
            return QColor(0, 255, 0)
        elif self.value < 70:
            return QColor(255, 165, 0)
        else:
            return QColor(255, 0, 0)

class RealTimeGraphWidget(QWidget):
    """Real-time performance graph (Pure PySide6)"""
    
    def __init__(self, title="Performance", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = [0] * 50
        self.setMinimumHeight(150)
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)
        
    def update_data(self):
        # Get real CPU or generate random data
        import psutil
        self.data.pop(0)
        self.data.append(psutil.cpu_percent())
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(30, 30, 35))
        
        # Draw border
        painter.setPen(QPen(QColor(60, 60, 65), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        # Draw title
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 20, self.title)
        
        # Draw grid
        painter.setPen(QPen(QColor(60, 60, 65), 1))
        for i in range(0, self.height(), 30):
            painter.drawLine(0, i, self.width(), i)
        
        # Draw graph
        painter.setPen(QPen(QColor(0, 120, 215), 2))
        
        step = self.width() / len(self.data)
        points = []
        
        for i, value in enumerate(self.data):
            x = i * step
            y = self.height() - 30 - (value / 100) * (self.height() - 60)
            points.append(QPointF(x, y))
        
        # Draw line
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])
        
        # Draw fill under graph
        if len(points) > 1:
            path = QPainterPath()
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            path.lineTo(points[-1].x(), self.height() - 30)
            path.lineTo(points[0].x(), self.height() - 30)
            path.closeSubpath()
            
            painter.fillPath(path, QColor(0, 120, 215, 50))

class ThreatHeatmapWidget(QWidget):
    """Threat heatmap visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threats = []
        self.setMinimumHeight(200)
        
    def update_threats(self, threats):
        self.threats = threats
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw heatmap background
        painter.fillRect(self.rect(), QColor(20, 20, 25))
        
        # Draw title
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 20, "Threat Activity Heatmap")
        
        if not self.threats:
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawText(self.rect(), Qt.AlignCenter, "No threats detected")
            return
        
        # Draw threat blocks
        block_width = self.width() // 10
        block_height = (self.height() - 40) // 10
        
        for i, threat in enumerate(self.threats[:100]):
            row = i // 10
            col = i % 10
            
            x = col * block_width
            y = 30 + row * block_height
            
            # Color based on severity
            severity = threat.get("severity", "LOW")
            if severity == "CRITICAL":
                color = QColor(255, 0, 0, 200)
            elif severity == "HIGH":
                color = QColor(255, 100, 0, 180)
            elif severity == "MEDIUM":
                color = QColor(255, 200, 0, 150)
            else:
                color = QColor(0, 255, 0, 100)
            
            painter.fillRect(x, y, block_width - 2, block_height - 2, color)

class NetworkMapWidget(QWidget):
    """Network connection visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connections = []
        self.setMinimumHeight(250)
        
    def update_connections(self, connections):
        self.connections = connections
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(20, 20, 25))
        
        # Draw title
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 20, "Network Connection Map")
        
        # Draw center node (local machine)
        center = QPoint(self.width() // 2, self.height() // 2)
        painter.setBrush(QBrush(QColor(0, 120, 215)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawEllipse(center, 25, 25)
        
        painter.setFont(QFont("Arial", 9))
        painter.drawText(center, Qt.AlignCenter, "Local")
        
        # Draw connections
        if self.connections:
            angle_step = (2 * 3.14159) / min(len(self.connections), 20)
            radius = 100
            
            for i, conn in enumerate(self.connections[:20]):
                angle = i * angle_step
                x = center.x() + radius * (angle)
                y = center.y() + radius * (angle)
                
                # Keep within bounds
                x = min(max(50, x), self.width() - 50)
                y = min(max(50, y), self.height() - 50)
                
                # Draw remote node
                if conn.get("suspicious", False):
                    painter.setBrush(QBrush(QColor(255, 0, 0)))
                else:
                    painter.setBrush(QBrush(QColor(100, 100, 100)))
                
                painter.drawEllipse(int(x) - 12, int(y) - 12, 24, 24)
                
                # Draw connection line
                painter.setPen(QPen(QColor(100, 100, 150), 1))
                painter.drawLine(center, QPointF(x, y))
                
                # Draw port label
                painter.setFont(QFont("Arial", 8))
                painter.drawText(int(x) - 15, int(y) - 15, str(conn.get("port", "?")))

class ModernButton(QPushButton):
    """Modern animated button"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(35)
        self.setCursor(Qt.PointingHandCursor)
        
    def enterEvent(self, event):
        self.animate(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animate(False)
        super().leaveEvent(event)
        
    def animate(self, hover):
        # Simple animation using style sheet
        if hover:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #00aaff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #0088cc;
                }
            """)
        else:
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
                    background-color: #0088cc;
                }
            """)