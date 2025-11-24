# 🔥 Flask Termostat – Webový Backend

## 📌 Popis projektu

Tento projekt implementuje **webový backend pro domácí termostat**, napsaný ve Flasku.
Poskytuje tyto funkce:

* Přihlášení uživatele (role: *admin*, *user*)
* Ovládání topení (termostat/manual)
* Zobrazení aktuálních a historických dat ze senzorů
* REST API pro frontend`
* Logování přihlášení
* Integraci s:
  * interní SQLite databází prostřednictvím které ovládá část Thermostat
  * API prostředictvím kterého získává aktuální venkovní teplotu
* Backend je chráněný pomocí **Flask-Login**
* V tomto konceptu existuje role:
  * User s omezeným právem na ovládání Thermostatu
  * Admin bez omezení ovládání Thermostatu

---

## 📁 Struktura projektu

```
frontend/
├── app.py                 # hlavní App
├── database.py            # modul pro komunikaci s DB
├── meteoapi.py            # modul pro komunikaci s API open-meteo.com
│
├── templates/             # vzory renderovaných HTML stránek
│   ├── index.html  
│   ├── login.html
│   └── history.html
│
├── static/               # Statický obsa - CSS, JavScripty, obrázky, atd.
│   ├── css/
│   └── js/
│
└── requirements.txt      # Soubor obsahující moduly Python instalované přes PIP
```

---

## 🛠 Instalace a spuštění

## 🔒 Autentizace a role

V projektu jsou vestavěni dva uživatelé:

| Uživatelské jméno | Heslo       | Role  |
| ----------------- | ----------- | ----- |
| `admin`           | `adminpass` | admin |
| `user`            | `userpass`  | user  |

Role *admin* může měnit přepínače/slidery.
Role *user* může pouze číst data.

---

## 🧩 ASCII diagram – architektura

```
                ┌──────────────────────────────┐
                │            Browser            │
                │  index.html / history.html    │
                └───────────────┬──────────────┘
                                │  HTTP/JSON
                                ▼
                   ┌──────────────────────────┐
                   │        Flask App         │
                   │         app.py           │
                   ├───────────┬──────────────┤
                   │           │               │
             Auth/Login   Sensor API      Config API
                   │           │               │
                   ▼           ▼               ▼
        ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐
        │ flask_login    │  │ database.py    │  │ database.py      │
        │ sessions/roles │  │ read sensor    │  │ read/write config│
        └────────────────┘  └────────────────┘  └──────────────────┘
                                │
                                ▼
                 ┌─────────────────────────┐
                 │ meteoapi.GetOutTemp()   │   ← venkovní teplota
                 └─────────────────────────┘
```

---

## 🚀 API Dokumentace

### 1) **Aktuální teplota**

```
GET /api/temp/now
```

Vrací:

```json
{
  "timestamp": "...",
  "temperature": 22.3,
  "humidity": 45.2,
  "pressure": 1013.5,
  "dew_point": 9.8,
  "out_temp": 7.4
}
```

---

### 2) **Získání stavu přepínače**

```
GET /api/switch/get/<name>
```

Odpověď:

```json
{ "state": true }
```

---

### 3) **Nastavení přepínače (ADMIN ONLY)**

```
POST /api/switch/set/<name>
```

JSON tělo:

```json
{ "state": true }
```

---

### 4) **Získání hodnoty slideru**

```
GET /api/slider/get/<name>
```

---

### 5) **Nastavení slideru (ADMIN ONLY)**

```
POST /api/slider/set/<name>
```

---

### 6) **Historie pro graf**

```
GET /api/history/last
```

Vrací list záznamů:

```json
[
  { "timestamp": "...", "temperature": 21.3, "humidity": 50, "dewpoint": 10.1 },
  ...
]
```

---

## 🔐 Login / Logout

### Login stránka:

```
POST /login
```

### Logout:

```
GET /logout
```

Obojí se loguje do STDOUT pomocí:

```python
login_logger.info(...)
```

---

## ⚙️ Automatizované spouštění – Gunicorn + Systemd

Pro nasazení Flask aplikace do produkčního prostředí se doporučuje využití **Gunicorn** a **systemd**.

### 2️⃣ Spuštění aplikace přes Gunicorn

```bash
# z adresáře s app.py
gunicorn -w 2 -b 0.0.0.0:5008 app:app
```

* `-w 2` → počet workerů (doporučeno podle CPU)
* `-b 0.0.0.0:5008` → bind na všechny IP, port 5008
* `app:app` → `modul:flask_app_object`

---

### 3️⃣ Systemd služba

Vytvořte soubor např. `/etc/systemd/system/flask.service`:

```ini
[Unit]
Description=Teplota Flask app
After=network-online.target
Wants=network-online.target

[Service]
User= <zde doplint>
Group=www-data
PIDFile=/var/tmp/flask.pid

WorkingDirectory= <zde doplnit cestu do adresare se skriptem>
Environment="PATH= <zde doplnit cestu do adresare se skriptem a Pythno environmentem>"
ExecStart= <zde doplnit cestu do adresare se skriptem>/.env/bin/gunicorn --workers 2 --bind 0.0.0.0:5008 -m 007 wsgi:app

Restart=on-failure
RestartSec=30
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

* `User` a `Group` nastav podle svého systému
* `WorkingDirectory` → cesta k projektu
* `PATH` → cesta k virtuálnímu prostředí
* `ExecStart` → spuštění Gunicorn s Flask aplikací

---

### 4️⃣ Aktivace a spuštění služby

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask.service
sudo systemctl start flask.service
sudo systemctl status flask.service
```

* `enable` → automaticky start při bootu
* `status` → kontrola běhu služby
* `restart` → restart služby po změně kódu

---

### 5️⃣ Logy

Gunicorn, systemd logy a logování přihlášení se ukládají journalu systemd a lze je sledovat např.:

```bash
journalctl -u flask.service -f
```
---

## 🌐 Publikace přes Nginx

Pro přístup k aplikaci z internetu nebo z lokální sítě doporučujeme použít **Nginx** jako reverzní proxy.

### 1️⃣ Instalace Nginx

#### Debian / Ubuntu

```bash
sudo apt update
sudo apt install nginx -y
```
### 2️⃣ Konfigurace Nginx

Vytvořte nový soubor, např. `/etc/nginx/sites-available/frontend`:

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

* `proxy_pass` → adresa Gunicorn serveru (localhost:5008)

---

### 3️⃣ Aktivace konfigurace

```bash
sudo ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/
sudo nginx -t   # otestování konfigurace
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### 4️⃣ SSL / HTTPS (doporučeno) v příapdě publikace do internetu

Pro zabezpeceni sifrovani prenasenych dat mezi uzivatelem a frontendem lze použít CA **Let's Encrypt**:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain
```
* `your_domain` → adresa serveru v internetu, pro kterou se vytváří a obnovuje vydaný certifikát

Certbot automaticky nastaví HTTPS a přesměrování HTTP → HTTPS.
