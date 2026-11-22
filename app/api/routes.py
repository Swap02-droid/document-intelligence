from pathlib import Path
from uuid import uuid4
import re

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.core.constants import ALLOWED_EXTENSIONS, DocumentType, OutputFormat
from app.services.job_manager import job_manager
from app.ingestion.pdf_processor import pdf_page_count

router = APIRouter(prefix="/api")


def _safe_name(filename: str | None) -> str:
    name = Path(filename or "document").name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return name or "document"


def _valid_signature(extension: str, data: bytes) -> bool:
    if extension == ".pdf":
        return data.startswith(b"%PDF-")
    if extension == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if extension in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if extension == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False


@router.get("/health")
def health():
    return {
        "status": "ok",
        "application": "Local Document Intelligence",
        "inference": "Cactus Mirage (lazy initialization)",
        "privacy": "local-only; telemetry disabled",
        "demo_mode": __import__("os").getenv("DEMO_MODE", "0") == "1",
    }


@router.post("/extract", status_code=202)
async def submit_extraction(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    output_format: OutputFormat = Form("json"),
    dpi: int = Form(250),
):
    settings = get_settings()
    original_name = _safe_name(file.filename)
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type. Upload PDF, PNG, JPG, JPEG or WEBP.")
    if not 150 <= dpi <= 300:
        raise HTTPException(400, "DPI must be between 150 and 300.")

    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    await file.close()
    if not content:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Maximum upload size is {settings.max_upload_mb} MB.")
    if not _valid_signature(extension, content):
        raise HTTPException(400, "File signature does not match the selected file extension.")

    source_path = settings.temp_path / f"upload_{uuid4().hex}{extension}"
    source_path.write_bytes(content)
    if extension == ".pdf":
        try:
            count = pdf_page_count(source_path)
        except Exception as exc:
            source_path.unlink(missing_ok=True)
            raise HTTPException(400, str(exc)) from exc
        if count > settings.max_pdf_pages:
            source_path.unlink(missing_ok=True)
            raise HTTPException(400, f"This PDF has {count} pages. Maximum allowed: {settings.max_pdf_pages}.")

    job_id = job_manager.create_job(source_path, original_name, document_type.value, output_format.value, dpi)
    return {"job_id": job_id, "status": "queued", "message": "Document accepted for local processing."}


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found or expired.")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "total_pages": job.total_pages,
        "message": job.message,
        "error": job.error,
        "download_ready": bool(job.export_path and job.export_path.exists()),
    }


@router.get("/jobs/{job_id}/result")
def job_result(job_id: str):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found or expired.")
    if job.status != "completed" or job.result is None:
        raise HTTPException(409, "The extraction result is not ready.")
    return job.result


@router.get("/jobs/{job_id}/download")
def download_result(job_id: str):
    job = job_manager.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found or expired.")
    if job.status != "completed" or not job.export_path or not job.export_path.exists():
        raise HTTPException(409, "The export file is not ready.")
    media_types = {"json": "application/json", "csv": "text/csv", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    return FileResponse(job.export_path, filename=job.export_name, media_type=media_types[job.output_format])
