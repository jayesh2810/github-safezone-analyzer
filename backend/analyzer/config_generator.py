from enum import Enum
from typing import List, Dict
from backend.models.schemas import AnalysisResult

class IDEType(Enum):
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    CLAUDE_CODE = "claude_code"

class ConfigGenerator:
    """
    Generates IDE-specific configuration files based on the safety zone analysis.
    """
    
    def __init__(self):
        self.templates = {
            IDEType.CURSOR: self._cursor_template,
            IDEType.WINDSURF: self._windsurf_template,
            IDEType.CLAUDE_CODE: self._claude_code_template,
        }
        self.filenames = {
            IDEType.CURSOR: ".cursorrules",
            IDEType.WINDSURF: ".windsurfrules",
            IDEType.CLAUDE_CODE: ".clauderules",
        }

    def get_filename(self, ide: IDEType) -> str:
        """Returns the standard filename for the given IDE."""
        return self.filenames.get(ide, "ai_rules.txt")

    def generate_rules(self, result: AnalysisResult, ide: IDEType) -> str:

        """
        Generates a rule set for the specified IDE based on the analysis result.
        """
        restricted_files = self._get_files_by_zone(result, "restricted")
        caution_files = self._get_files_by_zone(result, "caution")
        
        template_func = self.templates.get(ide)
        if not template_func:
            raise ValueError(f"Unsupported IDE type: {ide}")
            
        return template_func(restricted_files, caution_files)

    def _get_files_by_zone(self, result: AnalysisResult, zone: str) -> List[str]:
        """
        Extracts file paths that belong to a specific zone.
        """
        # file_details is a List[Dict] based on schemas.py
        return [f["path"] for f in result.file_details if f.get("zone") == zone]

    def _cursor_template(self, restricted: List[str], caution: List[str]) -> str:
        rules = ["# AI Safety Rules\n"]
        
        if restricted:
            rules.append("## Restricted Files\nDo NOT modify the following files. If you believe a change is necessary, ask the user for explicit permission first:\n")
            rules.append("\n".join([f"- {f}" for f in restricted]))
            rules.append("\n")
            
        if caution:
            rules.append("## Caution Files\nBe careful when modifying these files. Always explain the potential impact and ask for a review:\n")
            rules.append("\n".join([f"- {f}" for f in caution]))
            rules.append("\n")
            
        return "\n".join(rules)

    def _windsurf_template(self, restricted: List[str], caution: List[str]) -> str:
        # Windsurf rules are very similar to Cursor but we can tailor the phrasing
        rules = ["# Windsurf AI Guardrails\n"]
        
        if restricted:
            rules.append("### CRITICAL: RESTRICTED ZONES\nAvoid editing these files entirely:\n")
            rules.append("\n".join([f"- {f}" for f in restricted]))
            rules.append("\n")
            
        if caution:
            rules.append("### CAUTION ZONES\nProceed with caution and request review for these files:\n")
            rules.append("\n".join([f"- {f}" for f in caution]))
            rules.append("\n")
            
        return "\n".join(rules)

    def _claude_code_template(self, restricted: List[str], caution: List[str]) -> str:
        rules = ["# Project Safety Map for Claude Code\n"]
        
        if restricted:
            rules.append("The following files are in the RESTRICTED zone. You must not edit them without direct confirmation from the user:\n")
            rules.append("\n".join([f"- {f}" for f in restricted]))
            rules.append("\n")
            
        if caution:
            rules.append("The following files are in the CAUTION zone. Be cautious and provide a detailed explanation of changes:\n")
            rules.append("\n".join([f"- {f}" for f in caution]))
            rules.append("\n")
            
        return "\n".join(rules)
