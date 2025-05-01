#!/usr/bin/env python

from utils import now
from forecast import get_forecast
from charging_plan import calculate_hourly_charging_plan
from victron_mqtt import set_max_charge_current

# from victron_interface import set_max_charge_current


def main():
    current_time = now()
    now_hour = current_time.replace(minute=0, second=0, microsecond=0)

    # Prognose abrufen
    valid_forecast_full, valid_forecast_future = get_forecast()
    if valid_forecast_future:
        charging_plan = calculate_hourly_charging_plan(valid_forecast_future)

        # Ladeplan-Abgleich
        charging_current_now = charging_plan.get(now_hour, 0)
        set_max_charge_current(charging_current_now)
    else:
        print("❌ No valid forecast available.")


if __name__ == "__main__":
    main()
