<script lang="ts">
  import { startAnalysis, getAnalysis, getAnalysisTree } from '$lib/api';
  import TreeMap from '$lib/TreeMap.svelte';

  let repoUrl = '';
  let analysisId: string | null = null;
  let status: 'idle' | 'analyzing' | 'completed' | 'failed' | 'error' = 'idle';
  let errorMessage = '';
  let analysisData: any = null;
  let fileDetails: any[] = [];
  let selectedFile: any = null;
  let pollingInterval: ReturnType<typeof setInterval> | null = null;

  async function handleStartAnalysis() {
    if (!repoUrl) {
      errorMessage = 'Please enter a repository URL or path.';
      return;

    }

    status = 'analyzing';
    errorMessage = '';
    analysisId = null;
    analysisData = null;
    selectedFile = null;

    try {
      const response = await startAnalysis(repoUrl);
      analysisId = response.analysis_id;
      startPolling(response.analysis_id);
    } catch (err) {
      status = 'error';
      errorMessage = 'Failed to start analysis. Make sure the backend is running.';
      console.error(err);
    }
  }

  function startPolling(id: string) {
    pollingInterval = setInterval(async () => {
      try {
        const data = await getAnalysis(id);
        if (data.status === 'completed') {
          analysisData = data.data;
          status = 'completed';
          stopPolling();
          fetchTree(id);
        } else if (data.status === 'failed') {
          status = 'failed';
          errorMessage = 'Analysis failed on the server.';
          stopPolling();
        }
      } catch (err) {
        status = 'error';
        errorMessage = 'Error polling analysis status.';
        stopPolling();
        console.error(err);
      }
    }, 3000);
  }

  async function fetchTree(id: string) {
    try {
      fileDetails = await getAnalysisTree(id);
    } catch (err) {
      console.error('Error fetching tree:', err);
    }
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  function handleFileSelect(file: any) {
    selectedFile = file;
  }
</script>

<div class="dashboard">
  <header>
    <h1>Safe Zone Analyzer</h1>
    <div class="input-group">
      <input
        type="text"
        bind:value={repoUrl}
        placeholder="Enter repo URL or local path (e.g., ./test_repo)"
        disabled={status === 'analyzing'}
      />
      <button on:click={handleStartAnalysis} disabled={status === '...'

    <div class="status-bar">
      Status: <span class="status-{status}">{status.toUpperCase()}</span>
      {#if errorMessage}
        <span class="error-text">{errorMessage}</span>
      {/if}
    </div>
  </header>

  <main>
    {#if status === 'analyzing' || status === 'completed' || status === 'failed'}
      <div class="content-layout">
        <div class="treemap-section">
          {#if analysisData && fileDetails.length > 0}
            <TreeMap data={fileDetails} onFileSelect={handleFileSelect} />
          {:else if status === 'analyzing'}
            <div class="loading-spinner">Processing files...</div>
          {/if}
        </div>

        {#if selectedFile}
          <aside class="details-panel">
            <h2>File Details</h2>
            <div class="detail-card">
              <p><strong>Path:</strong> {selectedFile.path}</p>
              <p><strong>Zone:</strong>
                <span class="zone-badge zone-{selectedFile.zone}">
                  {selectedFile.zone.toUpperCase()}
                </span>
              </p>
              <p><strong>Confidence:</strong> {(selectedFile.confidence * 100).toFixed(0)}%</p>
              <p><strong>Reason:</strong> {selectedFile.reason}</p>
              {#if selectedFile.details}
                <h4>Detected Patterns:</h4>
                <ul>
                  {#each selectedFile.details as detail}
                    <li>{detail}</li>
                  {/each}
                </ul>
              {/if}
            </div>
          </aside>
        {:else if status === 'completed' && !selectedFile}
          <div class="empty-state">
            <p>Select a file in the treemap to see details.</p>
          </div>
        {/if}
      </div>
    {:else}
      <div class="empty-state">
        <p>Enter a repository path above to begin the security analysis.</p>
      </div>
    {/if}
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: sans-serif;
    background-color: #f9fafb;
  }

  .dashboard {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  header {
    padding: 1.5rem;
    background: white;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  h1 { margin: 0 0 1rem 0; font-size: 1.5rem; color: #111827; }

  .input-group {
    display: flex;
    gap: 0.5rem;
  }

  input {
    flex-grow: 1;
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-round: 0.375rem;
    font-size: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    font-weight: 500;
  }

  button:disabled { background-color: #93c5fd; cursor: not-allowed; }

  .status-bar {
    margin-top: 1rem;
    font-size: 0.875rem;
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .status-idle { color: #6b7280; }
  .status-analyzing { color: #2563eb; font-weight: bold; }
  .status-completed { color: #059669; font-weight: bold; }
  .status-failed { color: #dc2626; font-weight: bold; }
  .status-error { color: #dc2626; font-weight: bold; }

  .error-text { color: #dc2626; }

  main {
    flex-grow: 1;
    overflow: hidden;
    padding: 1rem;
  }

  .content-layout {
    display: grid;
    grid-template-columns: 1fr 350px;
    gap: 1rem;
    height: 100%;
  }

  .treemap-section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    overflow: hidden;
  }

  .details-panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.25rem;
    overflow-y: auto;
  }

  .detail-card p { margin: 0.5rem 0; font-size: 0.9rem; }

  .zone-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }
  .zone-safe { background: #dcfce7; color: #166534; }
  .zone-caution { background: #fef9c3; color: #854d0e; }
  .zone-restricted { background: #fee2e2; color: #991b1b; }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #9ca3af;
  }

  .loading-spinner {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    font-style: italic;
  }

  h2 { margin-top: 0; font-size: 1.25rem; }
  h4 { margin: 1rem 0 0.5rem 0; font-size: 0.9rem; }
  ul { padding-left: 1.25rem; font-size: 0.875rem; }
</style>
