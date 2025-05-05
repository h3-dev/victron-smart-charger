from typing import List, Dict, Tuple
import config

latest_solar_forecast: List[Tuple[str, int]] = []
latest_consumption_forecast: List[Tuple[str, int]] = []
latest_plan: Dict[str, int] = {}
latest_status: Dict[str, int] = {}  # {"soc": 83, "current_a": 12}

latest_target_soc: int = config.BATTERY_TARGET_SOC


def set_solar_forecast(data):
    global latest_solar_forecast
    latest_solar_forecast = data

def set_consumption_forecast(data):
    global latest_consumption_forecast
    latest_consumption_forecast = data

def set_plan(data):
    global latest_plan
    latest_plan = data


def set_status(data):
    global latest_status
    latest_status = data


def set_target_soc(value: int):
    global latest_target_soc
    latest_target_soc = value
