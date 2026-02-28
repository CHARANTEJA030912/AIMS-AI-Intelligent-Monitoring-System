import time
import logging

from config import COLLECTION_INTERVAL
from agent.collector import collect_system_metrics
from storage.database import get_connection, insert_risk_event
from ai.model import AnomalyModel
from ai.risk_engine import calculate_risk
from control.telegram_bot import send_alert
from core.state import get_engine_status   # ✅ Proper state import

model = AnomalyModel()


def fetch_latest_row():
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


def start_engine():
    logging.info("AIMS Monitoring Engine Started with AI (DB-Based Retrain)")

    while True:

        # ✅ Check monitoring state safely
        if not get_engine_status():
            time.sleep(2)
            continue

        try:
            # 1️⃣ Collect system metrics
            collect_system_metrics()

            # 2️⃣ DB-based retraining trigger
            if model.should_retrain():
                trained = model.train()
                if trained:
                    logging.info("AI Model Retrained Successfully (DB Trigger)")

            # 3️⃣ Prediction
            latest = fetch_latest_row()

            if latest and model.trained:
                timestamp, cpu, ram, disk, net_sent, net_recv = latest

                prediction, score = model.predict(
                    [cpu, ram, disk, net_sent, net_recv]
                )

                risk_score, severity = calculate_risk(
                    prediction,
                    score,
                    cpu,
                    ram,
                    net_sent,
                    net_recv
                )

                # Store meaningful risk events
                if severity != "LOW":
                    insert_risk_event(timestamp, score, risk_score, severity)

                    # 🚨 HIGH risk telegram alert
                    if severity == "HIGH":
                        alert_message = (
                            f"🚨 HIGH RISK DETECTED 🚨\n\n"
                            f"Time: {timestamp}\n"
                            f"CPU: {cpu}%\n"
                            f"RAM: {ram}%\n"
                            f"Anomaly Score: {round(score,3)}\n"
                            f"Risk Score: {risk_score}\n"
                            f"Immediate Attention Required!"
                        )

                        send_alert(alert_message)

                logging.info(
                    f"AI | Prediction:{prediction} "
                    f"Score:{round(score,3)} "
                    f"Risk:{risk_score} "
                    f"Severity:{severity}"
                )

            time.sleep(COLLECTION_INTERVAL)

        except Exception as e:
            logging.error(f"Engine Error: {str(e)}")
            time.sleep(5)