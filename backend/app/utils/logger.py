import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/superstats.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger("superstats")

# Set level based on environment
logger.setLevel(logging.DEBUG)  # Change to INFO in production


def log_info(message: str):
    """Log info message."""
    logger.info(message)


def log_error(message: str):
    """Log error message."""
    logger.error(message)


def log_warning(message: str):
    """Log warning message."""
    logger.warning(message)


def log_debug(message: str):
    """Log debug message."""
    logger.debug(message)
