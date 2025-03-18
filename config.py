"""Configuration management for Mini Card Popup addon."""

import json
import os
from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip
from typing import Any, Dict
import logging

from .config_schema import CONFIG_SCHEMA

logger = logging.getLogger(__name__)

class Config:
    """Handle addon configuration."""
    
    DEFAULT_CONFIG = {
        "window_width": 400,
        "window_height": 200,
        "button_height": 40,
        "shortcut": "Ctrl+Shift+M",
        "position_x": 100,
        "position_y": 100,
        "stay_on_top": True,
        "buttons": {
            "show_again": True,
            "show_hard": False,
            "show_good": True,
            "show_easy": False,
            "styles": {
                "height": 30,
                "min_width": 50,
                "border_radius": 3,
                "font_weight": "bold",
                "colors": {
                    "again": {
                        "background": "#2F2F31",
                        "background hover": "#FF1211",
                        "text": "#FF1211",
                        "text hover": "#2F2F31",
                        "border": "#FF1211"
                    },
                    "hard": {
                        "background": "#2F2F31",
                        "background hover": "#FF9814",
                        "text": "#FF9814",
                        "text hover": "#2F2F31",
                        "border": "#FF9814"
                    },
                    "good": {
                        "background": "#2F2F31",
                        "background hover": "#33FF2D",
                        "text": "#33FF2D",
                        "text hover": "#2F2F31",
                        "border": "#33FF2D"
                    },
                    "easy": {
                        "background": "#2F2F31",
                        "background hover": "#21C0FF",
                        "text": "#21C0FF",
                        "text hover": "#2F2F31",
                        "border": "#21C0FF"
                    },
                    "show_answer": {
                        "background": "#2F2F31",
                        "background hover": "#F0F0F0",
                        "text": "#F0F0F0",
                        "text hover": "#2F2F31",
                        "border": "#F0F0F0"
                    }
                }
            }
        },
        "hotkeys": {
            "show_answer": "Space",
            "again": "1",
            "hard": "2",
            "good": "3",
            "easy": "4",
            "toggle_stay_on_top": "Ctrl+T",
            "replay_sound": "R",
            "replay_second_sound": "Ctrl+R",
            "toggle_scheduling": "Ctrl+Alt+S",
            "toggle_auto_close": "Ctrl+Alt+A"
        },
        "theme": {
            "light": {
                "background": "#ffffff",
                "text": "#000000",
                "button_bg": "#e0e0e0",
                "button_text": "#000000",
                "button_border": "#cccccc"
            },
            "dark": {
                "background": "#2f2f31",
                "text": "#ffffff",
                "button_bg": "#444444",
                "button_text": "#ffffff",
                "button_border": "#666666"
            }
        },
        "scheduling": {
            "enabled": False,
            "frequency": 1,  # Default to 1 minute
            "deck": "Default",
            "auto_close_on_answer": False
        },
        "background": {
            "enabled": False,
            "image_path": "",
            "opacity": 100  # 0-100%
        }
    }

    @classmethod
    def get_config(cls):
        """Get the addon configuration, creating it if it doesn't exist."""
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(addon_dir, "config.json")
        
        if not os.path.exists(config_path):
            cls.save_config(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Deep update of config with any missing default values
            def update_dict_recursive(target, source):
                updated = False
                for key, value in source.items():
                    if key not in target:
                        target[key] = value
                        updated = True
                    elif isinstance(value, dict) and isinstance(target[key], dict):
                        if update_dict_recursive(target[key], value):
                            updated = True
                return updated
            
            # Update config with any missing values
            if update_dict_recursive(config, cls.DEFAULT_CONFIG):
                cls.save_config(config)
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return cls.DEFAULT_CONFIG

    @classmethod
    def save_config(cls, config):
        """Save the configuration to disk."""
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(addon_dir, "config.json")
        try:
            # Create a backup of the current config file if it exists
            if os.path.exists(config_path):
                backup_path = config_path + '.bak'
                try:
                    with open(config_path, 'r', encoding='utf-8') as src:
                        with open(backup_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                except Exception as e:
                    logger.warning(f"Failed to create config backup: {e}")

            # Write the new config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Verify the config was written correctly
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                if saved_config != config:
                    logger.error("Config verification failed - saved config does not match original")
                    raise Exception("Config verification failed")
            except Exception as e:
                logger.error(f"Error verifying saved config: {e}")
                # Restore from backup if verification fails
                if os.path.exists(backup_path):
                    os.replace(backup_path, config_path)
                raise

            # Remove backup if everything succeeded
            if os.path.exists(backup_path):
                os.remove(backup_path)

            # Also update Anki's addon manager config
            try:
                write_config(config)
            except Exception as e:
                logger.warning(f"Failed to update addon manager config: {e}")

            logger.info("Configuration saved successfully")
        except Exception as e:
            error_msg = f"Error saving config: {e}"
            logger.error(error_msg)
            tooltip(error_msg)
            raise

    @classmethod
    def update_config(cls, key, value):
        """Update a specific config value and save immediately."""
        try:
            # Get current config
            config = cls.get_config()
            
            # Update the value
            if '.' in key:
                # Handle nested keys (e.g., 'buttons.styles.height')
                keys = key.split('.')
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            else:
                config[key] = value
            
            # Save the updated config
            cls.save_config(config)
            logger.debug(f"Updated config: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}", exc_info=True)
            raise

    @classmethod
    def open_config_dialog(cls):
        """Open a dialog to edit the configuration."""
        config = cls.get_config()
        dialog = QDialog(mw)
        dialog.setWindowTitle("Float Cards Configuration")
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        
        # General Settings Tab (combining Window and Scheduling)
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        general_layout.setSpacing(15)
        
        # Window Settings Group
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout()
        window_layout.setSpacing(8)
        
        width_input = QSpinBox()
        width_input.setRange(100, 1000)
        width_input.setValue(config['window_width'])
        width_input.setSuffix(" px")
        window_layout.addRow("Width:", width_input)
        
        height_input = QSpinBox()
        height_input.setRange(100, 1000)
        height_input.setValue(config['window_height'])
        height_input.setSuffix(" px")
        window_layout.addRow("Height:", height_input)
        
        stay_on_top_checkbox = QCheckBox()
        stay_on_top_checkbox.setChecked(config['stay_on_top'])
        window_layout.addRow("Stay on Top:", stay_on_top_checkbox)
        
        shortcut_input = QLineEdit()
        shortcut_input.setText(config['shortcut'])
        window_layout.addRow("Toggle Window:", shortcut_input)
        
        window_group.setLayout(window_layout)
        general_layout.addWidget(window_group)
        
        # Scheduling Settings Group
        scheduling_group = QGroupBox("Scheduling Settings")
        scheduling_layout = QFormLayout()
        scheduling_layout.setSpacing(8)
        
        scheduling_enabled = QCheckBox()
        scheduling_enabled.setChecked(config.get('scheduling', {}).get('enabled', False))
        scheduling_layout.addRow("Enable:", scheduling_enabled)
        
        # Frequency settings
        frequency_group = QGroupBox("Frequency Settings")
        frequency_layout = QVBoxLayout()
        
        # Create a grid layout for the frequency controls
        frequency_grid = QGridLayout()
        
        # First row: Labels
        frequency_grid.addWidget(QLabel("Quick Select:"), 0, 0)
        frequency_grid.addWidget(QLabel("Minutes:"), 0, 1)

        # Second row: Controls
        # Create preset times with specific common intervals
        preset_times = [
            "1 minute",
            "2 minutes",
            "5 minutes",
            "10 minutes",
            "15 minutes",
            "20 minutes",
            "30 minutes",
            "1 hour",
            "2 hours",
            "3 hours",
            "4 hours"
        ]
        
        preset_combo = QComboBox()
        preset_combo.addItems(preset_times)
        
        # Get current frequency in minutes from config
        current_frequency = config.get('scheduling', {}).get('frequency', 30)  # Default to 30 minutes
        
        # Set initial values
        preset_combo.setCurrentText(f"{current_frequency} minute{'s' if current_frequency != 1 else ''}")
        
        minutes_input = QSpinBox()
        minutes_input.setRange(1, 240)  # Allow 1 minute to 4 hours
        minutes_input.setValue(current_frequency)
        minutes_input.valueChanged.connect(lambda: cls._update_preset_combo(preset_combo, minutes_input))
        
        # Connect preset combo to update inputs
        preset_combo.currentIndexChanged.connect(lambda idx: cls._update_frequency_inputs(preset_combo, minutes_input))
        
        # Add controls to the grid
        frequency_grid.addWidget(preset_combo, 1, 0)
        frequency_grid.addWidget(minutes_input, 1, 1)
        
        # Add the grid to the frequency layout
        frequency_layout.addLayout(frequency_grid)
        
        # Add frequency settings to the main layout
        frequency_group.setLayout(frequency_layout)
        scheduling_layout.addRow("Frequency (minutes):", frequency_group)
        
        deck_selector = QComboBox()
        current_deck = config.get('scheduling', {}).get('deck', "Default")
        all_decks = mw.col.decks.all_names_and_ids()
        deck_selector.addItems([d.name for d in all_decks])
        current_index = deck_selector.findText(current_deck)
        if current_index >= 0:
            deck_selector.setCurrentIndex(current_index)
        scheduling_layout.addRow("Deck:", deck_selector)

        auto_close_checkbox = QCheckBox()
        auto_close_checkbox.setChecked(config.get('scheduling', {}).get('auto_close_on_answer', False))
        scheduling_layout.addRow("Auto-close after answering:", auto_close_checkbox)
        
        scheduling_group.setLayout(scheduling_layout)
        general_layout.addWidget(scheduling_group)
        
        # Add background settings group
        background_group = QGroupBox("Background Settings")
        background_layout = QVBoxLayout()
        
        # Enable background checkbox
        background_enabled = QCheckBox("Enable custom background")
        background_enabled.setChecked(config.get('background', {}).get('enabled', False))
        
        # Function to update background settings
        def update_background_settings():
            current_config = cls.get_config()
            if 'background' not in current_config:
                current_config['background'] = {}
            current_config['background']['enabled'] = background_enabled.isChecked()
            current_config['background']['image_path'] = image_path_input.text().strip()
            current_config['background']['opacity'] = opacity_slider.value()
            cls.save_config(current_config)
            # Update the mini card window if it exists
            if hasattr(mw, 'float_card'):
                mw.float_card.config = current_config  # Update the instance config
                mw.float_card.update_card()  # Force a card update
        
        # Connect checkbox to update function
        background_enabled.stateChanged.connect(update_background_settings)
        background_layout.addWidget(background_enabled)
        
        # Image path selection with preview
        image_path_layout = QHBoxLayout()
        image_path_layout.setSpacing(10)
        
        # Left side: Browse button and preview
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        # Browse button
        browse_button = QPushButton("Browse Image...")
        browse_button.setMinimumWidth(120)  # Make button wider
        browse_button.clicked.connect(lambda: cls._browse_image(image_path_input))
        left_layout.addWidget(browse_button)
        
        # Image preview below the button
        preview_label = QLabel()
        preview_label.setMinimumSize(200, 150)  # Larger size for preview
        preview_label.setMaximumSize(200, 150)  # Fixed size
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #666;
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        preview_label.setText("No image selected")
        left_layout.addWidget(preview_label)
        
        image_path_layout.addLayout(left_layout)
        
        # Right side: Opacity slider
        opacity_layout = QVBoxLayout()
        opacity_layout.setSpacing(5)
        opacity_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        opacity_label = QLabel("Opacity:")
        opacity_slider = QSlider(Qt.Orientation.Horizontal)  # Horizontal slider
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(config.get('background', {}).get('opacity', 100))
        opacity_slider.setMinimumWidth(150)  # Match preview width
        opacity_value = QLabel(f"{opacity_slider.value()}%")
        
        # Connect slider to update both label and settings
        def on_opacity_change(value):
            opacity_value.setText(f"{value}%")
            update_background_settings()
        
        opacity_slider.valueChanged.connect(on_opacity_change)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(opacity_slider)
        opacity_layout.addWidget(opacity_value)
        opacity_layout.addStretch()  # Add stretch to center the controls
        
        image_path_layout.addLayout(opacity_layout)
        
        # Add the layout to the background layout
        background_layout.addLayout(image_path_layout)
        
        # Hidden image path input (for storing the path)
        image_path_input = QLineEdit()
        image_path_input.setVisible(False)  # Hide the input
        image_path_input.setText(config.get('background', {}).get('image_path', ''))
        image_path_input.textChanged.connect(update_background_settings)
        
        # Function to update preview
        def update_preview():
            image_path = image_path_input.text().strip()
            if image_path:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale pixmap to fit preview label while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        preview_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    preview_label.setPixmap(scaled_pixmap)
                else:
                    preview_label.setText("Invalid image")
            else:
                preview_label.setText("No image selected")
        
        # Connect image path changes to update preview
        image_path_input.textChanged.connect(update_preview)
        
        # Initial preview update
        update_preview()
        
        background_group.setLayout(background_layout)
        
        # Add background settings to the general tab
        general_layout.addWidget(background_group)
        
        # Add stretch at the bottom to keep groups at the top
        general_layout.addStretch()
        
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "General Settings")
        
        # Button Settings Tab
        button_tab = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Visibility settings
        visibility_group = QGroupBox("Button Visibility")
        visibility_layout = QVBoxLayout()
        visibility_layout.setSpacing(8)
        
        button_checkboxes = {}
        for button_name in ["Again", "Hard", "Good", "Easy"]:
            checkbox = QCheckBox(button_name)
            config_key = f"show_{button_name.lower()}"
            checkbox.setChecked(config['buttons'][config_key])
            button_checkboxes[config_key] = checkbox
            visibility_layout.addWidget(checkbox)
        
        visibility_group.setLayout(visibility_layout)
        button_layout.addWidget(visibility_group)

        # Button Style Settings
        style_group = QGroupBox("Button Styles")
        style_layout = QFormLayout()
        style_layout.setSpacing(8)

        button_height_input = QSpinBox()
        button_height_input.setRange(20, 100)
        button_height_input.setValue(config['buttons']['styles'].get('height', 30))
        button_height_input.setSuffix(" px")
        style_layout.addRow("Height:", button_height_input)

        min_width_input = QSpinBox()
        min_width_input.setRange(30, 200)
        min_width_input.setValue(config['buttons']['styles'].get('min_width', 50))
        min_width_input.setSuffix(" px")
        style_layout.addRow("Min Width:", min_width_input)

        border_radius_input = QSpinBox()
        border_radius_input.setRange(0, 20)
        border_radius_input.setValue(config['buttons']['styles'].get('border_radius', 3))
        border_radius_input.setSuffix(" px")
        style_layout.addRow("Border Radius:", border_radius_input)

        font_weight_input = QComboBox()
        font_weight_input.addItems(["normal", "bold"])
        current_weight = config['buttons']['styles'].get('font_weight', 'bold')
        font_weight_input.setCurrentText(current_weight)
        style_layout.addRow("Font Weight:", font_weight_input)

        style_group.setLayout(style_layout)
        button_layout.addWidget(style_group)

        # Color settings scroll area
        color_scroll = QScrollArea()
        color_scroll.setWidgetResizable(True)
        color_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        color_scroll.setMinimumHeight(300)  # Set minimum height for color section
        
        color_widget = QWidget()
        color_layout = QHBoxLayout()
        color_layout.setSpacing(10)
        color_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Color settings for each button type
        colors = config['buttons']['styles'].get('colors', {})
        color_inputs = {}

        def create_color_button(color):
            """Create a button for color picking."""
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid #666;")
            return btn

        def on_color_click(button, current_color, color_key):
            """Handle color button click."""
            color = QColorDialog.getColor(QColor(current_color), dialog)
            if color.isValid():
                hex_color = color.name()
                button.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #666;")
                button.color = hex_color

        button_types = {
            "again": "Again Button",
            "hard": "Hard Button",
            "good": "Good Button",
            "easy": "Easy Button",
            "show_answer": "Show Answer Button"
        }

        for btn_type, btn_label in button_types.items():
            btn_colors = colors.get(btn_type, {})
            group = QGroupBox(btn_label)
            group_layout = QFormLayout()
            group_layout.setSpacing(5)  # Reduce spacing
            group_layout.setContentsMargins(5, 10, 5, 5)  # Reduce padding

            color_inputs[btn_type] = {}
            
            bg_btn = create_color_button(btn_colors.get('background', '#2F2F31'))
            bg_btn.color = btn_colors.get('background', '#2F2F31')
            bg_btn.clicked.connect(lambda checked, b=bg_btn, c=btn_colors.get('background', '#2F2F31'), k=f"{btn_type}_bg": 
                                 on_color_click(b, c, k))
            color_inputs[btn_type]['background'] = bg_btn
            group_layout.addRow("Background:", bg_btn)

            bg_hover_btn = create_color_button(btn_colors.get('background hover', '#d0d0d0'))
            bg_hover_btn.color = btn_colors.get('background hover', '#d0d0d0')
            bg_hover_btn.clicked.connect(lambda checked, b=bg_hover_btn, c=btn_colors.get('background hover', '#d0d0d0'), k=f"{btn_type}_bg_hover": 
                                       on_color_click(b, c, k))
            color_inputs[btn_type]['background hover'] = bg_hover_btn
            group_layout.addRow("Background Hover:", bg_hover_btn)

            text_btn = create_color_button(btn_colors.get('text', '#000000'))
            text_btn.color = btn_colors.get('text', '#000000')
            text_btn.clicked.connect(lambda checked, b=text_btn, c=btn_colors.get('text', '#000000'), k=f"{btn_type}_text": 
                                   on_color_click(b, c, k))
            color_inputs[btn_type]['text'] = text_btn
            group_layout.addRow("Text:", text_btn)

            text_hover_btn = create_color_button(btn_colors.get('text hover', '#000000'))
            text_hover_btn.color = btn_colors.get('text hover', '#000000')
            text_hover_btn.clicked.connect(lambda checked, b=text_hover_btn, c=btn_colors.get('text hover', '#000000'), k=f"{btn_type}_text_hover": 
                                         on_color_click(b, c, k))
            color_inputs[btn_type]['text hover'] = text_hover_btn
            group_layout.addRow("Text Hover:", text_hover_btn)

            border_btn = create_color_button(btn_colors.get('border', '#666666'))
            border_btn.color = btn_colors.get('border', '#666666')
            border_btn.clicked.connect(lambda checked, b=border_btn, c=btn_colors.get('border', '#666666'), k=f"{btn_type}_border": 
                                     on_color_click(b, c, k))
            color_inputs[btn_type]['border'] = border_btn
            group_layout.addRow("Border:", border_btn)

            group.setLayout(group_layout)
            color_layout.addWidget(group)
            
            # Add stretch factor to make groups equal width
            color_layout.setStretch(color_layout.count() - 1, 1)

        color_widget.setLayout(color_layout)
        color_scroll.setWidget(color_widget)
        button_layout.addWidget(color_scroll)
        
        button_tab.setLayout(button_layout)
        tabs.addTab(button_tab, "Buttons")
        
        # Hotkeys Tab
        hotkeys_tab = QWidget()
        hotkeys_layout = QFormLayout()
        hotkeys_layout.setSpacing(8)
        
        hotkey_inputs = {}
        hotkey_fields = {
            'show_answer': 'Show Answer',
            'again': 'Again',
            'hard': 'Hard',
            'good': 'Good',
            'easy': 'Easy',
            'toggle_stay_on_top': 'Toggle Stay on Top',
            'replay_sound': 'Replay Sound',
            'replay_second_sound': 'Replay Second Sound',
            'toggle_scheduling': 'Toggle Scheduling',
            'toggle_auto_close': 'Toggle Auto-close'
        }
        
        for key, label in hotkey_fields.items():
            input_field = QLineEdit()
            input_field.setText(config['hotkeys'].get(key, ''))
            hotkey_inputs[key] = input_field
            hotkeys_layout.addRow(f"{label}:", input_field)
        
        hotkeys_tab.setLayout(hotkeys_layout)
        tabs.addTab(hotkeys_tab, "Hotkeys")
        
        # Get current theme colors for styling
        theme = cls.get_theme()
        bg_color = theme["background"]
        text_color = theme["text"]
        button_bg = theme["button_bg"]
        button_text = theme["button_text"]
        button_border = theme["button_border"]
        
        # Style all group boxes and inputs
        style = f"""
        QDialog {{
            background-color: {bg_color};
            color: {text_color};
        }}
        QTabWidget::pane {{
            border: 1px solid {button_border};
            border-radius: 6px;
            background-color: {bg_color};
        }}
        QTabBar::tab {{
            background-color: {button_bg};
            color: {button_text};
            border: 1px solid {button_border};
            padding: 8px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {bg_color};
            border-bottom: none;
        }}
        QTabBar::tab:hover {{
            background-color: {bg_color}99;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {button_border};
            border-radius: 6px;
            margin-top: 6px;
            padding-top: 10px;
            color: {text_color};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 7px;
            padding: 0px 5px 0px 5px;
            color: {text_color};
        }}
        QSpinBox, QLineEdit, QComboBox {{
            padding: 4px;
            border: 1px solid {button_border};
            border-radius: 4px;
            min-width: 100px;
            background-color: {button_bg};
            color: {button_text};
        }}
        QSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {button_text};
        }}
        QCheckBox {{
            spacing: 8px;
            color: {text_color};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            background-color: {bg_color};
            border: 1px solid {button_border};
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {button_bg};
            border: 1px solid {button_text};
        }}
        QCheckBox::indicator:unchecked {{
            background-color: {bg_color};
            border: 1px solid {button_border};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {button_text};
            background-color: {button_bg}55;
        }}
        QLabel {{
            color: {text_color};
        }}
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        """
        dialog.setStyleSheet(style)
        
        # Add tabs to main layout
        main_layout.addWidget(tabs)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        
        button_box.setStyleSheet(f"""
            QPushButton {{
                min-width: 80px;
                padding: 6px 14px;
                border-radius: 4px;
                border: 1px solid {button_border};
                background-color: {button_bg};
                color: {button_text};
            }}
            QPushButton:hover {{
                background-color: {bg_color};
                border: 1px solid {button_text};
            }}
            QPushButton:focus {{
                border: 1px solid {button_text};
                outline: none;
            }}
            QPushButton:pressed {{
                background-color: {button_bg};
                border: 2px solid {button_text};
            }}
        """)
        
        def on_accept():
            """Save settings when OK is clicked."""
            try:
                current_config = cls.get_config()
                
                # Update scheduling settings
                if 'scheduling' not in current_config:
                    current_config['scheduling'] = {}
                
                # Save frequency in minutes
                frequency_minutes = minutes_input.value()
                current_config['scheduling']['frequency'] = frequency_minutes
                current_config['scheduling']['enabled'] = scheduling_enabled.isChecked()
                current_config['scheduling']['deck'] = deck_selector.currentText()
                current_config['scheduling']['auto_close_on_answer'] = auto_close_checkbox.isChecked()
                
                # Update window settings
                current_config['window_width'] = width_input.value()
                current_config['window_height'] = height_input.value()
                current_config['stay_on_top'] = stay_on_top_checkbox.isChecked()
                current_config['shortcut'] = shortcut_input.text()
                
                # Update button visibility
                for key, checkbox in button_checkboxes.items():
                    current_config['buttons'][key] = checkbox.isChecked()

                # Update button styles
                if 'styles' not in current_config['buttons']:
                    current_config['buttons']['styles'] = {}
                current_config['buttons']['styles'].update({
                    'height': button_height_input.value(),
                    'min_width': min_width_input.value(),
                    'border_radius': border_radius_input.value(),
                    'font_weight': font_weight_input.currentText()
                })

                # Update button colors
                if 'colors' not in current_config['buttons']['styles']:
                    current_config['buttons']['styles']['colors'] = {}
                
                for btn_type, inputs in color_inputs.items():
                    current_config['buttons']['styles']['colors'][btn_type] = {
                        'background': inputs['background'].color,
                        'background hover': inputs['background hover'].color,
                        'text': inputs['text'].color,
                        'text hover': inputs['text hover'].color,
                        'border': inputs['border'].color
                    }
                
                # Update hotkeys
                for key, input_field in hotkey_inputs.items():
                    current_config['hotkeys'][key] = input_field.text()
                
                # Update background settings
                if 'background' not in current_config:
                    current_config['background'] = {}
                current_config['background']['enabled'] = background_enabled.isChecked()
                current_config['background']['image_path'] = image_path_input.text().strip()
                current_config['background']['opacity'] = opacity_slider.value()
                
                # Save the updated config
                cls.save_config(current_config)
                
                # Show success message
                tooltip("Configuration saved successfully")
                
                # Close the dialog
                dialog.accept()
                
            except Exception as e:
                logger.error(f"Error saving configuration: {str(e)}", exc_info=True)
                tooltip(f"Error saving configuration: {str(e)}")
        
        # Connect the buttons
        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dialog.reject)
        
        # Add button box to main layout
        main_layout.addWidget(button_box)
        
        # Set dialog layout
        dialog.setLayout(main_layout)
        
        # Set reasonable minimum size
        dialog.setMinimumWidth(900)
        dialog.setMinimumHeight(800)  # Increased height
        
        # Allow the dialog to be resized
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        dialog.setSizeGripEnabled(True)
        
        # Center the dialog on the screen
        screen = QApplication.primaryScreen().geometry()
        dialog_size = dialog.geometry()
        x = (screen.width() - dialog_size.width()) // 2
        y = (screen.height() - dialog_size.height()) // 2
        dialog.move(x, y)
        
        # Show the dialog
        dialog.exec()

    @classmethod
    def get_theme(cls):
        """Get the current theme based on Anki's night mode setting."""
        config = cls.get_config()
        is_night_mode = mw.pm.night_mode()
        return config["theme"]["dark"] if is_night_mode else config["theme"]["light"]

    @classmethod
    def _update_frequency_inputs(cls, preset_combo, minutes_input):
        """Update minutes and seconds inputs when preset is selected."""
        text = preset_combo.currentText()
        if "hour" in text:
            parts = text.split(" hour")
            hours = int(parts[0])
            if "and" in parts[1]:
                minutes = int(parts[1].split(" and ")[1].split(" minute")[0])
                total_minutes = hours * 60 + minutes
            else:
                total_minutes = hours * 60
        else:
            total_minutes = int(text.split(" minute")[0])
        
        minutes_input.setValue(total_minutes)
    
    @classmethod
    def _update_preset_combo(cls, preset_combo, minutes_input):
        """Update preset combo when minutes or seconds are changed."""
        total_minutes = minutes_input.value()
        if total_minutes == 0:
            preset_combo.setCurrentText("1 minute")
            return
            
        # Only update the preset if it's a direct match
        current_text = preset_combo.currentText()
        if "hour" in current_text:
            parts = current_text.split(" hour")
            hours = int(parts[0])
            if "and" in parts[1]:
                minutes = int(parts[1].split(" and ")[1].split(" minute")[0])
                current_total = hours * 60 + minutes
            else:
                current_total = hours * 60
        else:
            current_total = int(current_text.split(" minute")[0])
            
        # If the current preset doesn't match the input, clear the preset selection
        if total_minutes != current_total:
            preset_combo.setCurrentText("")  # Clear the selection

    @classmethod
    def _browse_image(cls, image_path_input):
        """Open file dialog to browse for background image."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path_input.setText(selected_files[0])

def get_config() -> Dict[str, Any]:
    """Get the current configuration.
    
    Returns:
        Dict containing the current configuration
    """
    return mw.addonManager.getConfig(__name__.split('.')[0])

def write_config(config: Dict[str, Any]) -> None:
    """Write configuration to disk.
    
    Args:
        config: Configuration dictionary to write
    """
    mw.addonManager.writeConfig(__name__.split('.')[0], config)

def get_default_config() -> Dict[str, Any]:
    """Get the default configuration from schema.
    
    Returns:
        Dict containing default configuration values
    """
    def extract_defaults(schema):
        if isinstance(schema, dict):
            if 'type' in schema:
                if 'default' in schema:
                    return schema['default']
                elif schema['type'] == 'object' and 'properties' in schema:
                    return {k: extract_defaults(v) for k, v in schema['properties'].items()}
                elif schema['type'] == 'array':
                    return []
            return {}
        return schema

    return extract_defaults(CONFIG_SCHEMA)

def update_config() -> None:
    """Update configuration with any missing default values."""
    try:
        current_config = get_config()
        default_config = get_default_config()
        
        def update_dict_recursive(target, source):
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    update_dict_recursive(target[key], value)
        
        update_dict_recursive(current_config, default_config)
        write_config(current_config)
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        # If there's an error, write the default config
        write_config(default_config) 