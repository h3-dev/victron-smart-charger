import threading, time, uvicorn
from web import app
from main import main as run_charger
from config import APP_REFRESH_INTERVAL_SEC

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()
    while True:
        run_charger()
        time.sleep(APP_REFRESH_INTERVAL_SEC)