"""
Read dat from temperature sensor and save it in Sqlite DB

"""
import time
import busio
import board
import math
import sys
import sqlite3
from adafruit_bme280 import basic as adafruit_bme280

# DB path
dbpath = '/opt/iot/'

# Dew point calculation
def dew_point_calc(temp_c, humi_h) -> float:
    """
    Calculation of dew point using Magnus' equation.
    """
    a = 17.62
    b = 243.12  # °C
    rh = humi_h / 100.0
    # Magnus
    magnus = (a * temp_c) / (b + temp_c) + math.log(rh)
    dewp = (b * magnus) / (a - magnus)
    return round(dewp,2)


try:
    # senzor BME280
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
except Exception as e:
    sys.exit(f"Hw init error: {e}")

# DB open
with sqlite3.connect(dbpath + "sensors.db") as conn:    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        dewpoint REAL
    )
    ''')

# naceteni dat a ulozeni do DB
try:
    temperature = round(sensor.temperature,2)
    humidity = round(sensor.humidity,2)
    pressure = round(sensor.pressure,2)
    dew_point = dew_point_calc(temperature, humidity)
    print(f"Temp:{temperature}°C Humidity:{humidity}% Pressure:{pressure}hPa DewPoint:{dew_point}°C")
  
    conn.execute('''
    INSERT INTO sensor_data (timestamp, temperature, humidity, pressure, dewpoint) VALUES (datetime('now', 'localtime'), ?, ?, ?, ?)
    ''', (temperature, humidity, pressure, dew_point))
    conn.commit()

#osetreni vyjimky
except Exception as e:
    print(f"Error: {e}")

# Close connection with DB
conn.close()
