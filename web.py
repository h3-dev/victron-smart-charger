from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
import app_state

# ---------- FastAPI root -----------------
app = FastAPI(
    title="Victron Smart Charger",
    version="0.1.0",
    docs_url="/api/docs",  # Swagger → /api/docs
    openapi_url="/api/openapi.json",
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
    status = app_state.latest_status.copy()
    status["target_soc"] = app_state.latest_target_soc
    return status


@api.post("/target-soc")
def post_target_soc(payload: dict):
    val = payload.get("target_soc")
    try:
        soc = int(val)
    except (TypeError, ValueError):
        raise HTTPException(400, "Invalid target_soc, must be an integer")
    if not 0 <= soc <= 100:
        raise HTTPException(400, "target_soc must be between 0 and 100")

    app_state.set_target_soc(soc)
    return {"target_soc": app_state.latest_target_soc}


app.include_router(api)

# ---------- Static UI --------------------
app.mount("/", StaticFiles(directory="static", html=True), name="ui")
