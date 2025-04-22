import math

import config

from victron_interface import get_battery_soc


def calculate_hourly_charging_plan(valid_forecast_future):
    battery_soc_current = get_battery_soc()

    if not valid_forecast_future:
        print("❌ Keine gültige Prognose für Ladeplan.")
        return {}

    # Ladebedarf in kWh berechnen
    energy_needed_kwh = (
        config.battery_capacity_kwh
        * (config.battery_target_soc - battery_soc_current)
        / 100
    )
    if energy_needed_kwh <= 0:
        print("🔋 Akku ist bereits ausreichend geladen.")
        return {}

    energy_needed_wh = energy_needed_kwh * 1000
    total_forecast_wh = sum([row[1] for row in valid_forecast_future])
    if total_forecast_wh == 0:
        print("❌ Keine PV-Erträge prognostiziert.")
        return {}

    charging_plan = {}
    soc = battery_soc_current

    print("\n📅 Ladeplan:")
    print("╔════════════════════╦════════════════╦══════════════╗")
    print("║ Uhrzeit            ║ Ladestrom [A]  ║ SoC [%]      ║")
    print("╠════════════════════╬════════════════╬══════════════╣")

    for timestamp, forecast_wh in valid_forecast_future:
        # Berechne den Ladestrom basierend auf dem prognostizierten PV-Ertrag
        if forecast_wh == 0:
            charging_current_a = config.battery_fallback_charge_current
        else:
            # Haushaltsverbrauch abziehen
            available_wh = max(forecast_wh - config.household_baseline_watt, 0)
            share = available_wh / total_forecast_wh
            energy_to_charge_wh = energy_needed_wh * share
            charging_current_a_raw = energy_to_charge_wh / config.battery_voltage

            # Ladecurrent aufrunden und begrenzen
            charging_current_a = math.ceil(charging_current_a_raw)
            charging_current_a = min(
                charging_current_a, config.battery_max_charge_current
            )

        # Mindeststrom durchsetzen, falls > 0
        if charging_current_a > 0:
            charging_current_a = max(
                charging_current_a, config.battery_min_charge_current
            )

        # Berechne den SoC nach dieser Stunde
        if soc < 100 and charging_current_a > 0:
            energy_added_kwh = (
                charging_current_a * config.battery_voltage / 1000
            ) * config.battery_charging_efficiency
            soc += (energy_added_kwh / config.battery_capacity_kwh) * 100
            soc = min(soc, 100.0)

        charging_plan[timestamp] = charging_current_a

        # Zeige den Ladeplan mit dem SoC zum Ende der Stunde an
        print(
            f"║ {timestamp.strftime('%Y-%m-%d %H:%M')}   ║    {charging_current_a:6.2f} A    ║   {soc:6.1f} %   ║"
        )

    print("╚════════════════════╩════════════════╩══════════════╝\n")
    print("Current SOC:", get_battery_soc(), "%")
    return charging_plan
