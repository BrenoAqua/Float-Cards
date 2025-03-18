from aqt import mw
from aqt.qt import QMenu, QAction, QKeySequence, QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QGroupBox, QCheckBox, QHBoxLayout, QSpinBox
from aqt.utils import qconnect
from .gui import FloatCardPopup
from .config import Config
from .logger import setup_logger

# Get logger
logger = setup_logger()

def cleanup():
    """Clean up resources when Anki is closing."""
    from . import float_card_popup
    try:
        if float_card_popup is not None:
            float_card_popup.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}", exc_info=True)

def toggle_float_card():
    """Toggles the floating float card window."""
    from . import float_card_popup
    try:
        if float_card_popup.isVisible():
            logger.info("Hiding float card popup")
            float_card_popup.hide()
        else:
            # If we have a card in the current deck, show it
            if mw.reviewer and mw.reviewer.card:
                logger.info("Showing float card popup with current card")
                float_card_popup.show()
                float_card_popup.update_card()
                float_card_popup.activateWindow()  # Activate and focus the window
                float_card_popup.setFocus()  # Set keyboard focus
                mw.showMinimized()  # Minimize Anki main window
            else:
                # If no deck is open, show deck selection dialog first
                logger.info("No deck open, showing deck selection dialog")
                
                # Create a deck selector dialog
                deck_dialog = QDialog(mw)
                deck_dialog.setWindowTitle("Select Deck")
                deck_dialog.setMinimumWidth(400)
                layout = QVBoxLayout()
                
                # Add label
                label = QLabel("Select a deck to review:")
                layout.addWidget(label)
                
                # Add deck selector
                deck_selector = QComboBox()
                all_decks = mw.col.decks.all_names_and_ids()
                deck_selector.addItems([d.name for d in all_decks])
                
                # Set the last selected deck if it exists
                config = Config.get_config()
                last_deck = config.get('scheduling', {}).get('deck')
                if last_deck:
                    index = deck_selector.findText(last_deck)
                    if index >= 0:
                        deck_selector.setCurrentIndex(index)
                
                layout.addWidget(deck_selector)
                
                # Add scheduling options
                scheduling_group = QGroupBox("Scheduling Options")
                scheduling_layout = QVBoxLayout()
                
                # Enable scheduling checkbox
                scheduling_enabled = QCheckBox("Enable Scheduling")
                scheduling_enabled.setChecked(Config.get_config().get('scheduling', {}).get('enabled', False))
                scheduling_layout.addWidget(scheduling_enabled)
                
                # Frequency settings
                frequency_layout = QHBoxLayout()
                
                # Quick select combo
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
                current_frequency = Config.get_config().get('scheduling', {}).get('frequency', 30)
                preset_combo.setCurrentText(f"{current_frequency} minute{'s' if current_frequency != 1 else ''}")
                
                # Minutes input
                minutes_input = QSpinBox()
                minutes_input.setRange(1, 240)
                minutes_input.setValue(current_frequency)
                
                # Connect preset combo to update minutes input
                def update_minutes_from_preset():
                    text = preset_combo.currentText()
                    if text == "1 minute":
                        minutes_input.setValue(1)
                    elif text == "2 minutes":
                        minutes_input.setValue(2)
                    elif text == "5 minutes":
                        minutes_input.setValue(5)
                    elif text == "10 minutes":
                        minutes_input.setValue(10)
                    elif text == "15 minutes":
                        minutes_input.setValue(15)
                    elif text == "20 minutes":
                        minutes_input.setValue(20)
                    elif text == "30 minutes":
                        minutes_input.setValue(30)
                    elif text == "1 hour":
                        minutes_input.setValue(60)
                    elif text == "2 hours":
                        minutes_input.setValue(120)
                    elif text == "3 hours":
                        minutes_input.setValue(180)
                    elif text == "4 hours":
                        minutes_input.setValue(240)
                
                preset_combo.currentIndexChanged.connect(update_minutes_from_preset)
                
                # Add frequency controls
                frequency_layout.addWidget(QLabel("Quick Select:"))
                frequency_layout.addWidget(preset_combo)
                frequency_layout.addWidget(QLabel("Minutes:"))
                frequency_layout.addWidget(minutes_input)
                frequency_layout.addStretch()
                
                scheduling_layout.addLayout(frequency_layout)
                
                # Auto-close checkbox
                auto_close = QCheckBox("Auto-close after answering")
                auto_close.setChecked(Config.get_config().get('scheduling', {}).get('auto_close_on_answer', False))
                scheduling_layout.addWidget(auto_close)
                
                scheduling_group.setLayout(scheduling_layout)
                layout.addWidget(scheduling_group)
                
                # Add buttons
                button_box = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | 
                    QDialogButtonBox.StandardButton.Cancel
                )
                layout.addWidget(button_box)
                
                deck_dialog.setLayout(layout)
                
                # Connect buttons
                def on_accept():
                    selected_deck = deck_selector.currentText()
                    if selected_deck:
                        # Select the deck and start review
                        deck = mw.col.decks.by_name(selected_deck)
                        if deck:
                            # Update scheduling settings
                            config = Config.get_config()
                            if 'scheduling' not in config:
                                config['scheduling'] = {}
                            
                            config['scheduling'].update({
                                'enabled': scheduling_enabled.isChecked(),
                                'frequency': minutes_input.value(),
                                'deck': selected_deck,  # Save the selected deck
                                'auto_close_on_answer': auto_close.isChecked()
                            })
                            Config.save_config(config)
                            
                            # Select deck and start review
                            mw.col.decks.select(deck['id'])
                            mw.moveToState('review')
                            
                            # Reset reviewer state to show new cards
                            if hasattr(mw.reviewer, 'reset'):
                                mw.reviewer.reset()
                            
                            # Show popup and update card
                            float_card_popup.show()
                            float_card_popup.update_card()
                            float_card_popup.activateWindow()  # Activate and focus the window
                            float_card_popup.setFocus()  # Set keyboard focus
                            
                            # Update scheduler if enabled
                            if scheduling_enabled.isChecked():
                                float_card_popup.scheduler.update_state(config)
                                float_card_popup.scheduler.start_schedule()
                            
                            # Minimize Anki main window
                            mw.showMinimized()
                    deck_dialog.accept()
                
                button_box.accepted.connect(on_accept)
                button_box.rejected.connect(deck_dialog.reject)
                
                # Show the dialog
                deck_dialog.exec()
                
    except Exception as e:
        logger.error(f"Error toggling float card: {str(e)}", exc_info=True)

def update_float_card():
    """Updates the float-card when a new card appears."""
    from . import float_card_popup
    try:
        if float_card_popup.isVisible():
            if mw.reviewer and mw.reviewer.card:
                logger.info("Updating float card with current reviewer card")
                float_card_popup.update_card()
            else:
                logger.warning("No card available to update in float popup")
    except Exception as e:
        logger.error(f"Error updating float card: {str(e)}", exc_info=True)

def show_scheduled_card():
    """Shows the float card popup and updates it with the current card."""
    from . import float_card_popup
    try:
        if not float_card_popup.isVisible():
            logger.info("Making float card popup visible for scheduled card")
            float_card_popup.show()
        
        if mw.reviewer and mw.reviewer.card:
            logger.info("Updating float card with scheduled card")
            float_card_popup.update_card()
        else:
            logger.warning("No card available to update in float popup")
    except Exception as e:
        logger.error(f"Error showing scheduled card: {str(e)}", exc_info=True)

def setup_menu():
    """Set up the menu items for the addon."""
    try:
        config = Config.get_config()
        
        # Create our top level menu
        menu = QMenu("Float Cards", mw)
        
        # Add toggle action
        toggle_action = QAction("Toggle Float Cards", menu)
        toggle_action.setShortcut(QKeySequence(config['shortcut']))
        qconnect(toggle_action.triggered, toggle_float_card)
        menu.addAction(toggle_action)
        
        # Add configuration action
        config_action = QAction("Configure", menu)
        qconnect(config_action.triggered, Config.open_config_dialog)
        menu.addAction(config_action)
        
        # Insert the menu before the Help menu
        menubar = mw.form.menubar
        help_menu = mw.form.menuHelp
        menubar.insertMenu(help_menu.menuAction(), menu)
        
        # Set up cleanup hook and card update hook
        from anki.hooks import addHook
        addHook("unloadProfile", cleanup)
        addHook("showQuestion", update_float_card)  # Add this back to keep card in sync
        
        # Initialize scheduler
        from .scheduler import FloatCardScheduler
        from . import float_card_popup
        if not hasattr(float_card_popup, 'scheduler'):
            logger.info("Creating new scheduler instance")
            float_card_popup.scheduler = FloatCardScheduler(show_scheduled_card)
            # Update scheduler state with current config
            float_card_popup.scheduler.update_state(config)
        
    except Exception as e:
        logger.error(f"Error setting up menu: {str(e)}", exc_info=True) 