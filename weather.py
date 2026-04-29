import requests

API_KEY = "046c21c1487f33afdd0e1313f58ca41e"

def get_weather():
    city = "Delhi"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    res = requests.get(url)
    data = res.json()

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    condition = data["weather"][0]["main"]

    return temp, humidity, condition


def get_weather_forecast():
    city = "Delhi"

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

    res = requests.get(url)
    data = res.json()

    rain_forecast = False

    # next 9 hours approx (3 entries)
    for item in data["list"][:3]:
        weather = item["weather"][0]["main"]

        if "Rain" in weather or "Thunderstorm" in weather:
            rain_forecast = True

    return rain_forecast