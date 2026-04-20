import re
from backend.models.schemas import FileInfo, Classification

class ASTInspector:
    def __init__(self):
        # Define risky patterns as regex
        self.risky_patterns = {
            "api_calls": [
                re.compile(r"fetch\("),
                re.compile(r"axios\."),
                re.compile(r"useSWR\("),
                re.compile(r"useQuery\("),
                re.compile(r"\$.ajax"),
            ],
            "auth_references": [
                re.compile(r"useSession\("),
                re.compile(r"useAuth\("),
                re.compile(r"jwt"),
                re.compile(r"token"),
                re.compile(r"login"),
            ],
            "database_access": [
                re.compile(r"prisma\."),
                re.compile(r"db\."),
                re.compile(r"mongoose\."),
                re.compile(r"sql\("),
                re.compile(r"query\("),
            ],
            "env_access": [
                re.compile(r"process\.env"),
                re.compile(r"import\.meta\.env"),
            ],
            "storage_access": [
                re.compile(r"localStorage\."),
                re.compile(r"sessionStorage\."),
            ]
        }

    def inspect(self, file: FileInfo) -> Classification | None:
        """
        Inspects the content of a file for risky patterns.
        Returns a Classification if risky patterns are found, otherwise None.
        """
        if not file.content:
            return None

        risky_patterns_found = []

        for category, patterns in self.risky_patterns.items():
            for pattern in patterns:
                if pattern.search(file.content):
                    risky_patterns_found.append(f"{category.replace('_', ' ')} pattern: {pattern.pattern}")

        if risky_patterns_found:
            return Classification(
                zone="restricted",
                reason=f"contains risky patterns: {', '.join(risky_patterns_found)}",
                confidence=0.9,
                details=risky_patterns_found,
                analysis_method="ast_regex"
            )

        return None # No risky patterns found
