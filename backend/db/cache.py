import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

class AnalysisCache:
    def __init__(self, db_path: str = "backend/db/cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    analysis_id TEXT PRIMARY KEY,
                    repo_url TEXT,
                    analyzed_at TEXT,
                    data TEXT,
                    status TEXT
                )
            """)

    def save_analysis(self, analysis_id: str, repo_url: str, data: Dict[str, Any], status: str = "completed"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO results (analysis_id, repo_url, analyzed_at, data, status) VALUES (?, ?, ?, ?, ?)",
                (analysis_id, repo_url, datetime.utcnow().isoformat(), json.dumps(data), status)
            )

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM results WHERE analysis_id = ?", (analysis_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def update_status(self, analysis_id: str, status: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE results SET status = ? WHERE analysis_id = ?", (status, analysis_id))

    def get_all_analyses(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT analysis_id, repo_url, analyzed_at, status FROM results")
            return [{"analysis_id": row[0], "repo_url": row[1], "analyzed_at": row[2], "status": row[3]} for row in cursor.fetchall()]
