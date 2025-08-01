import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLineEdit, QLabel, QTextEdit, QFrame, QScrollArea, QDialog)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QBrush
from agent import FloatingAppAgent

class AnalysisThread(QThread):
    """Thread for running screenshot analysis to prevent UI freezing."""
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, agent, question):
        super().__init__()
        self.agent = agent
        self.question = question
    
    def run(self):
        try:
            result = self.agent.analyze_screenshot_with_question(self.question)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class TransparentWidget(QWidget):
    """Custom widget with transparent background."""
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create semi-transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))  # Black with 180 alpha
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

class ResultDialog(QDialog):
    """Dialog to show AI analysis results."""
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Analysis Result")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 300)
        
        # Position dialog near the input window
        if parent:
            pos = parent.pos()
            self.move(pos.x() + 50, pos.y() + 100)
        
        self.init_ui(result)
    
    def init_ui(self, result):
        """Initialize the result dialog UI."""
        # Create central widget with transparent background
        central_widget = TransparentWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(central_widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Create layout for content
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create title
        title = QLabel("AI Analysis Result")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create text area for result
        result_text = QTextEdit()
        result_text.setPlainText(result)
        result_text.setReadOnly(True)
        result_text.setFont(QFont("SF Pro Display", 12))
        result_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 12px;
                line-height: 1.4;
                border-radius: 10px;
                padding: 10px;
            }
            QTextEdit QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 7px;
                width: 8px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 7px;
                min-height: 20px;
            }
        """)
        
        layout.addWidget(result_text)
        
        # Create close button
        close_btn = QLabel("Click anywhere to close")
        close_btn.setAlignment(Qt.AlignCenter)
        close_btn.setFont(QFont("SF Pro Display", 10))
        close_btn.setStyleSheet("color: rgba(255, 255, 255, 0.7); margin-top: 10px;")
        layout.addWidget(close_btn)
        
        # Make dialog draggable
        self.old_pos = None
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.old_pos = None
    
    def mouseDoubleClickEvent(self, event):
        """Close dialog on double click."""
        self.close()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

class FloatingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = FloatingAppAgent()
        self.analysis_thread = None
        self.result_dialog = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the floating window UI."""
        # Set window properties
        self.setWindowTitle("Floating AI Assistant")
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # Remove window frame
            Qt.WindowStaysOnTopHint |  # Always on top
            Qt.Tool  # Don't show in taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window size and position
        self.setFixedSize(500, 34)
        self.move(100, 100)
        
        # Create central widget with transparent background
        self.central_widget = TransparentWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)
        
        # Create input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.setFont(QFont("SF Pro Display", 14))
        self.input_field.setFixedHeight(34)  # hoặc 36, tùy font
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 15px;
                padding: 1px 1px;
                background-color: transparent;
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit:focus {
                background-color: transparent;
                outline: none;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.8);
            }
        """)
        self.input_field.returnPressed.connect(self.process_question)
        layout.addWidget(self.input_field)
        
        # Make window draggable
        self.old_pos = None
        
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.old_pos = None
    
    def process_question(self):
        """Process the user's question."""
        question = self.input_field.text().strip()
        if not question:
            return
        
        # Clear input field
        self.input_field.clear()
        
        # Start analysis in separate thread
        self.analysis_thread = AnalysisThread(self.agent, question)
        self.analysis_thread.finished.connect(self.show_result)
        self.analysis_thread.error.connect(self.show_error)
        self.analysis_thread.start()
    
    def show_result(self, result):
        """Show the analysis result in a separate dialog."""
        # Close existing result dialog if any
        if self.result_dialog:
            self.result_dialog.close()
        
        # Create and show result dialog
        self.result_dialog = ResultDialog(result, self)
        self.result_dialog.show()
        
        # Set focus back to input field
        self.input_field.setFocus()
    
    def show_error(self, error_msg):
        """Show error message in result widget."""
        self.show_result(f"Error: {error_msg}")
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event) 