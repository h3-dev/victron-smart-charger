import time
from main import main as run_charger
from config import APP_REFRESH_INTERVAL_SEC

while True:
    run_charger()
    time.sleep(APP_REFRESH_INTERVAL_SEC)
