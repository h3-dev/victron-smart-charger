# Victron Smart Charger

Forecast-driven battery-charging daemon for Victron Venus OS systems
(or any Victron installation that exposes MQTT).

The service fetches the hourly PV forecast from the Victron VRM API, subtracts a
configurable household baseline, and distributes the required energy so the
battery reaches the target SOC shortly before PV production ends.
`MaxChargeCurrent` is set via MQTT, so the code can run **off-device** (Docker,
Raspberry Pi, Home Server) or directly on a Venus GX with runit.

---

## Features

* **VRM PV forecast** (hourly) or JSON override for replay testing
* **Largest-remainder rounding** ⇒ integer amps, ≤ 52 Wh deviation from target
* Efficiency correction and min/max current limits
* Clean `.env`-based configuration (no code edits)
* Test mode: time freeze, SOC override, forecast override
* Runs as
  * Docker container (preferred for off-device use)
  * runit service on Venus OS

---

## Quick Start — Docker

```bash
# build
docker build -t victron-charger .

# run (auto-remove on stop, mount .env read-only)
docker run --rm -d \
  --name victron-charger \
  -v "$(pwd)/.env":/home/app/.env:ro \
  victron-charger

# local running without docker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt     # only 3 runtime deps
python main_loop.py