import board
import busio
import time

from adafruit_bme280 import basic as adafruit_bme280
from gpiozero import LED

PIN_HEATER = "GPIO27"

# set heater control
try:
    heater0 = LED(PIN_HEATER)  # output GPIO init
except Exception as e:
    sys.exit(f"Chyba inicializace hardwaru: {e}")

# set temp sensor
try:
    # senzor BME280 I2C
    i2c = busio.I2C(board.SCL, board.SDA)
    i2csensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
except Exception as e:
    sys.exit(f"Chyba inicializace hardwaru: {e}")

def read_temp() -> float:  
    temperature = round(i2csensor.temperature,2)
    # print(f"Temp:{temperature}°C")
    return float(temperature)

def heating(status) -> None:
    if status == True:
        heater0.on()
        print("[THERMOSTAT] heating is set to ON")
    else:
        heater0.off()
        print("[THERMOSTAT] heating is set to OFF")


if __name__ == "__main__":
    # Thread for temp reading
    print("Modul only!")