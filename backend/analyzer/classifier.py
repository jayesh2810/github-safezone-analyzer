from typing import List, Dict
import asyncio
import os
from backend.analyzer.repo import RepoAnalyzer
from backend.analyzer.heuristics import classify_file
from backend.analyzer.ast_inspector import ASTInspector
from backend.analyzer.llm_analyzer import LLMAnalyzer
from backend.models.schemas import FileInfo, Classification

class Classifier:
    def __init__(self, repo_path: str):
        self.analyzer = RepoAnalyzer(repo_path)
        self.inspector = ASTInspector()
        self.llm_analyzer = LLMAnalyzer()

    async def classify_all(self) -> List[Dict[str, any]]:
        """
        Runs the classification pipeline on all files in the repo.
        """
        files = self.analyzer.list_files()
        results = []

        for file in files:
            classification = classify_file(file)

            # Phase 3: AST Deep Analysis for "caution" files
            if classification.zone == "caution":
                inspection_result = self.inspector.inspect(file)
                if inspection_result:
                    # Upgrade to restricted if risky patterns found
                    classification = inspection_result
                else:
                    # Downgrade to safe if no risky patterns found
                    classification = Classification(
                        zone="safe",
                        reason="presentational component — no API, auth, or data access detected",
                        confidence=0.85,
                        analysis_method="ast_regex"
                    )

            # Phase 4: LLM Analysis for low-confidence files
            if classification.confidence < 0.7:
                context = {
                    "framework": "unknown", # Could be detected later
                    "neighboring_files": [] # Could be detected later
                }
                llm_result = await self.llm_analyzer.analyze_with_llm(file, context)
                if llm_result:
                    classification = llm_result

            # Merge file info and classification for the output
            result = {
                "path": file.path,
                "zone": classification.zone,
                "confidence": classification.confidence,
                "reason": classification.reason,
                "analysis_method": classification.analysis_method,
                "details": classification.details
            }
            results.append(result)

        return results

async def main():
    import sys
    import json
    if len(sys.argv) > 1:
        classifier = Classifier(sys.argv[1])
        results = await classifier.classify_all()
        print(json.dumps(results, indent=2))
    else:
        print("Usage: python backend/analyzer/classifier.py <path_to_repo>")

if __name__ == "__main__":
    asyncio.run(main())
