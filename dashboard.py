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
def get_coords_pincode(pincode):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/zip?zip={pincode},IN&appid={API_KEY}"
        data = requests.get(url).json()
        if data.get("cod") != 200:
            return None, None
        return data["lat"], data["lon"]
    except:
        return None, None



# -------------------------
# WEATHER FUNCTIONS
# -------------------------
def get_weather(lat, lon):
    data = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    ).json()

    return data["main"]["temp"], data["main"]["humidity"], data["weather"][0]["main"]

def get_forecast(lat, lon):
    data = requests.get(
        f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    ).json()

    if data.get("cod") == "200":
        for item in data["list"][:8]:
            if "rain" in item or item["weather"][0]["main"] in ["Rain", "Thunderstorm"]:
                return True
    return False

# -------------------------
# DECISION LOGIC
# -------------------------
def decision(moisture, temp, ph, rain):
    if rain:
        return "DELAY", "Rain expected", "Energy saving"

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
# ENERGY CALC
# -------------------------
def energy_calc(pump_kw, hours, tariff, rain):
    optimized_hours = hours * 0.6 if rain else hours
    base = pump_kw * hours * tariff
    opt = pump_kw * optimized_hours * tariff
    saving = base - opt
    return base, opt, saving

# -------------------------
# HEADER
# -------------------------
st.title("🌱 Soil Digital Twin -Kamra Version")

# -------------------------
# LOCATION BLOCK (CLEAN)
# -------------------------
st.sidebar.header("📍 Location")

mode = st.sidebar.radio("Mode", ["City", "Pincode", ])

city_coords = {
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Ahmedabad": (23.03, 72.58),
    "Jaipur": (26.91, 75.78),
    "Bangalore": (12.97, 77.59),
    "Chennai": (13.08, 80.27),
    "Kolkata": (22.57, 88.36)
}

if mode == "City":
    city = st.sidebar.selectbox("Select City", list(city_coords.keys()))
    lat, lon = city_coords[city]

elif mode == "Pincode":
    pincode = st.sidebar.text_input("Enter Pincode", "110001")
    lat, lon = get_coords_pincode(pincode)

    if lat is None:
        st.warning("Invalid pincode → using Delhi")
        lat, lon = city_coords["Delhi"]


# -------------------------
# WEATHER
# -------------------------
temp, humidity, condition = get_weather(lat, lon)
rain = get_forecast(lat, lon)

st.subheader("🌦 Weather")

c1, c2, c3 = st.columns(3)
c1.metric("Temperature", f"{temp} °C")
c2.metric("Humidity", f"{humidity} %")
c3.metric("Condition", condition)

if rain:
    st.warning("Rain expected → Irrigation delay")
else:
    st.success("No rain → Normal irrigation")

# -------------------------
# INPUTS
# -------------------------
st.sidebar.header("🌱 Crop & Soil")

crop_type = st.sidebar.selectbox(
    "Select Crop",
    ["Wheat", "Rice", "Cotton", "Maize", "Millet"]
)

moisture = st.sidebar.slider("Moisture (%)", 0, 100, 30)
soil_temp = st.sidebar.slider("Temperature (°C)", 0, 50, 30)
ph = st.sidebar.slider("pH", 4.0, 9.0, 7.0)

# -------------------------
# ENERGY INPUTS
# -------------------------
st.sidebar.header("⚡ Energy")

pump_kw = st.sidebar.number_input("Pump Power (kW)", 1.0, 50.0, 5.0)
hours = st.sidebar.number_input("Run Hours", 1.0, 24.0, 10.0)
tariff = st.sidebar.number_input("₹/kWh", 1.0, 20.0, 7.0)

# -------------------------
# LOGIC
# -------------------------
crop_suggestion = suggest_crop(soil_temp, moisture, ph)
irrigation, advice, energy_msg = decision(moisture, soil_temp, ph, rain)
base, opt, saving = energy_calc(pump_kw, hours, tariff, rain)

# -------------------------
# DECISION PANEL
# -------------------------
st.subheader("🤖 Decision Panel")

st.write("Selected Crop:", crop_type)
st.write("Suggested Crop:", crop_suggestion)
st.write("Irrigation:", irrigation)
st.write("Advice:", advice)
st.write("Energy Insight:", energy_msg)

if irrigation == "ON":
    st.success("🟢 Irrigation Running")
elif irrigation == "OFF":
    st.error("🔴 Irrigation Stopped")
else:
    st.warning("🟡 Monitoring")

# -------------------------
# COST
# -------------------------
st.subheader("⚡ Cost Impact")

c1, c2, c3 = st.columns(3)
c1.metric("Base Cost", f"₹ {round(base,2)}")
c2.metric("Optimized Cost", f"₹ {round(opt,2)}")
c3.metric("Saving", f"₹ {round(saving,2)}")

# -------------------------
# GRAPH
# -------------------------
st.subheader("📈 Soil Trend")

data = pd.DataFrame({
    "Moisture": [random.randint(20, 60) for _ in range(20)],
    "Temperature": [random.randint(25, 40) for _ in range(20)]
})

st.line_chart(data, use_container_width=True)

# -------------------------
# MAP
# -------------------------
st.subheader("🗺 Location Map")

m = folium.Map(location=[lat, lon], zoom_start=10)
folium.Marker([lat, lon]).add_to(m)

st_folium(m, width=700)

# -------------------------
# REPORT
# -------------------------
st.subheader("📄 Download Report")

df = pd.DataFrame({
    "Temperature": [temp],
    "Moisture": [moisture],
    "pH": [ph],
    "Crop": [crop_suggestion],
    "Saving": [saving]
})

st.download_button("Download CSV", df.to_csv(index=False), "report.csv")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("Developed by Kamra Digital Twin Systems")