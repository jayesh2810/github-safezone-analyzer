from pathlib import Path

from backend.models.schemas import FileInfo, Classification

# Constants for classification
SAFE_EXTENSIONS = {
    '.css', '.scss', '.md', '.mdx', '.txt', '.svg', '.json', '.html',
    '.rst', '.adoc', '.asciidoc',
}
COMPONENT_EXTMS = {'.tsx', '.jsx', '.vue', '.svelte', '.py'} # Added .py for simplicity in demo
RESTRICTED_EXTENSIONS = {'.env', '.pem', '.key', '.cert'}

RESTRICTED_DIR_PATTERNS = {'api', 'routes', 'controllers', 'middleware', 'prisma', 'drizzle', 'migrations'}
RESTRICTED_FILENAME_PATTERNS = {'auth', 'login', 'session', 'token', 'jwt', 'password'}

# Exact stems and prefixes for docs often shipped without an extension (e.g. GitHub "README")
KNOWN_DOC_STEMS = frozenset({
    'readme', 'license', 'licence', 'copying', 'contributing', 'changelog',
    'code_of_conduct', 'authors', 'maintainers', 'security', 'notice',
})
DOC_STEM_PREFIXES = ('readme', 'license', 'licence', 'changelog', 'contributing')


def _is_documentation_filename(filename: str) -> bool:
    stem = Path(filename).stem.lower()
    if stem in KNOWN_DOC_STEMS:
        return True
    return any(stem.startswith(p) for p in DOC_STEM_PREFIXES)


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

    # 6. Documentation / license files by basename (covers extensionless README, LICENSE, etc.)
    if _is_documentation_filename(file.filename):
        return Classification(
            zone="safe",
            reason="documentation or repository metadata file",
            confidence=0.9,
            analysis_method="heuristic"
        )

    # 7. Default to restricted for anything unknown
    return Classification(
        zone="restricted",
        reason="unrecognized file type — defaulting to restricted",
        confidence=0.5,
        analysis_method="heuristic"
    )
