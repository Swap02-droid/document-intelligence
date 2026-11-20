# document-intelligence

# 📄 MirageDoc — 100% On-Device Document & Table Extractor

**MirageDoc** is a privacy-first, locally running document and table extraction web application powered by **[Cactus Mirage](https://huggingface.co)** (`cactus-compute`), an ultra-compact 51.3M-parameter (~22 MB) vision-language and OCR model.

Upload multi-page PDFs or scanned images containing complex layouts—such as invoices, bank statements, medical forms, or dense tables—and convert them into structured **JSON**, **CSV**, or **Excel (`.xlsx`)** files completely offline.

---

## ✨ Key Features

- **🔒 100% On-Device & Private:** Zero external cloud APIs. All OCR, layout detection, and data structuring happen locally on your machine.
- **📑 Multi-Format Input:** Supports multi-page `.pdf` documents as well as `.png`, `.jpg`, `.jpeg`, and `.webp` images.
- **🗂️ Schema-Driven Document Modes:** Select your document type from a dropdown to apply tailored extraction schemas:
  - *Invoice / Receipt* (Vendor info, totals, itemized line items)
  - *Bank Statement* (Account summary, dates, transaction tables)
  - *Medical Form / Prescription* (Patient details, medications, dosages, lab values)
  - *General Table / Report* (Dynamic column headers and row extraction)
- **🔍 Multi-Pass Table Cropping:** Automatically detects and crops dense table regions at high resolution before inference so small text and multi-column numbers remain accurate on a compact 51.3M model.
- **📊 Flexible Export Formats:** Preview extracted data in the browser and download as `.json`, `.csv`, or `.xlsx`.
- **🌐 WebAssembly-Ready Architecture:** Built first as a modular Python + FastAPI server, designed for future client-side WebAssembly deployment.

---

## 🏗️ Architecture Overview

```text
[PDF / Image Upload]
        │
        ▼
[1. Ingestion & Rendering]  ──► pypdfium2 renders PDF pages at 250–300 DPI
        │
        ▼
[2. Region & Table Cropping] ──► OpenCV / Pillow isolates headers & dense tables
        │
        ▼
[3. Cactus Mirage Inference] ──► Local 51.3M VLM extracts schema-guided JSON
        │
        ▼
[4. Validation & Export]     ──► pandas formats output into JSON / CSV / Excel
```

---

## 📁 Project Structure

```text
document-intelligence/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   │
│   ├── ingestion/
│   │   ├── pdf_processor.py
│   │   └── image_processor.py
│   │
│   ├── preprocessing/
│   │   ├── image_normalizer.py
│   │   ├── layout_detector.py
│   │   └── table_cropper.py
│   │
│   ├── inference/
│   │   ├── base.py
│   │   └── cactus_engine.py
│   │
│   ├── extraction/
│   │   ├── prompts.py
│   │   ├── extractor.py
│   │   └── schemas/
│   │       ├── invoice.py
│   │       ├── bank_statement.py
│   │       ├── medical.py
│   │       └── general_table.py
│   │
│   ├── validation/
│   │   └── validator.py
│   │
│   ├── exporters/
│   │   ├── json_exporter.py
│   │   ├── csv_exporter.py
│   │   └── excel_exporter.py
│   │
│   └── services/
│       └── document_service.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/
│   ├── test_inference.py
│   └── test_extraction.py
│
├── samples/
│
├── temp/
│
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10+**
- 4 GB+ RAM (runs efficiently on CPU, Apple Silicon, or local GPU)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd mirage-doc-extractor
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   # venv\Scripts\activate         # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the local FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

Open your browser and go to:
```text
http://localhost:8000
```

---

## 📦 Core Dependencies

- [`cactus-compute`](https://cactuscompute.com) — Local inference runtime for Cactus Mirage (51.3M VLM/OCR)
- `fastapi` & `uvicorn` — Lightweight local web server
- `pypdfium2` — Fast, dependency-free PDF-to-image rendering
- `opencv-python-headless` & `pillow` — Image deskewing, contrast enhancement, and table cropping
- `pandas` & `openpyxl` — Structured data flattening and CSV/Excel export

---

## 🗺️ Roadmap

- [x] Project architecture & schema design
- [ ] Local Python + FastAPI MVP with document & export dropdowns
- [ ] Multi-pass horizontal row slicing for extra-tall financial tables
- [ ] Batch folder processing via CLI
- [ ] In-browser WebAssembly (WASM) build for zero-server execution

---

## 📄 License

This project is open-source under the **MIT License**.  
The underlying **Cactus Mirage** model weights are licensed under the **Apache 2.0 License** by Cactus Compute.
