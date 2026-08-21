import logging

from itisamanager.config.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

logger.info("AI Agent started")

def main():
    pass

if __name__ == "__main__":
    main()
    