import time
import busio
import board
from adafruit_bme280 import basic as adafruit_bme280

# komunikace se senzorem
try:
    # senzor BME280 pripojeny na SDA a SCL
    i2c = busio.I2C(board.SCL, board.SDA)
    i2csensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
except Exception as e:
    sys.exit(f"Chyba inicializace hardwaru: {e}")

def read_temp() -> None:  
    try:
        global current_temp
        while True:
            temperature = round(i2csensor.temperature,2)
            humidity = round(i2csensor.humidity,2)
            pressure = round(i2csensor.pressure,2)
            current_temp = float(temperature)
            print(f"Temp:{temperature}°C Humidity:{humidity}% Pressure:{pressure}hPa")

            time.sleep(10)
    except KeyboardInterrupt:
        print("\nUkončeno uživatelem (Ctrl+C)")

    except Exception as e:
        print(f"Jiná neočekávaná chyba: {e}")