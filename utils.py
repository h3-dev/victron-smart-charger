from datetime import datetime
import os
import time as sys_time

from config import TIME_OVERRIDE

# Set global timezone to Europe/Berlin
os.environ["TZ"] = "Europe/Berlin"
sys_time.tzset()


def now() -> datetime:
    """
    Return the current time or the override time if specified.
    """
    return TIME_OVERRIDE or datetime.now()


def get_unix_timestamp(dt: datetime) -> int:
    """
    Convert a datetime object to a Unix timestamp (seconds since epoch).
    """
    return int(dt.timestamp())
