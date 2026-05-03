from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from seo_service.models import Payment, Project


class ProjectStore:
    def __init__(self, path: Path | str = "data/projects.json") -> None:
        self.path = Path(path)
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_raw({"projects": []})

    def list_projects(self) -> list[Project]:
        with self._lock:
            data = self._read_raw()
        return [Project.from_dict(item) for item in data.get("projects", [])]

    def get_project(self, project_id: str) -> Project | None:
        return next((project for project in self.list_projects() if project.id == project_id), None)

    def save_project(self, project: Project) -> None:
        with self._lock:
            data = self._read_raw()
            projects = data.get("projects", [])
            for index, item in enumerate(projects):
                if item.get("id") == project.id:
                    projects[index] = project.to_dict()
                    break
            else:
                projects.append(project.to_dict())
            self._write_raw({"projects": projects})

    def find_payment(self, payment_id: str) -> tuple[Project | None, Payment | None]:
        for project in self.list_projects():
            payment = project.find_payment(payment_id)
            if payment:
                return project, payment
        return None, None

    def _read_raw(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"projects": [], "payments": []}

    def _write_raw(self, data: dict) -> None:
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
