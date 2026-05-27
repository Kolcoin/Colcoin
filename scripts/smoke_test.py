from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError
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
    token = os.environ.get("SEO_PAYMENT_CONFIRM_TOKEN", "dev-payment-token")

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

    try:
        fetch_json(f"{base_url}/api/projects/{project['id']}/audit", {})
    except HTTPError as error:
        if error.code != 402:
            raise
    else:
        raise RuntimeError("Audit should require payment before first run")

    payment = fetch_json(f"{base_url}/api/projects/{project['id']}/payments", {})
    if not isinstance(payment, dict) or payment.get("amount_rub") != 100:
        raise RuntimeError(f"Payment creation failed: {payment}")

    paid = fetch_json(f"{base_url}/api/payments/{payment['id']}/confirm", {"token": token})
    if not isinstance(paid, dict) or paid.get("status") != "paid":
        raise RuntimeError(f"Payment confirmation failed: {paid}")

    report = fetch_json(f"{base_url}/api/projects/{project['id']}/audit", {})
    if not isinstance(report, dict) or not report.get("summary"):
        raise RuntimeError(f"Audit failed: {report}")

    summary = report["summary"]
    print(
        "OK: health, project creation, payment, audit. "
        f"pages={summary.get('pages_crawled')} score={summary.get('average_score')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
