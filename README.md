# Victron Smart Charger

Prognosis‑based battery charging manager for Victron Venus OS controled by a Multiplus 2.

---

## Prerequisites

Before you start, make sure you have:
* **Docker** So it's not running on venus os..
* **Host/IP of Venus OS**: e.g. `192.168.1.42` or a resolvable hostname.
* **VRM API Token**: Create an API token on your Victron VRM Portal.
* **VRM Installation ID**: Found under your installation settings in VRM.
* **MQTT Broker on Venus OS**: Enable MQTT on your Cerbo/GX device (Settings → Services → MQTT).
* **Active Solar Forecast**: Ensure daily PV forecast is active in the VRM portal for your installation.

You will store these values in a `.env` file for the container.

---

## Environment Variables (`.env`)

Create a file named `.env` alongside your `docker-compose.yml` (or in your working directory for `docker run`) with these keys:

```dotenv
VRM_API_TOKEN=your_vrm_api_token_here
VRM_INSTALLATION_ID=your_installation_id_here
VENUS_HOST=venus_os_hostname_or_ip
VENUS_DEVICE_ID=your_device_mac_or_id
BATTERY_TARGET_SOC=95            # default target state of charge in percent
HOUSEHOLD_BASELINE_WATT=300      # daily household load baseline for net forecast
```

> **Tip:** Do not commit your `.env` into version control.

---

## Deployment

### 1. Single‑container with `docker run`

```bash
docker run -d \
  --name victron-smart-charger \
  --env-file ./.env:ro \
  -p 8000:8000 \
  ghcr.io/your_org/victron-smart-charger:latest
```

This will:

* Mount your `.env` file (read‑only).
* Expose the API & UI on `http://localhost:8000`.

### 2. Multi‑container with `docker-compose`

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  victron-charger:
    image: ghcr.io/your_org/victron-smart-charger:latest
    container_name: victron-smart-charger
    env_file:
      - ./.env
    ports:
      - 8000:8000
    restart: unless-stopped
```

Then start it:

```bash
docker-compose up -d
```

---

## Access

* **Web UI & API Docs**: `http://<host>:8000`
* **OpenAPI (Swagger)**: `http://<host>:8000/api/docs`

---

## Test Mode

You can run the app in **test mode** to simulate forecasts and battery state:

1. Set the `TEST_MODE_ON` flag in your `.env`:

   ```dotenv
   TEST_MODE_ON=true
   ```
2. Override values as needed:

   * **`FORECAST_OVERRIDE_JSON`**: Provide a JSON array of `[timestamp,wh]` pairs for PV forecast.

     ```dotenv
     FORECAST_OVERRIDE_JSON='[["2025-04-22 06:00",1500],["2025-04-22 07:00",3000],...]'
     ```
   * **`BATTERY_SOC_OVERRIDE`**: Set an initial SOC (%) to use instead of the real battery.

     ```dotenv
     BATTERY_SOC_OVERRIDE=30
     ```
   * **`TIME_OVERRIDE`**: Force the current time via ISO timestamp.

     ```dotenv
     TIME_OVERRIDE=2025-04-22T07:00:00
     ```
3. Restart the container; the UI and plan will use your override data.

