import sqlite3
from config import DATABASE_NAME


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # System metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            ram REAL,
            disk REAL,
            net_sent REAL,
            net_recv REAL
        )
        """)

        # Risk events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            anomaly_score REAL,
            risk_score REAL,
            severity TEXT
        )
        """)

        # System info table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            public_ip TEXT,
            logged_user TEXT,
            boot_time TEXT
        )
        """)

        conn.commit()


def insert_metrics(timestamp, cpu, ram, disk, net_sent, net_recv):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO system_metrics (timestamp, cpu, ram, disk, net_sent, net_recv)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, cpu, ram, disk, net_sent, net_recv))

        conn.commit()


def insert_risk_event(timestamp, anomaly_score, risk_score, severity):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO risk_events (timestamp, anomaly_score, risk_score, severity)
        VALUES (?, ?, ?, ?)
        """, (timestamp, anomaly_score, risk_score, severity))

        conn.commit()