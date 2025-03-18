import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from aqt.utils import showWarning

def setup_logger():
    """Set up the logger for the addon."""
    # Get logger
    logger = logging.getLogger('float_card_popup')
    
    try:
        # Only set up handlers if they haven't been set up already
        if not logger.handlers:
            # Set logger level to ERROR to only capture errors
            logger.setLevel(logging.ERROR)

            # Create log directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)

            # Create handlers
            log_file = os.path.join(log_dir, 'float_card.log')
            
            try:
                # Use RotatingFileHandler for errors
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=1024*1024,  # 1 MB
                    backupCount=3,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.ERROR)  # Only log errors to file
                
                # Create formatters and add it to handlers
                log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(log_format)
                
                # Add file handler to the logger
                logger.addHandler(file_handler)
            except (IOError, PermissionError) as e:
                # If we can't write to the log file, show a warning but continue with console logging
                showWarning(f"Could not create log file: {str(e)}\nLogging to console only.")
            
            # Console handler for debugging if needed
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.ERROR)  # Only show errors in console
            console_handler.setFormatter(log_format)
            logger.addHandler(console_handler)

    except Exception as e:
        # If logger setup fails completely, at least try to log to stderr
        print(f"Failed to set up logger: {str(e)}", file=sys.stderr)
        
    return logger 