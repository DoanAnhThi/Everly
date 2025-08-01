import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
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

class QueryDisplayDialog(QDialog):
    """Dialog to show user's query."""
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Query")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 45)
        
        # Position dialog centered below the input window
        if parent:
            parent_pos = parent.pos()
            parent_size = parent.size()
            dialog_size = self.size()
            
            # Calculate center alignment
            center_x = parent_pos.x() + (parent_size.width() - dialog_size.width()) // 2
            # Position dialog below input window with small gap
            center_y = parent_pos.y() + parent_size.height() + 10
            
            self.move(center_x, center_y)
        
        self.init_ui(query)
    
    def init_ui(self, query):
        """Initialize the query display dialog UI."""
        # Create central widget with transparent background
        central_widget = TransparentWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(central_widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Create layout for content
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create query display with icon
        query_layout = QHBoxLayout()
        
        # Icon (user symbol)
        icon_label = QLabel("👤")  # User emoji
        icon_label.setFont(QFont("SF Pro Display", 16))
        icon_label.setStyleSheet("color: white; margin-right: 10px;")
        query_layout.addWidget(icon_label)
        
        # Query text with ellipsis
        query_text = QLabel(query)
        query_text.setFont(QFont("SF Pro Display", 12))
        query_text.setStyleSheet("color: white;")
        query_text.setWordWrap(False)
        query_text.setTextFormat(Qt.PlainText)
        
        # Truncate text if too long
        if len(query) > 50:
            query = query[:47] + "..."
        query_text.setText(query)
        
        query_layout.addWidget(query_text)
        query_layout.addStretch()
        layout.addLayout(query_layout)
        
        # Add spacing to center vertically
        layout.addStretch()

class ThinkingDialog(QDialog):
    """Dialog to show thinking spinner."""
    def __init__(self, parent=None, query=None):
        super().__init__(parent)
        self.setWindowTitle("Thinking...")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 45)  # Further reduced height for better centering
        
        # Position dialog centered below the input window
        if parent:
            parent_pos = parent.pos()
            parent_size = parent.size()
            dialog_size = self.size()
            
            # Calculate center alignment
            center_x = parent_pos.x() + (parent_size.width() - dialog_size.width()) // 2
            # Position dialog below input window with small gap
            center_y = parent_pos.y() + parent_size.height() + 10
            
            self.move(center_x, center_y)
        
        self.init_ui(query)
        self.start_animation()
    
    def init_ui(self, query=None):
        """Initialize the thinking dialog UI."""
        # Create central widget with transparent background
        central_widget = TransparentWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(central_widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Create layout for content
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create title row with fixed left and right sections
        title_layout = QHBoxLayout()
        
        # Left section: Icon, title, and dots
        left_section = QHBoxLayout()
        
        # Icon (paper airplane or thinking symbol)
        icon_label = QLabel("✈️")  # Paper airplane emoji
        icon_label.setFont(QFont("SF Pro Display", 20))
        icon_label.setStyleSheet("color: white; margin-right: 10px;")
        left_section.addWidget(icon_label)
        
        # Title
        title = QLabel("Thinking")
        title.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        left_section.addWidget(title)
        
        # Dots label
        self.dots_label = QLabel("")
        self.dots_label.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        self.dots_label.setStyleSheet("color: white;")
        left_section.addWidget(self.dots_label)
        
        # Add left section to main layout
        title_layout.addLayout(left_section)
        
        # Add stretch to separate left and right sections
        title_layout.addStretch()
        
        # Right section: Query container (if available)
        if query:
            # Create query container with border
            query_container = QWidget()
            query_container.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 8px;
                    padding: 4px 8px;
                }
            """)
            query_inner_layout = QHBoxLayout(query_container)
            query_inner_layout.setContentsMargins(4, 4, 4, 4)
            
            # Query text with ellipsis
            query_text = QLabel(query)
            query_text.setFont(QFont("SF Pro Display", 11))
            query_text.setStyleSheet("color: white;")
            query_text.setWordWrap(False)
            query_text.setTextFormat(Qt.PlainText)
            
            # Truncate text if too long (max width ~200px)
            if len(query) > 25:
                query = query[:22] + "..."
            query_text.setText(query)
            
            query_inner_layout.addWidget(query_text)
            title_layout.addWidget(query_container)
        layout.addLayout(title_layout)
        
        # Add spacing to match ResultDialog positioning
        layout.addStretch()
    
    def start_animation(self):
        """Start the dots animation."""
        self.dots_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)  # Update every 500ms
    
    def update_dots(self):
        """Update the dots animation."""
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.dots_label.setText(dots)
    
    def stop_animation(self):
        """Stop the dots animation."""
        if hasattr(self, 'timer'):
            self.timer.stop()

class ResultDialog(QDialog):
    """Dialog to show AI analysis results."""
    def __init__(self, result, parent=None, query=None):
        super().__init__(parent)
        self.setWindowTitle("AI Analysis Result")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 300)
        
        # Position dialog centered below the input window
        if parent:
            parent_pos = parent.pos()
            parent_size = parent.size()
            dialog_size = self.size()
            
            # Calculate center alignment
            center_x = parent_pos.x() + (parent_size.width() - dialog_size.width()) // 2
            # Position dialog below input window with small gap
            center_y = parent_pos.y() + parent_size.height() + 10
            
            self.move(center_x, center_y)
        
        self.init_ui(result, query)
    
    def init_ui(self, result, query=None):
        """Initialize the result dialog UI."""
        # Create central widget with transparent background
        central_widget = TransparentWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(central_widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Create layout for content
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create title row with fixed left and right sections
        title_layout = QHBoxLayout()
        
        # Left section: Icon and title
        left_section = QHBoxLayout()
        
        # Icon (AI brain symbol)
        icon_label = QLabel("🧠")  # Brain emoji for AI
        icon_label.setFont(QFont("SF Pro Display", 20))
        icon_label.setStyleSheet("color: white; margin-right: 10px;")
        left_section.addWidget(icon_label)
        
        # Title
        title = QLabel("AI Analysis Result")
        title.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        left_section.addWidget(title)
        
        # Add left section to main layout
        title_layout.addLayout(left_section)
        
        # Add stretch to separate left and right sections
        title_layout.addStretch()
        
        # Right section: Query container (if available)
        if query:
            # Create query container with border
            query_container = QWidget()
            query_container.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 8px;
                    padding: 4px 8px;
                }
            """)
            query_inner_layout = QHBoxLayout(query_container)
            query_inner_layout.setContentsMargins(4, 4, 4, 4)
            
            # Query text with ellipsis
            query_text = QLabel(query)
            query_text.setStyleSheet("color: white;")
            query_text.setFont(QFont("SF Pro Display", 11))
            query_text.setWordWrap(False)
            query_text.setTextFormat(Qt.PlainText)
            
            # Truncate text if too long (max width ~200px)
            if len(query) > 25:
                query = query[:22] + "..."
            query_text.setText(query)
            
            query_inner_layout.addWidget(query_text)
            title_layout.addWidget(query_container)
        layout.addLayout(title_layout)
        
        # Add spacing
        layout.addStretch()
        
        # Create text area for result with top-left alignment
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
                text-align: left;
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
        """Handle mouse press for window dragging - disabled for result dialog."""
        # Disable dragging for result dialog - it only moves with parent
        pass
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging - disabled for result dialog."""
        # Disable dragging for result dialog - it only moves with parent
        pass
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - disabled for result dialog."""
        # Disable dragging for result dialog - it only moves with parent
        pass
    
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
        self.thinking_dialog = None
        self.query_dialog = None
        self.current_query = None
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
        self.move(100, 50) # Điều chỉnh chiều cao
        
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
        """Handle mouse move for window dragging - only horizontal movement."""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            # Only allow horizontal movement (x-axis), keep y position fixed
            new_x = self.pos().x() + delta.x()
            new_y = self.pos().y()  # Keep y position unchanged
            self.move(new_x, new_y)
            self.old_pos = event.globalPos()
            
            # Move result dialog along with the input window
            if self.result_dialog and self.result_dialog.isVisible():
                dialog_size = self.result_dialog.size()
                # Keep dialog centered below input window
                center_x = new_x + (self.size().width() - dialog_size.width()) // 2
                center_y = new_y + self.size().height() + 10
                self.result_dialog.move(center_x, center_y)
            

            

            
            # Move thinking dialog along with the input window
            if self.thinking_dialog and self.thinking_dialog.isVisible():
                dialog_size = self.thinking_dialog.size()
                # Keep dialog centered below input window
                center_x = new_x + (self.size().width() - dialog_size.width()) // 2
                center_y = new_y + self.size().height() + 10
                self.thinking_dialog.move(center_x, center_y)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.old_pos = None
    
    def process_question(self):
        """Process the user's question."""
        question = self.input_field.text().strip()
        if not question:
            return
        
        # Store current query
        self.current_query = question
        
        # Clear input field
        self.input_field.clear()
        
        # Show thinking dialog
        self.show_thinking_dialog()
        
        # Start analysis in separate thread
        self.analysis_thread = AnalysisThread(self.agent, question)
        self.analysis_thread.finished.connect(self.show_result)
        self.analysis_thread.error.connect(self.show_error)
        self.analysis_thread.start()
    

    
    def show_thinking_dialog(self):
        """Show the thinking dialog."""
        # Close existing dialogs if any
        if self.result_dialog:
            self.result_dialog.close()
        if self.thinking_dialog:
            self.thinking_dialog.close()
        
        # Create and show thinking dialog
        self.thinking_dialog = ThinkingDialog(self, self.current_query)
        self.thinking_dialog.show()
        
        # Position thinking dialog correctly from the start
        if self.thinking_dialog and self.thinking_dialog.isVisible():
            dialog_size = self.thinking_dialog.size()
            # Keep dialog centered below input window with proper spacing
            center_x = self.pos().x() + (self.size().width() - dialog_size.width()) // 2
            center_y = self.pos().y() + self.size().height() + 10
            self.thinking_dialog.move(center_x, center_y)
        
        # Set focus back to input field
        self.input_field.setFocus()
    
    def show_result(self, result):
        """Show the analysis result in a separate dialog."""
        # Close thinking dialog if any
        if self.thinking_dialog:
            self.thinking_dialog.stop_animation()
            self.thinking_dialog.close()
        
        # Close existing result dialog if any
        if self.result_dialog:
            self.result_dialog.close()
        
        # Create and show result dialog with query
        self.result_dialog = ResultDialog(result, self, self.current_query)
        self.result_dialog.show()
        
        # Position result dialog correctly from the start
        if self.result_dialog and self.result_dialog.isVisible():
            dialog_size = self.result_dialog.size()
            # Keep dialog centered below input window with proper spacing
            center_x = self.pos().x() + (self.size().width() - dialog_size.width()) // 2
            center_y = self.pos().y() + self.size().height() + 10
            self.result_dialog.move(center_x, center_y)
        
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