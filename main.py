from utils import now
from forecast import get_forecast
from charging_plan import calculate_hourly_charging_plan
from victron_mqtt import set_max_charge_current, get_battery_soc
import app_state
import config

TARGET_SOC = config.BATTERY_TARGET_SOC

def main():
    current_time = now()
    now_hour = current_time.replace(minute=0, second=0, microsecond=0)

    # 1) Forecast holen
    valid_forecast_full, valid_forecast_future = get_forecast()
    if not valid_forecast_future:
        print("❌ No valid forecast available.")
        return

    charging_plan = calculate_hourly_charging_plan(valid_forecast_future)

    charging_current_now = charging_plan.get(now_hour, 0)
    set_max_charge_current(charging_current_now)

    status = {
        "current_soc": get_battery_soc(),
        "current_a": charging_current_now,
        "target_soc": config.BATTERY_TARGET_SOC,
    }

    app_state.set_forecast(valid_forecast_full)
    app_state.set_plan(charging_plan)
    app_state.set_status(status)


if __name__ == "__main__":
    main()
