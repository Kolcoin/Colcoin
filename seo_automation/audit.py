from __future__ import annotations

from .models import AuditIssue, CrawlResult, PageAudit


def _penalty(issue: AuditIssue) -> int:
    if issue.level == "error":
        return 20
    if issue.level == "warning":
        return 10
    return 3


def _audit_single_page(page) -> PageAudit:
    issues: list[AuditIssue] = []

    if page.status_code >= 400:
        issues.append(
            AuditIssue(
                level="error",
                code="status_error",
                message=f"HTTP status {page.status_code}",
            )
        )

    if not page.title.strip():
        issues.append(
            AuditIssue(level="error", code="missing_title", message="Missing title tag")
        )
    elif len(page.title) > 70:
        issues.append(
            AuditIssue(
                level="warning",
                code="title_too_long",
                message=f"Title length is {len(page.title)} chars (>70)",
            )
        )
    elif len(page.title) < 20:
        issues.append(
            AuditIssue(
                level="warning",
                code="title_too_short",
                message=f"Title length is {len(page.title)} chars (<20)",
            )
        )

    if not page.description.strip():
        issues.append(
            AuditIssue(
                level="warning",
                code="missing_description",
                message="Missing meta description",
            )
        )
    elif len(page.description) > 170:
        issues.append(
            AuditIssue(
                level="warning",
                code="description_too_long",
                message=f"Description length is {len(page.description)} chars (>170)",
            )
        )

    if not page.h1:
        issues.append(
            AuditIssue(level="warning", code="missing_h1", message="No H1 heading found")
        )
    elif len(page.h1) > 1:
        issues.append(
            AuditIssue(
                level="warning",
                code="multiple_h1",
                message=f"Found {len(page.h1)} H1 headings",
            )
        )

    if page.word_count < 150:
        issues.append(
            AuditIssue(
                level="warning",
                code="thin_content",
                message=f"Low content depth: {page.word_count} words",
            )
        )

    if not page.canonical:
        issues.append(
            AuditIssue(
                level="info",
                code="missing_canonical",
                message="Canonical URL is not declared",
            )
        )

    score = max(0, 100 - sum(_penalty(issue) for issue in issues))
    return PageAudit(url=page.url, issues=issues, score=score)


def run_seo_audit(crawl_result: CrawlResult) -> dict:
    page_audits = [_audit_single_page(page) for page in crawl_result.pages]
    site_score = (
        int(sum(page.score for page in page_audits) / len(page_audits))
        if page_audits
        else 0
    )
    total_issues = sum(len(page.issues) for page in page_audits)

    return {
        "site_score": site_score,
        "total_pages": len(page_audits),
        "total_issues": total_issues,
        "pages": [page.to_dict() for page in page_audits],
    }
