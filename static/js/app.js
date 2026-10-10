/**
 * Inspection Paper - Dashboard Application Controller
 */

// Application State
const state = {
  auth: {
    is_authenticated: false,
    auth_mode: 'none',
    is_configured: false,
    user: null,
  },
  drive: {
    folder_id: '1A2b3C4d_LIS2025_ExamMid',
    folder_name: '2025_Spring_Midterm_Exams',
    folder_path: 'LIS_Drive / 2025_Spring / Midterm_Official',
    synced_at: '-',
    total_subjects: 0,
    uploaded_count: 0,
    approved_count: 0,
    files: [],
  },
  activeFilter: 'all',
  searchQuery: '',
  activeDocId: 'g10_eng',
  currentDocData: null,
  isJsonViewOpen: false,
};

// Subject mapping
const DOC_KEY_MAP = {
  'gdoc_001_eng': 'g10_eng',
  'gdoc_002_math': 'g11_math',
  'docx_003_hist': 'g9_hist',
  'gdoc_004_kor': 'g10_kor',
  'empty_005_bio': 'g12_bio',
  'g10_eng': 'g10_eng',
  'g11_math': 'g11_math',
  'g9_hist': 'g9_hist',
  'g10_kor': 'g10_kor',
  'g12_bio': 'g12_bio',
};

// Notification Toast
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  const bgColors = {
    info: 'bg-primary text-on-primary',
    success: 'bg-secondary text-white',
    warning: 'bg-tertiary-container text-tertiary',
    error: 'bg-error text-white',
  };

  toast.className = `px-4 py-2.5 rounded-xl text-xs font-semibold shadow-lg flex items-center gap-2 transition-all transform translate-y-2 opacity-0 ${bgColors[type] || bgColors.info}`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-[18px]">
      ${type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info'}
    </span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Navigation Tab Active Style
function setActiveNav(navKey) {
  const btnDashboard = document.getElementById('navDashboardBtn');
  const btnAudit = document.getElementById('navAuditBtn');
  const btnSettings = document.getElementById('navSettingsBtn');

  if (navKey === 'dashboard') {
    btnDashboard.className = 'px-3.5 py-1.5 rounded-lg bg-primary-container text-on-primary transition-all';
    btnAudit.className = 'px-3.5 py-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container transition-colors';
    btnSettings.className = 'px-3.5 py-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container transition-colors flex items-center gap-1';
  }
}

// UI State Renderers
function renderHeader(user) {
  const headerUserCard = document.getElementById('headerUserCard');
  const headerUserName = document.getElementById('headerUserName');
  const headerUserEmail = document.getElementById('headerUserEmail');

  if (user && user.is_authenticated) {
    headerUserCard.classList.remove('hidden');
    headerUserName.textContent = user.name || 'Vice Principal Kyumun Hwang';
    headerUserEmail.textContent = user.email || 'kyumun.hwang@gmail.com';
  } else {
    headerUserCard.classList.add('hidden');
  }
}

function renderAuthCard(auth) {
  const authStatusBadge = document.getElementById('authStatusBadge');
  const authUserEmail = document.getElementById('authUserEmail');
  const authRoleBadge = document.getElementById('authRoleBadge');
  const authActionBtn = document.getElementById('authActionBtn');
  const mockSwitchBtn = document.getElementById('mockSwitchBtn');
  const apiStatusText = document.getElementById('apiStatusText');

  if (auth.is_authenticated && auth.user) {
    const isMock = auth.auth_mode === 'mock';
    authStatusBadge.className = `inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
      isMock ? 'bg-surface-container-high text-primary' : 'bg-secondary-fixed text-on-secondary-fixed-variant'
    }`;
    authStatusBadge.innerHTML = `
      <span class="w-1.5 h-1.5 rounded-full ${isMock ? 'bg-primary' : 'bg-secondary'}"></span>
      ${isMock ? 'Mock Simulation Mode' : 'OAuth 2.0 Connected'}
    `;

    authUserEmail.textContent = auth.user.email || 'kyumun.hwang@gmail.com';
    authRoleBadge.textContent = auth.user.role || 'Vice Principal (Administrator)';
    apiStatusText.innerHTML = `
      <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
      ${isMock ? 'Simulation Adapter Active (Read-only)' : 'Google Drive & Docs API v3 Active'}
    `;

    authActionBtn.innerHTML = `
      <span class="material-symbols-outlined text-[15px]">logout</span>
      Sign Out
    `;
    authActionBtn.onclick = handleSignOut;

    mockSwitchBtn.classList.remove('hidden');
    mockSwitchBtn.textContent = isMock ? 'Connect Real Google Account' : 'Switch to Mock Mode';
    mockSwitchBtn.onclick = () => {
      if (isMock) {
        triggerRealGoogleLogin();
      } else {
        handleMockSignIn();
      }
    };
  } else {
    authStatusBadge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-error-container text-on-error-container text-xs font-semibold';
    authStatusBadge.innerHTML = `
      <span class="w-1.5 h-1.5 rounded-full bg-error"></span>
      Not Signed In
    `;
    authUserEmail.textContent = 'Sign in required to inspect Drive folder';
    authRoleBadge.textContent = 'Guest';
    apiStatusText.innerHTML = `
      <span class="material-symbols-outlined text-[16px] text-outline-variant">lock</span>
      Authentication Required
    `;

    authActionBtn.innerHTML = `
      <span class="material-symbols-outlined text-[15px]">login</span>
      Sign In with Google
    `;
    authActionBtn.onclick = triggerRealGoogleLogin;

    mockSwitchBtn.classList.remove('hidden');
    mockSwitchBtn.textContent = 'Sign In as Mock Admin';
    mockSwitchBtn.onclick = handleMockSignIn;
  }
}

function triggerRealGoogleLogin() {
  if (!state.auth.is_configured) {
    // Show settings modal with clear guidance
    openSettingsModal();
    showToast('Google OAuth Credentials required to connect real account.', 'warning');
  } else {
    window.location.href = '/api/auth/google/login';
  }
}

function renderMetrics(drive) {
  const metricTotalSubjects = document.getElementById('metricTotalSubjects');
  const metricUploaded = document.getElementById('metricUploaded');
  const metricUploadedPercent = document.getElementById('metricUploadedPercent');
  const metricProgressBar = document.getElementById('metricProgressBar');
  const metricApproved = document.getElementById('metricApproved');
  const metricPending = document.getElementById('metricPending');

  const total = drive.total_subjects || drive.files.length || 0;
  const uploaded = drive.uploaded_count || 0;
  const approved = drive.approved_count || 0;
  const pending = Math.max(0, uploaded - approved);

  const percent = total > 0 ? ((uploaded / total) * 100).toFixed(1) : '0.0';

  metricTotalSubjects.textContent = total;
  metricUploaded.textContent = uploaded;
  metricUploadedPercent.textContent = `/ ${total} (${percent}%)`;
  metricProgressBar.style.width = `${percent}%`;

  metricApproved.textContent = approved;
  metricPending.innerHTML = `
    <span class="material-symbols-outlined text-[15px]">pending_actions</span>
    Pending Review: ${pending} papers
  `;
}

function renderTable(files) {
  const tableBody = document.getElementById('tableBody');
  const rowCountBadge = document.getElementById('rowCountBadge');
  const emptyStateRow = document.getElementById('emptyStateRow');
  const footerActiveFilterText = document.getElementById('footerActiveFilterText');

  tableBody.querySelectorAll('tr:not(#emptyStateRow)').forEach(el => el.remove());

  const query = state.searchQuery.toLowerCase().trim();
  const filtered = files.filter(file => {
    const matchesQuery = !query ||
      file.subject.toLowerCase().includes(query) ||
      file.teacher.toLowerCase().includes(query) ||
      file.name.toLowerCase().includes(query);

    if (!matchesQuery) return false;

    if (state.activeFilter === 'warning') {
      return file.quality_status === 'warning' || file.quality_status === 'error' || !file.pdf_exists;
    }
    if (state.activeFilter === 'unchecked') {
      return !file.pdf_exists && file.is_uploaded;
    }
    if (state.activeFilter === 'score') {
      return file.quality_status === 'error' || file.quality_summary.includes('Exceeds') || file.quality_summary.includes('초과');
    }
    if (state.activeFilter === 'missing') {
      return !file.is_uploaded;
    }
    return true;
  });

  rowCountBadge.textContent = `Total ${filtered.length} rows`;
  footerActiveFilterText.textContent = `${state.activeFilter.toUpperCase()} (${filtered.length} items)`;

  if (filtered.length === 0) {
    emptyStateRow.classList.remove('hidden');
    return;
  }
  emptyStateRow.classList.add('hidden');

  filtered.forEach(file => {
    const tr = document.createElement('tr');
    tr.className = `hover:bg-surface transition-all h-16 ${
      !file.is_uploaded ? 'bg-surface-container-low/40' : file.quality_status === 'error' ? 'bg-error-container/10' : ''
    }`;

    const uploadBadge = file.is_uploaded
      ? '<span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant font-bold text-xs shadow-sm">O</span>'
      : '<span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-error-container text-on-error-container font-bold text-xs shadow-sm">X</span>';

    const pdfBadge = file.pdf_exists
      ? `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant text-xs font-semibold shadow-sm">
          <span class="material-symbols-outlined text-[14px]">picture_as_pdf</span>Verified (PDF)
        </span>`
      : `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full ${
          file.is_uploaded ? 'bg-surface-container-high text-on-surface' : 'bg-surface-container text-on-surface-variant'
        } text-xs font-medium">
          <span class="material-symbols-outlined text-[14px]">hourglass_empty</span>Pending PDF
        </span>`;

    const qualityBadge = file.quality_status === 'error'
      ? `<span class="font-mono text-xs text-error font-bold">${file.quality_summary}</span>`
      : file.quality_status === 'warning'
      ? `<span class="font-mono text-xs text-tertiary font-bold">${file.quality_summary}</span>`
      : `<span class="font-mono text-xs text-on-surface">${file.quality_summary}</span>`;

    const docKey = DOC_KEY_MAP[file.id] || 'g10_eng';

    tr.innerHTML = `
      <td class="py-3 px-4 font-bold whitespace-nowrap">
        <div class="flex flex-col">
          <span class="text-sm font-bold text-on-surface">${file.subject}</span>
          ${file.folder_path ? `
            <span class="text-[10px] text-on-surface-variant font-mono font-normal flex items-center gap-1 mt-0.5" title="Recursive Subfolder Location">
              <span class="material-symbols-outlined text-[12px] text-primary">folder_open</span>
              <span>${file.folder_path}</span>
            </span>
          ` : ''}
        </div>
      </td>
      <td class="py-3 px-3 whitespace-nowrap">
        <span class="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-medium text-xs">${file.teacher}</span>
      </td>
      <td class="py-3 px-4 font-mono text-xs text-primary font-semibold whitespace-nowrap">${file.name}</td>
      <td class="py-3 px-3 font-mono text-xs text-on-surface-variant whitespace-nowrap">${file.exam_date}</td>
      <td class="py-3 px-3 text-center whitespace-nowrap">
        <div class="inline-flex items-center gap-1.5">
          ${file.web_view_link && file.web_view_link !== '#' ? `
            <a href="${file.web_view_link}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1 rounded bg-surface-container hover:bg-surface-container-high text-primary text-xs font-medium inline-flex items-center gap-0.5 transition-colors">
              Open <span class="material-symbols-outlined text-[13px]">north_east</span>
            </a>
          ` : `
            <span class="px-2.5 py-1 rounded bg-surface-container text-on-surface-variant text-xs font-mono">-</span>
          `}
          <button onclick="openDocsParsingModal('${docKey}')" class="px-2.5 py-1 rounded-lg bg-primary/10 hover:bg-primary hover:text-white text-primary text-xs font-semibold inline-flex items-center gap-1 transition-all shadow-sm">
            <span class="material-symbols-outlined text-[14px]">description</span>
            <span>Docs Parse</span>
          </button>
        </div>
      </td>
      <td class="py-3 px-3 text-center whitespace-nowrap">${uploadBadge}</td>
      <td class="py-3 px-4">${qualityBadge}</td>
      <td class="py-3 px-3 text-center whitespace-nowrap">${pdfBadge}</td>
      <td class="py-3 px-4 text-xs ${file.quality_status === 'error' ? 'text-error font-medium' : 'text-on-surface-variant'}">${file.memo}</td>
    `;
    tableBody.insertBefore(tr, emptyStateRow);
  });
}

// Controller Handlers
async function handleSyncFolder() {
  const folderInput = document.getElementById('folderIdInput');
  const syncBtn = document.getElementById('btnSyncFolder');
  const syncBtnText = document.getElementById('btnSyncFolderText');
  const syncBtnIcon = document.getElementById('btnSyncFolderIcon');
  const syncStatusTime = document.getElementById('syncStatusTime');
  const folderPathText = document.getElementById('folderPathText');
  const folderIdMeta = document.getElementById('folderIdMeta');

  let rawFolder = folderInput.value.trim() || state.drive.folder_id;
  const match = rawFolder.match(/folders\/([a-zA-Z0-9_-]+)/);
  const folderId = match ? match[1] : rawFolder.split('?')[0].split('&')[0].trim();
  folderInput.value = folderId;

  syncBtn.disabled = true;
  syncBtnIcon.classList.add('animate-spin');
  syncBtnText.textContent = 'Syncing...';

  try {
    const response = await ApiClient.syncFolder(folderId);
    state.drive = response;

    syncStatusTime.textContent = `Synced: Just now`;
    folderPathText.textContent = response.folder_path;
    folderIdMeta.textContent = `Folder ID: ${response.folder_id}`;

    renderMetrics(response);
    renderTable(response.files);
    showToast(`Successfully synchronized Google Drive folder (${response.files.length} papers)`, 'success');
  } catch (error) {
    showToast(`Folder sync failed: ${error.message}`, 'error');
  } finally {
    syncBtn.disabled = false;
    syncBtnIcon.classList.remove('animate-spin');
    syncBtnText.textContent = 'Sync Folder & Files';
  }
}

async function handleMockSignIn() {
  try {
    const auth = await ApiClient.loginMock();
    state.auth = auth;
    renderHeader(auth.user);
    renderAuthCard(auth);
    showToast('Signed in as Vice Principal (Mock Simulation Mode)', 'success');
    await handleSyncFolder();
  } catch (error) {
    showToast(`Sign in error: ${error.message}`, 'error');
  }
}

async function handleSignOut() {
  try {
    const auth = await ApiClient.logout();
    state.auth = auth;
    renderHeader(null);
    renderAuthCard(auth);
    showToast('Signed out successfully.', 'info');
  } catch (error) {
    showToast(`Sign out error: ${error.message}`, 'error');
  }
}

function setFilter(filterType) {
  state.activeFilter = filterType;

  const buttons = {
    all: document.getElementById('filterAllBtn'),
    warning: document.getElementById('filterWarningBtn'),
    unchecked: document.getElementById('filterPillUnchecked'),
    score: document.getElementById('filterPillScore'),
    missing: document.getElementById('filterPillMissing'),
  };

  Object.entries(buttons).forEach(([key, btn]) => {
    if (!btn) return;
    if (key === filterType) {
      btn.classList.add('bg-primary', 'text-on-primary', 'shadow-sm');
      btn.classList.remove('bg-surface-container', 'text-on-surface-variant');
    } else {
      btn.classList.remove('bg-primary', 'text-on-primary', 'shadow-sm');
      btn.classList.add('bg-surface-container', 'text-on-surface-variant');
    }
  });

  renderTable(state.drive.files);
}

function resetFilters() {
  document.getElementById('tableSearchInput').value = '';
  state.searchQuery = '';
  setFilter('all');
}

// ================= [F3] Google Docs Parsing Modal Functions =================
async function openDocsParsingModal(docId = 'g10_eng') {
  state.activeDocId = docId;
  const modal = document.getElementById('docsParsingModal');
  modal.classList.remove('hidden');
  await loadAndRenderDocData(docId);
}

function closeDocsParsingModal() {
  document.getElementById('docsParsingModal').classList.add('hidden');
}

async function switchDocsParsingSubject(docId) {
  state.activeDocId = docId;
  await loadAndRenderDocData(docId);
}

async function loadAndRenderDocData(docId) {
  const tabIds = ['g10_eng', 'g11_math', 'g10_kor', 'g9_hist', 'g12_bio'];
  tabIds.forEach(id => {
    const btn = document.getElementById(`tabBtn-${id}`);
    if (!btn) return;
    if (id === docId) {
      btn.className = 'px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all bg-primary text-on-primary shadow-sm';
    } else {
      btn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all bg-surface-container hover:bg-surface-container-high text-on-surface';
    }
  });

  try {
    const data = await ApiClient.getParsedDoc(docId);
    state.currentDocData = data;

    document.getElementById('metricSizeText').textContent = `Size: ${data.size}`;
    document.getElementById('metricLatencyText').textContent = `Latency: ${data.latency}`;
    document.getElementById('leftColumnFileName').textContent = data.fileName;
    document.getElementById('characterCountText').textContent = `Characters: ${data.charCount}`;
    document.getElementById('docHashText').textContent = data.hash;
    document.getElementById('rawTextStreamBox').value = data.rawText;

    const statusBadge = document.getElementById('parsingStatusBadge');
    statusBadge.textContent = data.statusBadge;
    statusBadge.className = `px-2.5 py-0.5 rounded-full text-xs font-bold ${data.badgeClass}`;

    document.getElementById('extractedSubject').textContent = data.metadata.subject;
    document.getElementById('extractedTeacher').textContent = data.metadata.teacher;
    document.getElementById('extractedDate').textContent = data.metadata.date;
    document.getElementById('extractedTotalScore').textContent = data.metadata.score;
    document.getElementById('step1ScoreBadge').textContent = data.metadata.step1Score;

    document.getElementById('scoreBreakdownSummary').textContent = data.scores.summary;
    document.getElementById('scoreSumTotal').textContent = data.scores.total;
    document.getElementById('barClosed').style.width = data.scores.barClosed;
    document.getElementById('barOpen').style.width = data.scores.barOpen;
    document.getElementById('barEssay').style.width = data.scores.barEssay;
    document.getElementById('totalQuestionsCount').textContent = data.scores.qCount;
    document.getElementById('scoreGuidelineBadge').textContent = data.scores.guidelineBadge;
    document.getElementById('scoreGuidelineBadge').className = `text-[11px] font-semibold px-2 py-0.5 rounded ${data.scores.guidelineBadgeClass}`;
    document.getElementById('scoreAuditMessage').innerHTML = `
      <span class="font-medium flex items-center gap-1">
        <span class="material-symbols-outlined text-[15px]">verified</span>
        ${data.scores.auditMessage}
      </span>
    `;

    document.getElementById('step3StatusTag').textContent = data.step3.statusTag;
    document.getElementById('step3StatusTag').className = `text-[11px] font-semibold ${data.step3.statusTagClass}`;
    document.getElementById('step3McqStatus').textContent = data.step3.mcqStatus;
    document.getElementById('step3PtsStatus').textContent = data.step3.ptsStatus;

    document.getElementById('rawJsonPreBlock').textContent = JSON.stringify(data.parsedJson || data, null, 2);
  } catch (err) {
    showToast(`Error loading doc details: ${err.message}`, 'error');
  }
}

async function reRunDocsParsing() {
  const progressContainer = document.getElementById('parsingProgressContainer');
  const progressBarTrack = document.getElementById('parsingProgressBarTrack');
  const progressPercent = document.getElementById('parsingProgressPercent');
  const reParseIcon = document.getElementById('reParseIcon');

  progressContainer.classList.remove('hidden');
  reParseIcon.classList.add('animate-spin');

  let pct = 15;
  const interval = setInterval(() => {
    pct = Math.min(90, pct + 25);
    progressBarTrack.style.width = `${pct}%`;
    progressPercent.textContent = `${pct}%`;
  }, 100);

  try {
    const refreshed = await ApiClient.reparseDoc(state.activeDocId);
    clearInterval(interval);
    progressBarTrack.style.width = '100%';
    progressPercent.textContent = '100%';

    setTimeout(async () => {
      progressContainer.classList.add('hidden');
      reParseIcon.classList.remove('animate-spin');
      await loadAndRenderDocData(state.activeDocId);
      showToast(`Re-parsed stream buffer for ${refreshed.fileName}`, 'success');
    }, 300);
  } catch (err) {
    clearInterval(interval);
    progressContainer.classList.add('hidden');
    reParseIcon.classList.remove('animate-spin');
    showToast(`Re-parsing failed: ${err.message}`, 'error');
  }
}

function toggleParsedJsonView() {
  const container = document.getElementById('rawJsonViewContainer');
  const label = document.getElementById('btnJsonToggleLabel');
  state.isJsonViewOpen = !state.isJsonViewOpen;

  if (state.isJsonViewOpen) {
    container.classList.remove('hidden');
    label.textContent = 'Hide JSON';
  } else {
    container.classList.add('hidden');
    label.textContent = 'View JSON';
  }
}

function copyParsedJson() {
  const code = document.getElementById('rawJsonPreBlock').textContent;
  navigator.clipboard.writeText(code).then(() => {
    showToast('Copied parsed JSON to clipboard.', 'success');
  });
}

function copyRawTextStream() {
  const text = document.getElementById('rawTextStreamBox').value;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied raw document text stream.', 'success');
  });
}

// ================= [F6] AI Batch Quality Audit Modal Functions =================
async function openAiBatchModal() {
  const modal = document.getElementById('aiBatchModal');
  modal.classList.remove('hidden');
  await loadAndRenderAiBatchAudit();
}

function closeAiBatchModal() {
  document.getElementById('aiBatchModal').classList.add('hidden');
}

async function loadAndRenderAiBatchAudit() {
  try {
    const data = await ApiClient.runBatchAudit();

    document.getElementById('aiBatchStatusText').textContent = `Evaluation Complete (${data.completed_count}/${data.total_exams} Exams - ${data.missing_count} Unsubmitted Excluded)`;
    document.getElementById('aiMetricCompleted').textContent = data.completed_count;
    document.getElementById('aiMetricCompliant').textContent = data.compliant_count;
    document.getElementById('aiMetricRevision').textContent = data.revision_count;
    document.getElementById('aiMetricMissing').textContent = data.missing_count;
    document.getElementById('aiLastAuditedText').textContent = `Last audit: ${data.audited_at}`;

    const container = document.getElementById('aiSubjectCardsContainer');
    container.innerHTML = '';

    data.reports.forEach(report => {
      const card = document.createElement('div');
      const isCompliant = report.status === 'COMPLIANT';
      const isMissing = report.status === 'MISSING';

      const bgStyle = isMissing
        ? 'bg-surface-container-low/60 border-surface-container'
        : isCompliant
        ? 'bg-surface-container-lowest border-surface-container'
        : 'bg-error-container/15 border-error/30';

      card.className = `p-4 rounded-xl border flex flex-col gap-2.5 ${bgStyle}`;
      card.innerHTML = `
        <div class="flex items-center justify-between pb-2 border-b border-surface-container">
          <div class="flex items-center gap-2">
            <span class="font-bold text-sm text-on-surface">${report.subject}</span>
            <span class="px-2 py-0.5 rounded bg-surface-container text-xs text-on-surface-variant font-medium">${report.teacher}</span>
          </div>
          <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${report.status_badge_class}">
            ${report.status_label}
          </span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs pt-1">
          <div class="p-2.5 bg-surface-container-low rounded-lg">
            <strong class="text-primary block mb-0.5 font-bold">[Check 1: Header Info]</strong>
            <span>${report.check1_header || 'Verified'}</span>
          </div>
          <div class="p-2.5 bg-surface-container-low rounded-lg">
            <strong class="text-primary block mb-0.5 font-bold">[Check 2: Grammar & Typos]</strong>
            <span>${report.check2_grammar || 'Clean'}</span>
          </div>
          <div class="p-2.5 bg-surface-container-low rounded-lg">
            <strong class="text-primary block mb-0.5 font-bold">[Check 3: Logical Errors]</strong>
            <span>${report.check3_logic || 'Verified'}</span>
          </div>
          <div class="p-2.5 ${report.check4_q_pagination && report.check4_q_pagination.includes('Warning') ? 'bg-error-container/30 border border-error/20' : 'bg-surface-container-low'} rounded-lg">
            <strong class="${report.check4_q_pagination && report.check4_q_pagination.includes('Warning') ? 'text-error' : 'text-primary'} block mb-0.5 font-bold">[Check 4: Q. Pagination]</strong>
            <span>${report.check4_q_pagination || 'Intact'}</span>
          </div>
          <div class="p-2.5 ${report.check5_opt_pagination && report.check5_opt_pagination.includes('Warning') ? 'bg-error-container/30 border border-error/20' : 'bg-surface-container-low'} rounded-lg">
            <strong class="${report.check5_opt_pagination && report.check5_opt_pagination.includes('Warning') ? 'text-error' : 'text-primary'} block mb-0.5 font-bold">[Check 5: Options Pagination]</strong>
            <span>${report.check5_opt_pagination || 'Intact'}</span>
          </div>
          <div class="p-2.5 ${report.check6_spacing && report.check6_spacing.includes('Warning') ? 'bg-error-container/30 border border-error/20' : 'bg-surface-container-low'} rounded-lg">
            <strong class="${report.check6_spacing && report.check6_spacing.includes('Warning') ? 'text-error' : 'text-primary'} block mb-0.5 font-bold">[Check 6: Formatting Spacing]</strong>
            <span>${report.check6_spacing || 'Consistent'}</span>
          </div>
          <div class="p-2.5 ${report.check7_time_balance && report.check7_time_balance.includes('Warning') ? 'bg-error-container/30 border border-error/20' : 'bg-surface-container-low'} rounded-lg sm:col-span-2 lg:col-span-3">
            <strong class="${report.check7_time_balance && report.check7_time_balance.includes('Warning') ? 'text-error' : 'text-primary'} block mb-0.5 font-bold">[Check 7: Time vs Workload Balance]</strong>
            <span>${report.check7_time_balance || 'Balanced'}</span>
          </div>
        </div>
        <div class="text-xs ${isCompliant ? 'text-secondary' : 'text-error'} font-semibold flex items-center gap-1.5 mt-1 p-2.5 bg-surface-container-lowest rounded-lg border border-surface-container">
          <span class="material-symbols-outlined text-[16px]">${isCompliant ? 'verified' : 'priority_high'}</span>
          <span>Recommendation: ${report.recommendation}</span>
        </div>
      `;
      container.appendChild(card);
    });

    // Synchronize 7-Step AI Quality Audit evaluations directly into the main inspection table
    if (state.drive && state.drive.files) {
      data.reports.forEach(report => {
        const file = state.drive.files.find(f =>
          f.subject.toLowerCase().includes(report.subject.toLowerCase()) ||
          report.subject.toLowerCase().includes(f.subject.toLowerCase())
        );
        if (file) {
          file.check1_header = report.check1_header;
          file.check2_grammar = report.check2_grammar;
          file.check3_logic = report.check3_logic;
          file.check4_q_pagination = report.check4_q_pagination;
          file.check5_opt_pagination = report.check5_opt_pagination;
          file.check6_spacing = report.check6_spacing;
          file.check7_time_balance = report.check7_time_balance;

          file.quality_summary = report.status === 'COMPLIANT'
            ? `Passed 7 Checks (${report.check7_time_balance ? report.check7_time_balance.slice(0, 30) : 'Compliant'})`
            : report.status === 'MISSING'
            ? 'Not submitted'
            : `Flagged (${report.check4_q_pagination && report.check4_q_pagination.includes('Warning') ? 'Pagination Issue' : report.check5_opt_pagination && report.check5_opt_pagination.includes('Warning') ? 'Options Issue' : 'Review Needed'})`;
          file.quality_status = report.status === 'COMPLIANT' ? 'normal' : 'error';
          file.memo = report.recommendation;
        }
      });
      renderTable(state.drive.files);
      renderMetrics(state.drive);
    }
  } catch (err) {
    showToast(`AI audit error: ${err.message}`, 'error');
  }
}

async function reRunAiBatchAudit() {
  const icon = document.getElementById('aiRerunIcon');
  icon.classList.add('animate-spin');
  try {
    await loadAndRenderAiBatchAudit();
    showToast('Re-evaluated all exams with Gemini rules engine.', 'success');
  } finally {
    icon.classList.remove('animate-spin');
  }
}

// ================= MODAL 3 & 4: Audit Logs & Settings =================
function openAuditLogsModal() {
  document.getElementById('auditLogsModal').classList.remove('hidden');
}

function closeAuditLogsModal() {
  document.getElementById('auditLogsModal').classList.add('hidden');
}

function openSettingsModal() {
  const display = document.getElementById('redirectUriDisplay');
  if (display && window.location.origin) {
    display.textContent = `${window.location.origin}/api/auth/google/callback`;
  }
  document.getElementById('settingsModal').classList.remove('hidden');
}

function closeSettingsModal() {
  document.getElementById('settingsModal').classList.add('hidden');
}

function copyRedirectUri() {
  const text = document.getElementById('redirectUriDisplay').textContent.trim();
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied redirect URI to clipboard.', 'success');
  });
}

function saveSettingsChanges() {
  const newFolder = document.getElementById('settingsFolderIdInput').value.trim();
  if (newFolder) {
    state.drive.folder_id = newFolder;
    document.getElementById('folderIdInput').value = newFolder;
    document.getElementById('folderIdMeta').textContent = `Folder ID: ${newFolder}`;
  }
  closeSettingsModal();
  showToast('Settings saved. Syncing folder...', 'success');
  handleSyncFolder();
// ================= Export to Google Sheets (.xlsx) and CSV =================
function exportToGoogleSheetsExcel() {
  if (!state.drive || !state.drive.files || state.drive.files.length === 0) {
    showToast('No exam papers available to export.', 'warning');
    return;
  }
  if (typeof XLSX === 'undefined') {
    showToast('SheetJS library is still loading. Please try again in a moment.', 'warning');
    return;
  }

  const exportRows = state.drive.files.map((f, idx) => ({
    "Index": idx + 1,
    "Subject": f.subject,
    "Teacher": f.teacher,
    "Exam File": f.name,
    "Folder Path (Recursive)": f.folder_path || "Root",
    "Exam Date": f.exam_date,
    "Uploaded (O/X)": f.is_uploaded ? "O" : "X",
    "PDF Verified (O/X)": f.pdf_exists ? "O" : "X",
    "Quality Status": f.quality_status.toUpperCase(),
    "Quality Summary": f.quality_summary,
    "Check 1: Header Info": f.check1_header || "Verified",
    "Check 2: Grammar & Typos": f.check2_grammar || "Passed",
    "Check 3: Logical Errors": f.check3_logic || "Passed",
    "Check 4: Q. Pagination": f.check4_q_pagination || "Passed",
    "Check 5: Options Pagination": f.check5_opt_pagination || "Passed",
    "Check 6: Formatting Spacing": f.check6_spacing || "Passed",
    "Check 7: Time vs Workload": f.check7_time_balance || "Passed",
    "Recommendation / Notes": f.memo
  }));

  const worksheet = XLSX.utils.json_to_sheet(exportRows);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "LIS_Exam_Audit");

  const today = new Date().toISOString().slice(0, 10);
  const fileName = `LIS_Exam_Inspection_Report_${today}.xlsx`;
  XLSX.writeFile(workbook, fileName);
  showToast(`Successfully exported Google Sheets / Excel file (${fileName}).`, 'success');
}

function exportToCsv() {
  if (!state.drive || !state.drive.files || state.drive.files.length === 0) {
    showToast('No exam papers available to export.', 'warning');
    return;
  }
  if (typeof XLSX === 'undefined') {
    showToast('SheetJS library is still loading. Please try again in a moment.', 'warning');
    return;
  }

  const exportRows = state.drive.files.map((f, idx) => ({
    "Index": idx + 1,
    "Subject": f.subject,
    "Teacher": f.teacher,
    "Exam File": f.name,
    "Folder Path": f.folder_path || "Root",
    "Exam Date": f.exam_date,
    "Uploaded": f.is_uploaded ? "O" : "X",
    "PDF Verified": f.pdf_exists ? "O" : "X",
    "Quality Status": f.quality_status.toUpperCase(),
    "Quality Summary": f.quality_summary,
    "Recommendation": f.memo
  }));

  const worksheet = XLSX.utils.json_to_sheet(exportRows);
  const csvContent = XLSX.utils.sheet_to_csv(worksheet);
  const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  const today = new Date().toISOString().slice(0, 10);
  const fileName = `LIS_Exam_Inspection_Report_${today}.csv`;
  link.setAttribute("href", url);
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast(`Successfully downloaded CSV report (${fileName}).`, 'success');
}

// Initial Boot Sequence
async function initializeApp() {
  try {
    // 1. Fetch Auth Status
    const auth = await ApiClient.getAuthStatus();
    state.auth = auth;
    renderHeader(auth.user);
    renderAuthCard(auth);

    // 2. Fetch Initial Examination Files
    const drive = await ApiClient.getFiles(state.drive.folder_id);
    state.drive = drive;
    renderMetrics(drive);
    renderTable(drive.files);

    // 3. Event Listeners
    document.getElementById('btnSyncFolder').addEventListener('click', handleSyncFolder);
    document.getElementById('folderIdInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSyncFolder();
    });

    document.getElementById('tableSearchInput').addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderTable(state.drive.files);
    });

    // Check URL parameters for OAuth status or errors
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth_status') === 'success') {
      showToast('Successfully authenticated with Google Workspace OAuth 2.0', 'success');
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('oauth_error') === 'not_configured') {
      openSettingsModal();
      showToast('Google OAuth Credentials are not configured yet.', 'warning');
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  } catch (error) {
    showToast(`Initialization failed: ${error.message}`, 'error');
  }
}

// Start application on DOM ready
document.addEventListener('DOMContentLoaded', initializeApp);
