from functools import lru_cache
from pathlib import Path
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    max_upload_mb: int = Field(default=50, alias="MAX_UPLOAD_MB")
    max_pdf_pages: int = Field(default=50, alias="MAX_PDF_PAGES")
    default_dpi: int = Field(default=250, alias="DEFAULT_DPI")
    max_render_pixels: int = Field(default=18_000_000, alias="MAX_RENDER_PIXELS")
    max_image_edge: int = Field(default=5000, alias="MAX_IMAGE_EDGE")
    max_image_pixels: int = Field(default=18_000_000, alias="MAX_IMAGE_PIXELS")
    job_retention_minutes: int = Field(default=60, alias="JOB_RETENTION_MINUTES")
    temp_dir: str = Field(default="temp", alias="TEMP_DIR")
    export_dir: str = Field(default="temp/exports", alias="EXPORT_DIR")
    cactus_telemetry: str = Field(default="0", alias="CACTUS_TELEMETRY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    @property
    def temp_path(self) -> Path:
        return Path(self.temp_dir).resolve()

    @property
    def export_path(self) -> Path:
        return Path(self.export_dir).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    # Enforce privacy setting before importing/initializing Cactus.
    os.environ["CACTUS_TELEMETRY"] = "0"
    settings.temp_path.mkdir(parents=True, exist_ok=True)
    settings.export_path.mkdir(parents=True, exist_ok=True)
    return settings
