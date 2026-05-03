from __future__ import annotations

import json
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from seo_service.app import create_app
from seo_service.crawler import normalize_url


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class DemoSiteHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/robots.txt":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"User-agent: *\nAllow: /\n")
            return
        if self.path == "/":
            body = """
            <html>
              <head>
                <title>Automation SEO Service</title>
                <meta name="description" content="Automation SEO Service for technical promotion audits.">
                <link rel="canonical" href="/">
              </head>
              <body>
                <h1>Automation SEO Service</h1>
                <h2>Promotion audit</h2>
                <p>Automation SEO Service helps plan promotion tasks and content fixes.</p>
                <img src="/logo.png">
                <a href="/pricing">Pricing</a>
              </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body.encode())
            return
        if self.path == "/pricing":
            body = """
            <html>
              <head><title>Pricing</title></head>
              <body><h1>Pricing</h1><p>Short page.</p></body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body.encode())
            return
        self.send_error(404)


class SeoServiceEndToEndTest(unittest.TestCase):
    def setUp(self) -> None:
        self.site_port = free_port()
        self.site = ThreadingHTTPServer(("127.0.0.1", self.site_port), DemoSiteHandler)
        self.site_thread = threading.Thread(target=self.site.serve_forever, daemon=True)
        self.site_thread.start()

        self.tmp = TemporaryDirectory()
        self.app_port = free_port()
        self.app = create_app(Path(self.tmp.name) / "projects.json")
        self.app_server = ThreadingHTTPServer(("127.0.0.1", self.app_port), self.app)
        self.app_thread = threading.Thread(target=self.app_server.serve_forever, daemon=True)
        self.app_thread.start()

    def tearDown(self) -> None:
        self.app_server.shutdown()
        self.site.shutdown()
        self.app_server.server_close()
        self.site.server_close()
        self.tmp.cleanup()

    def post_json(self, path: str, data: dict[str, object] | None = None) -> dict[str, object]:
        encoded = json.dumps(data or {}).encode()
        request = Request(
            f"http://127.0.0.1:{self.app_port}{path}",
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode())

    def post_json_error(self, path: str, data: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
        try:
            return 200, self.post_json(path, data)
        except HTTPError as error:
            return error.code, json.loads(error.read().decode())

    def get_json(self, path: str) -> dict[str, object]:
        with urlopen(f"http://127.0.0.1:{self.app_port}{path}", timeout=10) as response:
            return json.loads(response.read().decode())

    def test_project_creation_audit_and_export(self) -> None:
        health = self.get_json("/health")
        self.assertEqual(health["status"], "ok")

        project = self.post_json(
            "/api/projects",
            {
                "name": "Demo",
                "site_url": f"http://127.0.0.1:{self.site_port}/",
                "keywords": ["Automation SEO Service", "promotion audit"],
            },
        )
        project_id = str(project["id"])

        status, payment_required = self.post_json_error(f"/api/projects/{project_id}/audit")
        self.assertEqual(status, 402)
        self.assertEqual(payment_required["error"], "payment_required")
        self.assertEqual(payment_required["amount_rub"], 100)

        payment = self.post_json(f"/api/projects/{project_id}/payments")
        self.assertEqual(payment["amount_rub"], 100)
        paid = self.post_json(f"/api/payments/{payment['id']}/confirm", {"token": "dev-payment-token"})
        self.assertEqual(paid["status"], "paid")
        self.assertEqual(paid["project"]["audit_credits"], 1)

        report = self.post_json(f"/api/projects/{project_id}/audit")
        self.assertEqual(report["summary"]["pages_crawled"], 2)
        self.assertGreaterEqual(report["summary"]["average_score"], 0)
        self.assertTrue(report["action_plan"])

        pages = {page["url"]: page for page in report["pages"]}
        home = pages[f"http://127.0.0.1:{self.site_port}/"]
        self.assertEqual(home["keywords_found"]["Automation SEO Service"], 3)
        self.assertIn("Добавьте описательные alt-атрибуты к важным изображениям.", home["recommendations"])

        exported = self.get_json(f"/api/projects/{project_id}")
        self.assertEqual(exported["last_report"]["summary"]["pages_crawled"], 2)
        self.assertEqual(exported["audit_credits"], 0)

    def test_cyrillic_urls_are_encoded_for_http(self) -> None:
        encoded = normalize_url("https://умныйсервис.рф/страница тест")
        self.assertEqual(encoded, "https://xn--b1afkbogxgel4g.xn--p1ai/" + quote("страница тест"))


if __name__ == "__main__":
    unittest.main()
