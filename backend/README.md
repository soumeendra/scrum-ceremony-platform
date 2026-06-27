# Scrum Ceremony Platform – Backend

AI-augmented Scrum ceremonies (retrospectives, standups, sprint planning) with multi-tenant isolation, real-time collaboration, and intelligent summarisation.

## Tech Stack

| Layer          | Technology                                    |
| -------------- | --------------------------------------------- |
| Framework      | FastAPI (async)                               |
| ORM            | SQLAlchemy 2.0 (async) + asyncpg              |
| Migrations     | Alembic                                       |
| Task Queue     | ARQ (Redis-backed)                            |
| Auth           | Clerk (JWKS / JWT validation)                |
| Database       | PostgreSQL 16 + pgvector                      |
| Cache / PubSub | Redis 7                                       |
| AI             | Ollama (local) / OpenRouter (fallback)        |
| Validation     | Pydantic v2                                   |
| Linting        | Ruff                                          |
| Typing         | mypy (strict)                                 |
| Testing        | pytest + pytest-asyncio + httpx               |

## Quick Start

### 1. Prerequisites

- Python 3.12+
- Docker & Docker Compose (for PostgreSQL + Redis)
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### 2. Clone & install

```bash
cd backend
cp .env.example .env        # edit .env with your real values
```

**With uv (recommended):**
```bash
uv venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

**With pip:**
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Start backing services

```bash
docker compose -f docker-compose.override.yml up -d
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory, middleware, routers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Pydantic Settings (env vars)
│   │   ├── database.py       # Async engine + session
│   │   └── security.py      # Clerk JWT verification
│   ├── models/
│   │   ├── __init__.py       # Re-exports all models
│   │   ├── base.py           # Declarative base + mixins
│   │   ├── organization.py   # Organization, Workspace
│   │   ├── team.py           # Team, TeamMember
│   │   ├── user.py           # User
│   │   ├── ceremony.py       # Ceremony, BoardItem, Vote, …
│   │   ├── action.py         # Action, ActionRegister, IntegrationLink
│   │   ├── template.py       # Template
│   │   ├── embedding.py      # Embedding, Cluster, Summary
│   │   ├── integration.py    # IntegrationConfig, AuditEvent
│   │   └── health.py         # TeamHealth, RecurringTheme
│   ├── api/
│   │   ├── __init__.py       # Router aggregation
│   │   ├── health.py
│   │   ├── teams.py
│   │   ├── ceremonies.py
│   │   ├── actions.py
│   │   ├── templates.py
│   │   ├── analytics.py
│   │   └── integrations.py
│   └── services/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   └── test_health.py
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.override.yml
├── .env.example
├── .gitignore
└── README.md
```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

## Linting & Type Checking

```bash
ruff check .                 # lint
ruff format .                # auto-format
mypy app/                    # type check
```

## Environment Variables

See `.env.example` for the full list. All variables can also be set via the host environment (no `.env` file needed in production).

## Docker

```bash
docker build -t scrum-platform-backend .
docker run -p 8000:8000 --env-file .env scrum-platform-backend
```

## License

MIT
