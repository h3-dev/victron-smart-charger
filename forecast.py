import requests
from datetime import datetime, time as dtime
import config
from utils import (
    get_unix_timestamp,
    now,
)


def get_forecast():
    """Return today’s PV yield forecast – either from VRM API or from override data."""

    current_time = now()
    now_hour = current_time.replace(minute=0, second=0, microsecond=0)

    # ==========================================================
    # 🧪 Test mode: use forecast override from .env / config.py
    # ==========================================================
    if config.TEST_MODE_ON and config.FORECAST_OVERRIDE_DATA:
        print("⚠️  Using forecast override from config.py")
        valid_forecast_full = []
        valid_forecast_future = []
        total_forecast = 0

        for time_str, yield_wh in config.FORECAST_OVERRIDE_DATA:
            ts = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            valid_forecast_full.append((ts, yield_wh))
            total_forecast += yield_wh
            if ts >= now_hour:
                valid_forecast_future.append((ts, yield_wh))

        if config.OUTPUT_FORECAST:
            print("🔆 (Test) PV forecast (Wh):")
            for ts, val in valid_forecast_future:
                print(f"{ts.strftime('%Y-%m-%d %H:%M')}: {val:.0f} Wh")
            print(f"\n📊 (Test) Total solar yield: {total_forecast / 1000:.2f} kWh")

        return valid_forecast_full, valid_forecast_future

    # ==========================================================
    # 🌤 Live mode: fetch forecast from VRM API
    # ==========================================================
    start_date = datetime.combine(current_time.date(), dtime.min)
    end_date = datetime.combine(current_time.date(), dtime.max)
    start_ts = get_unix_timestamp(start_date)
    end_ts = get_unix_timestamp(end_date)

    url = (
        f"https://vrmapi.victronenergy.com/v2/installations/"
        f"{config.VRM_INSTALLATION_ID}/stats"
        f"?type=forecast&interval=hours&start={start_ts}&end={end_ts}"
    )

    headers = {
        "content-type": "application/json",
        "x-authorization": f"Token {config.VRM_API_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Error fetching data:", response.status_code, response.text)
        return None, None

    try:
        data = response.json()
        forecast_data = data["records"]["solar_yield_forecast"]

        valid_forecast_full = []
        valid_forecast_future = []
        total_forecast = 0

        for row in forecast_data:
            timestamp = datetime.fromtimestamp(row[0] / 1000)
            yield_wh = row[1]

            if yield_wh > 0 and timestamp.date() == current_time.date():
                valid_forecast_full.append((timestamp, yield_wh))
                total_forecast += yield_wh
                if timestamp >= now_hour:
                    valid_forecast_future.append((timestamp, yield_wh))

        if config.OUTPUT_FORECAST:
            print("🔆 PV forecast (upcoming hours, Wh):")
            for timestamp, yield_wh in valid_forecast_future:
                print(f"{timestamp.strftime('%Y-%m-%d %H:%M')}: {yield_wh:.0f} Wh")
            print(f"\n📊 Total solar daily yield: {total_forecast / 1000:.2f} kWh")

        if not valid_forecast_full:
            print("❌ No valid forecasts for today.")

        return valid_forecast_full, valid_forecast_future

    except Exception as e:
        print("❌ Error processing API response:", e)
        return None, None
