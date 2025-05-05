import requests
from datetime import datetime, time as dtime
import config
from utils import (
    get_unix_timestamp,
    now,
)

def get_solar_forecast():
    """
    Return today’s PV yield forecast (Wh/h) – either from VRM API or from override data.
    """
    current_time = now()
    now_hour = current_time.replace(minute=0, second=0, microsecond=0)

    # Test mode: use forecast override
    if config.TEST_MODE_ON and config.FORECAST_OVERRIDE_DATA:
        print("⚠️  Using solar forecast override from config.py")
        full = []
        future = []
        total = 0
        for time_str, yield_wh in config.FORECAST_OVERRIDE_DATA:
            ts = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            full.append((ts, yield_wh))
            total += yield_wh
            if ts >= now_hour:
                future.append((ts, yield_wh))
        if config.OUTPUT_FORECAST:
            print("🔆 (Test) PV forecast (Wh):")
            for ts, val in future:
                print(f"{ts.strftime('%Y-%m-%d %H:%M')}: {val:.0f} Wh")
            print(f"\n📊 Total solar yield: {total/1000:.2f} kWh")
        return full, future

    # Live mode: fetch from VRM API
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
        print("❌ Error fetching solar forecast:", response.status_code, response.text)
        return None, None

    try:
        data = response.json()
        records = data["records"].get("solar_yield_forecast", [])
        full = []
        future = []
        total = 0
        for ts_ms, yield_wh in records:
            ts = datetime.fromtimestamp(ts_ms / 1000)
            if ts.date() == current_time.date():
                full.append((ts, yield_wh))
                total += yield_wh
                if ts >= now_hour:
                    future.append((ts, yield_wh))
        if config.OUTPUT_FORECAST:
            print("🔆 PV forecast (upcoming hours, Wh):")
            for ts, val in future:
                print(f"{ts.strftime('%Y-%m-%d %H:%M')}: {val:.0f} Wh")
            print(f"\n📊 Total solar yield: {total/1000:.2f} kWh")
        return full, future

    except Exception as e:
        print("❌ Error processing solar forecast response:", e)
        return None, None


def get_consumption_forecast():
    """
    Return today’s consumption forecast (Wh/h) from VRM API.
    """
    current_time = now()
    now_hour = current_time.replace(minute=0, second=0, microsecond=0)

    # Live mode: fetch from VRM API
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
    print("response:",response)
    if response.status_code != 200:
        print("❌ Error fetching consumption forecast:", response.status_code, response.text)
        return None, None

    try:
        data = response.json()
        records = data["records"].get("vrm_consumption_fc", [])
        full = []
        future = []
        total = 0
        for ts_ms, cons_wh in records:
            ts = datetime.fromtimestamp(ts_ms / 1000)
            if ts.date() == current_time.date():
                full.append((ts, cons_wh))
                total += cons_wh
                if ts >= now_hour:
                    future.append((ts, cons_wh))
        print("🔆 Consumption forecast (upcoming hours, Wh):")
        for ts, val in future:
            print(f"{ts.strftime('%Y-%m-%d %H:%M')}: {val:.0f} Wh")
        print(f"\n📊 Total consumption: {total/1000:.2f} kWh")
        return full, future

    except Exception as e:
        print("❌ Error processing consumption forecast response:", e)
        return None, None
