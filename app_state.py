from typing import List, Dict, Tuple

latest_forecast: List[Tuple[str, int]] = []
latest_plan: Dict[str, int] = {}
latest_status: Dict[str, int] = {}      # {"soc": 83, "current_a": 12}

def set_forecast(data):
    global latest_forecast
    latest_forecast = data

def set_plan(data):
    global latest_plan
    latest_plan = data

def set_status(data):
    global latest_status
    latest_status = data
