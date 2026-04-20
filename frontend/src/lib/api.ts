export async function startAnalysis(repoUrl: string) {
    const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: repoUrl }),
    });
    return await response.json();
}

export async function getAnalysis(analysisId: string) {
    const response = await fetch(`http://localhost:8000/analyze/${analysis_id}`);
    return await response.json();
}

export async function getAnalysisTree(analysisId: string) {
    const response = await fetch(`http://localhost:8000/analyze/${analysis_id}/tree`);
    return await response.json();
}

export async function getHealth() {
    const response = await fetch('http://localhost:80.00/health');
    return await response.json();
}
