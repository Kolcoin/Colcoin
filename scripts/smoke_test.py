from __future__ import annotations

import json
import sys
from urllib.request import Request, urlopen


def fetch_json(url: str, payload: dict[str, object] | None = None) -> dict[str, object] | list[object]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8080"
    site_url = sys.argv[2] if len(sys.argv) > 2 else "https://example.com"

    health = fetch_json(f"{base_url}/health")
    if not isinstance(health, dict) or health.get("status") != "ok":
        raise RuntimeError(f"Health check failed: {health}")

    project = fetch_json(
        f"{base_url}/api/projects",
        {
            "name": "Smoke test",
            "site_url": site_url,
            "keywords": ["example"],
        },
    )
    if not isinstance(project, dict) or not project.get("id"):
        raise RuntimeError(f"Project creation failed: {project}")

    report = fetch_json(f"{base_url}/api/projects/{project['id']}/audit", {})
    if not isinstance(report, dict) or not report.get("summary"):
        raise RuntimeError(f"Audit failed: {report}")

    summary = report["summary"]
    print(
        "OK: health, project creation, audit. "
        f"pages={summary.get('pages_crawled')} score={summary.get('average_score')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
