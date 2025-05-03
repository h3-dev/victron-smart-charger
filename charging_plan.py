import config
from victron_mqtt import get_battery_soc
from math import floor
from app_state import latest_target_soc

def calculate_hourly_charging_plan(valid_forecast_future):
    """Return an hourly charging plan (integer amps, max deviation < 1 A·V)."""

    batt_soc_now = get_battery_soc()

    if not valid_forecast_future:
        print("❌ No valid forecast available.")
        return {}

    # -------------------------------------------------------------
    # 1. Required DC energy (Wh) to reach target SOC
    # -------------------------------------------------------------
    need_kwh = (
        config.BATTERY_CAPACITY_KWH * (latest_target_soc - batt_soc_now) / 100
    )
    if need_kwh <= 0:
        print("🔋 Battery already sufficiently charged.")
        return {}

    need_wh_dc = need_kwh * 1000 / config.BATTERY_CHARGING_EFFICIENCY
    V = config.BATTERY_VOLTAGE

    # -------------------------------------------------------------
    # 2. Net forecast (PV minus baseline consumption)
    # -------------------------------------------------------------
    net = [
        (ts, max(y - config.HOUSEHOLD_BASELINE_WATT, 0))
        for ts, y in valid_forecast_future
    ]
    total_net_wh = sum(w for _, w in net)
    if total_net_wh == 0:
        print("❌ No usable PV generation forecast.")
        return {}

    # -------------------------------------------------------------
    # 3. Raw currents, floor, fractional parts
    # -------------------------------------------------------------
    rows = []
    for ts, wh in net:
        share = wh / total_net_wh
        energy_h = need_wh_dc * share  # Wh for this hour
        raw_a = energy_h / V  # A before rounding

        # Apply min/max limits
        if raw_a > 0:
            raw_a = max(raw_a, config.BATTERY_MIN_CHARGE_CURRENT)
        raw_a = min(raw_a, config.BATTERY_MAX_CHARGE_CURRENT)

        floor_a = int(floor(raw_a))
        fraction = raw_a - floor_a
        rows.append(
            {
                "ts": ts.replace(minute=0, second=0, microsecond=0),
                "floor": floor_a,
                "frac": fraction,
            }
        )

    # -------------------------------------------------------------
    # 4. Energy balance after flooring
    # -------------------------------------------------------------
    supplied_wh = sum(r["floor"] * V for r in rows)
    delta_wh = need_wh_dc - supplied_wh  # positive → missing, negative → surplus

    # -------------------------------------------------------------
    # 5. Largest-remainder adjustment (+1 A or –1 A steps)
    # -------------------------------------------------------------
    if abs(delta_wh) >= V:  # at least 1 A deviation
        rows_sorted = sorted(rows, key=lambda r: r["frac"], reverse=(delta_wh > 0))

        step = V if delta_wh > 0 else -V
        idx = 0
        while abs(delta_wh) >= V and idx < len(rows_sorted):
            r = rows_sorted[idx]
            within_limits = (
                delta_wh > 0 and r["floor"] < config.BATTERY_MAX_CHARGE_CURRENT
            ) or (delta_wh < 0 and r["floor"] > config.BATTERY_MIN_CHARGE_CURRENT)
            if within_limits and r["floor"] > 0:
                r["floor"] += 1 if delta_wh > 0 else -1
                delta_wh -= step
            idx += 1

    # -------------------------------------------------------------
    # 6. Assemble result & SOC projection
    # -------------------------------------------------------------
    rows.sort(key=lambda r: r["ts"])  # chronological order
    charging_plan = {}
    soc = batt_soc_now

    if soc + 0.2 < latest_target_soc:
        print(f"⚠️  Target SOC {latest_target_soc}% likely not reached.")

    return charging_plan
