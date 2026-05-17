import logging
import os

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_info(message: str, **kwargs):
    logger.info(f"{message} | {kwargs}")

def log_error(message: str, **kwargs):
    logger.error(f"{message} | {kwargs}")

def log_debug(message: str, **kwargs):
    logger.debug(f"{message} | {kwargs}")

