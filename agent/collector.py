import psutil
import datetime
import getpass
import logging

from storage.database import insert_metrics

# Store previous network counters for delta calculation
previous_net = psutil.net_io_counters()

def collect_system_metrics():
    global previous_net

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    current_net = psutil.net_io_counters()

    net_sent = (current_net.bytes_sent - previous_net.bytes_sent) / (1024 * 1024)
    net_recv = (current_net.bytes_recv - previous_net.bytes_recv) / (1024 * 1024)

    previous_net = current_net

    insert_metrics(timestamp, cpu, ram, disk, net_sent, net_recv)

    logging.info(
        f"{timestamp} | CPU:{cpu}% RAM:{ram}% DISK:{disk}% "
        f"NET_SENT:{round(net_sent,2)}MB NET_RECV:{round(net_recv,2)}MB"
    )