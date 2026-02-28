engine_running = True

def start_monitoring():
    global engine_running
    engine_running = True

def stop_monitoring():
    global engine_running
    engine_running = False

def get_engine_status():
    return engine_running