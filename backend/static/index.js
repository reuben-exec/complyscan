/* ==============================================================
   ComplyScan — NABH Compliance Dashboard
   Vanilla SPA: state, views, API, keyboard, theme
   ============================================================== */

/* ==============================================================
   UI Helpers
   ============================================================== */
const ICONS = {
  shield: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5c0 4.3-2.6 8.2-7 10-4.4-1.8-7-5.7-7-10V6l7-3Z"/><path d="M9.5 12.2l1.6 1.6 3.4-3.4"/></svg>',
  clipboard: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4h6a2 2 0 0 1 2 2v1H7V6a2 2 0 0 1 2-2Z"/><path d="M7 7h10a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"/><path d="M9 11h6"/><path d="M9 15h4"/></svg>',
  upload: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v10"/><path d="m8 8 4-4 4 4"/><path d="M5 16v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2"/></svg>',
  check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 13 4 4 10-10"/></svg>',
  alert: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4 3 19h18L12 4Z"/><path d="M12 9v4"/><path d="M12 16h.01"/></svg>',
  spark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3Z"/><path d="m18 15 1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3Z"/></svg>',
  chart: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19V10"/><path d="M12 19V5"/><path d="M19 19v-7"/></svg>',
  pulse: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h3l2-5 3 10 2-5h8"/></svg>',
  file: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h6l4 4v14H7z"/><path d="M13 3v5h5"/></svg>'
};

function iconMarkup(name) {
  return `<span class="icon-svg">${ICONS[name] || ''}</span>`;
}

function setIcon(elementId, name) {
  const el = document.getElementById(elementId);
  if (el) el.innerHTML = iconMarkup(name);
}

const FileUpload = (() => {
  const dropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input');
  const progressArea = document.getElementById('file-upload-progress');
  const successArea = document.getElementById('file-upload-success');
  const statusText = document.getElementById('file-upload-status');
  const filenameSpan = document.getElementById('file-upload-filename');
  const browseLink = document.getElementById('file-browse-link');
  const dismissBtn = document.getElementById('file-upload-dismiss');
  const textarea = document.getElementById('analysis-text');
  const uploadArea = document.getElementById('file-upload-area');
  const uploadIcon = document.getElementById('upload-icon');

  function showProgress(msg) {
    dropzone.style.display = 'none';
    successArea.style.display = 'none';
    progressArea.style.display = 'flex';
    statusText.textContent = msg || 'Extracting text...';
    if (uploadIcon) uploadIcon.innerHTML = iconMarkup('pulse');
  }

  function showSuccess(filename) {
    progressArea.style.display = 'none';
    successArea.style.display = 'flex';
    filenameSpan.textContent = filename;
    dropzone.style.display = 'none';
    if (uploadIcon) uploadIcon.innerHTML = iconMarkup('check');
  }

  function showDropzone() {
    progressArea.style.display = 'none';
    successArea.style.display = 'none';
    dropzone.style.display = 'block';
    if (uploadIcon) uploadIcon.innerHTML = iconMarkup('upload');
  }

  function reset() {
    showDropzone();
    fileInput.value = '';
  }

  async function uploadFile(file) {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['txt', 'pdf', 'docx'].includes(ext)) {
      alert('Unsupported file format. Please upload a .txt, .pdf, or .docx file.');
      return;
    }

    showProgress(`Reading ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const resp = await fetch('/api/extract-text', {
        method: 'POST',
        body: formData
      });

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || `Extraction failed (${resp.status})`);
      }

      const data = await resp.json();
      textarea.value = data.text;
      showSuccess(file.name);

      // Update placeholder to reflect file loaded
      textarea.dataset.loadedFile = file.name;
    } catch (err) {
      alert('File extraction failed: ' + err.message);
      reset();
      textarea.focus();
    }
  }

  /* --- Event wiring --- */

  // Browse link click
  browseLink.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileInput.click();
  });

  // Dropzone click (delegates to file input)
  dropzone.addEventListener('click', () => fileInput.click());

  // File input change
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  });

  // Drag and drop events
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.add('drag-over');
  });

  dropzone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.remove('drag-over');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });

  // Dismiss file
  dismissBtn.addEventListener('click', () => {
    textarea.value = '';
    delete textarea.dataset.loadedFile;
    reset();
    textarea.focus();
  });

  // Clear button also resets file upload state
  document.getElementById('btn-clear-text').addEventListener('click', () => {
    delete textarea.dataset.loadedFile;
    reset();
  });

  return { reset };
})();

/* ==============================================================
   Theme System
   ============================================================== */
const Theme = (() => {
  const STORAGE_KEY = 'complyscan-theme';
  const icon = document.getElementById('theme-icon');

  function getSystemPreference() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (_) {}
  }

  function init() {
    const stored = (() => {
      try { return localStorage.getItem(STORAGE_KEY); } catch (_) { return null; }
    })();
    if (stored === 'light' || stored === 'dark') {
      apply(stored);
    } else {
      apply(getSystemPreference());
    }
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const current = (() => {
        try { return localStorage.getItem(STORAGE_KEY); } catch (_) { return null; }
      })();
      if (!current) {
        apply(e.matches ? 'dark' : 'light');
      }
    });
  }

  function toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    apply(current === 'dark' ? 'light' : 'dark');
  }

  return { init, toggle };
})();

/* ==============================================================
   Shortcuts help overlay
   ============================================================== */
const ShortcutsOverlay = (() => {
  const overlay = document.getElementById('shortcuts-overlay');

  function open() {
    overlay.classList.remove('hidden');
    document.addEventListener('keydown', handleKey);
  }

  function close() {
    overlay.classList.add('hidden');
    document.removeEventListener('keydown', handleKey);
  }

  function toggle() {
    if (overlay.classList.contains('hidden')) open();
    else close();
  }

  function handleKey(e) {
    if (e.key === 'Escape' || e.key === '?') {
      e.preventDefault();
      close();
    }
  }

  document.getElementById('shortcuts-btn').addEventListener('click', open);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });

  return { open, close, toggle };
})();

/* ==============================================================
   Data (Chapters & Requirements)
   ============================================================== */
const CHAPTERS = {
  HIC: {
    code: 'HIC',
    title: 'Hospital Infection Control',
    description: 'Standards for infection prevention, surveillance, and control programs in healthcare facilities.',
    count: 12,
    requirements: [
      { id: 'HIC-R01', title: 'Hand Hygiene Policy', criticality: 'Critical' },
      { id: 'HIC-R02', title: 'Sharps Management', criticality: 'Critical' },
      { id: 'HIC-R03', title: 'Biomedical Waste Disposal', criticality: 'Critical' },
      { id: 'HIC-R04', title: 'Antimicrobial Stewardship', criticality: 'Important' },
      { id: 'HIC-R05', title: 'Hospital Acquired Infection Surveillance', criticality: 'Critical' },
      { id: 'HIC-R06', title: 'Isolation & Barrier Precautions', criticality: 'Important' },
      { id: 'HIC-R07', title: 'Sterilization & Disinfection', criticality: 'Critical' },
      { id: 'HIC-R08', title: 'Antibiotic Usage Policy', criticality: 'Important' },
      { id: 'HIC-R09', title: 'Infection Control Committee', criticality: 'Important' },
      { id: 'HIC-R10', title: 'Tuberculosis Control', criticality: 'Standard' },
      { id: 'HIC-R11', title: 'Staff Immunization Program', criticality: 'Standard' },
      { id: 'HIC-R12', title: 'Outbreak Response Plan', criticality: 'Important' }
    ]
  },
  PRE: {
    code: 'PRE',
    title: 'Patient Rights & Education',
    description: 'Standards for patient rights, informed consent, privacy, and health education programs.',
    count: 12,
    requirements: [
      { id: 'PRE-R01', title: 'Patient Rights Charter', criticality: 'Critical' },
      { id: 'PRE-R02', title: 'Informed Consent Process', criticality: 'Critical' },
      { id: 'PRE-R03', title: 'Patient Confidentiality & Privacy', criticality: 'Critical' },
      { id: 'PRE-R04', title: 'Patient & Family Education', criticality: 'Important' },
      { id: 'PRE-R05', title: 'Grievance Redressal System', criticality: 'Important' },
      { id: 'PRE-R06', title: 'Patient Feedback Mechanism', criticality: 'Important' },
      { id: 'PRE-R07', title: 'End of Life Care & Advance Directives', criticality: 'Standard' },
      { id: 'PRE-R08', title: 'Patient Financial Transparency', criticality: 'Important' },
      { id: 'PRE-R09', title: 'Restraint & Seclusion Protocol', criticality: 'Standard' },
      { id: 'PRE-R10', title: 'Clinical Trial & Research Ethics', criticality: 'Standard' },
      { id: 'PRE-R11', title: 'Patient Identification Protocol', criticality: 'Critical' },
      { id: 'PRE-R12', title: 'Transfer & Discharge Protocol', criticality: 'Important' }
    ]
  }
};

/* ==============================================================
   Override Modal
   ============================================================== */
const OverrideModal = (() => {
  const modal = document.getElementById('override-modal');
  const evidenceName = document.getElementById('modal-evidence-name');
  const statusSelect = document.getElementById('modal-status');
  const reasonInput = document.getElementById('modal-reason');
  const cancelBtn = document.getElementById('modal-cancel');
  const confirmBtn = document.getElementById('modal-confirm');

  let currentEvidence = null;
  let currentResults = null;

  function open(evidenceId, evidenceText, currentStatus, results) {
    currentEvidence = evidenceId;
    currentResults = results;
    evidenceName.textContent = evidenceText;
    statusSelect.value = currentStatus === 'NOT_FOUND' ? 'NOT_FOUND' : currentStatus;
    reasonInput.value = '';
    modal.classList.remove('hidden');
    statusSelect.focus();
  }

  function close() {
    modal.classList.add('hidden');
    currentEvidence = null;
    currentResults = null;
  }

  cancelBtn.addEventListener('click', close);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) close();
  });

  confirmBtn.addEventListener('click', async () => {
    if (!currentEvidence || !currentResults) return;
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner"></span>';
    try {
      const resp = await fetch('/api/override', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          result: currentResults,
          evidence_id: currentEvidence,
          new_status: statusSelect.value,
          override_note: reasonInput.value.trim() || ''
        })
      });
      if (!resp.ok) throw new Error(`Override failed (${resp.status})`);
      const data = await resp.json();
      close();
      App.refreshResults(data.result);
    } catch (err) {
      confirmBtn.textContent = 'Error — Try Again';
      setTimeout(() => { confirmBtn.disabled = false; confirmBtn.textContent = 'Confirm Override'; }, 2000);
    }
  });

  return { open, close };
})();

/* ==============================================================
   App State & Navigation
   ============================================================== */
const App = (() => {
  const state = {
    currentView: 'chapters',
    currentChapter: null,
    currentRequirement: null,
    currentResults: null,
    focusedIndex: 0,
    searchQuery: '',
    isAnalyzing: false,
    reviewHistory: []
  };

  /* --- View switching --- */
  function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const view = document.getElementById(viewId);
    if (view) {
      view.classList.add('active');
      view.style.animation = 'none';
      requestAnimationFrame(() => { view.style.animation = ''; });
    }
  }

  /* --- Chapter Selection (View A) --- */
  function renderChapters() {
    const grid = document.getElementById('chapter-grid');
    grid.innerHTML = '';
    Object.values(CHAPTERS).forEach(ch => {
      const card = document.createElement('button');
      card.className = 'chapter-card';
      card.setAttribute('data-chapter', ch.code);
      card.setAttribute('aria-label', `${ch.code}: ${ch.title}`);
      const iconName = ch.code === 'HIC' ? 'shield' : 'clipboard';
      card.innerHTML = `
        <div class="chapter-card-top">
          <span class="chapter-icon">${iconMarkup(iconName)}</span>
          <span class="chapter-code">${ch.code}</span>
        </div>
        <h2>${ch.title}</h2>
        <p>${ch.description}</p>
        <div class="chapter-meta"><span>${iconMarkup('file')} ${ch.count} requirements</span></div>
      `;
      card.addEventListener('click', () => goToRequirements(ch.code));
      grid.appendChild(card);
    });
  }

  /* --- Requirement List (View B) --- */
  function renderRequirements(chapterCode) {
    state.currentChapter = chapterCode;
    state.focusedIndex = 0;
    state.searchQuery = '';
    state.currentResults = null;

    const ch = CHAPTERS[chapterCode];
    if (!ch) return;

    document.getElementById('bc-chapter-name').textContent = chapterCode;
    document.getElementById('req-chapter-title').textContent = ch.title;
    document.getElementById('req-search').value = '';

    showView('view-requirements');
    renderFilteredRequirements(ch, '');
    document.getElementById('req-search').focus();
  }

  function renderFilteredRequirements(ch, query) {
    const container = document.getElementById('req-list-container');
    const q = query.toLowerCase().trim();
    const filtered = ch.requirements.filter(r =>
      r.id.toLowerCase().includes(q) || r.title.toLowerCase().includes(q)
    );

    if (filtered.length === 0) {
      container.innerHTML = `<div class="req-list-empty">No requirements match your search.</div>`;
      return;
    }

    const list = document.createElement('div');
    list.className = 'req-list';
    list.setAttribute('role', 'listbox');
    list.setAttribute('aria-label', 'Requirements');

    filtered.forEach((r, idx) => {
      const item = document.createElement('div');
      item.className = 'req-item' + (idx === 0 && state.currentView === 'requirements' ? ' active' : '');
      item.setAttribute('role', 'option');
      item.setAttribute('aria-selected', String(idx === 0));
      item.setAttribute('tabindex', '0');
      item.dataset.index = idx;
      item.dataset.reqId = r.id;

      const pillClass = r.criticality === 'Critical' ? 'pill-critical'
        : r.criticality === 'Important' ? 'pill-important'
        : 'pill-standard';

      item.innerHTML = `
        <span class="req-id">${r.id}</span>
        <div class="req-info">
          <div class="req-title">${r.title}</div>
          <div class="req-criticality"><span class="pill ${pillClass}">${r.criticality}</span></div>
        </div>
        <div class="req-actions">
          <button class="btn btn-primary btn-sm analyze-btn" data-req-id="${r.id}">Analyze</button>
        </div>
      `;

      item.addEventListener('click', (e) => {
        if (e.target.closest('.analyze-btn')) return;
        selectReqItem(idx);
      });

      item.querySelector('.analyze-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        goToAnalysis(ch.code, r.id);
      });

      item.addEventListener('dblclick', () => {
        goToAnalysis(ch.code, r.id);
      });

      list.appendChild(item);
    });

    container.innerHTML = '';
    container.appendChild(list);

    const items = container.querySelectorAll('.req-item');
    if (items.length > 0) {
      const idx = Math.min(state.focusedIndex, items.length - 1);
      items[idx].classList.add('active');
      items[idx].setAttribute('aria-selected', 'true');
      items[idx].focus();
    }
  }

  function selectReqItem(index) {
    const items = document.querySelectorAll('#req-list-container .req-item');
    if (index < 0) index = 0;
    if (index >= items.length) index = items.length - 1;
    items.forEach(el => {
      el.classList.remove('active');
      el.setAttribute('aria-selected', 'false');
    });
    if (items[index]) {
      items[index].classList.add('active');
      items[index].setAttribute('aria-selected', 'true');
      items[index].focus();
      state.focusedIndex = index;
    }
  }

  /* --- Analysis (View C) --- */
  function goToAnalysis(chapterCode, reqId) {
    state.currentChapter = chapterCode;
    state.currentRequirement = reqId;
    state.currentResults = null;
    state.isAnalyzing = false;

    const ch = CHAPTERS[chapterCode];
    const req = ch.requirements.find(r => r.id === reqId);
    if (!req) return;

    document.getElementById('bc-back-reqs').textContent = chapterCode;
    document.getElementById('bc-req-name').textContent = `${reqId}: ${req.title}`;

    document.getElementById('analysis-text').value = '';
    document.getElementById('results-content').style.display = 'none';
    document.getElementById('results-empty').style.display = 'flex';
    document.getElementById('results-loading').style.display = 'none';
    document.getElementById('results-error').style.display = 'none';
    document.getElementById('btn-download-pdf').style.display = 'inline-flex';

    showView('view-analysis');
    document.getElementById('analysis-text').focus();
  }

  /* --- Results Rendering --- */
  function refreshResults(data) {
    state.currentResults = data;
    renderResults(data);
  }

  function normalizeStatus(status) {
    const value = String(status || 'Not Found').replace(/_/g, ' ').trim();
    if (!value) return 'Not Found';
    const lowered = value.toLowerCase();
    if (lowered === 'compliant') return 'Compliant';
    if (lowered === 'partial') return 'Partial';
    if (lowered === 'non compliant' || lowered === 'non-compliant') return 'Non-Compliant';
    if (lowered === 'not found' || lowered === 'not_found' || lowered === 'not-found') return 'Not Found';
    return value;
  }

  function getStatusClass(status) {
    const normalized = normalizeStatus(status);
    return normalized === 'Compliant' ? 'badge-compliant'
      : normalized === 'Partial' ? 'badge-partial'
      : normalized === 'Non-Compliant' ? 'badge-non-compliant'
      : 'badge-not-found';
  }

  function renderStatusBreakdown(evidence) {
    const container = document.getElementById('status-breakdown');
    container.innerHTML = '';

    if (!evidence.length) {
      container.innerHTML = '<div class="status-breakdown-empty">No evidence items were returned for this review.</div>';
      return;
    }

    const counts = {
      Compliant: 0,
      Partial: 0,
      'Non-Compliant': 0,
      'Not Found': 0
    };

    evidence.forEach(ev => {
      const status = normalizeStatus(ev.status || 'Not Found');
      counts[status] = (counts[status] || 0) + 1;
    });

    ['Compliant', 'Partial', 'Non-Compliant', 'Not Found'].forEach(label => {
      const value = counts[label] || 0;
      const pct = evidence.length ? Math.round((value / evidence.length) * 100) : 0;
      const row = document.createElement('div');
      row.className = 'status-row';
      row.innerHTML = `
        <span class="status-row-label">${label}</span>
        <div class="status-row-bar"><span style="width:${pct}%"></span></div>
        <strong>${value}</strong>
      `;
      container.appendChild(row);
    });
  }

  function renderEvidenceNavigator(evidence) {
    const container = document.getElementById('evidence-navigator');
    if (!container) return;

    if (!evidence.length) {
      container.innerHTML = '<div class="navigator-empty">Evidence will appear here as soon as the review completes.</div>';
      return;
    }

    container.innerHTML = '';
    evidence.forEach((ev) => {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'navigator-item';
      item.dataset.evidenceId = ev.evidence_id || '';
      const evStatus = normalizeStatus(ev.status || 'Not Found');
      const badgeClass = getStatusClass(evStatus);
      item.innerHTML = `
        <span class="navigator-title">${escapeHtml(ev.name || ev.evidence_id || 'Evidence')}</span>
        <span class="badge ${badgeClass}">${escapeHtml(evStatus)}</span>
      `;
      item.addEventListener('click', () => {
        const row = document.querySelector(`tr[data-evidence-id="${CSS.escape(ev.evidence_id || '')}"]`);
        if (row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      container.appendChild(item);
    });
  }

  function renderReviewTimeline() {
    const container = document.getElementById('review-timeline');
    if (!container) return;

    if (!state.reviewHistory.length) {
      container.innerHTML = '<div class="timeline-empty">Repeated reviews will appear here after you run the analysis more than once.</div>';
      return;
    }

    container.innerHTML = '';
    state.reviewHistory.slice().reverse().forEach((entry) => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      item.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <strong>${escapeHtml(entry.requirementId || 'Review')}</strong>
          <span>${escapeHtml(entry.timestamp || '')}</span>
          <small>${entry.score}% • ${escapeHtml(entry.status || 'Review')}</small>
        </div>
      `;
      container.appendChild(item);
    });
  }

  function renderResults(data) {
    if (!data) return;

    document.getElementById('results-empty').style.display = 'none';
    document.getElementById('results-loading').style.display = 'none';
    document.getElementById('results-error').style.display = 'none';
    document.getElementById('results-content').style.display = 'block';

    const evidence = data.evidence_items || [];
    const scoreRaw = data.compliance_score != null ? data.compliance_score : 0;
    const score = Math.round(scoreRaw * 100);
    const cappedScore = Math.min(100, Math.max(0, score));

    const pctEl = document.getElementById('score-pct');
    const barEl = document.getElementById('score-bar');
    const ringEl = document.getElementById('score-ring');
    const badgeEl = document.getElementById('status-badge');
    const metaEl = document.getElementById('analysis-meta');
    const subtitleEl = document.getElementById('score-subtitle');
    const analyticsNoteEl = document.getElementById('analytics-note');
    const summaryConfidenceEl = document.getElementById('summary-confidence');
    const summaryStrengthEl = document.getElementById('summary-strength');
    const summaryPriorityEl = document.getElementById('summary-priority');
    const evidenceCountEl = document.getElementById('metric-evidence-count');
    const criticalCountEl = document.getElementById('metric-critical-count');
    const overrideCountEl = document.getElementById('metric-override-count');
    const llmCountEl = document.getElementById('metric-llm-count');

    pctEl.textContent = `${cappedScore}%`;

    const scoreColor = cappedScore >= 85 ? 'var(--success)'
      : cappedScore >= 40 ? 'var(--warning)'
      : 'var(--danger)';
    pctEl.style.color = scoreColor;
    barEl.style.background = scoreColor;
    ringEl.style.setProperty('--score-color', scoreColor);
    ringEl.style.setProperty('--score-degree', String(cappedScore));

    requestAnimationFrame(() => {
      barEl.style.width = `${cappedScore}%`;
    });

    const status = normalizeStatus(data.overall_status || data.status || 'NOT_FOUND');
    const badgeClass = getStatusClass(status);
    badgeEl.className = `badge ${badgeClass}`;
    badgeEl.textContent = status;

    const hasLLM = evidence.some(e => e.llm_evaluated);
    const hasOverride = evidence.some(e => e.manually_overridden);
    const criticalCount = evidence.filter(e => e.critical).length;
    const tags = [];
    if (hasLLM) tags.push('LLM-enhanced');
    if (hasOverride) tags.push('includes overrides');
    metaEl.textContent = tags.length ? tags.join(' · ') : 'Deterministic review summary';

    const subtitle = cappedScore >= 85 ? 'Strong alignment with policy intent' : cappedScore >= 40 ? 'Targeted follow-up recommended' : 'Immediate review and remediation advised';
    subtitleEl.textContent = subtitle;
    analyticsNoteEl.textContent = `${evidence.length} evidence points • ${criticalCount} critical checks`;

    const confidenceLabel = cappedScore >= 85 ? 'High confidence' : cappedScore >= 60 ? 'Moderate confidence' : 'Lower confidence';
    const strengthLabel = cappedScore >= 85 ? 'Strong evidence alignment' : cappedScore >= 40 ? 'Mixed evidence clarity' : 'Needs stronger evidence';
    const priorityLabel = cappedScore >= 85 ? 'Maintain monitoring' : cappedScore >= 40 ? 'Prioritize remediation' : 'Escalate for immediate action';

    summaryConfidenceEl.textContent = confidenceLabel;
    summaryStrengthEl.textContent = strengthLabel;
    summaryPriorityEl.textContent = priorityLabel;

    evidenceCountEl.textContent = evidence.length;
    criticalCountEl.textContent = criticalCount;
    overrideCountEl.textContent = evidence.filter(e => e.manually_overridden).length;
    llmCountEl.textContent = evidence.filter(e => e.llm_evaluated).length;

    renderStatusBreakdown(evidence);
    renderEvidenceNavigator(evidence);
    renderReviewTimeline();

    const tbody = document.getElementById('evidence-body');
    tbody.innerHTML = '';

    evidence.forEach(ev => {
      const tr = document.createElement('tr');
      tr.dataset.evidenceId = ev.evidence_id || '';

      const evStatus = normalizeStatus(ev.status || 'Not Found');
      const statusClass = getStatusClass(evStatus);

      const tagsHtml = [];
      if (ev.llm_evaluated) tagsHtml.push('<span class="tag tag-llm">LLM</span>');
      if (ev.llm_disagreement) tagsHtml.push('<span class="tag tag-disagreement">⚠ Override</span>');
      if (ev.manually_overridden) tagsHtml.push('<span class="tag tag-override">Manual</span>');

      tr.innerHTML = `
        <td><span class="cell-name" title="${escapeAttr(ev.evidence_id || '')}">${escapeHtml(ev.evidence_id || '')}</span></td>
        <td><span class="cell-name" title="${escapeAttr(ev.name || '')}">${escapeHtml(ev.name || '')}</span></td>
        <td>${escapeHtml(ev.type || '-')}</td>
        <td>${ev.critical ? 'Yes' : 'No'}</td>
        <td><span class="badge ${statusClass}">${escapeHtml(evStatus.replace(/_/g, ' '))}</span> ${tagsHtml.join(' ')}</td>
        <td><span class="cell-justification" title="${escapeAttr(ev.justification || '')}">${escapeHtml(ev.justification || '-')}</span></td>
        <td class="cell-action">
          <button class="override-btn${ev.manually_overridden ? ' active' : ''}"
                  data-evidence-id="${escapeAttr(ev.evidence_id || '')}"
                  data-evidence-name="${escapeAttr(ev.name || ev.evidence_id || '')}"
                  data-evidence-status="${escapeAttr(evStatus)}">
            Override
          </button>
        </td>
      `;

      tbody.appendChild(tr);
    });

    tbody.querySelectorAll('.override-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        OverrideModal.open(
          btn.dataset.evidenceId,
          btn.dataset.evidenceName,
          btn.dataset.evidenceStatus,
          data
        );
      });
    });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
  function escapeAttr(str) {
    return escapeHtml(str).replace(/"/g, '&quot;');
  }

  /* --- Loading / Error / Empty --- */
  function showResultsLoading() {
    document.getElementById('results-empty').style.display = 'none';
    document.getElementById('results-content').style.display = 'none';
    document.getElementById('results-error').style.display = 'none';
    document.getElementById('results-loading').style.display = 'block';
  }

  function showResultsError(msg) {
    document.getElementById('results-empty').style.display = 'none';
    document.getElementById('results-content').style.display = 'none';
    document.getElementById('results-loading').style.display = 'none';
    document.getElementById('results-error').style.display = 'block';
    document.getElementById('error-message').textContent = msg || 'Analysis failed. Please try again.';
  }

  /* --- Analysis API --- */
  async function runAnalysis(pass2) {
    const text = document.getElementById('analysis-text').value.trim();
    if (!text) {
      showResultsError('Please enter or paste document text before analyzing.');
      return;
    }
    if (state.isAnalyzing) return;
    state.isAnalyzing = true;

    const reqId = state.currentRequirement;
    if (!reqId) return;

    const endpoint = pass2
      ? `/api/analyze-semantic/${reqId}`
      : `/api/analyze-text/${reqId}`;

    showResultsLoading();
    disableAnalyzeButtons(true);

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: text
      });
      if (!resp.ok) {
        const errText = await resp.text().catch(() => '');
        throw new Error(errText || `Analysis failed (${resp.status})`);
      }
      const data = await resp.json();
      state.reviewHistory.push({
        requirementId: state.currentRequirement || 'Review',
        score: Math.round((data.compliance_score != null ? data.compliance_score : 0) * 100),
        status: normalizeStatus(data.overall_status || data.status || 'NOT_FOUND'),
        timestamp: new Date().toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
      });
      state.reviewHistory = state.reviewHistory.slice(-6);
      state.currentResults = data;
      renderResults(data);
    } catch (err) {
      showResultsError(err.message);
    } finally {
      state.isAnalyzing = false;
      disableAnalyzeButtons(false);
    }
  }

  function disableAnalyzeButtons(disabled) {
    const b1 = document.getElementById('btn-analyze-pass1');
    const b2 = document.getElementById('btn-analyze-pass2');
    [b1, b2].forEach(b => {
      if (disabled) {
        // Save original content before changing
        if (!b.getAttribute('data-original')) {
          b.setAttribute('data-original', b.innerHTML);
        }
        b.disabled = true;
        b.innerHTML = '<span class="spinner"></span> Analyzing\u2026';
      } else {
        b.disabled = false;
        b.innerHTML = b.getAttribute('data-original') || 'Analyze';
      }
    });
  }

  /* --- PDF Download --- */
  async function downloadPDF() {
    const results = state.currentResults;
    if (!results) {
      showResultsError('No results to export. Run an analysis first.');
      return;
    }

    const btn = document.getElementById('btn-download-pdf');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';

    try {
      const resp = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(results)
      });
      if (!resp.ok) throw new Error(`Report generation failed (${resp.status})`);
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ComplyScan_${state.currentRequirement || 'report'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      showResultsError(err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '\u2B07 Download PDF Report';
    }
  }

  /* --- Navigation helpers --- */
  function goToChapters() {
    state.currentView = 'chapters';
    state.currentChapter = null;
    state.currentRequirement = null;
    state.currentResults = null;
    showView('view-chapters');
  }

  function goToRequirements(chapterCode) {
    state.currentView = 'requirements';
    state.currentChapter = chapterCode;
    state.currentRequirement = null;
    state.currentResults = null;
    renderRequirements(chapterCode);
  }

  function goBack() {
    if (state.currentView === 'analysis') {
      if (state.currentChapter) {
        goToRequirements(state.currentChapter);
      } else {
        goToChapters();
      }
    } else if (state.currentView === 'requirements') {
      goToChapters();
    }
  }

  /* --- Sample text --- */
  function insertSampleText() {
    const samples = {
      'HIC-R01': 'Hand hygiene is performed by all healthcare workers before and after patient contact. '
        + 'Alcohol-based hand rub is available at all points of care. '
        + 'Compliance with hand hygiene protocols is monitored monthly and feedback is provided to staff. '
        + 'Hand hygiene training is conducted annually for all clinical staff.',
      'HIC-R02': 'Sharps containers are puncture-resistant and located in all clinical areas. '
        + 'Needles are not recapped after use. Disposal follows biomedical waste rules.',
      'PRE-R01': 'Patients are provided with a charter of rights upon admission. '
        + 'The charter includes information about treatment, consent, and grievance mechanisms. '
        + 'Staff are trained on patient rights annually.'
    };
    const textarea = document.getElementById('analysis-text');
    textarea.value = samples[state.currentRequirement] || Object.values(samples)[0];
  }

  function isInView(viewId) {
    const view = document.getElementById(viewId);
    return view && view.classList.contains('active');
  }

  return {
    state,
    renderChapters,
    goToChapters,
    goToRequirements,
    goToAnalysis,
    refreshResults,
    renderResults,
    runAnalysis,
    downloadPDF,
    goBack,
    insertSampleText,
    isInView,
    selectReqItem,
    renderFilteredRequirements
  };
})();

/* ==============================================================
   Event Wiring
   ============================================================== */
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  setIcon('nav-brand-icon', 'shield');
  setIcon('upload-icon', 'upload');
  setIcon('empty-state-icon', 'clipboard');
  setIcon('metric-evidence-icon', 'clipboard');
  setIcon('metric-critical-icon', 'alert');
  setIcon('metric-override-icon', 'spark');
  setIcon('metric-llm-icon', 'chart');
  App.renderChapters();

  // Breadcrumb clicks
  document.querySelectorAll('[data-action="go-chapters"]').forEach(el => {
    el.addEventListener('click', (e) => { e.preventDefault(); App.goToChapters(); });
  });
  document.querySelectorAll('[data-action="go-requirements"]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      if (App.state.currentChapter) App.goToRequirements(App.state.currentChapter);
    });
  });

  // Search
  const searchInput = document.getElementById('req-search');
  searchInput.addEventListener('input', (e) => {
    App.state.searchQuery = e.target.value;
    const ch = CHAPTERS[App.state.currentChapter];
    if (ch) App.renderFilteredRequirements(ch, e.target.value);
  });

  // Analysis buttons
  document.getElementById('btn-analyze-pass1').addEventListener('click', () => App.runAnalysis(false));
  document.getElementById('btn-analyze-pass2').addEventListener('click', () => App.runAnalysis(true));

  // Clear / Sample text
  document.getElementById('btn-clear-text').addEventListener('click', () => {
    document.getElementById('analysis-text').value = '';
    document.getElementById('analysis-text').focus();
  });
  document.getElementById('btn-sample-text').addEventListener('click', App.insertSampleText);

  // PDF download
  document.getElementById('btn-download-pdf').addEventListener('click', App.downloadPDF);

  // Error dismiss
  document.getElementById('error-close').addEventListener('click', () => {
    document.getElementById('results-error').style.display = 'none';
  });

  // Theme toggle
  document.getElementById('theme-toggle').addEventListener('click', Theme.toggle);
});

/* ==============================================================
   Keyboard Shortcuts
   ============================================================== */
document.addEventListener('keydown', (e) => {
  const tag = e.target.tagName;
  const isInput = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';

  // Always-available shortcuts
  if (e.key === 't' && !isInput) {
    e.preventDefault();
    Theme.toggle();
    return;
  }

  if (e.key === '?' && !isInput) {
    e.preventDefault();
    ShortcutsOverlay.toggle();
    return;
  }

  if (e.key === 'Escape' && !isInput) {
    if (!document.getElementById('override-modal').classList.contains('hidden')) {
      OverrideModal.close();
      return;
    }
    if (!document.getElementById('shortcuts-overlay').classList.contains('hidden')) {
      ShortcutsOverlay.close();
      return;
    }
    App.goBack();
    return;
  }

  // View-specific: Requirement List
  if (App.isInView('view-requirements')) {
    if (e.key === '/' && !isInput) {
      e.preventDefault();
      document.getElementById('req-search').focus();
      return;
    }
    if ((e.key === 'j' || e.key === 'k') && !isInput) {
      e.preventDefault();
      const items = document.querySelectorAll('#req-list-container .req-item');
      if (!items.length) return;
      const dir = e.key === 'j' ? 1 : -1;
      const next = Math.max(0, Math.min(items.length - 1, App.state.focusedIndex + dir));
      App.selectReqItem(next);
      return;
    }
    if (e.key === 'Enter' && !isInput) {
      const items = document.querySelectorAll('#req-list-container .req-item');
      const focused = items[App.state.focusedIndex];
      if (focused && App.state.currentChapter) {
        const reqId = focused.dataset.reqId;
        if (reqId) App.goToAnalysis(App.state.currentChapter, reqId);
      }
      return;
    }
  }

  // View-specific: Analysis
  if (App.isInView('view-analysis')) {
    if (e.key === '1' && !isInput) {
      e.preventDefault();
      App.runAnalysis(false);
      return;
    }
    if (e.key === '2' && !isInput) {
      e.preventDefault();
      App.runAnalysis(true);
      return;
    }
    if (e.key === 'o' && !isInput) {
      e.preventDefault();
      const btn = document.querySelector('#evidence-body .override-btn');
      if (btn) btn.click();
      return;
    }
    if (e.key === 'p' && !isInput) {
      e.preventDefault();
      App.downloadPDF();
      return;
    }
    if (e.key === '.' && !isInput) {
      e.preventDefault();
      document.getElementById('analysis-text').value = '';
      return;
    }
  }
});
