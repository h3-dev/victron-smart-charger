from datetime import timedelta
from config import forecast_start_offset_hours, forecast_end_offset_hours
from utils import now


def calculate_charge_control_flag(forecast_data, current_time=None):
    """
    Berechnet, ob sich die aktuelle Zeit innerhalb des Steuerfensters befindet,
    das auf der Solarprognose basiert (inkl. konfigurierbarer Offsets).
    """
    global daily_control_window

    charge_control_active = False
    control_start_time = None
    control_end_time = None

    if current_time is None:
        current_time = now()

    # Filtere Stunden mit positiver Prognose
    positive_forecasts = [row for row in forecast_data if row[1] > 0]
    if not positive_forecasts:
        return charge_control_active, None, None

    first_production = positive_forecasts[0][0]
    last_production = positive_forecasts[-1][0]

    # Offset anwenden
    control_start_time = first_production + timedelta(hours=forecast_start_offset_hours)
    control_end_time = last_production + timedelta(hours=forecast_end_offset_hours)

    # Prüfen, ob wir uns im aktiven Fenster befinden
    if control_start_time <= current_time <= control_end_time:
        charge_control_active = True

    return charge_control_active, control_start_time, control_end_time
