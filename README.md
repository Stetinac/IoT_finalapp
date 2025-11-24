```markdown
# 🏠 Domácí Termostat - finální úloha

---

## 📌 Popis

Projekt implementuje **domácí termostat** pro Raspberry Pi4.  

Poskytuje:
- Měření teploty, vlhkosti a tlaku pomocí senzoru (např. BME280)
- Výpočet teploty rosného bodu na zákaldě naměřených hodnot ze senzoru
- Řízení topného okruhu přes relé  
- Záznam naměřených dat a jejich ukládání do SQLite databáze  
- Automatické řízení topení na základě nastavené cílové teploty a hysterese
- Webový frontend pro zobrazení aktuálních hodnot a historii s možností ovládání termostatu

---

## 🏗 Architektura

Projekt je rozdělen do tří hlavních modulů:

1. **Data Logger** – snímá data ze senzoru a ukládá je do SQLite DB.  
2. **Thermostat** – řídí topení, vyhodnocuje cílovou teplotu a hysteresi, zapisuje stav do DB.  
3. **Frontend** – Flask aplikace, poskytuje webové rozhraní a REST API pro zobrazení dat a ovládání termostatu.  

- Data jsou ukládána do **SQLite DB**, která slouží jako propojení mezi **Data Loggerem**, **Thermostatem** a **Frontendem**.  
- Webové rozhraní umožňuje zobrazit aktuální a historické hodnoty, nastavit cílovou teplotu a přepínače pro automatický / manuální režim.

---

### 📦 ASCII Architektura
```
          ┌─────────────────────┐
          │    Raspberry Pi 4   │
          │     Debian OS       │
          └─────────┬──────────┘
                    │
        ┌───────────┴───────────┐
        │       SQLite DB       │
        └─────────┬─────────────┘
         ┌────────┴───────────┐
         │                    │
┌────────┴───────┐   ┌────────┴─────────┐
│ Data Logger    │   │ Thermostat       │
│ (sensor → DB)  │   │ (DB → relé)      │
└────────┬───────┘   └────────┬─────────┘
         │                    │
         └────────────┬───────┘
                      │
                ┌─────┴─────┐
                │ Frontend  │
                │ (Flask)   │
                └───────────┘
```

---

## 📁 Struktura projektu

```

├── data_logger/           # Modul pro snímání dat ze senzoru
│   ├── zapis_dat.py       # Hlavní skript pro čtení a zápis do DB
│   └── data-logger.sh     # Bash script spoutěný Cronem
│
├── thermostat/            # Modul pro automatické řízení topení
│   ├── main.py            # Hlavní skript pro řízení topení
│   ├── database.py        # Modul obsluhující DB
│   ├── hwhandler.py       # Modul obsluhující HW GPIO
│   └── sensors.py         # Modul pro vyčítání teploty z cidla
│
└── frontend/              # Webový modul
    ├── app.py             # Flask aplikace
    ├── database.py        # Modul obsluhující DB
    ├── meteoapi.py        # Modul pro komunikaci s API OpenMeteo    
    ├── meteoapi.py        # Modul pro Gunicorn
    ├── templates/         # HTML šablony
    └── static/            # CSS, JS, obrázky
```

---

## ⚙️ Popis požadavků na systém

- **Hardware**: Raspberry Pi 4  
- **OS**: Debian (Raspberry Pi OS)  
- **Senzor**: Teplotní, vlhkostní a tlakový senzor (např. BME280)  
- **Výstup**: Relé pro ovládání topného okruhu  
- **Software**: Python 3, Flask, SQLite3  
- **Internet**: Publikace frontendu, veřejné Meteo API 
- **Pevná IP adresa**: Publikace dat, generování Let's Encrypt certifikátu

---

## 🚀 Další potencionální rozšíření a optimalizace:

- Doplnění modulu pro komunikaci prostřednictvím MQTT
- Doplnění dalšího logování pro případý debug problémů
- Mobilní aplikace v Python Flet
- Doplnění dalších senzorů a ukládání dat do DB
- Doplnění dalších historických grafů
- Agregace a skartace dat v DB
- Napojení na LDAP, nebo vytvoření lokální DB jen pro uživatele a role, včetně registrace a administrace
- Napojení na Tepelné čerpadlo prostřednictvím ModBus a vyčítání dat
- Otestování a ošetření výjimek
- Ochrana API
- Optimaliazce frontentu, doplnění cachování a publikace statického obsahu na Nginx

---

## Zapojeni sezoru, LED (představuje rele) a RPi
![RPi and BME280 wiring](wiring_rpi.png)