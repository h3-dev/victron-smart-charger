import time
from main import main as run_charger        # deine bestehende main()

INTERVAL = 15 * 60  # alle 15 min

while True:
    run_charger()
    time.sleep(INTERVAL)