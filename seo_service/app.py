from __future__ import annotations

import argparse
import html
import json
import os
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .crawler import SEOAuditor
from .models import Payment, Project, utc_now_iso
from .storage import ProjectStore


DEFAULT_DATA_FILE = Path(os.environ.get("SEO_SERVICE_DATA", "data/projects.json"))
AUDIT_PRICE_RUB = int(os.environ.get("SEO_AUDIT_PRICE_RUB", "100"))
PAYMENT_CONFIRM_TOKEN = os.environ.get("SEO_PAYMENT_CONFIRM_TOKEN", "dev-payment-token")


def html_page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; color: #172033; background: #f5f7fb; }}
    header {{ background: #111827; color: white; padding: 28px 36px; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 28px; }}
    section, form {{ background: white; border-radius: 14px; padding: 22px; margin-bottom: 18px; box-shadow: 0 8px 24px #1f29370f; }}
    input, textarea {{ width: 100%; padding: 10px; margin: 6px 0 14px; border: 1px solid #cbd5e1; border-radius: 8px; }}
    button, .button {{ background: #2563eb; color: white; border: 0; padding: 11px 16px; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; text-align: left; padding: 10px; vertical-align: top; }}
    .score {{ font-size: 42px; font-weight: 700; color: #16a34a; }}
    .warn {{ color: #b45309; }}
    .bad {{ color: #b91c1c; }}
    .muted {{ color: #64748b; }}
  </style>
</head>
<body>
  <header>
    <h1>Автоматизированный SEO-сервис</h1>
    <p>Аудит, мониторинг и план продвижения без накрутки посещений и имитации поведения людей.</p>
  </header>
  <main>{body}</main>
</body>
</html>""".encode("utf-8")


class SEOServiceHandler(BaseHTTPRequestHandler):
    store: ProjectStore
    auditor: SEOAuditor
    audit_price_rub: int
    payment_confirm_token: str

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.write_json({"status": "ok"})
        elif path == "/":
            self.render_home()
        elif path.startswith("/projects/") and path.endswith("/report.json"):
            self.render_report_json(path.split("/")[2])
        elif path.startswith("/projects/") and path.endswith("/pay"):
            self.render_payment_page(path.split("/")[2], parse_qs(urlparse(self.path).query))
        elif path.startswith("/api/projects/") and path.endswith("/audit"):
            self.run_audit_json(path.split("/")[3])
        elif path.startswith("/api/projects/"):
            self.render_project_json(path.split("/")[3])
        elif path.startswith("/projects/"):
            self.render_project(path.split("/")[2])
        elif path == "/api/projects":
            self.write_json([project.to_dict() for project in self.store.list_projects()])
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/projects":
            self.create_project()
        elif path == "/api/projects":
            self.create_project_json()
        elif path.startswith("/api/projects/") and path.endswith("/payments"):
            self.create_payment_json(path.split("/")[3])
        elif path.startswith("/projects/") and path.endswith("/payments"):
            self.create_payment(path.split("/")[2])
        elif path.startswith("/api/payments/") and path.endswith("/confirm"):
            self.confirm_payment_json(path.split("/")[3])
        elif path.startswith("/payments/") and path.endswith("/confirm"):
            self.confirm_payment_form(path.split("/")[2])
        elif path.startswith("/api/projects/") and path.endswith("/audit"):
            self.run_audit_json(path.split("/")[3])
        elif path.startswith("/projects/") and path.endswith("/audit"):
            self.run_audit(path.split("/")[2])
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def render_home(self) -> None:
        rows = []
        for project in self.store.list_projects():
            report = project.last_report or {}
            score = report.get("summary", {}).get("average_score", "нет аудита")
            rows.append(
                "<tr>"
                f"<td><a href='/projects/{project.id}'>{html.escape(project.name)}</a></td>"
                f"<td>{html.escape(project.site_url)}</td>"
                f"<td>{html.escape(str(score))}</td>"
                "</tr>"
            )
        project_rows = "".join(rows) or "<tr><td colspan='3' class='muted'>Проекты еще не добавлены</td></tr>"
        body = f"""
<section>
  <h2>Что делает сервис</h2>
  <p>Он обходит страницы вашего сайта как технический SEO-аудитор: проверяет заголовки, описания, H1, канонические URL, внутренние ссылки, изображения, объем текста и присутствие ключевых запросов.</p>
  <p>Результат — понятный список задач для роста органического трафика: какие страницы дописать, где исправить мета-теги, как усилить перелинковку и какие запросы не покрыты контентом.</p>
</section>
<form method="post" action="/projects">
  <h2>Добавить сайт</h2>
  <label>Название проекта</label>
  <input name="name" required placeholder="Например: Интернет-магазин">
  <label>Адрес сайта</label>
  <input name="site_url" required placeholder="https://example.com">
  <label>Ключевые запросы, по одному на строку</label>
  <textarea name="keywords" rows="5" required placeholder="купить окна&#10;ремонт окон"></textarea>
  <button type="submit">Создать проект</button>
</form>
<section>
  <h2>Проекты</h2>
  <table><thead><tr><th>Проект</th><th>Сайт</th><th>Средний SEO-балл</th></tr></thead><tbody>{project_rows}</tbody></table>
</section>
"""
        self.write_html("SEO-сервис", body)

    def render_project(self, project_id: str) -> None:
        project = self.store.get_project(project_id)
        if not project:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        report = project.last_report
        if not report:
            report_html = "<p class='muted'>Аудит еще не запускался.</p>"
        else:
            pages = "".join(
                "<tr>"
                f"<td>{html.escape(page['url'])}</td>"
                f"<td>{page['score']}</td>"
                f"<td>{html.escape('; '.join(page['issues']) or 'Ошибок не найдено')}</td>"
                "</tr>"
                for page in report["pages"]
            )
            actions = "".join(f"<li>{html.escape(item)}</li>" for item in report["action_plan"])
            report_html = f"""
<p class="score">{report['summary']['average_score']}/100</p>
<p>Проверено страниц: {report['summary']['pages_crawled']}. Найдено задач: {report['summary']['issues_found']}.</p>
<h3>План продвижения</h3>
<ol>{actions}</ol>
<p><a class="button" href="/projects/{project.id}/report.json">Скачать JSON-отчет</a></p>
<table><thead><tr><th>Страница</th><th>Балл</th><th>Проблемы</th></tr></thead><tbody>{pages}</tbody></table>
"""
        payment_rows = "".join(
            "<tr>"
            f"<td>{html.escape(payment.created_at)}</td>"
            f"<td>{payment.amount_rub} ₽</td>"
            f"<td>{'оплачен' if payment.status == 'paid' else 'ожидает оплаты'}</td>"
            "</tr>"
            for payment in project.payments[-5:]
        ) or "<tr><td colspan='3' class='muted'>Платежей пока нет</td></tr>"
        audit_button = (
            f'<form method="post" action="/projects/{project.id}/audit"><button type="submit">Запустить аудит</button></form>'
            if project.audit_credits > 0
            else (
                "<p class='warn'>Для запуска аудита оплатите 100 ₽. "
                "После подтверждения оплаты появится 1 запуск аудита.</p>"
                f'<form method="post" action="/projects/{project.id}/payments">'
                "<button type='submit'>Оплатить аудит 100 ₽</button></form>"
            )
        )
        body = f"""
<section>
  <p><a href="/">← Все проекты</a></p>
  <h2>{html.escape(project.name)}</h2>
  <p>{html.escape(project.site_url)}</p>
  <p><strong>Ключи:</strong> {html.escape(', '.join(project.keywords))}</p>
  <p><strong>Оплаченных запусков аудита:</strong> {project.audit_credits}</p>
  {audit_button}
</section>
<section>
  <h3>Платежи</h3>
  <table><thead><tr><th>Дата</th><th>Сумма</th><th>Статус</th></tr></thead><tbody>{payment_rows}</tbody></table>
</section>
<section>{report_html}</section>
"""
        self.write_html(project.name, body)

    def render_payment_page(self, project_id: str, query: dict[str, list[str]]) -> None:
        project = self.store.get_project(project_id)
        payment_id = query.get("payment_id", [""])[0]
        payment = project.find_payment(payment_id) if project else None
        if not project or not payment:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = f"""
<section>
  <p><a href="/projects/{project.id}">← Вернуться к проекту</a></p>
  <h2>Оплата аудита</h2>
  <p>Проект: <strong>{html.escape(project.name)}</strong></p>
  <p>Сумма: <strong>{payment.amount_rub} ₽</strong></p>
  <p>Статус: <strong>{'оплачен' if payment.status == 'paid' else 'ожидает оплаты'}</strong></p>
  <p class="muted">MVP-режим: карта не хранится и реальный эквайринг не подключен. Для боевого приема денег подключите ЮKassa/CloudPayments к API подтверждения платежа.</p>
  <form method="post" action="/payments/{payment.id}/confirm">
    <label>Токен подтверждения платежа</label>
    <input name="token" required placeholder="Введите токен кассы">
    <button type="submit">Подтвердить оплату</button>
  </form>
</section>
"""
        self.write_html("Оплата аудита", body)

    def render_report_json(self, project_id: str) -> None:
        project = self.store.get_project(project_id)
        if not project or not project.last_report:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.write_json(project.last_report)

    def create_project(self) -> None:
        form = self.read_form()
        keywords = [item.strip() for item in form.get("keywords", [""])[0].splitlines() if item.strip()]
        project = Project(
            id=uuid.uuid4().hex[:10],
            name=form.get("name", ["Новый проект"])[0].strip(),
            site_url=form.get("site_url", [""])[0].strip(),
            keywords=keywords,
        )
        self.store.save_project(project)
        self.redirect(f"/projects/{project.id}")

    def create_project_json(self) -> None:
        payload = self.read_json()
        project = Project(
            id=uuid.uuid4().hex[:10],
            name=str(payload.get("name") or "Новый проект").strip(),
            site_url=str(payload.get("site_url") or "").strip(),
            keywords=[str(item).strip() for item in payload.get("keywords", []) if str(item).strip()],
        )
        if not project.site_url or not project.keywords:
            self.write_json({"error": "site_url and keywords are required"}, HTTPStatus.BAD_REQUEST)
            return
        self.store.save_project(project)
        self.write_json(project.to_dict(), HTTPStatus.CREATED)

    def create_payment(self, project_id: str) -> None:
        payment = self.issue_payment(project_id)
        if payment is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.redirect(f"/projects/{payment.project_id}/pay?payment_id={payment.id}")

    def create_payment_json(self, project_id: str) -> None:
        payment = self.issue_payment(project_id)
        if payment is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.write_json(payment.to_dict(), HTTPStatus.CREATED)

    def issue_payment(self, project_id: str) -> Payment | None:
        project = self.store.get_project(project_id)
        if not project:
            return None
        payment = Payment(id=uuid.uuid4().hex[:12], project_id=project.id, amount_rub=self.audit_price_rub)
        project.payments.append(payment)
        project.updated_at = payment.created_at
        self.store.save_project(project)
        return payment

    def confirm_payment_json(self, payment_id: str) -> None:
        payload = self.read_json()
        if str(payload.get("token") or "") != self.payment_confirm_token:
            self.write_json({"error": "invalid payment token"}, HTTPStatus.FORBIDDEN)
            return
        project, payment = self.store.find_payment(payment_id)
        if not project or not payment:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.mark_payment_paid(project, payment)
        self.write_json({"status": "paid", "project": project.to_dict()})

    def confirm_payment_form(self, payment_id: str) -> None:
        form = self.read_form()
        if form.get("token", [""])[0] != self.payment_confirm_token:
            self.write_html("Ошибка оплаты", "<section><h2>Неверный токен оплаты</h2></section>", HTTPStatus.FORBIDDEN)
            return
        project, payment = self.store.find_payment(payment_id)
        if not project or not payment:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.mark_payment_paid(project, payment)
        self.redirect(f"/projects/{project.id}")

    def mark_payment_paid(self, project: Project, payment: Payment) -> None:
        if payment.status != "paid":
            payment.status = "paid"
            payment.paid_at = utc_now_iso()
            project.audit_credits += 1
            project.updated_at = payment.paid_at
            self.store.save_project(project)

    def run_audit(self, project_id: str) -> None:
        project = self.store.get_project(project_id)
        if not project:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if project.audit_credits < 1:
            self.redirect(f"/projects/{project.id}")
            return
        report = self.auditor.audit(project).to_dict()
        project.audit_credits -= 1
        project.last_report = report
        project.updated_at = report["generated_at"]
        self.store.save_project(project)
        self.redirect(f"/projects/{project.id}")

    def run_audit_json(self, project_id: str) -> None:
        project = self.store.get_project(project_id)
        if not project:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if project.audit_credits < 1:
            self.write_json({"error": "payment_required", "amount_rub": self.audit_price_rub}, HTTPStatus.PAYMENT_REQUIRED)
            return
        report = self.auditor.audit(project).to_dict()
        project.audit_credits -= 1
        project.last_report = report
        project.updated_at = report["generated_at"]
        self.store.save_project(project)
        self.write_json(report)

    def render_project_json(self, project_id: str) -> None:
        project = self.store.get_project(project_id)
        if not project:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.write_json(project.to_dict())

    def read_form(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return parse_qs(raw)

    def read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(raw or "{}")
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def write_html(self, title: str, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = html_page(title, body)
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def write_json(self, data: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()


def create_app(data_file: Path, max_pages: int = 25) -> type[SEOServiceHandler]:
    class ConfiguredHandler(SEOServiceHandler):
        store = ProjectStore(data_file)
        auditor = SEOAuditor(max_pages=max_pages)
        audit_price_rub = AUDIT_PRICE_RUB
        payment_confirm_token = PAYMENT_CONFIRM_TOKEN

    return ConfiguredHandler


def serve(host: str, port: int, data_file: Path, max_pages: int) -> None:
    server = ThreadingHTTPServer((host, port), create_app(data_file, max_pages))
    print(f"SEO service is running at http://{host}:{port}")
    server.serve_forever()
