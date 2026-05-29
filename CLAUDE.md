# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask-based dog data analysis & visualization platform. Supports MySQL (primary) and SQLite (demo mode). Features: data dashboards, 6 chart types (pyecharts), AI chat assistant with local LLM (Ollama/LM Studio), knowledge base, user auth (session + JWT), breed CRUD, virtual pet, feedback system, monitoring (Prometheus + Grafana), and i18n (Flask-Babel, zh_CN/en_US/ja_JP).

**Note:** Despite the repo being named `fastApiProject`, the main app is Flask (port 5000). There is no FastAPI app currently active.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
npm ci                           # Playwright test deps only

# Environment check
python check_env.py

# Database
python init_db.py                # Create MySQL DB + seed data
flask db migrate -m "message"    # Generate new Alembic migration
flask db upgrade                 # Apply pending migrations
python scripts/seed_demo_data.py # Seed demo data

# Run application
python app.py                    # Flask dev server on :5000
FLASK_ENV=demo python app.py     # Demo mode (SQLite, no MySQL needed)
python reset_admin_password.py   # Reset admin password

# Run tests
pytest                           # All Python tests (Test/ is default in pytest.ini)
pytest Test/test_auth.py         # Single test file
pytest -m "p0"                   # By marker (p0/p1/p2/api/ui/playwright/e2e/slow)
pytest --cov=. --cov-report=html:Test/reports/coverage_html --cov-report=term-missing
python Test/run_tests.py         # Custom test runner
npx playwright test              # Playwright E2E (TypeScript, in tests/)

# Code quality
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
black --check .
```

## Architecture

### App factory: `app.py`
`create_app(config_name)` creates and configures the Flask app. Three configs: `development` (MySQL, debug), `testing` (transaction isolation), `demo` (SQLite via `config_demo.py`). On every `create_app()` call, `db.create_all()` runs — tables are auto-created at startup. Flask-Migrate (Alembic) is wired in for explicit schema migrations.

Extensions initialized: Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-Caching, APScheduler, Flask-Babel, CSRFProtect, PrometheusMetrics.

### Blueprints (in `routes/`)
- **main** (`routes/main.py`) — `/`, `/charts`, `/admin/breeds`, chart pages
- **api** (`routes/api.py`) — RESTful API endpoints, including chart embed (`/api/chart/<name>`)
- **auth** (`routes/auth.py`) — login/register
- **ai_assistant** (`routes/ai_assistant.py`) — AI chat with local LLM, session management, guest support
- **analytics** (`routes/analytics.py`) — usage analytics dashboard
- **feedback** (`routes/feedback.py`) — user feedback system
- **alert_system** (`routes/alert_system.py`) — monitoring alerts
- **pet_api** (`routes/pet_api.py`) — virtual pet state persistence
- **user_preference** (`routes/user_preference.py`) — user settings/preferences
- **ai_log_viewer** (`routes/ai_log_viewer.py`) — AI chat log viewer

### Data layer
- `models.py` — SQLAlchemy core: `User` (with password hashing), `DogBreed`
- `models_extended.py` — 14 extended tables: `UserProfile`, `ChatSession`, `ChatMessage`, `AppToken`, favorites, etc.
- `models_analytics.py` — Analytics event models
- `models_dog_breeds.py` — Additional breed models
- `charts.py` — Standalone chart functions using **raw PyMySQL** (not SQLAlchemy). Each chart function opens its own DB connection via module-level `DB_CONFIG`.
- `database.py` — SQLite engine for FastAPI pilot (if present)

### Key patterns
- **Guest user support**: Unauthenticated users share a single `username="guest"` system user for AI chat. Guest sessions are reused.
- **Chart loading**: Charts rendered server-side as embed HTML. `/charts` dashboard loads 6 charts asynchronously via JS fetch to `/api/chart/<name>`.
- **Dashboard summary**: `dashboard_summary` table caches homepage stats, updated every 6 hours via APScheduler.
- **Scheduler guard**: `_scheduler_started` global flag in `app.py` prevents APScheduler from starting twice under Flask's reloader.
- **Knowledge base**: `utils/knowledge_base.py` provides local keyword-based QA matching before falling back to the LLM.
- **CSRF**: Enabled for HTML/form routes (WTForms CSRF). **Exempted** for all API blueprints: `api_bp`, `feedback_bp`, `analytics_bp`, `ai_bp`, `log_viewer_bp`, `pet_api_bp`.
- **i18n**: Flask-Babel 4.0+ with `locale_selector` — resolves locale from URL param → session → Accept-Language header → default (zh_CN).
- **Monitoring**: Prometheus metrics exposed via `prometheus_flask_exporter`. Docker Compose stack available at `docker-compose.monitoring.yml` (Prometheus :9090, Grafana :3000).
- **Utils**: `utils/auth.py` (JWT decorator), `utils/api_response.py` (response helpers), `utils/knowledge_base.py` (local QA), `utils/analytics_collector.py`, `utils/data_freshness.py`, `utils/monitoring.py`, `utils/timezone.py`.

### Frontend
- `templates/` — Jinja2 HTML templates
- `static/` — CSS, JS (Alpine.js), images
- `frontend/` — currently a stub (`package.json` only, no Vue app). The main UI is server-rendered.
- `node_modules/` — Playwright test dependencies only; no npm build step for the Flask frontend.

## Testing conventions

- **`Test/`** = Python pytest (default in `pytest.ini`), **`tests/`** = Playwright TypeScript E2E.
- **Root `conftest.py`** provides session-scoped fixtures: `app` (TestingConfig), `client`, `db`, `session` (per-function transaction rollback), `login_user`, `logged_in_client` (user/123456), `admin_client` (admin/123456).
- **Test users** auto-created once per session: `user`/`123456` (normal), `admin`/`123456` (admin).
- **Prefix test records with `TEST_`** — the `session` fixture auto-cleans them via `User.username.like("TEST_%")` and `DogBreed.breed_name.like("TEST_%")`.
- **Markers** (from `pytest.ini`): `p0`, `p1`, `p2`, `api`, `ui`, `alpine`, `accessibility`, `performance`, `integration`, `monitoring`, `charts`, `slow`, `playwright`, `e2e`.
- **Custom framework** in `Test/test_framework.py`: `TestResult`, `TestExecutionManager`, `@test_case` decorator. Extra deps in `Test/requirements-test.txt`.
- **Filtering**: `pytest_collection_modifyitems` in `conftest.py` excludes bare `test_case` functions from `test_framework.py`.
- **Test database**: uses the MySQL `dog` database (same as dev) with transactional rollback isolation. No separate test database.
- Playwright config in `playwright.config.ts` and `Test/playwright_config.py`. Base URL: `http://localhost:5000`.

## Key gotchas

- **Charts bypass ORM**: `charts.py` uses raw PyMySQL connections. Don't expect SQLAlchemy session management there.
- **Scheduler double-start**: `_scheduler_started` global prevents APScheduler from running twice under Flask's reloader. Don't remove this guard.
- **`.env` required** for MySQL credentials; loaded via `python-dotenv`.
- **`db.create_all()` runs at startup** in `create_app()`, so tables are auto-created. Migrations (Alembic) exist but aren't auto-applied — you must run `flask db upgrade` if you want to use migration-based schema management.
- **Demo mode**: set `FLASK_ENV=demo` to bypass MySQL entirely. Uses `config_demo.py` with SQLite (`demo.db`).
- **Monitoring stack**: Prometheus + Grafana via `docker-compose.monitoring.yml`. Grafana admin password is `admin123` (default, change in production).

## Environment variables (`.env`)
- `SECRET_KEY`, `JWT_SECRET_KEY` — auto-generated with warnings if unset
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME` — MySQL connection (defaults: `doguser`/`123456`/`localhost`/`dog`)
- `LOCAL_MODEL_URL` — Ollama/LM Studio endpoint (default: `http://localhost:11434`)
- `FLASK_ENV` — `development`, `production`, `testing`, or `demo`
- `LOG_LEVEL`, `LOG_FILE` — logging configuration
