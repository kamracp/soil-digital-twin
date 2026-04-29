import streamlit as st
import pandas as pd
import random
import requests
import folium
from streamlit_folium import st_folium

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Soil Digital Twin", layout="wide")

API_KEY = "046c21c1487f33afdd0e1313f58ca41e"

# -------------------------
# LOCATION FUNCTIONS
# -------------------------
def get_coords(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},IN&limit=1&appid={API_KEY}"
    res = requests.get(url)
    data = res.json()
    if len(data) == 0:
        return None, None
    return data[0]["lat"], data[0]["lon"]

def get_coords_pincode(pincode):
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={pincode},IN&appid={API_KEY}"
    res = requests.get(url)
    data = res.json()
    if data.get("cod") != 200:
        return None, None
    return data["lat"], data["lon"]

def get_ip_location():
    res = requests.get("http://ip-api.com/json/")
    data = res.json()
    return data["lat"], data["lon"]

# -------------------------
# WEATHER FUNCTIONS
# -------------------------
def get_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    data = res.json()
    if data.get("cod") != 200:
        return None, None, "Error"
    return data["main"]["temp"], data["main"]["humidity"], data["weather"][0]["main"]

def get_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    data = res.json()
    rain = False
    if data.get("cod") == "200":
        for item in data["list"][:8]:
            if "rain" in item or item["weather"][0]["main"] in ["Rain", "Thunderstorm"]:
                rain = True
    return rain

# -------------------------
# DECISION FUNCTION
# -------------------------
def decision(moisture, temp, ph, rain):
    if rain:
        return "DELAY", "Rain expected", "Energy saving due to rain"
    if moisture < 30:
        return "ON", "Irrigation needed", "High energy use"
    elif moisture > 60:
        return "OFF", "Soil wet", "Energy saved"
    else:
        return "MONITOR", "Balanced", "Normal energy"

# -------------------------
# CROP SUGGESTION
# -------------------------
def suggest_crop(temp, moisture, ph):
    if temp > 30 and moisture < 40:
        return "Millet / Bajra"
    elif moisture > 60:
        return "Rice"
    elif 20 < temp < 30 and 6 < ph < 7.5:
        return "Wheat"
    else:
        return "General Crop"

# -------------------------
# ENERGY CALCULATION
# -------------------------
def energy_calc(pump_kw, hours, tariff, rain):
    optimized_hours = hours * 0.6 if rain else hours
    base_cost = pump_kw * hours * tariff
    opt_cost = pump_kw * optimized_hours * tariff
    saving = base_cost - opt_cost
    return base_cost, opt_cost, saving

# -------------------------
# HEADER
# -------------------------
st.title("🌱 Soil Digital Twin Platform")

# -------------------------
# SIDEBAR - LOCATION
# -------------------------
st.sidebar.header("📍 Location")

mode = st.sidebar.radio("Select Mode", ["City", "Pincode", "Auto GPS"])

if mode == "City":
    location = st.sidebar.text_input("Enter City", "Delhi")
    lat, lon = get_coords(location)

elif mode == "Pincode":
    location = st.sidebar.text_input("Enter Pincode", "110001")
    lat, lon = get_coords_pincode(location)

else:
    lat, lon = get_ip_location()

if lat is None:
    st.error("Invalid location")
    st.stop()

# -------------------------
# WEATHER
# -------------------------
temp, humidity, condition = get_weather(lat, lon)
rain = get_forecast(lat, lon)

st.subheader("🌦 Weather")

col1, col2, col3 = st.columns(3)
col1.metric("Temperature", f"{temp} °C")
col2.metric("Humidity", f"{humidity} %")
col3.metric("Condition", condition)

if rain:
    st.warning("Rain expected → Irrigation delay")
else:
    st.success("No rain → Normal irrigation")

# -------------------------
# SIDEBAR - CROP & SOIL
# -------------------------
st.sidebar.header("🌱 Crop & Soil Inputs")

crop_type = st.sidebar.selectbox(
    "Select Crop",
    ["Wheat", "Rice", "Cotton", "Maize", "Millet"]
)

moisture = st.sidebar.slider("Soil Moisture (%)", 0, 100, 30)
soil_temp = st.sidebar.slider("Soil Temperature (°C)", 0, 50, 30)
ph = st.sidebar.slider("Soil pH", 4.0, 9.0, 7.0)

# -------------------------
# SIDEBAR - ENERGY
# -------------------------
st.sidebar.header("⚡ Energy Inputs")

pump_kw = st.sidebar.number_input("Pump Power (kW)", 1.0, 50.0, 5.0)
hours = st.sidebar.number_input("Run Hours", 1.0, 24.0, 10.0)
tariff = st.sidebar.number_input("Electricity Cost (₹/kWh)", 1.0, 20.0, 7.0)

# -------------------------
# LOGIC
# -------------------------
crop_suggestion = suggest_crop(soil_temp, moisture, ph)
irrigation, crop_advice, energy_msg = decision(moisture, soil_temp, ph, rain)
base, opt, saving = energy_calc(pump_kw, hours, tariff, rain)

# -------------------------
# DECISION PANEL
# -------------------------
st.subheader("🤖 Decision Panel")

st.write("User Selected Crop:", crop_type)
st.write("Suggested Crop:", crop_suggestion)

st.write("Irrigation:", irrigation)
st.write("Advice:", crop_advice)
st.write("Energy Insight:", energy_msg)

# -------------------------
# ENERGY DISPLAY
# -------------------------
st.subheader("⚡ Energy & Cost Impact")

col1, col2, col3 = st.columns(3)

col1.metric("Base Cost", f"₹ {round(base,2)}")
col2.metric("Optimized Cost", f"₹ {round(opt,2)}")
col3.metric("Saving", f"₹ {round(saving,2)}")

# -------------------------
# GRAPH
# -------------------------
st.subheader("📈 Soil Trend")

data = pd.DataFrame({
    "Moisture": [random.randint(20, 60) for _ in range(10)],
    "Temperature": [random.randint(25, 40) for _ in range(10)]
})

st.line_chart(data)

# -------------------------
# MAP
# -------------------------
st.subheader("🗺 Location Map")

m = folium.Map(location=[lat, lon], zoom_start=10)
folium.Marker([lat, lon]).add_to(m)

st_folium(m, width=700)

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("Developed by Kamra Digital Twin Systems")