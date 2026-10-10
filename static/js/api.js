/**
 * Inspection Paper - API Client
 * Interfaces with FastAPI backend for Authentication, Drive Sync, Docs Parsing, and AI Quality Audit.
 */

const ApiClient = {
  /**
   * Fetch current authentication state.
   */
  async getAuthStatus() {
    const response = await fetch('/api/auth/status');
    if (!response.ok) {
      throw new Error(`Failed to fetch auth status: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * Switch or sign into Mock Administrator mode.
   */
  async loginMock() {
    const response = await fetch('/api/auth/mock/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Failed to sign in via Mock mode: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * Sign out current user.
   */
  async logout() {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Failed to sign out: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * Fetch examination files from specified Google Drive folder.
   * @param {string} folderId 
   */
  async getFiles(folderId) {
    const params = new URLSearchParams();
    if (folderId) {
      params.append('folder_id', folderId);
    }
    const response = await fetch(`/api/drive/files?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`Failed to load drive files: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * Trigger folder synchronization.
   * @param {string} folderId 
   */
  async syncFolder(folderId) {
    const response = await fetch('/api/drive/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_id: folderId }),
    });
    if (!response.ok) {
      throw new Error(`Failed to sync folder: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * [F3] Fetch parsed document details and raw text stream.
   * @param {string} docId 
   */
  async getParsedDoc(docId) {
    const response = await fetch(`/api/parser/doc/${docId}`);
    if (!response.ok) {
      throw new Error(`Failed to load parsed document: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * [F3] Re-run parsing for a document.
   * @param {string} docId 
   */
  async reparseDoc(docId) {
    const response = await fetch(`/api/parser/doc/${docId}/reparse`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to re-parse document: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * [F6] Trigger batch quality audit across all examination papers.
   */
  async runBatchAudit() {
    const response = await fetch('/api/ai/batch-audit', {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to execute AI batch audit: ${response.statusText}`);
    }
    return await response.json();
  },

  /**
   * [F6] Audit single document via AI engine.
   * @param {string} docId 
   */
  async auditDoc(docId) {
    const response = await fetch(`/api/ai/audit/${docId}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to audit document: ${response.statusText}`);
    }
    return await response.json();
  },
};
