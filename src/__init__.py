from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


STATIONS = [
    {"station": "North Basin", "district": "North", "lat": 12.9716, "lon": 77.5946},
    {"station": "Central Reach", "district": "Central", "lat": 12.9141, "lon": 77.6387},
    {"station": "South Creek", "district": "South", "lat": 12.9352, "lon": 77.6245},
    {"station": "Harbor Gate", "district": "Coastal", "lat": 12.8430, "lon": 77.6600},
    {"station": "Green Valley", "district": "East", "lat": 13.0320, "lon": 77.5780},
]


def classify_risk(score: float) -> str:
    if score >= 80:
        return "Severe"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def get_alert_recommendations(score: float) -> str:
    if score >= 80:
        return "Activate emergency alerts, deploy temporary barriers, and issue evacuation guidance for low-lying neighborhoods."
    if score >= 60:
        return "Increase patrols, prepare sandbags, and prioritize drainage clearance in flood-prone zones."
    if score >= 35:
        return "Continue monitoring and keep emergency teams on standby for possible escalation."
    return "Routine monitoring is sufficient; maintain readiness and inspect drainage after the next rainfall event."


def compute_risk_index(rainfall_mm: float, river_level_m: float, soil_moisture_pct: float, drainage_capacity_pct: float) -> float:
    rainfall_component = min((rainfall_mm / 120) * 45, 45)
    river_component = min((river_level_m / 9) * 25, 25)
    soil_component = min((soil_moisture_pct / 100) * 18, 18)
    drainage_component = min(((100 - drainage_capacity_pct) / 100) * 18, 18)
    risk_score = rainfall_component + river_component + soil_component + drainage_component
    return round(float(np.clip(risk_score, 0, 100)), 1)


def build_station_data(rainfall_intensity: float, soil_saturation: float, drainage_capacity: float) -> pd.DataFrame:
    rows = []

    for station_meta in STATIONS:
        river_base = {
            "North Basin": 6.5,
            "Central Reach": 7.2,
            "South Creek": 5.8,
            "Harbor Gate": 7.8,
            "Green Valley": 6.1,
        }

        rainfall_adjustment = {
            "North Basin": 1.0,
            "Central Reach": 1.22,
            "South Creek": 1.15,
            "Harbor Gate": 1.35,
            "Green Valley": 1.08,
        }

        station_name = station_meta["station"]
        rainfall = rainfall_intensity * rainfall_adjustment[station_name]
        river_level = river_base[station_name] + (rainfall_intensity / 60) * 0.8
        river_level = min(river_level, 10.5)

        if station_name == "Harbor Gate":
            river_level += 0.7

        risk_index = compute_risk_index(
            rainfall_mm=rainfall,
            river_level_m=river_level,
            soil_moisture_pct=max(soil_saturation - 8, 15),
            drainage_capacity_pct=max(drainage_capacity - 5, 10),
        )

        rows.append(
            {
                "station": station_name,
                "district": station_meta["district"],
                "lat": station_meta["lat"],
                "lon": station_meta["lon"],
                "rainfall_mm": round(rainfall, 1),
                "river_level_m": round(river_level, 2),
                "soil_moisture_pct": round(max(soil_saturation - 8, 15), 1),
                "drainage_capacity_pct": round(max(drainage_capacity - 5, 10), 1),
                "risk_index": risk_index,
            }
        )

    return pd.DataFrame(rows).sort_values("risk_index", ascending=False)


def summarize_overall_risk(station_df: pd.DataFrame) -> Dict[str, float | int | str]:
    avg_score = float(station_df["risk_index"].mean())
    severe = int((station_df["risk_index"] >= 80).sum())
    high_risk = int((station_df["risk_index"] >= 60).sum())
    alert_count = int((station_df["risk_index"] >= 35).sum())

    if avg_score >= 75:
        status = "Severe Flood Risk"
    elif avg_score >= 55:
        status = "High Flood Risk"
    elif avg_score >= 30:
        status = "Moderate Flood Risk"
    else:
        status = "Low Flood Risk"

    return {
        "overall_score": round(avg_score, 1),
        "overall_status": status,
        "alert_count": alert_count,
        "high_risk_stations": high_risk,
        "severe_stations": severe,
    }


def forecast_station_data(station_df: pd.DataFrame, hours: int = 6) -> pd.DataFrame:
    forecast_rows = []
    for _, row in station_df.iterrows():
        for hour in range(1, hours + 1):
            risk_at_hour = max(0, row["risk_index"] - (hour * 2.2) + (hour * 0.8))
            forecast_rows.append(
                {
                    "station": row["station"],
                    "hour": f"+{hour}h",
                    "risk_index": round(float(risk_at_hour), 1),
                }
            )
    return pd.DataFrame(forecast_rows)


if __name__ == "__main__":
    sample_df = build_station_data(120, 72, 58)
    print(sample_df)
    print(summarize_overall_risk(sample_df))
