# AGENTS.md — Dog Data Analysis System

## Project overview

Flask-based data visualization platform for dog breed analysis. Despite the repo name `fastApiProject`, the **primary app is Flask** (`app.py`, port 5000). A FastAPI pilot (`app_fastapi.py`, port 8000, v5.0.0-alpha) exists as a tech-stack migration experiment targeting pet/bread APIs only.

## Quick start

```bash
pip install -r requirements.txt
npm ci                            # Playwright test deps only
cp .env.example .env
python init_db.py                 # create MySQL database + seed data
python app.py                     # Flask dev server on :5000
```

## Architecture

- **Flask app**: `app.py` (`create_app()` factory), 10 blueprints in `routes/`. Port 5000.
- **FastAPI pilot**: `app_fastapi.py`, port 8000, routes in `routes_fastapi/`. Uses separate SQLite engine (`database.py`, `demo.db`).
- **Vue 3 frontend**: `frontend/` dir, proxies `/api/v1` → `localhost:8000`. Port 3000.
- **ORM**: SQLAlchemy 2.0 + PyMySQL → MySQL 8.0. `models.py` (core: User, DogBreed) + `models_extended.py` (14 extended tables).
- **Charts** (`charts.py`): uses raw PyMySQL, not SQLAlchemy.
- **I18n**: Flask-Babel 4.0+, `locale_selector` in `config.py`.
- **Monitoring**: Prometheus + Grafana via `docker-compose.monitoring.yml` (ports 9090, 3000).
- **Scheduler**: APScheduler in `app.py:start_scheduler()`, 6-hour dashboard summary. Uses `_scheduler_started` global flag to avoid duplicate jobs under reloader.
- **Auth**: Flask-Login (session) + PyJWT (`utils/auth.py`).
- **CSRF**: enabled for HTML routes, **exempted** for all API blueprints (`csrf.exempt(api_bp)` etc).

## Commands

| What | Command |
|------|---------|
| Flask dev server | `python app.py` (port 5000) |
| FastAPI pilot | `python app_fastapi.py` (port 8000) |
| Vue frontend | `cd frontend && npm run dev` (port 3000) |
| Init DB + seed | `python init_db.py` |
| Demo data | `python scripts/seed_demo_data.py` |
| Breed migration | `python scripts/migrate_dog_breed_db.py` |
| Run all Python tests | `pytest` (`Test/` is default in `pytest.ini`) |
| By marker | `pytest -m "p0"` / `"api"` / `"playwright"` |
| Single file | `pytest Test/test_auth.py` |
| Coverage | `pytest --cov=. --cov-report=html:Test/reports/coverage_html --cov-report=term-missing` |
| Playwright (TS) | `npx playwright test` |
| Custom runner | `python Test/run_tests.py` |
| Code quality | `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` then `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics` then `black --check .` |

## Testing conventions

- **`Test/`** = Python pytest, **`tests/`** = Playwright TypeScript.
- **Root `conftest.py`** provides: `app` (session-scoped), `client`, `db`, `session` (per-function rollback), `login_user`, `logged_in_client` (user/123456), `admin_client` (admin/123456).
- **Test users** auto-created: `user`/`123456` (normal), `admin`/`123456` (admin).
- **Prefix test records with `TEST_`** (e.g. `TEST_user`, `TEST_breed`). The `session` fixture auto-cleans them.
- **Markers** in `pytest.ini`: `p0 p1 p2 api ui alpine accessibility performance integration monitoring charts slow playwright e2e`.
- **Custom framework** in `Test/test_framework.py`: `TestResult`, `TestExecutionManager`, `@test_case` decorator.
- **Extra test deps** in `Test/requirements-test.txt`.
- **`db.create_all()`** runs on every `create_app()` call — tables auto-created at startup.

## Key gotchas

- **Repo name lies**: the main app is Flask, not FastAPI. FastAPI is a side experiment.
- **CSRF exempt** for all API blueprints but enforced on HTML routes.
- **FastAPI has its own DB**: `database.py` → SQLite `demo.db`, not Flask-SQLAlchemy/MySQL.
- **Charts bypass ORM**: `charts.py` uses raw PyMySQL connections for queries.
- **Scheduler guard**: `_scheduler_started` global prevents APScheduler from starting twice under Flask reloader.
- **`.env` required** for MySQL credentials; loaded via `python-dotenv`.
- **`node_modules/`** is Playwright-only; no npm build for the Flask frontend (served from `static/`).
- **Demo mode**: set `FLASK_ENV=demo` to use `config_demo.py` with SQLite (`demo.db`).
