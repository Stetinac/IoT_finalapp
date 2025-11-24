import sqlite3

# DB path
dbpath = '/opt/iot/'

def ConToDB(sql, oneline=False, commit=False):
    conn = sqlite3.connect(dbpath + "sensors.db")
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        # pokud je SELECT, vracíme data
        if oneline:
            data = cursor.fetchone()            
        else:
            data = cursor.fetchall()
        if commit:
            conn.commit()
        return data

    except sqlite3.Error as e:
        return {"error": str(e)}

    finally:
        conn.close()

def ListCurrentSensorData():
    sql = '''
    SELECT * FROM sensor_data 
    ORDER BY id DESC
    LIMIT 1;'''        
    data_from_db = ConToDB(sql,True)
    return data_from_db

# set value of termostat parameter
def ThmWriteCfg(param, value):
    sql = f"UPDATE thermostat SET {param} = {value}"
    ConToDB(sql,commit=True)

# get current set of termostat
def ThmLoadCfg(switch):
    sql = f"SELECT {switch} FROM thermostat"
    data = ConToDB(sql,True)
    # print(data)
    return data

# vypis dat pro graf za poslednich 7 dni
def HisSensorData():
    sql = """
    SELECT strftime('%Y-%m-%d %H:00', timestamp) AS hodina,
        AVG(temperature) AS avg_temp,
        AVG(humidity) AS avg_humi,
        AVG(dewpoint) AS avg_dew
    FROM sensor_data
    WHERE timestamp >= datetime('now', '-1 day','localtime')
        GROUP BY hodina
        ORDER BY hodina;
    """
    data = ConToDB(sql)
    # print(data)
    return data

if __name__ == "__main__":
    # Thread for temp reading
    print("Modul only!")
