import os, requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

class BackendQueryTool:
    def project_summary(self, project_id: str):
        url = f"{API_BASE}/projects/{project_id}/summary"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()
