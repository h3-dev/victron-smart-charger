import config
from victron_mqtt import get_battery_soc
from math import floor
from app_state import latest_target_soc
from forecast import get_consumption_forecast
from utils import now

def calculate_hourly_charging_plan(valid_forecast_future):
    """
    Return an hourly charging plan (integer amps, max deviation < 1 A·V),
    computing net solar energy minus forecasted consumption per hour.
    """
    batt_soc_now = get_battery_soc()
    if not valid_forecast_future:
        print("❌ No valid solar forecast available.")
        return {}

    # fetch consumption forecast for today
    _, consumption_future = get_consumption_forecast()
    cons_map = {ts: wh for ts, wh in consumption_future}

    # -------------------------------------------------------------
    # 1. Required DC energy (Wh) to reach target SOC
    # -------------------------------------------------------------
    need_kwh = config.BATTERY_CAPACITY_KWH * (latest_target_soc - batt_soc_now) / 100
    if need_kwh <= 0:
        print("🔋 Battery already sufficiently charged or at target SOC.")
        return {}
    need_wh_dc = need_kwh * 1000 / config.BATTERY_CHARGING_EFFICIENCY
    V = config.BATTERY_VOLTAGE

    # -------------------------------------------------------------
    # 2. Net forecast (PV minus consumption forecast)
    # -------------------------------------------------------------
    net = []
    for ts, solar_wh in valid_forecast_future:
        cons_wh = cons_map.get(ts, 0)
        net_wh = max(solar_wh - cons_wh, 0)
        net.append((ts, net_wh))
    total_net_wh = sum(w for _, w in net)
    if total_net_wh == 0:
        print("❌ No net energy available after consumption forecast.")
        return {}

    # -------------------------------------------------------------
    # 3. Raw currents, floor, fractional parts
    # -------------------------------------------------------------
    rows = []
    for ts, net_wh in net:
        share = net_wh / total_net_wh
        energy_h = need_wh_dc * share  # Wh for this hour
        raw_a = energy_h / V
        if raw_a > 0:
            raw_a = max(raw_a, config.BATTERY_MIN_CHARGE_CURRENT)
        raw_a = min(raw_a, config.BATTERY_MAX_CHARGE_CURRENT)
        floor_a = int(floor(raw_a))
        frac = raw_a - floor_a
        rows.append({"ts": ts.replace(minute=0, second=0, microsecond=0),
                     "floor": floor_a, "frac": frac})

    # -------------------------------------------------------------
    # 4. Energy balance after flooring
    # -------------------------------------------------------------
    step_wh = V
    supplied_wh = sum(r["floor"] * V for r in rows)
    delta_wh = need_wh_dc - supplied_wh
    if abs(delta_wh) >= step_wh:
        # largest remainder method
        rows_sorted = sorted(rows, key=lambda r: r["frac"], reverse=(delta_wh > 0))
        idx = 0
        while abs(delta_wh) >= step_wh and idx < len(rows_sorted):
            r = rows_sorted[idx]
            if (delta_wh > 0 and r["floor"] < config.BATTERY_MAX_CHARGE_CURRENT) or \
               (delta_wh < 0 and r["floor"] > config.BATTERY_MIN_CHARGE_CURRENT):
                r["floor"] += 1 if delta_wh > 0 else -1
                delta_wh -= step_wh
            idx += 1

    # -------------------------------------------------------------
    # 5. Assemble result & SOC projection
    # -------------------------------------------------------------
    rows.sort(key=lambda r: r["ts"])
    # filter past
    current_hour = now().replace(minute=0, second=0, microsecond=0)
    rows = [r for r in rows if r["ts"] >= current_hour]

    charging_plan = {}
    soc = batt_soc_now
    print("\n📅 Charging plan:")
    for r in rows:
        ts, amp = r["ts"], r["floor"]
        charging_plan[ts] = amp
        if amp > 0 and soc < 100:
            added = (amp * V / 1000) * config.BATTERY_CHARGING_EFFICIENCY
            soc += (added / config.BATTERY_CAPACITY_KWH) * 100
            soc = min(soc, 100)
        print(f"║ {ts.strftime('%Y-%m-%d %H:%M')}   ║ {amp:5d} A   ║ {soc:5.1f} % ║")
    print("╚═══════╩═════════╩════════╩")
    print(f"🔋 Start SOC: {batt_soc_now}%  –  Target SOC: {latest_target_soc}%")
    if soc + 0.2 < latest_target_soc:
        print(f"⚠️  Target SOC {latest_target_soc}% likely not reached.")
    return charging_plan
