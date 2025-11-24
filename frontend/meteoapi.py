import requests

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 50.088,
    "longitude": 14.4208,
    "current_weather": True,
    "timezone": "Europe/Berlin"
}

def GetOutTemp():
    try:
        r = requests.get(url, params=params, timeout=1)
        r.raise_for_status()
        data = r.json()
        current_temp = data["current_weather"]["temperature"]
        return current_temp

    except Exception as e:
        # print("Error:", e)
        return 100