from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4
import os

from app.core.config import get_settings
from app.inference.cactus_engine import CactusMirageEngine, FakeMirageEngine
from app.services.document_service import DocumentService
from app.exporters.exporter import export_result


@dataclass
class Job:
    job_id: str
    status: str = "queued"
    progress: int = 0
    total_pages: int = 0
    message: str = "Queued"
    document_type: str = ""
    output_format: str = "json"
    result: dict[str, Any] | None = None
    export_path: Path | None = None
    export_name: str | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class JobManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._jobs: dict[str, Job] = {}
        self._lock = RLock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="local-document-worker")
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            if os.getenv("DEMO_MODE", "0") == "1":
                self._engine = FakeMirageEngine()
            else:
                self._engine = CactusMirageEngine()
        return self._engine

    def create_job(self, source_path: Path, original_name: str, document_type: str, output_format: str, dpi: int) -> str:
        self.cleanup_expired()
        job_id = uuid4().hex
        job = Job(job_id=job_id, document_type=document_type, output_format=output_format)
        with self._lock:
            self._jobs[job_id] = job
        self._executor.submit(self._run_job, job_id, source_path, original_name, dpi)
        return job_id

    def _progress(self, job_id: str, current: int, total: int, message: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.progress = int((current / total) * 100) if total else 0
                job.total_pages = total
                job.message = message
                job.status = "processing"

    def _run_job(self, job_id: str, source_path: Path, original_name: str, dpi: int) -> None:
        try:
            with self._lock:
                job = self._jobs[job_id]
                job.status = "processing"
                job.message = "Initializing local inference engine"
            engine = self._get_engine()
            service = DocumentService(engine, progress=lambda c, t, m: self._progress(job_id, c, t, m))
            result = service.process(source_path, job.document_type, dpi=dpi)
            export_name = f"{Path(original_name).stem}_extracted.{job.output_format}"
            export_path = self.settings.export_path / f"{job_id}_{export_name}"
            export_result(result, job.output_format, export_path)
            with self._lock:
                job.result = result
                job.export_path = export_path
                job.export_name = export_name
                job.status = "completed"
                job.progress = 100
                job.message = "Extraction completed. Please review the results before relying on them."
        except Exception as exc:
            with self._lock:
                job = self._jobs.get(job_id)
                if job:
                    job.status = "failed"
                    job.error = str(exc)
                    job.message = "Processing failed"
        finally:
            try:
                source_path.unlink(missing_ok=True)
            except OSError:
                pass

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cleanup_expired(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.settings.job_retention_minutes)
        with self._lock:
            expired = [job_id for job_id, job in self._jobs.items() if job.created_at < cutoff and job.status in {"completed", "failed"}]
            for job_id in expired:
                job = self._jobs.pop(job_id)
                if job.export_path:
                    job.export_path.unlink(missing_ok=True)


job_manager = JobManager()
