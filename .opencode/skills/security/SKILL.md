---
name: security-audit
description: Use when the user asks to audit, scan, or check security of the codebase, or to run Bandit/pip-audit. Use ONLY when explicitly asked about security.
---

# Security Audit Skill

## Bandit (Python SAST)
```bash
bandit -r . --exclude .git,node_modules,__pycache__,venv -f json -o bandit_report.json
```

## pip-audit (Dependency vulns)
```bash
pip-audit --desc=
```

## Key findings from last scan (2026-05-17)
- HIGH: `app.py:220` Flask debug=True on 0.0.0.0 (dev only)
- MEDIUM: SQL injection via f-string in `charts.py`, `ai_assistant.py`, `user_preference.py`, `demo_data_freshness.py`, `migrate_create_analytics_tables.py`
- MEDIUM: `requests` without timeout in `auto_test_ai_delete.py`, `force_clear_cache.py`, `verify_pet.py`, `check_pet_html.py`
- MEDIUM: XML parse in `report_generator.py:35`
- ~~HIGH: `shell=True` in `run_ai_tests.py`, `run_playwright_tests.py`~~ (FIXED)
