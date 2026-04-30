from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from backend.analyzer.classifier import Classifier
from backend.analyzer.config_generator import ConfigGenerator, IDEType

app = FastAPI(title="Safe Zone Analyzer API")
generator = ConfigGenerator()

class AnalyzeRequest(BaseModel):
    repo_path: str

class ExportRequest(BaseModel):
    repo_path: str
    ide_type: str

@app.post("/analyze")
async def analyze_repo(request: AnalyzeRequest):
    """
    Analyzes a repository and returns the full AnalysisResult.
    """
    try:
        classifier = Classifier(request.repo_path)
        result = await classifier.classify_all()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-rules")
async def export_rules(request: ExportRequest):
    """
    Analyzes a repository and writes the IDE-specific rules file directly to the repo root.
    """
    try:
        # Validate IDE type
        try:
            ide = IDEType(request.ide_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid ide_type. Supported: {[i.value for i in IDEType]}")

        # 1. Analyze the repo
        classifier = Classifier(request.repo_path)
        analysis_result = await classifier.classify_all()
        
        # 2. Generate the rules content
        rules_content = generator.generate_rules(analysis_result, ide)
        
        # 3. Write the file to the repo root
        repo_root = Path(request.repo_path).resolve()
        filename = generator.get_filename(ide)
        file_path = repo_root / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rules_content)
        
        return {
            "status": "success",
            "ide": ide.value,
            "file_written": str(file_path),
            "summary": analysis_result.summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/export-rules")
async def export_rules(request: ExportRequest):
    """
    Analyzes a repository and returns the IDE-specific rules.
    """
    try:
        # Validate IDE type
        try:
            ide = IDEType(request.ide_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid ide_type. Supported: {[i.value for i in IDEType]}")

        # 1. Analyze the repo
        classifier = Classifier(request.repo_path)
        analysis_result = await classifier.classify_all()
        
        # 2. Generate the rules
        rules = generator.generate_rules(analysis_result, ide)
        
        return {
            "ide": ide.value,
            "rules": rules,
            "summary": analysis_result.summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
