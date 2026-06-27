# Scrum Ceremony Platform

> The ceremony operating system for Scrum Masters — run better retrospectives, planning poker, standups, and health checks with measurable outcomes.

## Quick Start

```bash
# Clone
git clone https://github.com/soumeendra/scrum-ceremony-platform.git
cd scrum-ceremony-platform

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 15)                   │
│  React 19 + TailwindCSS + Radix UI + Yjs CRDT + XState     │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP + WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  SQLAlchemy + Alembic + ARQ + Pydantic                     │
└───────┬──────────────┬──────────────┬───────────────────────┘
        │              │              │
   ┌────▼────┐   ┌─────▼─────┐  ┌────▼────┐
   │PostgreSQL│   │   Redis   │  │ Ollama  │
   │+pgvector │   │ (sessions │  │ (Gemma  │
   │          │   │  presence │  │  3 9B)  │
   └──────────┘   │  tokens)  │  └─────────┘
                  └───────────┘
```

## Project Structure

```
scrum-ceremony-platform/
├── backend/               # FastAPI + SQLAlchemy
├── frontend/              # Next.js 15 + React 19
├── ai-service/            # Ollama + Gemma 3 9B
├── integration-service/   # Jira, ERPNext, Stripe connectors
├── tests/playwright/      # E2E tests
├── database/              # Docker Compose + init scripts
├── scripts/               # Agent tools + guardrails
├── docs/                  # Project documentation
└── stories/               # User story backlog
```

## Documentation

| Document | Description |
|----------|-------------|
| [Project Charter](docs/00-PROJECT-CHARTER.md) | Vision, scope, risks |
| [Market Analysis](docs/01-BUSINESS/market-analysis.md) | TAM/SAM/SOM, competitive matrix |
| [Go-to-Market](docs/01-BUSINESS/go-to-market.md) | GTM strategy, pricing, launch plan |
| [Ground Rules](docs/10-GUARDRAILS/ground-rules.md) | Agentic development standards |
| [Data Model](docs/03-ARCHITECTURE/data-model.md) | Entity definitions, RLS policies |
| [State Machine](docs/03-ARCHITECTURE/ceremony-state-machine.md) | Ceremony FSM spec |
| [Anonymity](docs/03-ARCHITECTURE/anonymity-architecture.md) | Privacy engineering |
| [Stories](stories/README.md) | 10 epics, 129 stories |

## Development

See [Ground Rules](docs/10-GUARDRAILS/ground-rules.md) for the full development workflow including:
- Quality gates (Ruff, Biome, pytest, CodeQL)
- Branching strategy (master/develop/feature)
- CI/CD pipeline
- Domain-specific guardrails
- Agent session protocols

## License

MIT
