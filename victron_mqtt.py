import json
import time
import config
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


def set_max_charge_current(current_a: int):
    if not config.TEST_MODE_ON:
        topic = f"W/{config.VENUS_DEVICE_ID}/settings/0/Settings/SystemSetup/MaxChargeCurrent"
        payload = json.dumps({"value": int(current_a)})

        try:
            publish.single(topic, payload, hostname=config.VENUS_HOST)
            print(f"✅ Set DVCC MaxChargeCurrent to: {current_a}A")
            return True
        except Exception as e:
            print(f"❌ Error setting MaxChargeCurrent to: {e}")
            return False
    else:
        print(f"[TESTMODE] MaxChargeCurrent = {current_a}A")
        return True


def get_battery_soc():
    if config.BATTERY_SOC_OVERRIDE is not None:
        return int(config.BATTERY_SOC_OVERRIDE)

    result = {"value": None}

    def on_message(client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        result["value"] = payload.get("value")

    topic = f"N/{config.VENUS_DEVICE_ID}/system/0/Dc/Battery/Soc"
    trigger_topic = f"R/{config.VENUS_DEVICE_ID}/system/0/Serial"

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(config.VENUS_HOST)
    client.subscribe(topic)
    client.loop_start()

    # Trigger: Send empty payload to wakeup MQTT Server on Venus
    try:
        publish.single(trigger_topic, payload=None, hostname=config.VENUS_HOST)
    except Exception as e:
        print(f"⚠️ MQTT wakeup trigger failed: {e}")

    timeout = 5
    for _ in range(timeout * 10):
        if result["value"] is not None:
            break
        time.sleep(0.1)

    client.loop_stop()
    client.disconnect()

    if result["value"] is not None:
        return int(result["value"])
    else:
        print("❌ Couldn't fetch MQTT value for battery soc.")
        return None
