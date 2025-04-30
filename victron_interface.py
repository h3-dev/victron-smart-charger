import config

if not config.test_mode_on:
    import dbus


def set_max_charge_current(current_a: int):
    if not config.test_mode_on:
        try:
            # Verbindung zum system bus
            bus = dbus.SystemBus()

            # Service und Pfad
            settings_service = "com.victronenergy.settings"
            object_path = "/Settings/SystemSetup/MaxChargeCurrent"
            interface = "com.victronenergy.BusItem"

            # Objekt und Methode holen
            obj = bus.get_object(settings_service, object_path)
            set_value = obj.get_dbus_method("SetValue", interface)

            # Wert setzen
            set_value(dbus.Int32(current_a))

            print(f"✅ DVCC MaxChargeCurrent set to {current_a}A")
            return True

        except Exception as e:
            print(f"❌ Error setting DVCC MaxChargeCurrent: {e}")
            return False
    else:
        print(f"✅ DVCC MaxChargeCurrent set to {current_a}A")
        print("[TESTMODE]")
        return True


def get_battery_soc():

    if config.battery_soc_override is None:
        import dbus

        bus = dbus.SystemBus()
        proxy = bus.get_object("com.victronenergy.system", "/Dc/Battery/Soc")
        interface = dbus.Interface(proxy, "com.victronenergy.BusItem")
        battery_soc = interface.GetValue()
    else:
        battery_soc = config.battery_soc_override
    return int(battery_soc)
