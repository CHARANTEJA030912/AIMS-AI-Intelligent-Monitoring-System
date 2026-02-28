import threading
import logging
import datetime
import atexit
import os
import sys
import time


if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)


from core.engine import start_engine
from control.telegram_bot import start_bot, send_alert
from storage.database import init_db


LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "system.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# ALERT FUNCTIONS
# -------------------------------
def boot_alert():
    boot_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"🟢 Laptop Booted\n\n"
        f"Time: {boot_time}\n"
        f"AIMS Monitoring Active."
    )
    send_alert(message)

def shutdown_alert():
    shutdown_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"🔴 Laptop Shutting Down\n\n"
        f"Time: {shutdown_time}"
    )
    send_alert(message)

# -------------------------------
# MAIN CONTROLLER
# -------------------------------
def main():

    time.sleep(30) # DELAY TO ENSURE SYSTEM STABILITY BEFORE STARTING SERVICES

    init_db()

    boot_alert()

    atexit.register(shutdown_alert)

    engine_thread = threading.Thread(target=start_engine, daemon=True)
    engine_thread.start()

    start_bot()

if __name__ == "__main__":
    main()