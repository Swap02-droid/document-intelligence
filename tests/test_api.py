from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["privacy"].startswith("local-only")


def test_upload_rejects_mismatched_pdf_signature():
    response = client.post(
        "/api/extract",
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
        data={"document_type": "invoice_receipt", "output_format": "json", "dpi": "250"},
    )
    assert response.status_code == 400
    assert "signature" in response.json()["detail"].lower()


def test_end_to_end_job_result_and_download(monkeypatch):
    import time
    from pathlib import Path
    from app.services.job_manager import job_manager
    from app.inference.cactus_engine import FakeMirageEngine

    sample = Path(__file__).resolve().parents[1] / "samples" / "sample_invoice.png"
    monkeypatch.setattr(job_manager, "_engine", FakeMirageEngine())
    with sample.open("rb") as handle:
        response = client.post(
            "/api/extract",
            files={"file": ("sample_invoice.png", handle, "image/png")},
            data={"document_type": "general_table_report", "output_format": "json", "dpi": "250"},
        )
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    deadline = time.time() + 10
    job = None
    while time.time() < deadline:
        job = client.get(f"/api/jobs/{job_id}").json()
        if job["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)
    assert job["status"] == "completed", job
    result = client.get(f"/api/jobs/{job_id}/result")
    assert result.status_code == 200
    assert result.json()["tables"][0]["rows"]
    download = client.get(f"/api/jobs/{job_id}/download")
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/json")


def test_local_frontend_is_served_without_external_assets():
    response = client.get("/")
    assert response.status_code == 200
    assert "Document Intelligence" in response.text
    script = client.get("/static/app.js")
    assert script.status_code == 200
    assert "fetch('/api" not in script.text or "fetch('/api/extract" in script.text
