from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
import app_state

# ---------- FastAPI root -----------------
app = FastAPI(
    title="Victron Smart Charger",
    version="0.1.0",
    docs_url="/api/docs",          # Swagger → /api/docs
    openapi_url="/api/openapi.json"
)

# ---------- API Router -------------------
api = APIRouter(prefix="/api")

@api.get("/forecast")
def get_forecast():
    return app_state.latest_forecast

@api.get("/charging-plan")
def get_plan():
    return app_state.latest_plan

@api.get("/status")
def get_status():
    return app_state.latest_status

app.include_router(api)

# ---------- Static UI --------------------
app.mount("/", StaticFiles(directory="static", html=True), name="ui")
