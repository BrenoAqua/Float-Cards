from PyQt6.QtCore import QTimer
import time
import logging
from aqt import mw
from .config import Config
from aqt.utils import showInfo, tooltip

logger = logging.getLogger(__name__)

class FloatCardScheduler:
    def __init__(self, show_card_func):
        """Initialize the scheduler.
        
        Args:
            show_card_func: Function to call when it's time to show a card
        """
        self.show_card_func = show_card_func
        self.schedule_interval = 30  # Default 30 minutes
        self.current_deck = "Default"
        self.timer = QTimer()
        self.timer.timeout.connect(self.exec_schedule)
        self.enabled = False
        
    def set_schedule(self, interval_minutes):
        """Set the schedule interval in minutes."""
        logger.info(f"Setting schedule interval to {interval_minutes} minutes")
        self.schedule_interval = interval_minutes
        
    def exec_schedule(self):
        """Execute the scheduled task - show a card."""
        logger.info(f"Executing schedule at {time.ctime()}")
        
        # Check if collection is loaded
        if not mw.col:
            logger.error("Collection not loaded")
            return
            
        # Check if we have a valid deck
        try:
            deck = mw.col.decks.by_name(self.current_deck)
            if not deck:
                logger.error(f"Could not find deck: {self.current_deck}")
                tooltip(f"Could not find deck: {self.current_deck}")
                self.stop_schedule()
                return
                
            logger.info(f"Found deck: {self.current_deck} (id: {deck['id']})")
                
            # Save current deck
            old_deck = mw.col.decks.current()
            logger.info(f"Current deck before switch: {old_deck['name']}")
                
            try:
                # Set the deck as current
                mw.col.decks.select(deck['id'])
                logger.info(f"Switched to deck: {self.current_deck}")
                
                # Move to review state if needed
                if not self._ensure_review_state():
                    logger.error("Failed to ensure review state")
                    return
                    
                # Try to get a card
                card = mw.col.sched.getCard()
                if card:
                    logger.info(f"Got card {card.id} from deck {self.current_deck}")
                    # Show the popup and update it with the current card
                    self.show_card_func()
                    tooltip(f"Showing scheduled card from deck: {self.current_deck}")
                else:
                    logger.warning(f"No cards available in deck: {self.current_deck}")
                    tooltip(f"No cards available in deck: {self.current_deck}")
                    self.stop_schedule()
            except Exception as e:
                logger.error(f"Error in exec_schedule: {e}", exc_info=True)
            finally:
                # Restore previous deck
                if old_deck:
                    logger.info(f"Restoring previous deck: {old_deck['name']}")
                    mw.col.decks.select(old_deck['id'])
        except Exception as e:
            logger.error(f"Error accessing collection: {e}", exc_info=True)
            self.stop_schedule()

    def _ensure_review_state(self):
        """Ensure we're in review state with the correct deck."""
        try:
            logger.info("Checking review state...")
            # If we're not in review state or no card is selected
            if not mw.reviewer or not mw.reviewer.card:
                logger.info("No active reviewer or card, attempting to start review")
                # Try to get a card directly
                card = mw.col.sched.getCard()
                if card:
                    logger.info("Card available, moving to review state")
                    mw.onOverview()
                    mw.moveToState('review')
                    return True
                else:
                    logger.warning("No cards available for review")
                    tooltip("No cards available for review")
                    return False
            logger.info("Review state is good")
            return True
        except Exception as e:
            logger.error(f"Error ensuring review state: {e}", exc_info=True)
            return False
        
    def start_schedule(self):
        """Start the scheduling timer."""
        logger.info(f"Starting schedule at {time.ctime()}")
        # Convert minutes to milliseconds
        interval_ms = self.schedule_interval * 60 * 1000
        logger.info(f"Setting timer interval to {interval_ms}ms ({self.schedule_interval} minutes)")
        self.timer.start(interval_ms)
        self.enabled = True
        
        # Show first card immediately
        logger.info("Showing first card immediately")
        self.exec_schedule()
        
    def stop_schedule(self):
        """Stop the scheduling timer."""
        logger.info(f"Stopping schedule at {time.ctime()}")
        self.timer.stop()
        self.enabled = False
        tooltip("Scheduled review stopped")
        
    def update_state(self, config=None):
        """Update scheduler state based on configuration."""
        if config is None:
            config = Config.get_config()
        
        sched_config = config.get('scheduling', {})
        new_interval = sched_config.get('frequency', 30)
        new_enabled = sched_config.get('enabled', False)
        new_deck = sched_config.get('deck', "Default")
        
        logger.info(f"Updating scheduler state: enabled={new_enabled}, interval={new_interval}, deck={new_deck}")
        
        # Always stop first to ensure clean state
        if self.enabled:
            self.stop_schedule()
            
        # Update settings
        if self.schedule_interval != new_interval:
            logger.info(f'Updating frequency from {self.schedule_interval} to {new_interval} minutes')
            self.schedule_interval = new_interval
            
        if self.current_deck != new_deck:
            logger.info(f'Updating deck from {self.current_deck} to {new_deck}')
            self.current_deck = new_deck
                
        # Only start if explicitly enabled
        if new_enabled:
            logger.info(f'Starting scheduler with {new_interval} minute interval for deck {new_deck}')
            self.start_schedule() 