from typing import List
from backend.models.schemas import FileInfo, Classification

# Constants for classification
SAFE_EXTENSIONS = {'.css', '.scss', '.md', '.mdx', '.txt', '.svg', '.json', '.html'}
COMPONENT_EXTMS = {'.tsx', '.jsx', '.vue', '.svelte', '.py'} # Added .py for simplicity in demo
RESTRICTED_EXTENSIONS = {'.env', '.pem', '.key', '.cert'}

RESTRICTED_DIR_PATTERNS = {'api', 'routes', 'controllers', 'middleware', 'prisma', 'drizzle', 'migrations'}
RESTRICTED_FILENAME_PATTERNS = {'auth', 'login', 'session', 'token', 'jwt', 'password'}

def classify_file(file: FileInfo) -> Classification:
    """
    Classifies a file into a safety zone based on heuristics.
    """
    path_lower = file.path.lower()
    filename_lower = file.filename.lower()
    directory_lower = file.directory.lower()

    # 1. Restricted by filename pattern (high priority)
    if any(pattern in filename_lower for pattern in RESTRICTED_FILENAME_PATTERNS):
        return Classification(
            zone="restricted",
            reason=f"sensitive filename pattern detected: {file.filename}",
            confidence=0.95,
            analysis_method="heuristic"
        )

    # 2. Restricted by directory
    if any(pattern in directory_lower.split('/') for pattern in RESTRICTED_DIR_PATTERNS):
        return Classification(
            zone="restricted",
            reason=f"file in restricted directory: {file.directory}",
            confidence=0.9,
            analysis_method="heuristic"
        )

    # 3. Restricted by extension
    if file.extension.lower() in RESTRICTED_EXTENSIONS:
        return Classification(
            zone="restricted",
            reason=f"sensitive file extension: {file.extension}",
            confidence=0.95,
            analysis_method="heuristic"
        )

    # 4. Safe by extension
    if file.extension.lower() in SAFE_EXTENSIONS:
        # But check if it's in a restricted directory (already checked above, but just in case)
        return Classification(
            zone="safe",
            reason="style/content file",
            confidence=0.85,
            analysis_method="heuristic"
        )

    # 5. Caution for component files
    if file.extension.lower() in COMPONENT_EXTMS:
        return Classification(
            zone="caution",
            reason="component file mixes UI and logic",
            confidence=0.7,
            analysis_method="heuristic"
        )

    # 6. Default to restricted for anything unknown
    return Classification(
        zone="restricted",
        reason="unrecognized file type — defaulting to restricted",
        confidence=0.5,
        analysis_method="heuristic"
    )
