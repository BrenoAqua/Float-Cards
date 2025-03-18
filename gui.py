from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSizePolicy, QDialog, QMenu, QApplication)
from PyQt6.QtCore import Qt, QSize, QUrl, pyqtSlot, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from aqt.webview import AnkiWebView
from aqt import mw
from aqt.sound import play_clicked_audio
from aqt.utils import tooltip
from anki.hooks import wrap
import os
import re
from PyQt6.QtWebChannel import QWebChannel

from .config import Config
from .logger import setup_logger

# Get logger
logger = setup_logger()

class FloatCardPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(None)  # Set parent to None for independent window
        self.setWindowTitle("Float Cards")
        # Update window flags for proper independent window
        self.setWindowFlags(
            Qt.WindowType.Window |  # Creates separate window
            Qt.WindowType.WindowMinMaxButtonsHint |  # Adds minimize/maximize buttons
            Qt.WindowType.WindowCloseButtonHint |  # Adds close button
            Qt.WindowType.WindowSystemMenuHint  # Adds system menu
        )
        
        # Re-add stay on top if configured (after setting other flags)
        self.config = Config.get_config()
        self.setup_ui()
        self.apply_theme()
        if self.config['stay_on_top']:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # Enable key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Don't show automatically
        self.answer_shown = False

    def validate_window_position(self):
        """Ensure the window is visible on screen."""
        try:
            # Get screen geometry
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            # Ensure minimum size
            min_width = 200
            min_height = 150
            self.setMinimumSize(min_width, min_height)
            
            # Validate window size
            if self.width() < min_width:
                self.resize(min_width, self.height())
            if self.height() < min_height:
                self.resize(self.width(), min_height)
            
            # Validate position
            if self.x() < screen_geometry.left():
                self.move(screen_geometry.left(), self.y())
            if self.y() < screen_geometry.top():
                self.move(self.x(), screen_geometry.top())
            
            # Ensure window is not off screen
            if self.x() + self.width() > screen_geometry.right():
                self.move(screen_geometry.right() - self.width(), self.y())
            if self.y() + self.height() > screen_geometry.bottom():
                self.move(self.x(), screen_geometry.bottom() - self.height())
                
            logger.debug(f"Window position validated: x={self.x()}, y={self.y()}, width={self.width()}, height={self.height()}")
        except Exception as e:
            logger.error(f"Error validating window position: {str(e)}", exc_info=True)

    def setup_ui(self):
        """Set up the user interface."""
        # Apply the configuration settings
        self.setGeometry(
            self.config['position_x'], 
            self.config['position_y'],
            self.config['window_width'],
            self.config['window_height']
        )
        
        # Set minimum size
        self.setMinimumSize(450, 620)
        
        # Validate window position
        self.validate_window_position()
        
        # Main layout with minimal spacing
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Web view for card content
        self.web_view = QWebEngineView()
        
        # Set up web view settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        
        # Create a channel between JavaScript and Python
        self.channel = QWebChannel()
        self.web_view.page().setWebChannel(self.channel)
        self.channel.registerObject("miniCard", self)
        
        # Set up page
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Add context menu for inspect element
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Apply modern scrollbar style to QWebEngineView
        self.web_view.setStyleSheet("""
            QWebEngineView {
                background: transparent;
                border: none;
            }
            QWebEngineView QScrollBar:vertical {
                width: 0;
                background: transparent;
                margin: 0;
                border: none;
            }
            QWebEngineView QScrollBar::handle:vertical {
                background: transparent;
            }
            QWebEngineView QScrollBar::add-line:vertical,
            QWebEngineView QScrollBar::sub-line:vertical,
            QWebEngineView QScrollBar::add-page:vertical,
            QWebEngineView QScrollBar::sub-page:vertical {
                height: 0;
                width: 0;
                background: transparent;
                border: none;
            }
        """)
        
        self.layout.addWidget(self.web_view, stretch=1)

        # Container widget for buttons
        button_container = QWidget()
        button_container.setFixedHeight(32)
        button_container_layout = QVBoxLayout(button_container)
        button_container_layout.setSpacing(0)
        button_container_layout.setContentsMargins(2, 0, 2, 2)

        # Button layouts
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(2)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setup_show_answer_button()
        
        # Answer buttons
        self.answer_buttons_layout = QHBoxLayout()
        self.answer_buttons_layout.setSpacing(2)
        self.answer_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_answer_buttons()
        
        # Add button layouts to container
        button_container_layout.addLayout(self.button_layout)
        button_container_layout.addWidget(self.answer_buttons_widget)
        
        # Add button container to main layout
        self.layout.addWidget(button_container)
        
        self.answer_shown = False

    def setup_answer_buttons(self):
        """Set up the answer buttons with styling from config."""
        self.answer_buttons = []
        button_data = [
            ("Again", 1, "again"),
            ("Hard", 2, "hard"),
            ("Good", 3, "good"),
            ("Easy", 4, "easy")
        ]

        # Clear existing buttons if any
        while self.answer_buttons_layout.count():
            item = self.answer_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get button styles from config
        button_styles = self.config['buttons'].get('styles', {})
        height = button_styles.get('height', 30)
        min_width = button_styles.get('min_width', 50)
        border_radius = button_styles.get('border_radius', 3)
        font_weight = button_styles.get('font_weight', 'normal')
        colors = button_styles.get('colors', {})

        for label, ease, color_key in button_data:
            # Check if this button should be shown
            config_key = f"show_{label.lower()}"
            if not self.config['buttons'].get(config_key, True):
                continue

            # Get colors for this button type
            button_colors = colors.get(color_key, {})
            bg_color = button_colors.get('background', '#2F2F31')
            bg_hover = button_colors.get('background hover', '#d0d0d0')
            text_color = button_colors.get('text', '#FFFFFF')
            text_hover = button_colors.get('text hover', '#000000')
            border_color = button_colors.get('border', '#666666')

            btn = QPushButton(label)
            btn.clicked.connect(lambda _, e=ease: self.grade_card(e))
            btn.setFixedHeight(height)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    padding: 0;
                    border-radius: {border_radius}px;
                    min-width: {min_width}px;
                    font-weight: {font_weight};
                    transition: all 0.2s;
                }}
                QPushButton:hover {{
                    background-color: {bg_hover};
                    color: {text_hover};
                    border: 1px solid {border_color};
                }}
            """)
            self.answer_buttons_layout.addWidget(btn)
            self.answer_buttons.append(btn)

        self.answer_buttons_widget = QWidget()
        self.answer_buttons_widget.setLayout(self.answer_buttons_layout)
        self.answer_buttons_widget.hide()

    def setup_show_answer_button(self):
        """Set up the Show Answer button with styling from config."""
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(2)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        # Get button styles from config
        button_styles = self.config['buttons'].get('styles', {})
        height = button_styles.get('height', 30)
        min_width = button_styles.get('min_width', 50)
        border_radius = button_styles.get('border_radius', 3)
        font_weight = button_styles.get('font_weight', 'normal')
        colors = button_styles.get('colors', {})

        # Get show answer button colors
        show_answer_colors = colors.get('show_answer', {})
        bg_color = show_answer_colors.get('background', '#2F2F31')
        bg_hover = show_answer_colors.get('background hover', '#F0F0F0')
        text_color = show_answer_colors.get('text', '#F0F0F0')
        text_hover = show_answer_colors.get('text hover', '#2F2F31')
        border_color = show_answer_colors.get('border', '#F0F0F0')

        self.show_answer_button = QPushButton("Show Answer")
        self.show_answer_button.clicked.connect(self.show_answer)
        self.show_answer_button.setFixedHeight(height)
        self.show_answer_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 0;
                border-radius: {border_radius}px;
                min-width: {min_width}px;
                font-weight: {font_weight};
                transition: all 0.2s;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
                color: {text_hover};
                border: 1px solid {border_color};
            }}
        """)
        self.button_layout.addWidget(self.show_answer_button)

    def show_context_menu(self, pos):
        """Show context menu with inspect element option."""
        menu = QMenu(self)
        
        # Add reload action
        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.web_view.reload)
        menu.addAction(reload_action)
        
        if len(menu.actions()) > 0:
            menu.exec(self.web_view.mapToGlobal(pos))

    def _generate_card_html(self, content, night_mode, platform_class, theme):
        """Generate the HTML template for card content."""
        # Get background settings
        background_config = self.config.get('background', {})
        background_enabled = background_config.get('enabled', False)
        background_image = background_config.get('image_path', '')
        background_opacity = background_config.get('opacity', 100)
        
        # Create background style if enabled
        background_style = ""
        background_before_style = ""
        if background_enabled and background_image:
            # Convert path to proper URL format with forward slashes
            image_path = background_image.replace('\\', '/')
            image_url = f"file:///{image_path}"
            
            # Base background style (without opacity)
            background_style = f"""
                background-image: url("{image_url}") !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
                background-size: cover !important;
            """
            
            # Before element style (with opacity)
            background_before_style = f"""
                content: "" !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                {background_style}
                opacity: {background_opacity / 100} !important;
                z-index: -1 !important;
                pointer-events: none !important;
            """

        # Convert [anki:play:*] links to proper audio buttons with onclick handlers
        def replace_audio_tag(match):
            tag = match.group(0)  # Original tag like [anki:play:q:0] or [anki:play:a:0]
            # Extract the side (q/a) and index from the tag
            side = tag[11]  # 'q' or 'a'
            index = tag[13:-1]  # The number
            # Create a button that uses the card's styling with SVG
            return f'''<span class="replay-button" onclick="miniCard.replay_sound_index({index})">
                <svg class="playImage" viewBox="0 0 32 32">
                    <path d="M 8,6 V 26 L 24,16 Z" />
                </svg>
            </span>'''
            
        content = re.sub(r'\[anki:play:[aq]:\d+\]', replace_audio_tag, content)

        return f"""
            <!doctype html>
            <html class="{'nightMode' if night_mode else ''}" style="height: 100%; margin: 0;">
            <head>
                <style>
                /* Theme colors */
                :root {{
                    --bg-color: {theme["background"]};
                    --text-color: {theme["text"]};
                }}
                
                html {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: overlay;
                }}

                /* Hide default scrollbars */
                ::-webkit-scrollbar {{
                    width: 8px;
                }}

                ::-webkit-scrollbar-track {{
                    background: transparent;
                }}

                ::-webkit-scrollbar-thumb {{
                    background-color: rgba(128, 128, 128, 0);
                    border-radius: 4px;
                    transition: background-color 0.2s ease;
                }}

                ::-webkit-scrollbar:hover {{
                    background-color: transparent;
                }}

                ::-webkit-scrollbar:hover ::-webkit-scrollbar-thumb,
                ::-webkit-scrollbar-thumb:hover {{
                    background-color: rgba(128, 128, 128, 0.1);
                }}

                ::-webkit-scrollbar-thumb:hover {{
                    background-color: rgba(128, 128, 128, 0.1);
                }}

                /* Base theme */
                body {{
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    position: relative;
                    z-index: 0;
                    min-height: 100%;
                }}

                body::before {{
                    {background_before_style}
                }}
                
                /* Card container */
                #qa {{
                    width: 100%;
                    min-height: 100%;
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                    text-align: center;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    align-items: center;
                    position: relative;
                    z-index: 1;
                }}
                
                /* Make sure all content is visible */
                #qa > * {{
                    max-width: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    flex: 0 0 auto;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }}
                
                /* Ensure images don't overflow */
                #qa img {{
                    max-width: 100%;
                    height: auto;
                    margin: 0;
                    padding: 0;
                }}
                
                /* Remove any margins from paragraphs and other elements */
                #qa p, #qa div, #qa span {{
                    margin: 0;
                    padding: 0;
                }}
                
                /* Audio button style - using SVG with fill */
                .replay-button {{
                    display: inline-flex;
                    align-items: center;
                    cursor: pointer;
                    padding: 0;
                    margin: 0;
                    opacity: 0.8;
                    transition: opacity 0.2s;
                }}
                
                .replay-button:hover {{
                    opacity: 1;
                }}
                
                .playImage {{
                    display: inline-block;
                    width: 40px;
                    height: 40px;
                    vertical-align: middle;
                }}
                
                .playImage path {{
                    fill: rgba(105, 105, 105, 0.3) !important;
                }}
                
                /* Modern Scrollbar - appears on hover, overlays content */
                ::-webkit-scrollbar-button,
                ::-webkit-scrollbar-track-piece,
                ::-webkit-scrollbar-corner,
                ::-webkit-resizer {{
                    display: none;
                }}
                
                /* Allow text selection only in specific elements */
                .selectable {{
                    user-select: text;
                    -webkit-user-select: text;
                }}
                
                /* Card CSS */
                {mw.reviewer.card.css() if mw.reviewer and mw.reviewer.card else ''}
                </style>
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <script>
                let miniCard;
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    miniCard = channel.objects.miniCard;
                }});
                
                function _runHook(hook) {{ return; }}
                function _updateQA(q, a, bodyclass) {{
                    document.body.className = bodyclass;
                }}
                
                document.addEventListener('DOMContentLoaded', function() {{
                    // Make card content selectable
                    var qaDiv = document.querySelector('#qa');
                    if (qaDiv) {{
                        qaDiv.classList.add('selectable');
                    }}
                }});
                </script>
            </head>
            <body class="card {platform_class} {'nightMode' if night_mode else ''}">{content}</body>
            </html>
        """

    def update_card(self):
        """Update the mini-card window with HTML content."""
        try:
            card = mw.reviewer.card
            if not card:
                logger.debug("No card available to update")
                return

            night_mode = mw.pm.night_mode()
            reviewer = mw.reviewer
            if not reviewer:
                logger.debug("No reviewer available")
                return
            
            # Get the latest config
            self.config = Config.get_config()
            
            # Get card content directly from reviewer
            content = reviewer.card.q()
            
            # Get platform class
            platform_class = "win"  # Default to windows since we're on windows
            
            # Get theme colors
            theme = self.config["theme"]["dark" if night_mode else "light"]
            
            html = self._generate_card_html(content, night_mode, platform_class, theme)
            
            # Set up media path and base URL
            media_path = self.get_media_path()
            if media_path:
                media_path = media_path.replace('\\', '/')
                base_url = QUrl.fromLocalFile(media_path + '/')
                self.web_view.setHtml(html, base_url)
            else:
                self.web_view.setHtml(html)

            self.show_answer_button.show()
            self.answer_buttons_widget.hide()
            self.answer_shown = False
        except Exception as e:
            logger.error(f"Error updating card: {str(e)}", exc_info=True)
            tooltip(f"Error updating card. Check the log file for details.")

    def show_answer(self):
        """Show the answer and display grading buttons."""
        try:
            card = mw.reviewer.card
            if not card:
                logger.debug("No card available to show answer")
                return

            night_mode = mw.pm.night_mode()
            reviewer = mw.reviewer
            if not reviewer:
                logger.debug("No reviewer available")
                return
            
            # Get the latest config
            self.config = Config.get_config()
            
            # Get card content directly from reviewer
            content = reviewer.card.a()
            
            # Get platform class
            platform_class = "win"  # Default to windows since we're on windows
            
            # Get theme colors
            theme = self.config["theme"]["dark" if night_mode else "light"]
            
            html = self._generate_card_html(content, night_mode, platform_class, theme)
            
            # Set up media path and base URL
            media_path = self.get_media_path()
            if media_path:
                media_path = media_path.replace('\\', '/')
                base_url = QUrl.fromLocalFile(media_path + '/')
                self.web_view.setHtml(html, base_url)
            else:
                self.web_view.setHtml(html)

            self.answer_shown = True
            self.show_answer_button.hide()
            self.answer_buttons_widget.show()

            # Also show answer in main window to sync state
            if hasattr(mw.reviewer, '_showAnswer'):
                mw.reviewer._showAnswer()
        except Exception as e:
            logger.error(f"Error showing answer: {str(e)}", exc_info=True)
            tooltip(f"Error showing answer. Check the log file for details.")

    def grade_card(self, ease):
        """Grade the card with the specified ease value."""
        try:
            if mw.reviewer and mw.reviewer.card and self.answer_shown:
                # Make sure answer is shown in main window
                if not mw.reviewer.state == 'answer':
                    mw.reviewer._showAnswer()
                # Use the reviewer's _answerCard method
                mw.reviewer._answerCard(ease)
                # Check if auto-close is enabled
                if self.config.get('scheduling', {}).get('auto_close_on_answer', False):
                    self.hide()
                # Don't update here - let the showQuestion hook handle it
                self.answer_shown = False
        except Exception as e:
            logger.error(f"Error grading card: {str(e)}", exc_info=True)
            tooltip(f"Error grading card. Check the log file for details.")

    def get_media_path(self):
        """Get the media folder path safely."""
        try:
            return mw.col.media.dir()
        except Exception as e:
            logger.error(f"Error getting media path: {str(e)}", exc_info=True)
            return ""

    def apply_theme(self):
        """Apply the current theme to the window."""
        try:
            theme = Config.get_theme()
            
            # Base style for the window
            style = f"""
                QDialog {{
                    background-color: {theme['background']};
                    color: {theme['text']};
                }}
            """
            
            # Apply the window style
            self.setStyleSheet(style)
            
            # Update card content to refresh the background
            if mw.reviewer and mw.reviewer.card:
                if self.answer_shown:
                    self.show_answer()
                else:
                    self.update_card()
                    
            logger.debug("Theme applied successfully")
        except Exception as e:
            logger.error(f"Error applying theme: {str(e)}", exc_info=True)
            tooltip(f"Error applying theme. Check the log file for details.")

    def resizeEvent(self, event):
        """Save window size when resized."""
        try:
            # Only save if the window is not minimized
            if not self.isMinimized():
                from .config import Config
                Config.update_config('window_width', self.width())
                Config.update_config('window_height', self.height())
                logger.debug(f"Window size saved: {self.width()}x{self.height()}")
        except Exception as e:
            logger.error(f"Error saving window size: {str(e)}", exc_info=True)
        super().resizeEvent(event)

    def closeEvent(self, event):
        """Save window position and size when closing."""
        try:
            # Only save if the window is not minimized
            if not self.isMinimized():
                from .config import Config
                Config.update_config('position_x', self.x())
                Config.update_config('position_y', self.y())
                Config.update_config('window_width', self.width())
                Config.update_config('window_height', self.height())
                logger.debug(f"Window state saved: pos=({self.x()}, {self.y()}), size={self.width()}x{self.height()}")
        except Exception as e:
            logger.error(f"Error saving window state: {str(e)}", exc_info=True)
        super().closeEvent(event)

    def toggle_scheduling(self):
        """Toggle the scheduling feature."""
        try:
            # Update local config
            if 'scheduling' not in self.config:
                self.config['scheduling'] = {}
            
            # Toggle scheduling
            self.config['scheduling']['enabled'] = not self.config['scheduling'].get('enabled', False)
            
            # Save to file
            Config.save_config(self.config)
            
            # Update scheduler state
            from . import float_card_popup
            if hasattr(float_card_popup, 'scheduler'):
                logger.debug("Updating scheduler state")
                float_card_popup.scheduler.update_state(self.config)
            
            # Show feedback
            if self.config['scheduling']['enabled']:
                deck = self.config['scheduling'].get('deck', "Default")
                freq = self.config['scheduling'].get('frequency', 30)
                tooltip(f"Scheduling enabled: Will show cards from '{deck}' every {freq} minutes")
            else:
                tooltip("Scheduling disabled")
                
        except Exception as e:
            logger.error(f"Error toggling scheduling: {str(e)}", exc_info=True)
            tooltip("Error toggling scheduling")

    def toggle_auto_close(self):
        """Toggle the auto-close after answering feature."""
        try:
            # Update local config
            if 'scheduling' not in self.config:
                self.config['scheduling'] = {}
            
            # Toggle auto-close
            self.config['scheduling']['auto_close_on_answer'] = not self.config['scheduling'].get('auto_close_on_answer', False)
            
            # Save to file
            Config.save_config(self.config)
            
            # Show feedback
            if self.config['scheduling']['auto_close_on_answer']:
                tooltip("Auto-close after answering enabled")
            else:
                tooltip("Auto-close after answering disabled")
                
        except Exception as e:
            logger.error(f"Error toggling auto-close: {str(e)}", exc_info=True)
            tooltip("Error toggling auto-close")

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        try:
            # Get hotkey config
            hotkeys = self.config.get('hotkeys', {})
            logger.debug(f"Current hotkeys config: {hotkeys}")
            
            # Check for modifier keys
            ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
            alt_pressed = event.modifiers() & Qt.KeyboardModifier.AltModifier
            shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            
            # Log key press details
            key_text = event.text().lower()
            key = event.key()
            logger.debug(f"Key pressed: {key_text} (key={key}), modifiers: ctrl={ctrl_pressed}, alt={alt_pressed}, shift={shift_pressed}")
            
            # Handle Ctrl+T for stay on top
            if ctrl_pressed and key == Qt.Key.Key_T:
                logger.debug("Handling Ctrl+T for stay on top")
                self.toggle_stay_on_top()
                event.accept()
                return
            
            # Handle Ctrl+R for second audio
            if ctrl_pressed and key == Qt.Key.Key_R:
                logger.debug("Handling Ctrl+R for second audio")
                self.replay_sound(1)  # Play second audio
                event.accept()
                return
            
            # Handle Ctrl+Alt+S for scheduling
            if ctrl_pressed and alt_pressed and key == Qt.Key.Key_S:
                logger.debug("Handling Ctrl+Alt+S for scheduling")
                self.toggle_scheduling()
                event.accept()
                return
            
            # Handle Ctrl+Alt+A for auto-close
            if ctrl_pressed and alt_pressed and key == Qt.Key.Key_A:
                logger.debug("Handling Ctrl+Alt+A for auto-close")
                self.toggle_auto_close()
                event.accept()
                return
            
            # Handle special keys
            if key == Qt.Key.Key_Space:
                key_text = 'space'
            elif key == Qt.Key.Key_Return:
                key_text = 'return'
            elif key == Qt.Key.Key_Enter:
                key_text = 'enter'
            
            # Handle R key for first audio
            if key == Qt.Key.Key_R and not (ctrl_pressed or alt_pressed or shift_pressed):
                logger.debug("Handling R for first audio")
                self.replay_sound(0)  # Play first audio
                event.accept()
                return
            
            # Convert hotkeys to lowercase for comparison
            hotkeys = {k: v.lower() for k, v in hotkeys.items()}
            
            # Only process other hotkeys if no modifiers are pressed
            if not (ctrl_pressed or alt_pressed or shift_pressed):
                logger.debug(f"Processing hotkey: {key_text}")
                
                # Show answer
                if not self.answer_shown and key_text == hotkeys.get('show_answer', ''):
                    logger.debug("Handling show answer hotkey")
                    self.show_answer()
                    event.accept()
                    return
                
                # Grade card
                if self.answer_shown:
                    if key_text == hotkeys.get('again', ''):
                        logger.debug("Handling again hotkey")
                        self.grade_card(1)
                        event.accept()
                        return
                    elif key_text == hotkeys.get('hard', ''):
                        logger.debug("Handling hard hotkey")
                        self.grade_card(2)
                        event.accept()
                        return
                    elif key_text == hotkeys.get('good', ''):
                        logger.debug("Handling good hotkey")
                        self.grade_card(3)
                        event.accept()
                        return
                    elif key_text == hotkeys.get('easy', ''):
                        logger.debug("Handling easy hotkey")
                        self.grade_card(4)
                        event.accept()
                        return
            
            # Let other handlers process the event if we didn't handle it
            logger.debug("No hotkey match found, ignoring event")
            event.ignore()
            super().keyPressEvent(event)
        except Exception as e:
            logger.error(f"Error handling key press: {str(e)}", exc_info=True)
            event.ignore()
            super().keyPressEvent(event)

    def toggle_stay_on_top(self):
        """Toggle the stay on top state of the window."""
        try:
            # Toggle the stay on top state
            self.config['stay_on_top'] = not self.config['stay_on_top']
            
            # Update window flags
            flags = self.windowFlags()
            if self.config['stay_on_top']:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowType.WindowStaysOnTopHint
            
            # Save position and size
            pos = self.pos()
            size = self.size()
            
            # Apply new flags
            self.setWindowFlags(flags)
            
            # Restore position and size
            self.move(pos)
            self.resize(size)
            
            # Show window again (required after changing flags)
            self.show()
            
            # Save config
            Config.save_config(self.config)
            
            # Show feedback
            tooltip("Stay on top: " + ("enabled" if self.config['stay_on_top'] else "disabled"))
        except Exception as e:
            logger.error(f"Error toggling stay on top: {str(e)}", exc_info=True)

    @pyqtSlot()
    def replay_sound(self, index=0):
        """Replay the current card's audio."""
        try:
            if mw.reviewer and mw.reviewer.card:
                if self.answer_shown:
                    # Use Anki's native audio playback
                    play_clicked_audio(f"play:a:{index}", mw.reviewer.card)
                else:
                    # Play question audio
                    play_clicked_audio(f"play:q:{index}", mw.reviewer.card)
        except Exception as e:
            logger.error(f"Error replaying sound: {str(e)}", exc_info=True)

    @pyqtSlot(int)
    def replay_sound_index(self, index):
        """Replay a specific audio file."""
        self.replay_sound(index)

    def show(self):
        """Show the popup window and ensure it gets focus."""
        super().show()
        self.activateWindow()  # Activate the window
        self.raise_()  # Bring window to front
        
        # Use QTimer to ensure window is fully shown before setting focus
        QTimer.singleShot(100, lambda: self._set_focus())
        logger.debug("Mini card popup shown and focusing")

    def _set_focus(self):
        """Set focus to the window and web view."""
        self.setFocus()  # Set keyboard focus to window
        self.web_view.setFocus()  # Set focus to web view
        self.activateWindow()  # Ensure window is active
        self.raise_()  # Ensure window is on top
        logger.debug("Focus set to mini card popup")

    def show_popup(self):
        """Show the popup window with the current card."""
        try:
            if not self.isVisible():
                # Restore the last saved size and position
                self.setGeometry(
                    self.config['position_x'],
                    self.config['position_y'],
                    self.config['window_width'],
                    self.config['window_height']
                )
                
                # Validate window position
                self.validate_window_position()
                
                self.show()
                logger.info("Mini card popup window shown")
                
                # Update with current card if available
                if mw.reviewer and mw.reviewer.card:
                    logger.info("Updating card in popup window")
                    self.update_card()
                else:
                    logger.warning("No card available to show in popup")
        except Exception as e:
            logger.error(f"Error showing popup: {str(e)}", exc_info=True)
            tooltip(f"Error showing popup: {str(e)}")

    def show_message(self, message):
        """Show a message in the card area."""
        try:
            # Create a simple HTML message
            html = f"""
                <!doctype html>
                <html style="height: 100%; margin: 0;">
                <head>
                    <style>
                        body {{
                            height: 100%;
                            margin: 0;
                            padding: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            background-color: var(--bg-color);
                            color: var(--text-color);
                            font-size: 16px;
                            text-align: center;
                        }}
                        .message {{
                            padding: 20px;
                            max-width: 80%;
                        }}
                    </style>
                </head>
                <body>
                    <div class="message">{message}</div>
                </body>
                </html>
            """
            
            # Set the HTML content
            self.web_view.setHtml(html)
            
            # Hide answer buttons
            self.show_answer_button.hide()
            self.answer_buttons_widget.hide()
            self.answer_shown = False
            
        except Exception as e:
            logger.error(f"Error showing message: {str(e)}", exc_info=True)