from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging
import os
import sys

# my own modules
import database
from meteoapi import GetOutTemp

# base Flask app Class
app = Flask(__name__)
app.secret_key = os.urandom(24)  # potřebné pro sessions, generuje se kazde spusteni (odhlasi existujici sessions)

# login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Logger to stdout
login_logger = logging.getLogger('user_login')
login_logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stdout_handler.setFormatter(formatter)
login_logger.addHandler(stdout_handler)

# User DB
users_db = {
    "admin": {
        "password": generate_password_hash("adminpass"),
        "role": "admin"
    },
    "user": {
        "password": generate_password_hash("userpass"),
        "role": "user"
    }
}

# USer Class
class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    u = users_db.get(user_id)
    if u:
        return User(user_id, u["role"])
    return None

# Role-based decorator
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role != role:
                abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Root for webapp
@app.get('/')
@login_required
def home():
    return render_template("index.html")

# sensor data
@app.get('/api/temp/now')
@login_required
def return_curren_temp():
    dbdata = database.ListCurrentSensorData()
    outtmp = round(GetOutTemp(),2)
    # print(f"timestamp: {dbdata[1]}, teplota: {dbdata[2]}, vlhkost:{dbdata[3]}, tlak: {dbdata[4]},rosny_bod: {dbdata[5]}, venkuje: {outtmp}")
    return {"timestamp": dbdata[1], "temperature": dbdata[2], "humidity": dbdata[3], "pressure": dbdata[4], "dew_point": dbdata[5], "out_temp": outtmp}

# get switch status
@app.get('/api/switch/get/<switchname>')
@login_required
def get_switch(switchname):
    swdata = database.ThmLoadCfg(switchname)
    # print(swdata[0])
    if swdata[0]:
        return {"state": True}
    else:
        return {"state": False}

# set switch status       
@app.post('/api/switch/set/<switchname>')
@login_required
@role_required("admin")
def set_switch(switchname):
    data = request.get_json()
    try:
        data = request.get_json()
        if not data or 'state' not in data:
            return jsonify({"ok": False, "error": "Missing 'state' in request"}), 400
        state = data['state']
        # 1/0
        value = 1 if state else 0
        # Save switch status
        # print(switchname, value)
        database.ThmWriteCfg(switchname, value)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# get slider status       
@app.get('/api/slider/get/<slidername>')
@login_required
def get_slider(slidername):
    sldata = database.ThmLoadCfg(slidername)
    # print(sldata[0])
    return {"state": sldata[0]}

# set slider status       
@app.post('/api/slider/set/<slidername>')
@login_required
@role_required("admin")
def set_slider(slidername):
    try:
        data = request.get_json()
        if not data or 'state' not in data:
            return jsonify({"ok": False, "error": "Missing 'state' in request"}), 400    
        value = data['state']
        # print(slidername, value)
        database.ThmWriteCfg(slidername, value)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# get history page      
@app.get('/history')
@login_required
def get_history():
     return render_template("history.html")


# get history page      
@app.get('/api/history/last')
@login_required
def get_graf_history():
    graf_data = database.HisSensorData()
    json_data = [
        {
            'timestamp': ts,
            'temperature': temp,
            'humidity': hum,
            'dewpoint': dew
        }
        for ts, temp, hum, dew in graf_data
    ]
    return jsonify(json_data)

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = users_db.get(username)
        if user and check_password_hash(user["password"], password):
            login_user(User(username, user["role"]))
            login_logger.info(f"User '{username}' logged in")  # <-- log přihlášení
            return redirect(url_for("home"))
        flash("Špatné uživatelské jméno nebo heslo", "danger")
    return render_template("login.html")

# def login():
    # if request.method == "POST":
        # username = request.form.get("username")
        # password = request.form.get("password")
        # user = users_db.get(username)
        # if user and check_password_hash(user["password"], password):
            # login_user(User(username, user["role"]))
            # return redirect(url_for("home"))
        # flash("Špatné uživatelské jméno nebo heslo", "danger")
    # return render_template("login.html")

# logout page
@app.route('/logout')
@login_required
def logout():
    username = current_user.id
    logout_user()
    login_logger.info(f"User '{username}' logged out")  # <-- log odhlášení
    flash('Byl jsi odhlášen.', 'info')
    return redirect(url_for('login'))
# def logout():
#     session.pop('username', None)
#     flash('Byl jsi odhlášen.', 'info')
#     return redirect(url_for('login'))


# main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True, use_reloader=False)
