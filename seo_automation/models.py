from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PageData:
    url: str
    final_url: str
    status_code: int
    content_type: str
    title: str = ""
    description: str = ""
    h1: list[str] = field(default_factory=list)
    canonical: str = ""
    robots: str = ""
    word_count: int = 0
    out_links: list[str] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CrawlResult:
    start_url: str
    pages: list[PageData]

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_url": self.start_url,
            "pages": [page.to_dict() for page in self.pages],
        }


@dataclass
class AuditIssue:
    level: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class PageAudit:
    url: str
    issues: list[AuditIssue] = field(default_factory=list)
    score: int = 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class PlanItem:
    keyword: str
    target_url: str
    action: str
    reason: str
    relevance: float
    next_steps: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
