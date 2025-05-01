"""
config.py – central configuration & override values
Best practice:
- All settings start with **defaults** in this file.
- If a `.env` file is present, keys defined there override these
  defaults (via `python-dotenv`).
- All public constants follow PEP 8’s UPPER_SNAKE_CASE style.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from dotenv import load_dotenv

# ------------------------------------------------------------------
# 1)  Load .env silently if present
# ------------------------------------------------------------------
load_dotenv()  # automatically looks for .env in the working directory


def _get_bool(env_key: str, default: bool = False) -> bool:
    """Return a boolean from .env (true/1/on/yes)."""
    val = os.getenv(env_key)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


# ------------------------------------------------------------------
# 2)  System / API
# ------------------------------------------------------------------
VRM_API_TOKEN: str = os.getenv("VRM_API_TOKEN", "")
VRM_INSTALLATION_ID: str = os.getenv("VRM_INSTALLATION_ID", "")
VENUS_HOST: str = os.getenv("VENUS_HOST", "")
VENUS_DEVICE_ID: str = os.getenv("VENUS_DEVICE_ID", "")
APP_REFRESH_INTERVAL_SEC: int = int(os.getenv("APP_REFRESH_INTERVAL_SEC", 900))

# ------------------------------------------------------------------
# 3)  Battery parameters
# ------------------------------------------------------------------
BATTERY_TARGET_SOC: int = int(os.getenv("BATTERY_TARGET_SOC", 95))
BATTERY_CAPACITY_KWH: float = float(os.getenv("BATTERY_CAPACITY_KWH", 16))
BATTERY_VOLTAGE: int = int(os.getenv("BATTERY_VOLTAGE", 52))
BATTERY_CHARGING_EFFICIENCY: float = float(
    os.getenv("BATTERY_CHARGING_EFFICIENCY", 0.90)
)
BATTERY_MIN_CHARGE_CURRENT: int = int(os.getenv("BATTERY_MIN_CHARGE_CURRENT", 1))
BATTERY_MAX_CHARGE_CURRENT: int = int(os.getenv("BATTERY_MAX_CHARGE_CURRENT", 80))
BATTERY_FALLBACK_CHARGE_CURRENT: int = int(
    os.getenv("BATTERY_FALLBACK_CHARGE_CURRENT", 80)
)

# ------------------------------------------------------------------
# 4)  Forecast / control
# ------------------------------------------------------------------
FORECAST_START_OFFSET_H: int = int(os.getenv("FORECAST_START_OFFSET_H", 0))
FORECAST_END_OFFSET_H: int = int(os.getenv("FORECAST_END_OFFSET_H", 0))
HOUSEHOLD_BASELINE_WATT: int = int(os.getenv("HOUSEHOLD_BASELINE_WATT", 300))

# ------------------------------------------------------------------
# 5)  Debug / test mode
# ------------------------------------------------------------------
TEST_MODE_ON: bool = _get_bool("TEST_MODE_ON", False)
OUTPUT_FORECAST: bool = _get_bool("OUTPUT_FORECAST", True)

# a) optional battery-SOC override
_batt_soc_override = os.getenv("BATTERY_SOC_OVERRIDE")
if _batt_soc_override:
    BATTERY_SOC_OVERRIDE = int(_batt_soc_override)
else:
    BATTERY_SOC_OVERRIDE = None

# b) optional timestamp override (e.g. for replay tests)
_time_override = os.getenv("TIME_OVERRIDE")
TIME_OVERRIDE: datetime | None = (
    datetime.fromisoformat(_time_override) if _time_override else None
)

# c) optional forecast override (JSON string in .env)
_forecast_json: str | None = os.getenv("FORECAST_OVERRIDE_JSON")
FORECAST_OVERRIDE_DATA: list[list] | None = (
    json.loads(_forecast_json) if _forecast_json else None
)

# ------------------------------------------------------------------
# 6)  Sanity checks & hints
# ------------------------------------------------------------------
if TEST_MODE_ON:
    print("⚠️  TEST_MODE_ON is enabled – overrides are active.")
    if BATTERY_SOC_OVERRIDE is None:
        print("   (No BATTERY_SOC_OVERRIDE set – live SOC will be used)")
    if FORECAST_OVERRIDE_DATA is None:
        print("   (No FORECAST_OVERRIDE_JSON set – real forecast will be used)")
