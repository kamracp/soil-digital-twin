import streamlit as st
import pandas as pd
import random
from digital_twin import decision
from weather import get_weather, get_weather_forecast
from energy import energy_calc
from report_generator import generate_report
# -------------------------
# PAGE CONFIG (TOP)
# -------------------------
st.set_page_config(page_title="Soil Digital Twin", layout="wide")

# -------------------------
# HEADER
# -------------------------
st.title("🌱 Soil Digital Twin - Smart Agriculture Platform")
st.markdown("### Real-Time Monitoring | AI Decision | Energy Optimization")

# -------------------------
# WEATHER DATA (FIRST)
# -------------------------
weather_temp, humidity, condition = get_weather()
rain_forecast = get_weather_forecast()

st.subheader("🌦 Weather Data")
st.write("Temperature:", weather_temp)
st.write("Humidity:", humidity)
st.write("Condition:", condition)

st.subheader("🌧 Rain Prediction")

if rain_forecast:
    st.warning("Rain expected → Irrigation delayed")
else:
    st.success("No rain → Normal irrigation")

# -------------------------
# SIDEBAR INPUTS
# -------------------------
st.sidebar.header("⚙️ Control Panel")

crop_type = st.sidebar.selectbox(
    "Select Crop",
    ["Wheat", "Rice", "Cotton", "Potato"]
)

moisture = st.sidebar.slider("Soil Moisture (%)", 0, 100, 30)
temp = st.sidebar.slider("Temperature (°C)", 0, 50, 30)
ph = st.sidebar.slider("Soil pH", 4.0, 9.0, 7.0)
st.sidebar.subheader("⚡ Energy Inputs")

pump_kw = st.sidebar.number_input("Pump Power (kW)", 1, 100, 5)
hours_run = st.sidebar.slider("Normal Run Hours", 1, 24, 10)
tariff = st.sidebar.number_input("Electricity Tariff (₹/kWh)", 1.0, 20.0, 7.0)
# -------------------------
# KPI DISPLAY
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💧 Moisture (%)", moisture)
col2.metric("🌡 Temperature (°C)", temp)
col3.metric("⚗️ pH Level", ph)

# -------------------------
# DIGITAL TWIN DECISION
# -------------------------
irrigation, crop_suggestion, energy = decision(moisture, temp, ph, rain_forecast)
optimized_hours = hours_run

if "DELAY" in irrigation:
    optimized_hours = hours_run * 0.5

elif irrigation == "OFF":
    optimized_hours = 0

elif irrigation == "ON":
    optimized_hours = hours_run * 0.8
result = energy_calc(pump_kw, hours_run, tariff, optimized_hours)

optimized_hours = hours_run

if "DELAY" in irrigation:
    optimized_hours = hours_run * 0.5

elif irrigation == "OFF":
    optimized_hours = 0

elif irrigation == "ON":
    optimized_hours = hours_run * 0.8
# Status indicator
if irrigation == "ON":
    status = "🟢 Irrigation Running"
elif irrigation == "OFF":
    status = "🔴 Irrigation Stopped"
else:
    status = "🟡 Monitoring"
report_data = {
    "crop": crop_type,
    "moisture": moisture,
    "temp": temp,
    "ph": ph,
    "irrigation": irrigation,
    "energy": energy,
    "base_cost": result["base_cost"],
    "opt_cost": result["opt_cost"],
    "saving": result["saving_rs"],
    "saving_percent": result["saving_percent"]
}
# -------------------------
# MAIN DASHBOARD
# -------------------------
col_left, col_right = st.columns([2, 1])

# LEFT: Graph
with col_left:
    st.subheader("📈 Soil Trend (Simulated)")

    data = pd.DataFrame({
        "Moisture": [random.randint(20, 60) for _ in range(10)],
        "Temperature": [random.randint(25, 40) for _ in range(10)]
    })

    st.line_chart(data)

# RIGHT: Decision Panel
# RIGHT: Decision Panel
with col_right:
    st.subheader("🤖 AI Decision Panel")

    st.info(f"**Selected Crop:** {crop_type}")
    st.success(f"💧 Irrigation: {irrigation}")
    st.write(f"🌾 Suggested Crop: {crop_suggestion}")
    st.write(f"⚡ Energy Insight: {energy}")
    st.markdown(f"### Status: {status}")

    # 👉 NEW ADDITION (₹ impact)
    st.markdown("---")
    st.subheader("⚡ Cost Impact")

    st.metric("Base Cost (₹)", result["base_cost"])
    st.metric("Optimized Cost (₹)", result["opt_cost"])
    st.metric("Saving (₹)", result["saving_rs"])

   
    st.caption(f"Saving %: {result['saving_percent']} %")
if result["saving_rs"] > 0:
        st.success(f"💰 You save ₹ {result['saving_rs']} ({result['saving_percent']}%)")
else:
        st.warning("No saving in current condition")
# -------------------------
# CONTROL BUTTONS
# -------------------------
st.subheader("🎛 Control")

colA, colB = st.columns(2)

if colA.button("▶️ Start Irrigation"):
    st.success("Pump Started")

if colB.button("⏹ Stop Irrigation"):
    st.error("Pump Stopped")
if st.button("📄 Generate Report"):
    file = generate_report(report_data)

    with open(file, "rb") as f:
        st.download_button(
            label="⬇ Download PDF",
            data=f,
            file_name="Soil_Report.pdf",
            mime="application/pdf"
        )
# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("**Developed by Kamra Energy Digital Twin Systems**")