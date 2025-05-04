import threading
import time
import uvicorn

from web import app  # FastAPI-Instanz
from main import main as run_charger  # dein Ladezyklus
from config import APP_REFRESH_INTERVAL_SEC


def start_api():
    # log_level optional auf "info" reduzieren
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()
    while True:
        run_charger()
        time.sleep(APP_REFRESH_INTERVAL_SEC)
import threading
import time

from main import main as run_charger  # dein Ladezyklus
from config import APP_REFRESH_INTERVAL_SEC


def start_api():
    # log_level optional auf "info" reduzieren
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()
    while True:
        run_charger()
        time.sleep(APP_REFRESH_INTERVAL_SEC)
