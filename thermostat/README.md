# Thermostat Control System

Automatická regulace teploty s hysterezí - Termostat

---

## 📄 Popis

Tato část prjektu implementuje jednoduchý, ale funkční **termostatický regulátor**.
Systém běží v nekonečné smyčce, načítá konfiguraci z databáze, čte aktuální teplotu z hardware a v automatickém režimu zapíná nebo vypíná topení podle principu hystereze.

Skript je navržen pro provoz na malých systémech (např. Raspberry Pi) s teplotním čidlem bme280 a relé pro ovládání topného okruhu.

---

## 📁 Architektura systému

```
+----------------------+        +-----------------------+
|      database        |        |      hwhandler        |
|----------------------|        |-----------------------|
| ThmLoadCfg()  ----+  |        | read_temp()      ----+ |
| ThmWriteCfg() <---|--+        | heating(status) <---|-+
+----------------------+        +-----------------------+
              ^                               ^
              |                               |
              |                               |
        +---------------------------------------------+
        |                 thermostat.py               |
        |---------------------------------------------|
        | load_init_cfg()                             |
        | thermostat_loop():                          |
        |   - načítá konfiguraci                      |
        |   - zjišťuje režim (auto/manual)            |
        |   - čte aktuální teplotu                    |
        |   - řídí topení (hystereze)                 |
        |---------------------------------------------|
        +---------------------------------------------+
```

---

## 🔧 Konfigurace

| Parametr     | Výchozí hodnota | Popis                                  |
| ------------ | --------------- | -------------------------------------- |
| `hysteresis` | `1`             | velikost hystereze v °C                |
| `interval`   | `2`             | prodleva mezi cykly smyčky v sekundách |

---

## 🔥 Logika regulace (hystereze)

Hystereze zabraňuje rychlému spínání relé v blízkosti cílové teploty.

Příklad:

* `cílová teplota = 22 °C`
* `hystereze = 1 °C`

| Podmínka                    | Akce           |
| --------------------------- | -------------- |
| aktuální teplota **< 21°C** | zapnout topení |
| aktuální teplota **> 23°C** | vypnout topení |

---

## 📌 Popis funkcí

### ### `load_init_cfg()`

Inicializuje systém po startu.
Načte předchozí stav topení z databáze a aplikuje ho přes `hwhandler.heating()`.

---

### `thermostat_loop()`

Hlavní regulační smyčka.
Provádí se v nekonečném cyklu.

Funkce:

* načítá konfiguraci (`automat/manual`, cílová teplota, stav topení)
* čte aktuální teplotu z hardware
* podle režimu a hystereze rozhoduje, zda:

  * zapnout topení
  * vypnout topení
* zapisuje změny zpět do databáze
* čeká definovaný interval

Zachytává chyby: `KeyboardInterrupt` a obecné výjimky.

---
## ▶️ Vytovření Pythno virtual environmentu

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Spuštění programu

Program se spouští standardně: 

```
python main.py
```

Po spuštění:

1. obnoví poslední uložený stav topení,
2. zahájí regulační cyklus.

---

## ▶️ Nastavení automatického spouštění po rebootu

Program se dá automatizovaně spouštět po rebootu a řídit jeho běh prostřednictvím SystemD.
V adresáři os-linux je připravený Systemd Unit soubor, který se nakopíruje do složky /etc/systemd/system

V soboru je nutné upravit/doplnit položky:
    User a Group příslušného uživatele/skupiny, pod kterou bude skript spuštěn a skript spustit
    prislusne adresare, kde je skript na disku ulozen


```
cp os-linux/thermostat.service /etc/systemd/system
systemctl daemon-reload
systemctl start thermostat.service
```