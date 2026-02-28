import logging
from config import LOG_FILE, LOG_LEVEL, ENABLE_LOGGING
from storage.database import init_db
from core.engine import start_engine

def setup_logging():
    if ENABLE_LOGGING:
        logging.basicConfig(
            filename=LOG_FILE,
            level=getattr(logging, LOG_LEVEL),
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

def main():
    setup_logging()
    init_db()
    start_engine()

if __name__ == "__main__":
    main()