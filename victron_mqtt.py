import json
import time
import config
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

def set_max_charge_current(current_a: int):
    if not config.test_mode_on:
        topic = f"W/{config.venus_device_id}/settings/0/Settings/SystemSetup/MaxChargeCurrent"
        payload = json.dumps({"value": int(current_a)})

        try:
            publish.single(topic, payload, hostname=config.venus_host)
            print(f"✅ MaxChargeCurrent via MQTT gesetzt: {current_a}A")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Setzen von MaxChargeCurrent via MQTT: {e}")
            return False
    else:
        print(f"[TESTMODE] MaxChargeCurrent = {current_a}A")
        return True


def get_battery_soc():
    if config.battery_soc_override is not None:
        return int(config.battery_soc_override)

    result = {"value": None}

    def on_message(client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        result["value"] = payload.get("value")

    topic = f"N/{config.venus_device_id}/system/0/Dc/Battery/Soc"
    trigger_topic = f"R/{config.venus_device_id}/system/0/Serial"

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(config.venus_host)
    client.subscribe(topic)
    client.loop_start()

    # Trigger: Leere Nachricht senden, um MQTT-Server aufzuwecken
    try:
        publish.single(trigger_topic, payload=None, hostname=config.venus_host)
    except Exception as e:
        print(f"⚠️ MQTT Trigger fehlgeschlagen: {e}")

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
        print("❌ Kein SOC-Wert über MQTT empfangen.")
        return None
