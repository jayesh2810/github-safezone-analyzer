/**
 * - Default `/api`: Vite proxies to FastAPI on 127.0.0.1:8000 so browsers only need the UI port open.
 * - Set PUBLIC_API_URL (e.g. http://VM:8000) only if the API is reachable from the browser on that host.
 */
function apiBase(): string {
    const raw = typeof import.meta.env.PUBLIC_API_URL === 'string' ? import.meta.env.PUBLIC_API_URL.trim() : '';
    if (raw) return raw.replace(/\/$/, '');
    return '/api';
}

const API_BASE = apiBase();

export async function startAnalysis(repoPath: string) {
    const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_path: repoPath }),
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Analysis failed with status ${response.status}`);
    }
    return await response.json();
}

export async function exportRules(repoPath: string, ideType: string) {
    const response = await fetch(`${API_BASE}/export-rules`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_path: repoPath, ide_type: ideType }),
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Export failed with status ${response.status}`);
    }
    return await response.json();
}

export async function getAnalysis(analysisId: string) {
    const response = await fetch(`${API_BASE}/analyze/${analysisId}`);
    return await response.json();
}

export async function getAnalysisTree(analysisId: string) {
    const response = await fetch(`${API_BASE}/analyze/${analysisId}/tree`);
    return await response.json();
}

