from utils import now
from forecast import get_solar_forecast, get_consumption_forecast
from charging_plan import calculate_hourly_charging_plan
from victron_mqtt import set_max_charge_current, get_battery_soc, get_battery_voltage
import app_state
import config

TARGET_SOC = config.BATTERY_TARGET_SOC


def main():
    current_time = now()
    now_hour = current_time.replace(minute=0, second=0, microsecond=0)

    valid_solar_forecast_full, valid_solar_forecast_future = get_solar_forecast()
    if not valid_solar_forecast_future:
        print("❌ No valid solar forecast available.")

    valid_consumption_forecast_full, valid_consumption_forecast_future = get_consumption_forecast()
    if not valid_solar_forecast_future:
        print("❌ No valid consumption forecast available.")

    charging_plan = calculate_hourly_charging_plan(valid_solar_forecast_future)

    charging_current_now = charging_plan.get(now_hour, 0)
    set_max_charge_current(charging_current_now)

    status = {
        "current_soc": get_battery_soc(),
        "current_v": get_battery_voltage(),
        "current_a": charging_current_now,
        "target_soc": config.BATTERY_TARGET_SOC,
    }

    app_state.set_solar_forecast(valid_solar_forecast_full)
    app_state.set_consumption_forecast(valid_consumption_forecast_full)
    app_state.set_plan(charging_plan)
    app_state.set_status(status)


if __name__ == "__main__":
    main()
