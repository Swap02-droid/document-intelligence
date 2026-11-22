import os

# Disable anonymous usage telemetry before any Cactus module can be imported.
os.environ["CACTUS_TELEMETRY"] = "0"
os.environ["DO_NOT_TRACK"] = "1"
# Model files must be pre-cached with scripts/download_model.py; runtime inference is offline.
os.environ["HF_HUB_OFFLINE"] = "1"

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

app = FastAPI(
    title="Local Document Intelligence",
    description="Private, on-device document extraction powered by Cactus Mirage.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)
app.include_router(router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("frontend/index.html")
