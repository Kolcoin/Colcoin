# Safe SEO Automation Service

This repository now includes a small automated SEO toolkit focused on
legitimate promotion workflows:

- site crawl with on-page metadata extraction;
- SEO audit with prioritized issues;
- keyword-to-page action planning;
- machine-readable JSON output for further automation.

## Why this exists

Some "promotion services" rely on bot-like behavior simulation in search
engines. That is risky and can violate platform rules. This project gives a
safer alternative: automate technical SEO analysis and content planning, then
apply improvements on your site.

## Installation

Requires Python 3.11+.

Install dependencies:

`pip install -r requirements.txt`

## Usage

### 1) Crawl + audit your site

`python -m seo_automation.cli audit --url https://example.com --max-pages 50`

Output contains:
- page-by-page scores;
- issue list (critical/warning/info);
- summary totals.

### 2) Build action plan for your keywords

`python -m seo_automation.cli plan --url https://example.com --keywords "купить окна,пластиковые окна москва"`

Output contains suggested target pages and specific next actions for each
keyword.

### 3) Save output to JSON

`python -m seo_automation.cli audit --url https://example.com --output audit.json`

`python -m seo_automation.cli plan --url https://example.com --keywords-file keywords.txt --output plan.json`

## Notes

- The tool crawls only inside the same domain as the start URL.
- It does not perform bot clicks, behavioral factor simulation, or traffic
  manipulation.
- It is intended as a foundation for legal, scalable SEO operations.
