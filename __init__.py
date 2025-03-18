"""
Mini Card Popup for Anki
A floating window that shows the current card, allowing you to review cards while doing other tasks.
"""

__version__ = "1.0.0"

from aqt import mw
from aqt.qt import *
from aqt.utils import showWarning, tooltip
from anki.hooks import addHook

from .gui import FloatCardPopup
from .config import Config
from .scheduler import FloatCardScheduler
from .main import setup_menu
import logging
import sys

# Setup logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Initialize the popup window but don't show it
float_card_popup = FloatCardPopup(mw)
float_card_popup.hide()  # Ensure it's hidden

# Initialize the scheduler with the popup window's show_popup method
scheduler = FloatCardScheduler(float_card_popup.show_popup)

# Initialize the addon
def init_addon():
    """Initialize the addon after Anki's main window is ready."""
    try:
        # Set up menu and hooks
        setup_menu()
        
        # Update scheduler state
        config = Config.get_config()
        scheduler.update_state(config)
        
        logger.info("Mini Card Popup addon initialized")
    except Exception as e:
        logger.error(f"Error initializing addon: {e}", exc_info=True)
        showWarning(f"Error initializing Mini Card Popup addon: {e}")

# Wait for Anki to be ready before initializing
addHook("profileLoaded", init_addon)

def show_options():
    """Show the addon configuration dialog."""
    Config.open_config_dialog()
    # Update scheduler state after config changes
    config = Config.get_config()
    scheduler.update_state(config)
    
    # Show feedback about scheduling state
    if config.get('scheduling', {}).get('enabled', False):
        deck = config.get('scheduling', {}).get('deck', "Default")
        freq = config.get('scheduling', {}).get('frequency', 30)
        tooltip(f"Scheduling enabled: Will show cards from '{deck}' every {freq} minutes")
    else:
        tooltip("Scheduling disabled")

# Add menu item
options_action = QAction("Mini Card Popup Options", mw)
options_action.triggered.connect(show_options)
mw.form.menuTools.addAction(options_action)

# Register config callback
def on_config_changed(config):
    """Handle configuration changes."""
    try:
        scheduler.update_state(config)
        logger.info("Configuration updated, scheduler state refreshed")
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        showWarning(f"Error updating configuration: {e}")

mw.addonManager.setConfigUpdatedAction(__name__, on_config_changed)