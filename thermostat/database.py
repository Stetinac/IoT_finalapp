import sqlite3

# DB path
dbpath = '/opt/iot/'

# open DB connection
with sqlite3.connect(dbpath + "sensors.db") as conn:    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS thermostat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        automat INTEGER,
        heating INTEGER,
        desire_temp REAL
    )
    ''')
    # DB init with default settings of termostat
    # run only in first time
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM thermostat")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
        INSERT INTO thermostat (automat, heating, desire_temp)
        VALUES (?, ?, ?)
        """, (0, 0, 22))
        conn.commit()
        print(f"Aktualizováno 1")

def ConToDB(sql, oneline=False, commit=False):
    cursor = conn.cursor()
    cursor = conn.execute(sql)
    if commit:
        conn.commit()   
    
    if oneline:
        data = cursor.fetchone()            
    else:
        data = cursor.fetchall()
    return data

# set value of termostat parameter
def ThmWriteCfg(param, value):
    sql = f"UPDATE thermostat SET {param} = {value}"
    ConToDB(sql,commit=True)

# get current set of termostat
def ThmLoadCfg():
    sql = f"SELECT * FROM thermostat"
    data = ConToDB(sql,True)
    # print(data)
    return data


if __name__ == "__main__":
    # Thread for temp reading
    print("Modul only!")