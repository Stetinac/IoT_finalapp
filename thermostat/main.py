import time
import database
import hwhandler

hysteresis = 1  # °C
interval = 2  # interval for Thermostat loop in sec

# startup cfg and recovery from last known heating status
def load_init_cfg() -> None:
    hwhandler.heating(database.ThmLoadCfg()[2])

def thermostat_loop():
    try:
        while True:
            thm_cfg = database.ThmLoadCfg()
            thm_automat = thm_cfg[1]
            heating_on = thm_cfg[2]
            desired_temperature = float(thm_cfg[3])
            current_temp = hwhandler.read_temp()
            if thm_automat:
                if current_temp < desired_temperature - hysteresis and not heating_on:
                    hwhandler.heating(True)
                    database.ThmWriteCfg("heating", 1)

                elif current_temp > desired_temperature + hysteresis and heating_on:
                    hwhandler.heating(False)
                    database.ThmWriteCfg("heating", 0)
            else:
                load_init_cfg()

            time.sleep(interval)
   
    # Exception capturing
    except KeyboardInterrupt:
        print("\nUser terminated by (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")

# Start
if __name__ == "__main__":
    # main loop
    load_init_cfg()
    thermostat_loop()