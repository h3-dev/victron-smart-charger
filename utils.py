# utils.py

from datetime import datetime
import os
import time as sys_time

from config import now_override

# Setze Zeitzone global (z. B. für Venus OS ohne zoneinfo)
os.environ["TZ"] = "Europe/Berlin"
sys_time.tzset()


def now():
    """
    Gibt die aktuelle Zeit zurück oder einen gesetzten Override.
    """
    return now_override or datetime.now()


def get_unix_timestamp(dt: datetime) -> int:
    """
    Wandelt ein datetime-Objekt in einen Unix-Zeitstempel (Sekunden).
    """
    return int(dt.timestamp())
