from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
import logging
from core.state import start_monitoring, stop_monitoring, get_engine_status

from config import DATABASE_NAME

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))


# ===============================
# DATABASE HELPERS
# ===============================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def get_latest_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, cpu, ram, disk, net_sent, net_recv
        FROM system_metrics
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()
    return row


def get_latest_risk():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, anomaly_score, risk_score, severity
        FROM risk_events
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()
    return row


def get_summary_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM system_metrics")
    total_metrics = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM risk_events")
    total_risks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM risk_events WHERE severity='HIGH'")
    high_risks = cursor.fetchone()[0]

    conn.close()

    return total_metrics, total_risks, high_risks


# ===============================
# TELEGRAM COMMANDS
# ===============================

def status(update: Update, context: CallbackContext):
    row = get_latest_metrics()

    if not row:
        update.message.reply_text("No data available yet.")
        return

    timestamp, cpu, ram, disk, net_sent, net_recv = row

    message = (
        f"🖥 AIMS Status\n\n"
        f"Time: {timestamp}\n"
        f"CPU: {cpu}%\n"
        f"RAM: {ram}%\n"
        f"Disk: {disk}%\n"
        f"Net Sent: {round(net_sent,2)} MB\n"
        f"Net Recv: {round(net_recv,2)} MB"
    )

    update.message.reply_text(message)


def risk(update: Update, context: CallbackContext):
    row = get_latest_risk()

    if not row:
        update.message.reply_text("No risk events detected yet.")
        return

    timestamp, anomaly_score, risk_score, severity = row

    message = (
        f"⚠ Risk Event\n\n"
        f"Time: {timestamp}\n"
        f"Anomaly Score: {round(anomaly_score,3)}\n"
        f"Risk Score: {risk_score}\n"
        f"Severity: {severity}"
    )

    update.message.reply_text(message)


def summary(update: Update, context: CallbackContext):
    total_metrics, total_risks, high_risks = get_summary_data()

    message = (
        f"📊 AIMS Summary\n\n"
        f"Total Metrics: {total_metrics}\n"
        f"Total Risk Events: {total_risks}\n"
        f"High Severity Events: {high_risks}"
    )

    update.message.reply_text(message)

def start_monitor(update: Update, context: CallbackContext):
    start_monitoring()
    update.message.reply_text("🟢 Monitoring Started")


def stop_monitor(update: Update, context: CallbackContext):
    stop_monitoring()
    update.message.reply_text("🔴 Monitoring Stopped")


def monitor_status(update: Update, context: CallbackContext):
    status = get_engine_status()
    if status:
        update.message.reply_text("🟢 Monitoring is ACTIVE")
    else:
        update.message.reply_text("🔴 Monitoring is STOPPED")

# ===============================
# AUTO ALERT FUNCTION (ENGINE USES THIS)
# ===============================

def send_alert(message_text):
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        bot = updater.bot
        bot.send_message(chat_id=CHAT_ID, text=message_text)
    except Exception as e:
        logging.error(f"Telegram Alert Error: {str(e)}")


# ===============================
# START BOT
# ===============================

def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("risk", risk))
    dp.add_handler(CommandHandler("summary", summary))
    dp.add_handler(CommandHandler("start_monitoring", start_monitor))
    dp.add_handler(CommandHandler("stop_monitoring", stop_monitor))
    dp.add_handler(CommandHandler("monitor_status", monitor_status))
    updater.start_polling()
    logging.info("Telegram Bot Started")
    updater.idle()