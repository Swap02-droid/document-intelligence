const $ = (id) => document.getElementById(id);
const fileInput = $('fileInput');
const dropzone = $('dropzone');
const processButton = $('processButton');
let selectedFile = null;
let pollTimer = null;
let currentJobId = null;

$('dpi').addEventListener('input', () => $('dpiValue').textContent = $('dpi').value);
fileInput.addEventListener('change', () => setFile(fileInput.files[0]));
['dragenter','dragover'].forEach(name => dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.add('dragover'); }));
['dragleave','drop'].forEach(name => dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.remove('dragover'); }));
dropzone.addEventListener('drop', event => setFile(event.dataTransfer.files[0]));

function setFile(file) {
  if (!file) return;
  const allowed = /\.(pdf|png|jpe?g|webp)$/i.test(file.name);
  if (!allowed) { alert('Choose a PDF, PNG, JPG, JPEG or WEBP file.'); return; }
  if (file.size > 50 * 1024 * 1024) { alert('The maximum file size is 50 MB.'); return; }
  selectedFile = file;
  $('dropTitle').textContent = 'Document ready';
  $('dropSubtitle').textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB · Click to change file`;
  $('fileChip').textContent = file.name;
  $('fileChip').classList.remove('hidden');
  processButton.disabled = false;
}

processButton.addEventListener('click', startExtraction);
async function startExtraction() {
  if (!selectedFile) return;
  processButton.disabled = true;
  processButton.querySelector('span:first-child').textContent = 'Submitting…';
  $('resultsPanel').classList.add('hidden');
  $('progressPanel').classList.remove('hidden');
  $('errorBox').classList.add('hidden');
  $('progressBar').style.width = '0%';
  $('progressPercent').textContent = '0%';
  $('statusLabel').textContent = 'Queued';
  const body = new FormData();
  body.append('file', selectedFile);
  body.append('document_type', $('documentType').value);
  body.append('output_format', $('outputFormat').value);
  body.append('dpi', $('dpi').value);
  try {
    const response = await fetch('/api/extract', { method: 'POST', body });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'Unable to submit document.');
    currentJobId = payload.job_id;
    pollJob();
  } catch (error) {
    showError(error.message);
    resetButton();
  }
}

async function pollJob() {
  if (!currentJobId) return;
  try {
    const response = await fetch(`/api/jobs/${currentJobId}`);
    const job = await response.json();
    if (!response.ok) throw new Error(job.detail || 'Unable to read job status.');
    $('progressBar').style.width = `${job.progress || 0}%`;
    $('progressPercent').textContent = `${job.progress || 0}%`;
    $('progressMessage').textContent = job.message || 'Processing…';
    $('statusLabel').textContent = job.status;
    if (job.status === 'completed') {
      const resultResponse = await fetch(`/api/jobs/${currentJobId}/result`);
      const result = await resultResponse.json();
      if (!resultResponse.ok) throw new Error(result.detail || 'Result is not available.');
      renderResult(result);
      $('downloadButton').href = `/api/jobs/${currentJobId}/download`;
      $('progressPanel').classList.add('hidden');
      $('resultsPanel').classList.remove('hidden');
      resetButton();
      return;
    }
    if (job.status === 'failed') throw new Error(job.error || 'Document processing failed.');
    pollTimer = setTimeout(pollJob, 1200);
  } catch (error) {
    showError(error.message);
    resetButton();
  }
}

function showError(message) {
  $('errorBox').textContent = message;
  $('errorBox').classList.remove('hidden');
  $('statusLabel').textContent = 'Failed';
}
function resetButton() {
  processButton.disabled = !selectedFile;
  processButton.querySelector('span:first-child').textContent = 'Extract document';
}

function renderResult(result) {
  $('resultMeta').textContent = `${result.document_name} · ${result.page_count} page(s) · ${result.metrics?.processing_seconds ?? '—'} seconds`;
  $('jsonOutput').textContent = JSON.stringify(result, null, 2);
  renderTable(result.tables?.[0]);
  renderFields(result.extracted_fields || {});
  const warnings = result.warnings || [];
  $('warningsList').innerHTML = '';
  warnings.forEach(warning => { const li = document.createElement('li'); li.textContent = warning; $('warningsList').appendChild(li); });
  $('warningsPanel').classList.toggle('hidden', warnings.length === 0);
}

function renderTable(table) {
  const container = $('tableContainer');
  container.innerHTML = '';
  if (!table || !table.headers?.length) {
    container.innerHTML = '<div class="empty-state">No table could be reconstructed automatically. Open Full JSON to inspect the page OCR summary and review notes.</div>';
    return;
  }
  if (!table.rows?.length) {
    container.innerHTML = '<div class="empty-state">Table headers were detected, but no data rows were reconstructed.</div>';
    return;
  }
  const tableEl = document.createElement('table');
  const thead = document.createElement('thead');
  const headRow = document.createElement('tr');
  table.headers.forEach(header => { const th = document.createElement('th'); th.textContent = header; headRow.appendChild(th); });
  thead.appendChild(headRow); tableEl.appendChild(thead);
  const tbody = document.createElement('tbody');
  table.rows.forEach(row => {
    const tr = document.createElement('tr');
    table.headers.forEach(header => { const td = document.createElement('td'); td.textContent = row[header] ?? ''; tr.appendChild(td); });
    tbody.appendChild(tr);
  });
  tableEl.appendChild(tbody); container.appendChild(tableEl);
}
function renderFields(fields) {
  const container = $('fieldsContainer'); container.innerHTML = '';
  Object.entries(fields).forEach(([key, value]) => {
    const card = document.createElement('div'); card.className = 'field-card';
    const label = document.createElement('span'); label.textContent = key.replaceAll('_', ' ');
    const content = document.createElement('strong'); content.textContent = value === null || value === '' ? 'Not detected' : String(value);
    card.append(label, content); container.appendChild(card);
  });
}

document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(item => item.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(item => item.classList.add('hidden'));
  tab.classList.add('active'); $(tab.dataset.tab).classList.remove('hidden');
}));
