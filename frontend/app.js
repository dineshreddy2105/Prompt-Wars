/**
 * app.js — CivicBridge AI Frontend Logic
 * Handles: form submission, drag-and-drop, Gemini API call,
 * ticket card rendering, live dashboard, health check.
 */

'use strict';

// ──────────────────────────────────────
// State
// ──────────────────────────────────────
const state = {
  selectedFile: null,
  tickets: [],
  stats: { total: 0, critical: 0, verified: 0 },
};

// ──────────────────────────────────────
// DOM References
// ──────────────────────────────────────
const $ = (id) => document.getElementById(id);

const dom = {
  form:           $('complaintForm'),
  description:    $('description'),
  location:       $('location'),
  imageInput:     $('imageInput'),
  dropZone:       $('dropZone'),
  previewContainer: $('previewContainer'),
  imagePreview:   $('imagePreview'),
  removeImageBtn: $('removeImage'),
  submitBtn:      $('submitBtn'),
  serverUrl:      $('serverUrl'),

  // Status
  serverDot:      $('serverStatusDot'),
  serverText:     $('serverStatusText'),

  // Ticket
  ticketPlaceholder: $('ticketPlaceholder'),
  ticketSkeleton: $('ticketSkeleton'),
  ticketCard:     $('ticketCard'),

  ticketId:       $('ticketId'),
  ticketSubject:  $('ticketSubject'),
  ticketPriority: $('ticketPriority'),
  ticketVerify:   $('ticketVerify'),

  metaCategory:   $('metaCategory'),
  metaDept:       $('metaDept'),
  metaComplexity: $('metaComplexity'),
  metaConfidence: $('metaConfidence'),
  confFill:       $('confFill'),
  cb1: $('cb1'), cb2: $('cb2'), cb3: $('cb3'),

  reportDescription: $('reportDescription'),
  reportVisual:   $('reportVisual'),
  reportHazard:   $('reportHazard'),
  hazardBlock:    $('hazardBlock'),
  citizenMessage: $('citizenMessage'),
  citizenNext:    $('citizenNext'),

  // Dashboard
  dashboardBody:  $('dashboardBody'),
  dashboardEmpty: $('dashboardEmpty'),
  statTotal:      $('statTotal'),
  statCritical:   $('statCritical'),
  statVerified:   $('statVerified'),

  // Error
  errorToast:     $('errorToast'),
  errorMsg:       $('errorMsg'),
  errorClose:     $('errorClose'),
};

// ──────────────────────────────────────
// Priority Helpers
// ──────────────────────────────────────
const PRIORITY_COLORS = {
  1: 'var(--p1)', 2: 'var(--p2)', 3: 'var(--p3)', 4: 'var(--p4)', 5: 'var(--p5)',
};

const PRIORITY_LABELS = {
  1: 'P1 — Low',
  2: 'P2 — Minor',
  3: 'P3 — Moderate',
  4: 'P4 — Serious',
  5: 'P5 — CRITICAL',
};

function priorityClass(score) {
  return `p${Math.max(1, Math.min(5, score))}`;
}

function confidenceConfig(level) {
  const map = {
    High:   { width: '90%',  color: 'var(--verified)' },
    Medium: { width: '55%',  color: 'var(--p3)' },
    Low:    { width: '25%',  color: 'var(--p4)' },
  };
  return map[level] || map['Medium'];
}

function complexityFill(level) {
  const fills = { Low: 1, Medium: 2, High: 3 };
  return fills[level] || 1;
}

// ──────────────────────────────────────
// Server Health Check
// ──────────────────────────────────────
async function checkServer() {
  const base = dom.serverUrl.value.trim().replace(/\/$/, '');
  try {
    const res = await fetch(`${base}/api/health`, { signal: AbortSignal.timeout(4000) });
    if (res.ok) {
      dom.serverDot.style.background = 'var(--verified)';
      dom.serverText.textContent = 'Server Online';
    } else {
      throw new Error('not ok');
    }
  } catch {
    dom.serverDot.style.background = 'var(--p5)';
    dom.serverText.textContent = 'Server Offline';
  }
}

// ──────────────────────────────────────
// Image Drag & Drop
// ──────────────────────────────────────
dom.dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dom.dropZone.classList.add('drag-over');
});

dom.dropZone.addEventListener('dragleave', () => {
  dom.dropZone.classList.remove('drag-over');
});

dom.dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dom.dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    setImage(file);
  }
});

dom.imageInput.addEventListener('change', () => {
  if (dom.imageInput.files[0]) setImage(dom.imageInput.files[0]);
});

dom.removeImageBtn.addEventListener('click', clearImage);

function setImage(file) {
  state.selectedFile = file;
  const url = URL.createObjectURL(file);
  dom.imagePreview.src = url;
  dom.previewContainer.classList.add('visible');
}

function clearImage() {
  state.selectedFile = null;
  dom.imageInput.value = '';
  dom.imagePreview.src = '';
  dom.previewContainer.classList.remove('visible');
}

// ──────────────────────────────────────
// Form Submission
// ──────────────────────────────────────
dom.form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const description = dom.description.value.trim();
  if (!description || description.length < 5) {
    showError('Please describe the issue (at least 5 characters).');
    return;
  }

  setLoading(true);
  hideError();

  const formData = new FormData();
  formData.append('description', description);
  if (dom.location.value.trim()) {
    formData.append('location', dom.location.value.trim());
  }
  if (state.selectedFile) {
    formData.append('image', state.selectedFile, state.selectedFile.name);
  }

  const base = dom.serverUrl.value.trim().replace(/\/$/, '');

  try {
    const res = await fetch(`${base}/api/submit-complaint`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `Server returned ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderTicket(data);
    addDashboardEntry(data);
    updateStats(data);

  } catch (err) {
    showError(`Failed to analyze complaint: ${err.message}`);
    showPlaceholder();
  } finally {
    setLoading(false);
  }
});

// ──────────────────────────────────────
// Loading States
// ──────────────────────────────────────
function setLoading(loading) {
  dom.submitBtn.disabled = loading;
  dom.submitBtn.classList.toggle('loading', loading);

  if (loading) {
    dom.ticketPlaceholder.style.display = 'none';
    dom.ticketCard.classList.remove('visible');
    dom.ticketSkeleton.style.display = 'block';
  } else {
    dom.ticketSkeleton.style.display = 'none';
  }
}

function showPlaceholder() {
  dom.ticketPlaceholder.style.display = 'flex';
  dom.ticketCard.classList.remove('visible');
}

// ──────────────────────────────────────
// Ticket Rendering
// ──────────────────────────────────────
function renderTicket(data) {
  const meta    = data.ticket_metadata   || {};
  const report  = data.official_report   || {};
  const citizen = data.citizen_feedback  || {};
  const score   = meta.priority_score    || 1;
  const verStat = data.verification_status || 'Verified';
  const conf    = data.confidence_level  || 'Medium';

  // Header
  dom.ticketId.textContent      = data.ticket_id || '—';
  dom.ticketSubject.textContent = report.subject_line || 'Civic Complaint';

  // Priority badge
  dom.ticketPriority.textContent  = PRIORITY_LABELS[score] || `P${score}`;
  dom.ticketPriority.className    = `badge-priority ${priorityClass(score)}`;

  // Verification badge
  const isFailed = verStat === 'Verification_Failed';
  dom.ticketVerify.textContent = isFailed ? '⚠ Verify Failed' : '✓ Verified';
  dom.ticketVerify.className   = `badge-verify ${isFailed ? 'failed' : 'verified'}`;

  // Metadata
  dom.metaCategory.textContent  = meta.issue_category        || '—';
  dom.metaDept.textContent      = meta.target_department      || '—';
  dom.metaComplexity.textContent= meta.estimated_repair_complexity || '—';

  // Complexity bars
  const fills = complexityFill(meta.estimated_repair_complexity);
  [dom.cb1, dom.cb2, dom.cb3].forEach((bar, i) => {
    bar.classList.toggle('filled', i < fills);
  });

  // Confidence bar
  const confConf = confidenceConfig(conf);
  dom.metaConfidence.textContent = conf;
  dom.confFill.style.width       = confConf.width;
  dom.confFill.style.background  = confConf.color;

  // Report
  dom.reportDescription.textContent = report.description_formalized  || '—';
  dom.reportVisual.textContent      = report.visual_evidence_summary  || 'No image provided.';

  const hazard = report.safety_hazard_warning || '';
  const noHazard = !hazard || hazard.toLowerCase().includes('no immediate hazard');
  dom.hazardBlock.style.display = noHazard ? 'none' : 'flex';
  dom.reportHazard.textContent  = hazard;

  // Citizen feedback
  dom.citizenMessage.textContent = citizen.status_message || '—';
  dom.citizenNext.textContent    = citizen.next_steps     || '—';

  // Show card
  dom.ticketPlaceholder.style.display = 'none';
  dom.ticketCard.classList.add('visible');
}

// ──────────────────────────────────────
// Dashboard
// ──────────────────────────────────────
function addDashboardEntry(data) {
  const meta   = data.ticket_metadata  || {};
  const report = data.official_report  || {};
  const score  = meta.priority_score   || 1;
  const color  = PRIORITY_COLORS[score] || 'var(--p1)';
  const now    = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  // Remove empty state
  dom.dashboardEmpty && dom.dashboardEmpty.remove();

  const entry = document.createElement('div');
  entry.className = 'dash-entry';
  entry.innerHTML = `
    <div class="dash-dot" style="background:${color};"></div>
    <div class="dash-info">
      <div class="dash-subject">${escHtml(report.subject_line || 'Civic Complaint')}</div>
      <div class="dash-meta">
        <span class="dash-dept">${escHtml(meta.target_department || '—')}</span>
        <span class="dash-sep">·</span>
        <span class="dash-cat">${escHtml(meta.issue_category || '—')}</span>
      </div>
    </div>
    <div class="dash-right">
      <div class="dash-time">${timeStr}</div>
      <div class="dash-id">${escHtml(data.ticket_id || '')}</div>
    </div>
  `;

  // Insert at top
  dom.dashboardBody.insertBefore(entry, dom.dashboardBody.firstChild);
  state.tickets.unshift(data);
}

// ──────────────────────────────────────
// Stats
// ──────────────────────────────────────
function updateStats(data) {
  state.stats.total++;
  if ((data.ticket_metadata?.priority_score || 0) >= 4) state.stats.critical++;
  if (data.verification_status !== 'Verification_Failed')  state.stats.verified++;

  dom.statTotal.textContent    = state.stats.total;
  dom.statCritical.textContent = state.stats.critical;
  dom.statVerified.textContent = state.stats.verified;
}

// ──────────────────────────────────────
// Error Toast
// ──────────────────────────────────────
function showError(msg) {
  dom.errorMsg.textContent  = msg;
  dom.errorToast.style.display = 'flex';
}

function hideError() {
  dom.errorToast.style.display = 'none';
}

dom.errorClose.addEventListener('click', hideError);

// ──────────────────────────────────────
// Utils
// ──────────────────────────────────────
function escHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// ──────────────────────────────────────
// Init
// ──────────────────────────────────────
(function init() {
  checkServer();
  // Re-check server health every 30 seconds
  setInterval(checkServer, 30_000);
  // Re-check when server URL changes
  dom.serverUrl.addEventListener('change', checkServer);
})();
