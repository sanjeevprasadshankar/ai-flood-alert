# AI Flood Alert Prototype

A polished AI-powered flood monitoring dashboard prototype designed to help teams assess flood risk in real time using sensor-like inputs, forecast patterns, and risk prioritization.

## What this prototype does

- Tracks flood risk across multiple river stations
- Combines rainfall, river level, soil saturation, and drainage capacity
- Produces a risk score and alert status
- Shows a 6-hour forecast and risk hotspots
- Recommends actions for public safety and operations

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- NumPy

## Project structure

- `app.py` — dashboard UI and simulation controls
- `src/flood_model.py` — risk logic and sample flood data
- `requirements.txt` — Python dependencies

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Demo behavior

The app simulates a flood monitoring environment with:

- Multiple districts / stations
- Real-time visual risk indicators
- Trigger logic for low / moderate / high / severe alerts
- Forecasted conditions for the next 6 hours
- Response suggestions for emergency teams

## AI logic

This prototype uses a rule-based AI risk engine inspired by real flood forecasting logic. It blends multiple factors:

- rainfall intensity
- river stage level
- soil saturation
- drainage efficiency
- urban runoff conditions

It then classifies the combined score into actionable alert categories.

## License

MIT
