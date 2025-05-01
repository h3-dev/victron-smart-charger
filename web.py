# web.py
from fastapi import FastAPI
import app_state

app = FastAPI(
    title="Victron Smart Charger API",
    version="0.1.0",
    docs_url="/",        # Swagger UI
)

@app.get("/forecast")
def read_forecast():
    return app_state.latest_forecast

@app.get("/charging-plan")
def read_plan():
    # Dict with ISO-Timestamp-Strings → Ampere
    return app_state.latest_plan

@app.get("/status")
def read_status():
    return app_state.latest_status
