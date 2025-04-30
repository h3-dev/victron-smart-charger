import math

import config

from victron_interface import get_battery_soc

def calculate_hourly_charging_plan(valid_forecast_future):

    battery_soc_current = get_battery_soc()

    if not valid_forecast_future:
        print("❌ Keine gültige Prognose für Ladeplan.")
        return {}

    # Ladebedarf in kWh berechnen
    energy_needed_kwh = config.battery_capacity_kwh * (config.battery_target_soc - battery_soc_current) / 100
    if energy_needed_kwh <= 0:
        print("🔋 Akku ist bereits ausreichend geladen.")
        return {}

    energy_needed_wh = energy_needed_kwh * 1000

    # Summe der gewichteten Prognose (mit exponentieller Gewichtung)
    weighted_forecasts = [(ts, max(yield_wh - config.household_baseline_watt, 0)) for ts, yield_wh in valid_forecast_future]
    weighted_values = [(ts, val ** config.charging_weight_exponent) for ts, val in weighted_forecasts if val > 0]
    total_weight = sum(val for _, val in weighted_values)

    if total_weight == 0:
        print("❌ Keine nutzbaren PV-Erträge prognostiziert (nach Baseline).")
        return {}

    charging_plan = {}
    soc_projection = []
    soc = battery_soc_current

    print("\n📅 Ladeplan:")
    print("╔════════════════════╦════════════════╦══════════════╗")
    print("║ Uhrzeit            ║ Ladestrom [A]  ║ SoC [%]      ║")
    print("╠════════════════════╬════════════════╬══════════════╣")

    for (ts, forecast_wh), (_, weighted_val) in zip(weighted_forecasts, weighted_values):
        share = weighted_val / total_weight
        energy_to_charge_wh = energy_needed_wh * share
        charging_current_a_raw = energy_to_charge_wh / config.battery_voltage
        charging_current_a = math.ceil(charging_current_a_raw)

        if soc >= config.battery_target_soc:
            charging_current_a = 0
        elif forecast_wh == 0:
            charging_current_a = config.battery_fallback_charge_current

        # Mindest- und Maximalwerte durchsetzen
        if charging_current_a > 0:
            charging_current_a = max(charging_current_a, config.battery_min_charge_current)
        charging_current_a = min(charging_current_a, config.battery_max_charge_current)

        rounded_timestamp = ts.replace(minute=0, second=0, microsecond=0)
        charging_plan[rounded_timestamp] = charging_current_a

        if soc < 100 and charging_current_a > 0:
            energy_added_kwh = (charging_current_a * config.battery_voltage / 1000) * config.battery_charging_efficiency
            soc += (energy_added_kwh / config.battery_capacity_kwh) * 100
            soc = min(soc, 100.0)

        soc_projection.append((rounded_timestamp, soc))
        print(f"║ {rounded_timestamp.strftime('%Y-%m-%d %H:%M')}   ║    {charging_current_a:6.2f} A    ║   {soc:6.1f} %   ║")

    print("╚════════════════════╩════════════════╩══════════════╝\n")
    print("🔋 Current SOC:", get_battery_soc(),"%")
    return charging_plan
