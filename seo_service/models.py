from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class PageAudit:
    url: str
    status_code: int
    title: str = ""
    meta_description: str = ""
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    canonical: str = ""
    word_count: int = 0
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    missing_alt_images: int = 0
    keywords_found: dict[str, int] = field(default_factory=dict)
    load_time_ms: int = 0
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def score(self) -> int:
        penalty = len(self.issues) * 8
        if self.status_code >= 400 or self.status_code == 0:
            penalty += 40
        if self.load_time_ms > 2500:
            penalty += 8
        return max(0, min(100, 100 - penalty))

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "title": self.title,
            "meta_description": self.meta_description,
            "h1": self.h1,
            "h2": self.h2,
            "canonical": self.canonical,
            "word_count": self.word_count,
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "missing_alt_images": self.missing_alt_images,
            "keywords_found": self.keywords_found,
            "load_time_ms": self.load_time_ms,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "score": self.score,
        }


@dataclass(slots=True)
class AuditReport:
    project_id: str
    site_url: str
    generated_at: str
    pages: list[PageAudit]
    action_plan: list[str]

    @property
    def summary(self) -> dict[str, int]:
        pages_crawled = len(self.pages)
        issues_found = sum(len(page.issues) for page in self.pages)
        average_score = round(sum(page.score for page in self.pages) / pages_crawled) if pages_crawled else 0
        return {
            "pages_crawled": pages_crawled,
            "issues_found": issues_found,
            "average_score": average_score,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "site_url": self.site_url,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "pages": [page.to_dict() for page in self.pages],
            "action_plan": self.action_plan,
        }


@dataclass(slots=True)
class Payment:
    id: str
    project_id: str
    amount_rub: int
    status: str = "pending"
    created_at: str = field(default_factory=utc_now_iso)
    paid_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "amount_rub": self.amount_rub,
            "status": self.status,
            "created_at": self.created_at,
            "paid_at": self.paid_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Payment":
        return cls(
            id=str(data["id"]),
            project_id=str(data["project_id"]),
            amount_rub=int(data.get("amount_rub", 100)),
            status=str(data.get("status") or "pending"),
            created_at=str(data.get("created_at") or utc_now_iso()),
            paid_at=str(data["paid_at"]) if data.get("paid_at") else None,
        )


@dataclass(slots=True)
class Project:
    id: str
    name: str
    site_url: str
    keywords: list[str]
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    last_report: dict[str, Any] | None = None
    audit_credits: int = 0
    payments: list[Payment] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "site_url": self.site_url,
            "keywords": self.keywords,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_report": self.last_report,
            "audit_credits": self.audit_credits,
            "payments": [payment.to_dict() for payment in self.payments],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            site_url=str(data["site_url"]),
            keywords=[str(item) for item in data.get("keywords", [])],
            created_at=str(data.get("created_at") or utc_now_iso()),
            updated_at=str(data.get("updated_at") or utc_now_iso()),
            last_report=data.get("last_report"),
            audit_credits=int(data.get("audit_credits", 0)),
            payments=[Payment.from_dict(item) for item in data.get("payments", [])],
        )

    def find_payment(self, payment_id: str) -> Payment | None:
        return next((payment for payment in self.payments if payment.id == payment_id), None)
