import streamlit as st
import pandas as pd
import plotly.express as px

from src.flood_model import (
    build_station_data,
    classify_risk,
    forecast_station_data,
    get_alert_recommendations,
    summarize_overall_risk,
)

st.set_page_config(page_title="AI Flood Alert System", page_icon="🌊", layout="wide")

st.title("AI Flood Alert Prototype")
st.caption("Smart monitoring for rainfall, river conditions, and flood risk management")

with st.sidebar:
    st.header("Scenario Controls")
    rainfall_intensity = st.slider("Rainfall intensity (mm/hr)", 10, 200, 110, 5)
    soil_saturation = st.slider("Soil saturation (%)", 20, 100, 72, 2)
    drainage_capacity = st.slider("Drainage capacity (%)", 15, 100, 58, 2)
    forecast_hours = st.slider("Forecast horizon (hours)", 3, 12, 6, 1)
    st.markdown("---")
    st.info("The model blends rainfall, river level, soil moisture, and drainage readiness to estimate flood risk.")

station_df = build_station_data(
    rainfall_intensity=rainfall_intensity,
    soil_saturation=soil_saturation,
    drainage_capacity=drainage_capacity,
)

station_df["alert_level"] = station_df["risk_index"].apply(classify_risk)
station_df["recommendation"] = station_df["risk_index"].apply(get_alert_recommendations)

summary = summarize_overall_risk(station_df)

st.markdown(f"## Risk Overview: {summary['overall_status']}")

cols = st.columns(4)
cols[0].metric("Overall Risk Score", f"{summary['overall_score']:.1f}/100")
cols[1].metric("Active Warnings", summary["alert_count"])
cols[2].metric("High Risk Stations", summary["high_risk_stations"])
cols[3].metric("Forecast Window", f"{forecast_hours} hrs")

if summary["overall_status"] == "Severe Flood Risk":
    st.warning("Severe flooding is likely. Prioritize warning dissemination, emergency preparation, and field inspections.")
elif summary["overall_status"] == "High Flood Risk":
    st.warning("High risk conditions exist in several catchments. Increase monitoring and prepare response teams.")
elif summary["overall_status"] == "Moderate Flood Risk":
    st.info("Conditions are manageable but require close monitoring and occasional readiness actions.")
else:
    st.success("Flood threat is relatively low. Continue routine monitoring and maintain readiness.")

# Map
station_map = px.scatter_geo(
    station_df,
    lat="lat",
    lon="lon",
    size="risk_index",
    color="risk_index",
    hover_name="station",
    hover_data={
        "risk_index": ":.1f",
        "rainfall_mm": ":.1f",
        "river_level_m": ":.2f",
        "soil_moisture_pct": ":.0f",
        "alert_level": True,
    },
    projection="natural earth",
    title="Flood Risk Hotspots",
    color_continuous_scale="RdYlGn_r",
    range_color=[0, 100],
)
station_map.update_layout(height=400, margin={"r": 0, "t": 40, "l": 0, "b": 0})
st.plotly_chart(station_map, use_container_width=True)

# Forecast chart
forecast_df = forecast_station_data(station_df, hours=forecast_hours)
forecast_chart = px.line(
    forecast_df,
    x="hour",
    y="risk_index",
    color="station",
    markers=True,
    title="6-Hour Flood Risk Forecast",
)
forecast_chart.update_layout(height=350)
st.plotly_chart(forecast_chart, use_container_width=True)

# Main data table
st.subheader("Monitoring Stations")
st.dataframe(
    station_df[[
        "station",
        "district",
        "rainfall_mm",
        "river_level_m",
        "soil_moisture_pct",
        "drainage_capacity_pct",
        "risk_index",
        "alert_level",
        "recommendation",
    ]].sort_values("risk_index", ascending=False),
    use_container_width=True,
    hide_index=True,
)

# Recommendations panel
st.subheader("Recommended Response Actions")
recs = station_df[["station", "alert_level", "recommendation"]].drop_duplicates()
for _, row in recs.iterrows():
    st.markdown(f"- **{row['station']}** ({row['alert_level']}): {row['recommendation']}")

# Explainability section
st.subheader("AI Explanation")
st.markdown(
    """
    The flood alert engine calculates a weighted risk score using rainfall intensity, river level, soil saturation, and drainage capacity.
    Higher rainfall and river stage increase the risk, while insufficient drainage and saturated soil amplify the chance of flash flooding.
    The result is translated into an alert level and recommended emergency response for each district.
    """
)

# Footer
st.caption("Prototype built for concept validation and stakeholder demos.")
