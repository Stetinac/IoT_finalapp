# Thermostat Control System

Automatická regulace teploty s hysterezí - Termostat

---

## 📄 Popis
Tento Python skript slouží k:

* načtení dat ze senzoru **BME280** (teplota, vlhkost, tlak),
* výpočtu **rosného bodu** pomocí Magnusovy rovnice,
* uložení naměřených hodnot do **SQLite databáze** (`sensors.db`),
* automatickému vytvoření databázové tabulky při prvním spuštění.

Skript je určen pro zařízení typu **Raspberry Pi** nebo jiné platformy podporující I2C sběrnici a Adafruit BME280 knihovny.

---

## 📁 Architektura systému

```
+------------------------------+
|         BME280 Sensor        |
|             (I2C)            |
+---------------+--------------+
                |
                v
+-----------------------------------+
|     Python Script                 |
|-----------------------------------|
| - inicializace I2C                |
| - čtení teploty, vlhkosti, tlaku |
| - výpočet rosného bodu           |
| - ukládání do SQLite             |
+----------------+------------------+
                 |
                 v
+-------------------------------------------+
|           SQLite Database                 |
|               sensors.db                  |
|-------------------------------------------|
|  TABLE sensor_data:                       |
|  - id (PK)                                |
|  - timestamp                              |
|  - temperature                            |
|  - humidity                               |
|  - pressure                               |
|  - dewpoint                               |
+-------------------------------------------+
```

---

## 🌡️ Výpočet rosného bodu

Použita je **Magnusova rovnice**, osvědčená metoda pro výpočet rosného bodu:

```
a = 17.62
b = 243.12 °C

magnus = (a * temp) / (b + temp) + ln(RH)
dewpoint = (b * magnus) / (a - magnus)
```
Výsledek se zaokrouhluje na **2 desetinná místa**.

---

## 🧪 Ukázkový výstup dat

```
Temp:22.31°C Humidity:45.2% Pressure:1013.58hPa DewPoint:9.87°C
```

## Automatizované ukládní dat ze senzoru bme280 do DB
- Úprava Bash skriptu ve složce s projektem
```
nano data-logger.sh
```

- Doplnění příslušných cest data-logger.sh
```
#!/bin/bash
cd <uplna cesta k souboru>
source .env/bin/activate
python zapis_dat.py
```

- Nastavení oprávnění pro spouštění skriptu:
```
chmode +x data-logger.sh
```

### Kontrola správného fungování skriptu
- Spuštěním `python zapis_dat.py` by mělo dojít k vypsání aktuálních naměřených
hodnot ze senzoru do konzole a vytvoření souboru sensors.db obshaující zopbrazená data.
    
- Spuštěním `./data-logger.sh` by mělo opět dojít k aktualizaci DB o získané hodnoty z čidla, doplněné o vypočítané hodnoty.

### Nastavení Cronu pro opakované spouštění data-loggeru po 1 minutě
Spuštěním `crontab -e` a vložením níže uvedeného řádku doplněného o cestu k souboru se data-logger.sh
```
* * * * * /<uplna cesta k souboru>/data-logger.sh
```
### Kontrola fungování pravidleně spouštěné úlohy
- Spuštěním níže uvedeného příkazu po několika minutách provozu by mělo dojít k vypsání osbahu DB,
který by měl obsahovat jednotlivá získaná data, včetně tiemstampu doby získání dat:
```    
sqlite3 data.db "SELECT * FROM sensor_data;"
```