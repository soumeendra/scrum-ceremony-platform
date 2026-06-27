# Backend Architecture Document
## Scrum Ceremony Platform — Backend

---

**Document Version:** 1.0.0  
**Status:** Draft  
**Author:** Backend Architecture Team  
**Last Updated:** June 2026  
**Audience:** Backend Engineers, Solution Architects, DevOps, Security Reviewers  
**Classification:** Internal

---

## Table of Contents

1. [Backend Architecture Overview](#1-backend-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [API Design](#4-api-design)
5. [Service Layer](#5-service-layer)
6. [Ceremony Orchestration Service](#6-ceremony-orchestration-service)
7. [Action Service](#7-action-service)
8. [Integration Service](#8-integration-service)
9. [AI Service](#9-ai-service)
10. [Background Jobs](#10-background-jobs)
11. [Multi-Tenancy Middleware](#11-multi-tenancy-middleware)
12. [Database Migrations](#12-database-migrations)
13. [Auth Middleware](#13-auth-middleware)
14. [Error Handling](#14-error-handling)
15. [Testing Strategy](#15-testing-strategy)

---

## 1. Backend Architecture Overview

### 1.1 Architectural Pattern

The backend follows a **modular monolith** with a **service layer pattern**. Domain logic is encapsulated in independent service classes with explicit API boundaries, following the Single Responsibility Principle. Dependency injection is managed through FastAPI's `Depends` mechanism.

### 1.2 High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Client["Client Layer"]
        FE["Next.js Frontend"]
        WS["WebSocket Client"]
    end
    
    subgraph Server["FastAPI Application"]
        API["API Router Layer"]
        MW["Middleware Stack<br/>Auth → Tenant → Logging → CORS"]
        SVC["Service Layer"]
        QM["Query Manager<br/>SQLAlchemy 2.0 Async"]
    end
    
    subgraph Data["Data Layer"]
        PG["PostgreSQL 16 + pgvector"]
        RD["Redis 7"]
        DL["Dead Letter Queue"]
    end
    
    subgraph External["External Systems"]
        JR["Jira Cloud"]
        SL["Slack"]
        ST["Stripe"]
        OL["Ollama Server"]
    end
    
    FE -->|"HTTPS/REST"| MW
    MW --> API
    API --> SVC
    SVC --> QM --> PG
    SVC --> RD
    SVC -->|"Async Tasks"| RD
    RD -->|"Fan-out"| WS
    SVC --> JR
    SVC --> SL
    SVC --> ST
    SVC --> OL
    RD --> DL
```

### 1.3 Dependency Injection Pattern

FastAPI's `Depends` system provides constructor injection to services:

```python
# Application dependency graph
# FastAPI manages this via dependency injection

class AppState:
    """Shared application state initialized at startup."""
    db_engine: AsyncSessionFactory
    redis: Redis
    ollama: OllamaClient
    settings: Settings

# Wired via FastAPI's dependency system
# api/dependencies.py
async def get_service[ServiceType](
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
) -> ServiceType:
    return ServiceType(db, user, redis)
```

### 1.4 Async I/O Strategy

All external I/O (database, network, file system) uses Python `async/await`:
- **Session/get_db**: Yields an `AsyncSession` from SQLAlchemy per request
- **Services**: All service methods that touch the DB or network are `async def`
- **Background tasks**: CPU-bound work (e.g., embedding generation) is offloaded to worker processes (Celery/ARQ)

---

## 2. Technology Stack

### 2.1 Core Dependencies

| Technology | Version | Purpose | Selection Rationale |
|---|---|---|---|
| **FastAPI** | 0.115+ | Web framework | Native async, OpenAPI auto-gen, dependency injection, type-safe |
| **SQLAlchemy** | 2.0+ (async) | ORM | AsyncSession, custom Mappers, wide ecosystem |
| **Alembic** | latest | Migrations | Integrated with SQLAlchemy, supports branching |
| **Pydantic** | v2 (pydantic-settings) | Validation & settings | High performance, JSON Schema, `model_validate` |
| **ARQ** | 0.5+ | Async Worker | Redis-based queue with asyncio support, alternative to Celery |
| **Uvicorn** | 0.34+ | ASGI server | High-performance async worker model |
| **Redis** | 7.x | Client/Cache | Standard pipeline, native JSON, sorted sets |
| **PostgreSQL** | 16 | Primary DB | Full Text Search, pgvector, Row Level Security |
| **pgvector** | 0.8+ | Vector operations | Semantic search, LLM clustering embeddings |

### 2.2 Supporting Libraries

| Library | Purpose |
|---|---|
| `httpx` | Async HTTP client (for Jira, Slack, ERP) |
| `pyjwt` + `cryptography` | JWT validation (Clerk JWKS) |
| `asyncpg` | High-performance PostgreSQL driver |
| `greenlet` | Implicit async→sync conversion for SQLAlchemy async sessions |
| `structlog` | Structured logging (JSON for production) |
| `sentry-sdk` | Error & performance monitoring |
| `tenacity` | Retry logic with exponential backoff |
| `strenv` | Strict environment variable parsing |
| `coloredlogs` | Readable console logs in development |

### 2.3 Dependency Justification

**Why FastAPI over Django/Flask?**
- First-class `async/await` support (critical for WebSocket fan-out and concurrent I/O)
- Automatic OpenAPI 3.1 documentation — frontend consumes API spec via `openapi-typescript`
- Pydantic integration — request validation is just type hints
- Dependency injection — unit testable services without complex patching

**Why SQLAlchemy 2.0 Async over Tortoise/Prisma?**
- Mature ecosystem, Alembic migrations
- Mature async support via `AsyncSession`
- Custom types (`JSONB`, `Vector`), hybrid properties
- Raw SQL escape hatch when ORM is insufficient

**Why ARQ over Celery?**
- Native `async/await` — no monkey-patching needed
- Zero broker setup (uses existing Redis)
- Simpler operational footprint (pure Python, no Erlang dependency)

---

## 3. Project Structure

### 3.1 Directory Layout

```
backend/
├── app/                          # Application package
│   ├── main.py                   # FastAPI app factory
│   ├── config.py                 # Settings via pydantic-settings
│   ├── database.py               # AsyncSessionFactory setup
│   ├── redis.py                  # Redis connection pool
│   ├── dependencies.py           # FastAPI dependency injection
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── base.py               # Declarative base
│   │   ├── ceremony.py           # Ceremony, Phase, Board
│   │   ├── team.py               # Team, Workspace, Membership
│   │   ├── action.py             # ActionItem
│   │   ├── template.py           # Template
│   │   ├── user.py               # User
│   │   ├── integration.py        # Integration, Webhook
│   │   ├── ai.py                 # Embedding, Cluster, Summary
│   │   └── audit.py              # AuditLog
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── ceremony.py
│   │   ├── action.py
│   │   ├── common.py             # Pagination, SortOrder, etc.
│   │   └── api.py                # Standard API envelope
│   │
│   ├── api/                      # REST API endpoints
│   │   ├── v1/                   # API version 1
│   │   │   ├── ceremonies.py     # /api/v1/ceremonies
│   │   │   ├── actions.py        # /api/v1/actions
│   │   │   ├── teams.py          # /api/v1/teams
│   │   │   ├── templates.py      # /api/v1/templates
│   │   │   ├── integrations.py   # /api/v1/integrations
│   │   │   ├── ai.py             # /api/v1/ai
│   │   │   └── webhooks.py       # /api/v1/webhooks
│   │   └── router.py             # Aggregates all v1 routers
│   │
│   ├── services/                 # Domain services (one per bounded context)
│   │   ├── ceremony_service.py   # Ceremony orchestration
│   │   ├── action_service.py     # Action lifecycle
│   │   ├── board_service.py      # Collaborative board logic
│   │   ├── team_service.py       # Team & membership management
│   │   ├── template_service.py   # Template CRUD
│   │   ├── integration_service.py # External system connectors
│   │   ├── ai_service.py         # AI job orchestration
│   │   ├── notification_service.py  # Multi-channel notifications
│   │   └── analytics_service.py  # Metrics & reporting
│   │
│   ├── middleware/                # Custom ASGI middleware
│   │   ├── auth.py              # JWT validation + user context
│   │   ├── tenant.py            # Tenant extraction from JWT
│   │   ├── logging.py           # Request/response logging
│   │   ├── correlation.py       # Correlation ID injection
│   │   └── rate_limit.py        # Redis-based rate limiting
│   │
│   ├── integrations/             # External system connectors
│   │   ├── base.py              # IntegrationConnector ABC
│   │   ├── jira_.py             # Jira Cloud connector
│   │   ├── slack.py             # Slack connector
│   │   ├── teams.py             # Microsoft Teams connector
│   │   ├── erpnext.py           # ERPNext connector
│   │   └── stripe.py            # Stripe webhook handler
│   │
│   ├── tasks/                    # Background job definitions (ARQ)
│   │   ├── sync_tasks.py         # Jira/ERP sync tasks
│   │   ├── ai_tasks.py           # Embedding, clustering, summarization
│   │   ├── notification_tasks.py    # Notification delivery
│   │   ├── audit_tasks.py        # Audit log archival
│   │   └── health_check.py       # Health check probes
│   │
│   └── utils/                    # Internal utilities
│       ├── id_generation.py      # KSUID / ULID generation
│       ├── text_processing.py    # Text preprocessing
│       └── vector_ops.py         # pgvector helper operations
│
├── alembic/                      # Alembic migration scripts
│   ├── env.py                    # Migration environment config
│   ├── script.py.mako            # Migration template
│   └── versions/
│       ├── 001_initial/
│       │   └── 001_initial_schema.py
│       ├── 002_add_ceremony/
│       │   └── 002_add_ceremony.py
│       └── ...
│
├── alembic.ini                   # Alembic config
├── tests/                        # Test suite
│   ├── conftest.py               # Test fixtures
│   ├── unit/
│   │   ├── services/
│   │   ├── models/
│   │   └── factories.py          # factory_boy factories
│   ├── integration/
│   │   ├── api/
│   │   ├── services/
│   │   └── integrations/
│   └── e2e/
│       └── full_ceremony.py
│
├── Dockerfile
└── pyproject.toml                # Project metadata + tool configs
```

### 3.2 Service Layer Convention

Every service class follows this pattern:

```python
# services/base.py
from typing import Protocol

class ServiceProtocol(Protocol):
    """Marker protocol for all services."""

# services/ceremony_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.redis import Redis

class CeremonyService:
    def __init__(self, db: AsyncSession, redis: Redis, user: UserContext):
        self.db = db
        self.redis = redis
        self.user = user
    
    async def create(self, config: CeremonyCreateConfig) -> Ceremony:
        """Create a new ceremony with initial board."""
        ...
```

Services are instantiated via FastAPI's `Depends`:

```python
# api/dependencies.py
async def get_ceremony_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user: UserContext = Depends(get_current_user),
) -> CeremonyService:
    return CeremonyService(db, redis, user)
```

---

## 4. API Design

### 4.1 RESTful Endpoint Structure

All endpoints are prefixed with `/api/v1/`.

| Domain | Endpoints | File |
|---|---|---|
| Ceremonies | `POST /api/v1/ceremonies`, `GET /api/v1/ceremonies/:id`, `POST /api/v1/ceremonies/:id/transition` | `api/v1/ceremonies.py` |
| Actions | `GET /api/v1/actions`, `POST /api/v1/actions`, `PATCH /api/v1/actions/:id` | `api/v1/actions.py` |
| Teams | `POST /api/v1/teams`, `GET /api/v1/teams/:id`, `POST /api/v1/teams/:id/members` | `api/v1/teams.py` |
| Templates | `GET /api/v1/templates`, `POST /api/v1/templates` | `api/v1/templates.py` |
| Integrations | `POST /api/v1/integrations`, `GET /api/v1/integrations/:id/sync` | `api/v1/integrations.py` |
| AI | `POST /api/v1/ai/cluster`, `POST /api/v1/ai/summarize`, `POST /api/v1/ai/embed` | `api/v1/ai.py` |
| Webhooks | `POST /api/v1/webhooks/jira`, `POST /api/v1/webhooks/stripe` | `api/v1/webhooks.py` |

### 4.2 API Versioning (URL-based)

```python
# app/main.py
from app.api.router import api_router

app = FastAPI(title="Scrum Ceremony Platform API")
app.include_router(api_router, prefix="/api/v1")

# Future: /api/v2/ when breaking changes are needed
# Strategy: Add new router, keep v1 alive with deprecation header
```

### 4.3 Request/Response Schemas with Pydantic

```python
# schemas/ceremony.py
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional

class CeremonyType(str, Enum):
    RETRO = "retro"
    POKER = "poker"
    STANDUP = "standup"
    HEALTH_CHECK = "health-check"

class CeremonyCreateConfig(BaseModel):
    """Request body for creating a ceremony."""
    
    name: str = Field(..., min_length=1, max_length=200, examples=["Sprint 42 Retro"])
    type: CeremonyType
    team_id: str = Field(..., pattern=r"^team_[a-z0-9]{20}$")
    template_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    anonymity_config: Optional[AnonymityConfig] = Field(default_factory=AnonymityConfig)
    timer_config: Optional[TimerConfig] = None
    
    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Name cannot be blank")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Sprint 42 Retrospective",
                    "type": "retro",
                    "team_id": "team_01hxj2g4e5f6g7h8i9j0k"
                }
            ]
        }
    )


class CeremonyResponse(BaseModel):
    """Response body for ceremony endpoints."""
    
    id: str
    name: str
    type: CeremonyType
    status: str  # idle, scheduled, active, completed, archived
    phase: Optional[str] = None
    team_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    @model_validator(mode="after")
    def ensure_phase_when_active(self):
        if self.status == "active" and not self.phase:
            raise ValueError("Active ceremony must have a phase")
        return self
    
    model_config = ConfigDict(from_attributes=True)


class TransitionRequest(BaseModel):
    event: PhaseEvent
    phase_duration_seconds: Optional[int] = Field(None, ge=0, le=3600)
    
    @field_validator("phase_duration_seconds")
    @classmethod
    def validate_timer(cls, v):
        if v is not None and v > 3600:
            raise ValueError("Timer cannot exceed 1 hour")
        return v


class AnonymityConfig(BaseModel):
    anonymous_creation: bool = True
    reveal_after_voting: bool = False
    anonymous_voting: bool = True
    show_participant_count: bool = True


class PhaseEvent(str, Enum):
    START_BRAINSTORM = "start_brainstorm"
    START_GROUPING = "start_grouping"
    START_VOTING = "start_voting"
    START_DISCUSSION = "start_discussion"
    START_ACTIONS = "start_actions"
    GO_BACK = "go_back"
    PAUSE = "pause"
    RESUME = "resume"
    COMPLETE = "complete"
    CANCEL = "cancel"
```

### 4.4 Standard API Envelope

```python
# schemas/api.py
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """Standard envelope for all API responses."""
    data: Optional[T] = None
    error: Optional[ApiError] = None
    meta: Optional[PaginatedMeta] = None

class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None
    correlation_id: str

class PaginatedMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    
    @classmethod
    def create(cls, page: int, page_size: int, total: int) -> "PaginatedMeta":
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        )
```

### 4.5 OpenAPI Documentation

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="Scrum Ceremony Platform",
        version="1.0.0",
        description="API for agile ceremony facilitation with real-time collaboration, AI-powered insights, and enterprise integrations.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(TenantMiddleware)
    
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app
```

### 4.6 Example Endpoint Implementation

```python
# api/v1/ceremonies.py
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/ceremonies", tags=["Ceremonies"])

@router.post(
    "",
    response_model=ApiResponse[CeremonyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ceremony",
    responses={
        201: {"description": "Ceremony created successfully"},
        403: {"description": "User does not have permission"},
        404: {"description": "Team or template not found"},
        422: {"description": "Validation error"},
    },
)
async def create_ceremony(
    config: CeremonyCreateConfig,
    service: CeremonyService = Depends(get_ceremony_service),
):
    """
    Create a new ceremony with:
    - Initial board configured from template (if provided)
    - on ceremony type
    - Facilitator role assigned to the creator
    """
    ceremony = await service.create(config)
    return ApiResponse(data=ceremony)


@router.post(
    "/{ceremony_id}/transition",
    response_model=ApiResponse[CeremonyResponse],
    summary="Transition ceremony to the next phase",
    responses={
        200: {"description": "Phase transitioned successfully"},
        400: {"description": "Invalid transition (guard condition failed)"},
        403: {"description": "Only the facilitator can transition phases"},
        404: {"description": "Ceremony not found"},
        409: {"description": "Ceremony is not active"},
    },
)
async def transition_phase(
    ceremony_id: str,
    request: TransitionRequest,
    service: CeremonyService = Depends(get_ceremony_service),
):
    ceremony = await service.transition_phase(ceremony_id, request.event)
    return ApiResponse(data=ceremony)
```

---

## 5. Service Layer

### 5.1 Service Layer Architecture

```mermaid
graph TD
    API["API Router Layer<br/>(api/v1/)"] -->|Depends| Deps["Dependency Injection<br/>(api/dependencies.py)"]
    Deps --> S1["CeremonyService"]
    Deps --> S2["ActionService"]
    Deps --> S3["BoardService"]
    Deps --> S4["TeamService"]
    Deps --> S5["IntegrationService"]
    Deps --> S6["AIService"]
    Deps --> S7["NotificationService"]
    
    S1 --> DB[(PostgreSQL)]
    S2 --> DB
    S3 --> DB
    S4 --> DB
    S5 --> DB
    S6 --> DB
    
    S1 --> RD[(Redis)]
    S2 --> RD
    S5 --> RD
    
    S1 -->|enqueues| T["Background Tasks"]
    S5 -->|calls| EXT["External Systems"]
    S6 -->|calls ext| OLLAMA["Ollama Server"]
```

### 5.2 Dependency Injection via FastAPI Depends

```python
# api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as session:
        yield session

# Redis
async def get_redis() -> AsyncGenerator[Redis, None]:
    yield get_redis_client()

# Services
async def get_ceremony_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user: UserContext = Depends(get_current_user),
) -> CeremonyService:
    return CeremonyService(db, redis, user)

async def get_integration_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    user: UserContext = Depends(get_current_user),
) -> IntegrationService:
    return IntegrationService(db, redis, user)
```

### 5.3 Transaction Management (Unit of Work Pattern)

```python
# app/unit_of_work.py
from contextlib import asynccontextmanager

class UnitOfWork:
    """Manages transaction boundaries for services."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.committed = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        elif not self.committed:
            await self.session.commit()
    
    async def commit(self):
        await self.session.commit()
        self.committed = True
    
    async def rollback(self):
        await self.session.rollback()


# Usage in services
class CeremonyService:
    def __init__(self, db: AsyncSession, redis: Redis, user: UserContext):
        self.db = db
        self.redis = redis
        self.user = user
    
    async def create(self, config: CeremonyCreateConfig) -> Ceremony:
        async with UnitOfWork(self.db) as uow:
            ceremony = Ceremony(
                name=config.name,
                type=config.type,
                team_id=config.team_id,
                created_by=self.user.user_id,
                status="idle",
            )
            self.db.add(ceremony)
            
            # Create board with columns from template
            board = Board(ceremony_id=ceremony.id, config=config.to_board_config())
            self.db.add(board)
            
            # Create initial phase
            phase = Phase(ceremony_id=ceremony.id, name="brainstorm")
            self.db.add(phase)
            
            # Audit log
            audit = AuditLog(
                user_id=self.user.user_id,
                action="ceremony.create",
                resource_id=ceremony.id,
            )
            self.db.add(audit)
            
            await uow.commit()
        
        # Cache ceremony state in Redis
        await self.redis.hset(
            f"ceremony:{ceremony.id mapping={"status": ceremony.status, "phase": None, "type": ceremony.type},
        )
        
        return ceremony
```

### 5.4 One Service Per Bounded Context

| Bounded Context | Service | Responsibilities | Dependencies |
|---|---|---|---|
| Ceremony | `CeremonyService` | Creation, phase transitions, state persistence | BoardService |
| Action | `ActionService` | CRUD, status tracking, carry-forward, overdue detection | NotificationService |
| Collaboration | `BoardService` | Board CRUD, sticky note operations, voting | WebSocket fan-out |
| Team | `TeamService` | Team & membership management, permissions | IdentityService |
| Template | `TemplateService` | Template CRUD, versioning, sharing | TeamService |
| Integration | `IntegrationService` | External system sync, webhook handling | HttpClient, CircuitBreaker |
| AI | `AIService` | Cluster jobs, summaries, embeddings | Ollama client, pgvector |
| Notification | `NotificationService` | Multi-channel notification delivery | Various senders |
| Analytics | `AnalyticsService` | Metric aggregation, health dashboards | PostgreSQL |

---

## 6. Ceremony Orchestration Service

### 6.1 Finite State Machine Enforcement

```mermaid
stateDiagram-v2
    [*] --> idle: Ceremony created
    idle --> scheduled: schedule
    scheduled --> active: start
    active --> completed: complete
    
    state active {
        [*] --> brainstorm
        brainstorm --> grouping: start_grouping
        grouping --> voting: start_voting
        voting --> discussion: start_discussion
        discussion --> actions: start_actions
        actions --> completed: complete
        
        brainstorm --> brainstorm: submit_item
        grouping --> grouping: modify_items, manual_group, ai_cluster
        voting --> voting: cast_vote
        discussion --> discussion: discuss_item
        actions --> actions: create_action, edit_action
        
        grouping --> brainstorm: go_back
        voting --> grouping: go_back
        discussion --> voting: go_back
        actions --> discussion: go_back
    }
    
    completed --> archived: archive
```

### 6.2 Phase Transition API with Guard Evaluation

```python
# services/ceremony_service.py
class CeremonyService:
    def __init__(self, db: AsyncSession, redis: Redis, user: UserContext):
        self.db = db
        self.redis = redis
        self.user = user
    
    # Guard conditions mapping
    GUARDS: dict[str, Callable[[Ceremony, UserContext], bool]] = {
        "must_be_facilitator": lambda c, u: c.facilitator_id == u.user_id,
        "certain_member": lambda c, u: u.user_id in [m.user_id for m in c.team.members],
        "min_items": lambda c, u: len(c.board.items) >= c.min_items_required,
        "phase_active": lambda c, u: c.status == "active",
    }
    
    async def transition_phase(
        self, ceremony_id: str, event: PhaseEvent
    ) -> Ceremony:
        """
        Transition ceremony to the next phase based on the event.
        
        Guards are evaluated BEFORE the transition:
        - User must have facilitator role
        - Ceremony must be active
        - Certain phases have additional requirements
        """
        ceremony = await self.get_ceremony(ceremony_id)
        
        # Validate guards
        transition_key = f"{ceremony.phase}:{event}"
        guards = self._get_transition_guards(ceremony, event)
        
        for guard_name, guard_fn in guards.items():
            if not guard_fn(ceremony, self.user):
                raise GuardConditionFailedError(
                    guard=guard_name,
                    description=GUARD_DESCRIPTIONS[guard_name],
                    current_phase=ceremony.phase,
                    current_state=ceremony.status,
                )
        
        # Execute transition
        old_phase = ceremony.phase
        new_phase = self.compute_next_phase(ceremony.type, ceremony.phase, event)
        
        # Persist
        ceremony.phase = new_phase
        ceremony.updated_at = datetime.now(UTC)
        await self.db.flush()
        
        # Audit
        self.db.add(AuditLog(
            user_id=self.user.user_id,
            action="ceremony.transition",
            resource_id=ceremony_id,
            details={"from": old_phase, "to": new_phase, "event": event},
        ))
        
        # Broadcast via Redis pub/sub → WebSocket server
        await self.redis.publish(
            f"ceremony:{ceremony_id}:state_changed",
            json.dumps({
                "ceremony_id": ceremony_id,
                "old_phase": old_phase,
                "new_phase": new_phase,
                "transitioned_by": self.user.user_id,
                "transitioned_at": datetime.now(UTC).isoformat(),
            }),
        )
        
        return ceremony
    
    def _get_transition_guards(
        self, ceremony: Ceremony, event: PhaseEvent
    ) -> list[tuple[str, Callable]]:
        """Return list of guard functions applicable to this transition."""
        guards = [
            ("must_be_facilitator", self.GUARDS["must_be_facilitator"]),
            ("phase_active", self.GUARDS["phase_active"]),
        ]
        
        if event == PhaseEvent.START_ACTIONS:
            guards.append(("min_items", self.GUARDS["min_items"]))
        
        return guards
```

### 6.3 State Persistence and Recovery

```python
# State is persisted to both PostgreSQL and Redis:
# - PostgreSQL: source of truth, durable across restarts
# - Redis: fast reads for WebSocket server
# On startup, Redis state is rebuilt from PostgreSQL if missing.

async def persist_state(self, ceremony_id: str, state: CeremonyState):
    # 1. Write to PostgreSQL
    await self.db.execute(
        update(Ceremony)
        .where(Ceremony.id == ceremony_id)
        .values(status=state.status, phase=state.phase)
    )
    
    # 2. Refresh Redis cache (TTL 1 hour)
    await self.redis.hset(f"ceremony:{ceremony_id}:state", mapping=state.dict())
    await self.redis.expire(f"ceremony:{ceremony_id}:state", 3600)
    
    # 3. Set "active ceremonies" sorted set for monitoring
    await self.redis.zadd(
        "ceremonies:active",
        {ceremony_id: int(datetime.now(UTC).timestamp())}
    )
```

### 6.4 Concurrent Access Handling (Optimistic Locking)

```python
# models/ceremony.py
class Ceremony(Base):
    __tablename__ = "ceremonies"
    
    id: str = mapped_column(String, primary_key=True)
    status: str = mapped_column(String, nullable=False)
    phase: str = mapped_column(String, nullable=True)
    version: int = mapped_column(Integer, nullable=False, default=1)
    # ... other fields

# Usage: SQLAlchemy automatically checks version on UPDATE
# If another process incremented version → raises StaleDataError
# Service catches this → returns 409 Conflict
```

```python
# Error handling
from sqlalchemy.orm.exc import StaleDataError

try:
    await self.db.commit()
except StaleDataError:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ceremony was modified by another request. Please refresh and retry.",
    )
```

---

## 7. Action Service

### 7.1 Cross-Ceremony Action Register

```python
# models/action.py
class ActionItem(Base):
    __tablename__ = "action_items"
    
    id: str = mapped_column(String, primary_key=True)
    title: str = mapped_column(String, nullable=False)
    description: str = mapped_column(Text, nullable=True)
    status: ActionStatus = mapped_column(Enum(ActionStatus), default=ActionStatus.OPEN)
    priority: Priority = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    
    # Traceability
    source_ceremony_id = mapped_column(ForeignKey("ceremonies.id"))
    team_id = mapped_column(ForeignKey("teams.id"))
    
    # Ownership & Dates
    creator_id = mapped_column(ForeignKey("users.id"))
    assignee_id = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    
    # External Integration
    linked_jira_issue_key = mapped_column(String, nullable=True)
    
    created_at = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
```

### 7.2 Idempotent Action Creation

```python
# services/action_service.py
class ActionService:
    async def create(
        self,
        ceremony_id: str,
        title: str,
        **kwargs,
    ) -> ActionItem:
        """
        Create an action item from a ceremony.
        Uses idempotency key to prevent duplicates from retries.
        """
        idempotency_key = kwargs.get("idempotency_key")
        
        if idempotency_key:
            # Check if already created
            existing = await self.db.execute(
                select(ActionItem)
                .where(ActionItem.idempotency_key == idempotency_key)
            )
            if existing:
                return existing.scalar_one()
        
        action = ActionItem(
            id=generate_id("action"),
            source_ceremony_id=ceremony_id,
            title=title,
            status=ActionStatus.OPEN,
            team_id=kwargs["team_id"],
            assignee_id=kwargs.get("assignee_id"),
            due_date=kwargs.get("due_date"),
            idempotency_key=idempotency_key,
        )
        
        self.db.add(action)
        await self.db.flush()
        return action
    
    async def bulk_create_from_ceremony(
        self, ceremony_id: str, items: list[ActionCreateConfig]
    ) -> list[ActionItem]:
        """Create multiple action items when a ceremony completes."""
        actions = []
        for config in items:
            action = await self.create(ceremony_id, **config)
            actions.append(action)
        
        await self.db.flush()
        return actions
```

### 7.3 Carry-Forward Logic

```python
async def get_carry_forward_actions(self, team_id: str) -> list[ActionItem]:
    """Get open action items from previous ceremonies in the team."""
    result = await self.db.execute(
        select(ActionItem)
        .where(
            ActionItem.team_id == team_id,
            ActionItem.status.in_([ActionStatus.OPEN, ActionStatus.OVERDUE]),
        )
        .order_by(ActionItem.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()
```

### 7.4 Overdue Detection Background Job

```python
# tasks/overdue_actions.py
from arq import cron

async def check_overdue_actions(ctx):
    """ARQ cron job: Mark overdue action items daily."""
    db = ctx["db"]
    now = datetime.now(UTC)
    
    # Find actions past due date
    overdue = await db.execute(
        update(ActionItem)
        .where(
            ActionItem.due_date < now,
            ActionItem.status.in_([ActionStatus.OPEN, ActionStatus.IN_PROGRESS]),
        )
        .values(status=ActionStatus.OVERDUE, updated_at=now)
        .returning(ActionItem)
    )
    
    actions = overdue.scalars().all()
    
    # Notify assignees
    notification_service = ctx["notification_service"]
    for action in actions:
        await notification_service.send(
            user_id=action.assignee_id,
            context={"action_title": action.title, "due_date": action.due_date},
        )
    
    return {"overdue_count": len(actions)}

# ARQ cron schedule
class WorkerSettings:
    cron_jobs = [
        cron(check_overdue_actions, hour=9, minute=0),  # Daily at 9 AM
    ]
```

---

## 8. Integration Service

### 8.1 Connector Pattern

```python
# integrations/base.py
from abc import ABC, abstractmethod

class IntegrationConnector(ABC):
    """Base class for all external system connectors."""
    
    def __init__(self, config: IntegrationConfig, http_client: AsyncClient):
        self.config = config
        self.http_client = http_client
    
    @abstractmethod
    async def authenticate(self) -> AuthToken:
        """Validate credentials and return auth token."""
        ...
    
    @abstractmethod
    async def sync(self) -> SyncResult:
        """Perform incremental sync."""
        ...
    
    @abstractmethod
    async def handle_webhook(self, payload: dict) -> None:
        """Process incoming webhook."""
        ...
```

### 8.2 Jira Cloud Connector

```python
# integrations/jira_.py
class JiraConnector(IntegrationConnector):
    """Jira Cloud bidirectional sync."""
    
    def __init__(self, config: JiraConfig, http_client: AsyncClient):
        super().__init__(config, http_client)
        self.base_url = f"https://{config.atlassian_subdomain}.atlassian.net"
        self.auth = BasicAuth(config.email, config.api_token)
    
    async def authenticate(self) -> AuthToken:
        resp = await self.http_client.get(
            f"{self.base_url}/rest/api/3/myself",
            auth=self.auth,
        )
        resp.raise_for_status()
        return AuthToken(
            token=f"{self.config.email}:{self.config.api_token}",
            expires_at=datetime.now(UTC) + timedelta(days=365),
        )
    
    async def sync(self) -> SyncResult:
        """Incremental sync: pull issues updated since last sync cursor."""
        return SyncResult(items=[], errors=[])
    
    async def create_issue(self, action: ActionItem) -> JiraIssue:
        """Create a Jira issue from an action item."""
        resp = await self.http_client.post(
            f"{self.base_url}/rest/api/3/issue",
            auth=self.auth,
            json={
                "fields": {
                    "project": {"key": self.config.project_key},
                    "summary": f"[Retro Action] {action.title}",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{
                                "type": "text",
                                "text": action.description or "No description.",
                            }],
                        }],
                    },
                    "issuetype": {"name": self.config.issue_type},
                },
            },
        )
        resp.raise_for_status()
        return JiraIssue(**resp.json())
    
    async def handle_webhook(self, payload: dict) -> None:
        """Handle Jira webhook: issue updated, created, deleted."""
        event_type = payload.get("webhookEvent", "")
        
        match event_type:
            case "jira:issue_updated":
                await self._handle_issue_updated(payload["issue"])
            case "jira:issue_created":
                await self._handle_issue_created(payload["issue"])
            case _:
                logger.warning(f"Unhandled Jira webhook event: {event_type}")
```

### 8.3 ERPNext Connector

```python
# integrations/erpnext.py
class ERPNextConnector(IntegrationConnector):
    """ERPNext REST API connector."""
    
    def __init__(self, config: ERPNextConfig, http_client: AsyncClient):
        super().__init__(config, http_client)
        self.base_url = f"{config.base_url}/api/resource"
        self.auth = (config.api_key, config.api_secret)
    
    async def sync(self) -> SyncResult:
        """Pull employee, department, and leave data."""
        return SyncResult(items=[], errors=[])
    
    async def handle_webhook(self, payload: dict) -> None:
        logger.info(f"ERPNext push: {payload}", extra={"payload": payload})
```

### 8.4 Stripe Webhook Handler

```python
# api/v1/webhooks.py
import stripe

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/stripe", include_in_schema=False)
async def handle_stripe_webhook(
    request: Request,
    integration_service: IntegrationService = Depends(get_integration_service),
):
    """Handle Stripe webhook events for subscription management."""
    body = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            body, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    
    tenant_id = event.data.object.metadata.get("tenant_id")
    
    match event.type:
        case "customer.subscription.created":
            await integration_service.activate_subscription(tenant_id, event.data.object)
        case "customer.subscription.deleted":
            await integration_service.suspend_subscription(tenant_id)
        case "payment_intent.succeeded":
            await integration_service.confirm_payment(tenant_id, event.data.object)
        case "payment_intent.payment_failed":
            await integration_service.notify_payment_failed(tenant_id, event.data.object)
        case _:
            logger.info(f"Unhandled Stripe webhook: {event.type}")
    
    return {"status": "ok"}
```

### 8.5 Dead-Letter Queue Processing

```python
# tasks/dead_letter.py
class DeadLetterQueue:
    """Process failed sync operations."""
    
    DLQ_KEY = "integrations:dead_letter"
    
    async def enqueue(self, redis: Redis, task: FailedTask):
        """Add a failed task to the dead letter queue."""
        await redis.lpush(self.DLQ_KEY, json.dumps(task.model_dump()))
    
    async def process(self, redis: Redis, max_items: int = 100) -> list[FailedTask]:
        """Process items from the DLQ (runs as a daily cron)."""
        items = []
        for _ in range(max_items):
            raw = await redis.rpop(self.DLQ_KEY)
            if not raw:
                break
            task = FailedTask.model_validate_json(raw)
            
            if task.retry_count >= 5:
                logger.error(f"Task {task.task_id} exceeded max retries")
                continue
            
            # Re-enqueue with exponential backoff
            delay = 2 ** task.retry_count
            await self.retry_after_delay(task, delay)
            items.append(task)
        
        return items
```

---

## 9. AI Service

### 9.1 Ollama Client Wrapper

```python
# services/ai/ollama_client.py
import httpx
from typing import AsyncGenerator

class OllamaClient:
    """Async wrapper for Ollama REST API."""
    
    def __init__(self, base_url: str, timeout: float = 300.0):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> str:
        """Single-response generation."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                **({"num_predict": max_tokens} if max_tokens else {}),
            },
        }
        if system:
            payload["system"] = system
        if response_format:
            payload["response_format"] = response_format
        
        response = await self.client.post("/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"]
    
    async def generate_stream(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming generation for long summaries."""
        payload = {"model": model, "prompt": prompt, "stream": True, "system": system}
        async with self.client.stream("POST", "/api/generate", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        yield chunk["response"]
    
    async def embed(self, model: str, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        embeddings = []
        for text in texts:
            response = await self.client.post(
                "/api/embeddings",
                json={"model": model, "input": text},
            )
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        return embeddings
    
    async def health_check(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            resp = await self.client.get("/api/tags")
            return resp.status_code == 200
        except httpx.TransportError:
            return False
```

### 9.2 Embedding Generation Batch Job

```python
# tasks/ai_tasks.py
from arq import cron

async def generate_embeddings_job(ctx, ceremony_id: str):
    """ARQ job: Generate embeddings for retro items."""
    db = ctx["db"]
    
    # Fetch items without embeddings
    result = await db.execute(
        select(RetroItem.content)
        .where(
            RetroItem.ceremony_id == ceremony_id,
            RetroItem.embedding.is_(None),
            RetroItem.content.is_not(None),
        )
    )
    texts = result.scalars().all()
    
    if not texts:
        return {"count": 0}
    
    # Generate embeddings via Ollama
    ollama: OllamaClient = ctx["ollama_client"]
    embeddings = await ollama.embed(
        model="mxbai-embed-large",
        texts=texts,
    )
    
    # Store embeddings via pgvector
    for text, embedding in zip(texts, embeddings):
        await db.execute(
            update(RetroItem)
            .where(RetroItem.content == text)
            .values(embedding=embedding)
        )
    
    await db.commit()
    return {"count": len(embeddings)}
```

### 9.3 Clustering Pipeline

```python
# services/ai/clustering.py
from sklearn.cluster import DBSCAN
import numpy as np

class ClusteringPipeline:
    """Embed → cluster → label pipeline."""
    
    def __init__(self, ollama: OllamaClient):
        self.ollama = ollama
    
    async def cluster_items(
        self,
        texts: list[str],
        eps: float = 0.3,
        min_samples: int = 2,
    ) -> list[Cluster]:
        """
        Cluster retro items by semantic similarity.
        
        Steps:
        1. Generate embeddings (Ollama: mxbai-embed-large)
        2. DBSCAN clustering
        3. Label generation via LLM (Ollama: gemma-3-9b)
        """
        if len(texts) < 2:
            return [Cluster(name="All items", items=texts)]
        
        # Step 1: Embed
        embeddings = await self.ollama.embed("mxbai-embed-large", texts)
        
        # Step 2: DBSCAN clustering
        X = np.array(embeddings)
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        labels = clustering.labels_
        
        # Group by cluster
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        groups: dict[int, list[str]] = {i: [] for i in range(n_clusters)}
        noise: list[str] = []
        
        for text, label in zip(texts, labels):
            if label == -1:
                noise.append(text)
            else:
                groups[label].append(text)
        
        # Step 3: Label clusters via LLM prompt
        clusters = []
        for label, items in groups.items():
            prompt = f"""Given these retrospective items, provide a short 2-5 word cluster label:

{chr(10).join(f"- {item}" for item in items)}

Label:"""
            
            cluster_name = await self.ollama.generate(
                model="gemma-3-9b-instruct",
                prompt=prompt,
                temperature=0.3,
                max_tokens=50,
            )
            
            clusters.append(Cluster(name=cluster_name.strip(), items=items))
        
        if noise:
            clusters.append(Cluster(name="Uncategorized", items=noise))
        
        return clusters
```

### 9.4 Summary Generation with Structured Output

```python
# services/ai/summarizer.py
class CeremonySummarizer:
    """Generate structured summaries from ceremony data using LLM."""
    
    SUMMARY_SCHEMA = {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "description": "2-3 sentence overview"},
            "key_themes": {
                "type": "array",
                "items": {"type": "string"},
            },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "owner": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    },
                },
            },
            "sentiment": {
                "type": "string",
                "enum": ["positive", "neutral", "negative", "mixed"],
            },
        },
        "required": ["summary", "key_themes", "action_items", "sentiment"],
    }
    
    async def summarize(self, ceremony: Ceremony) -> CeremonySummary:
        """Generate a structured summary for a completed ceremony."""
        board_items = [item.content for item in ceremony.board.items if item.content]
        
        prompt = f"""You are an agile coach. Analyze this retrospective and provide a structured summary.

Items discussed:
{chr(10).join(f"- {item}" for item in board_items)}

Voting results: {get_votes_text(ceremony)}

Provide a JSON summary with: summary, key_themes, suggested_actions, sentiment."""
        
        response = await self.ollama.generate(
            model="gemma-3-9b-instruct",
            prompt=prompt,
            temperature=0.5,
            max_tokens=1000,
            response_format={"type": "json_schema", "json_schema": {"name": "CeremonySummary", "schema": self.SUMMARY_SCHEMA}},
        )
        
        return CeremonySummary.model_validate_json(response)
```

### 9.5 Prompt Template Management

```python
# models/prompt_template.py
class PromptTemplate(Base):
    """Versioned prompt templates stored in DB."""
    __tablename__ = "prompt_templates"
    
    id = mapped_column(String, primary_key=True)
    name = mapped_column(String, index=True, unique=True)  # e.g., "retro_summary"
    version = mapped_column(Integer, default=1)
    system_prompt = mapped_column(Text)
    user_prompt_template = mapped_column(Text)  # Supports {variables}
    default_model = mapped_column(String, default="gemma-3-9b-instruct")
    temperature = mapped_column(Float, default=0.5)
    max_tokens = mapped_column(Integer, default=1000)
    json_schema = mapped_column(JSONB, nullable=True)
    
    created_at = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
```

### 9.6 Fallback to Cloud LLM

```python
# services/ai/fallback.py
class LLMService:
    """
    Primary: Ollama (on-prem)
    Fallback: Cloud LLM (e.g., OpenAI) via LiteLLM
    """
    def __init__(self, ollama: OllamaClient, cloud_client: AsyncClient):
        self.ollama = ollama
        self.cloud_client = cloud_client
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Try Ollama first, fallback to cloud."""
        try:
            return await self.ollama.generate(
                model=kwargs.get("model", "gemma-3-9b-instruct"),
                prompt=prompt,
            )
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            logger.warning(f"Ollama unavailable ({e}), falling back to cloud")
            
            cloud_model = kwargs.get("fallback_model", "gpt-4o-mini")
            response = await self.cloud_client.post(
                "/chat/completions",
                json={
                    "model": cloud_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.2),
                },
            )
            return response.json()["choices"][0]["message"]["content"]
```

---

## 10. Background Jobs

### 10.1 ARQ Task Definitions

```python
# tasks/definitions.py
# ARQ uses simple async functions as tasks

# --- AI Jobs ---
async def run_ai_clustering(ctx, ceremony_id: str) -> dict:
    """Cluster retro items using AI embeddings."""
    db = ctx["db"]
    items = await db.execute(
        select(RetroItem.content)
        .where(RetroItem.ceremony_id == ceremony_id)
    )
    texts = items.scalars().all()
    
    pipeline = ClusteringPipeline(ctx["ollama_client"])
    clusters = await pipeline.cluster_items(texts)
    
    # Store clusters
    for cluster in clusters:
        db.add(ClusterResult(ceremony_id=ceremony_id, name=cluster.name, items=cluster.items))
    await db.commit()
    return {"clusters_formed": len(clusters)}

async def generate_ceremony_summary(ctx, ceremony_id: str) -> None:
    """Generate AI summary for completed ceremony."""
    db = ctx["db"]
    ollama = ctx["ollama_client"]
    
    summarizer = CeremonySummarizer(db, ollama)
    summary = await summarizer.summarize(ceremony_id)
    
    db.add(summary)
    await db.commit()
```

### 10.2 Retry Policies (ARQ WorkerSettings)

```python
# app/worker.py
from arq import cron

class WorkerSettings:
    """ARQ worker configuration."""
    
    redis_settings = RedisSettings(host="localhost", port=6379)
    max_tries = 5                           # Retry failed jobs up to 5 times
    job_timeout = 300                       # 5 minutes max per job
    keep_result = 3600                      # Keep results for 1 hour
    max_jobs = 20                           # Max concurrent jobs
    
    # Cron jobs
    cron_jobs = [
        cron(sync_jira_projects, minute={0, 15, 30, 45}),   # Every 15 minutes
        cron(sync_erp_data, hour="*"),                        # Every hour
        cron(check_overdue_actions, hour=9, minute=0),        # Daily at 9 AM
        cron(process_dead_letter_queue, hour=2, minute=0),    # Daily 2 AM
    ]
    
    functions = [
        run_ai_clustering,
        generate_ceremony_summary,
        sync_jira_projects,
        sync_erp_data,
        check_overdue_actions,
        process_dead_letter_queue,
    ]


# Manual enqueueing from API
async def enqueue_clustering(redis: Redis, ceremony_id: str):
    await redis.enqueue_job("run_ai_clustering", ceremony_id=ceremony_id)
```

### 10.3 Idempotency Keys for Jobs

```python
# Idempotency prevents duplicate jobs when a task is retried
class IdempotencyManager:
    KEY_PREFIX = "idempotency:job:"
    
    async def check_and_set(self, redis: Redis, job_id: str, ttl: int = 3600) -> bool:
        """Returns True if this job is new. False if already processed."""
        return await redis.set(self.KEY_PREFIX + job_id, "1", nx=True, ex=ttl)
    
    async def clear(self, redis: Redis, job_id: str):
        await redis.delete(self.KEY_PREFIX + job_id)


# Usage
async def sync_jira_projects(ctx):
    idempotency = IdempotencyManager()
    
    # Check if already run this hour
    hour_key = f"jira_sync:{datetime.now(UTC).strftime('%Y%m%d%H')}"
    if not await idempotency.check_and_set(ctx["redis"], hour_key, ttl=7200):
        logger.info("Jira sync already ran this hour, skipping")
        return
    
    logger.info("Running Jira sync...")
    # ... sync logic
```

### 10.4 Dead-Letter Queue

```python
# tasks/dead_letter.py
async def process_dead_letter_queue(ctx):
    """Daily: Retry failed items from dead letter queue."""
    db = ctx["db"]
    redis = ctx["redis"]
    
    items = await redis.lrange("dead_letter:queue", 0, -1)
    await redis.delete("dead_letter:queue")
    
    processed = 0
    failed = []
    
    for raw in items:
        task = json.loads(raw)
        
        # Max retry check
        if task["retry_count"] >= 5:
            failed.append(task)
            continue
        
        # Re-enqueue with higher priority
        try:
            await redis.rpush("arq:queue:highest", json.dumps({
                "function": task["function"],
                "args": tuple(task.get("args", ())),
                "kwargs": dict(task.get("kwargs", {})),
            }))
            processed += 1
        except Exception:
            failed.append(task)
    
    if failed:
        await db.execute(
            insert(DeadLetterArchive),
            [{"task": json.dumps(f), "failed_at": datetime.now(UTC)} for f in failed]
        )
    
    return {"processed": processed, "failed_permanently": len(failed)}
```

### 10.5 Background Job Monitoring

```python
# Logging and observability for ARQ jobs
import structlog

logger = structlog.get_logger("background_jobs")

# Optional: custom metrics
from prometheus_client import Counter, Histogram

job_duration = Histogram(
    "background_job_duration_seconds",
    "Time spent processing background jobs",
    labelnames=["job_name"],
)
job_failures = Counter(
    "background_job_failures_total",
    "Total number of background job failures",
    labelnames=["job_name"],
)


# Decorator for job instrumentation
def monitored_job(name: str):
    def decorator(func):
        async def wrapper(ctx, *args, **kwargs):
            start = time.monotonic()
            try:
                result = await func(ctx, *args, **kwargs)
                job_duration.labels(job_name=name).observe(time.monotonic() - start)
                return result
            except Exception:
                job_failures.labels(job_name=name).inc()
                logger.error("Background job failed", job_name=name, exc_info=True)
                raise
        return wrapper
    return decorator
```

---

## 11. Multi-Tenancy Middleware

### 11.1 Tenant Context Extraction

```python
# middleware/tenant.py
from starlette.middleware.base import BaseHTTPMiddleware
import contextvars

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts tenant_id from JWT and sets it as context.
    Uses contextvars to propagate tenant_id through async call chain.
    """
    
    tenant_context = contextvars.ContextVar("tenant_id", default=None)
    
    async def dispatch(self, request: Request, call_next):
        tenant_id = None
        
        # Extract from JWT (set by auth middleware)
        user = getattr(request.state, "user", None)
        if user:
            tenant_id = user.tenant_id
        
        # Fallback: custom header for webhook endpoints
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")
        
        token = self.tenant_context.set(tenant_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Tenant-ID"] = tenant_id or "none"
            
            # Set PostgreSQL session variable for RLS
            if hasattr(request.state, "db"):
                await request.state.db.execute(
                    text("SET LOCAL app.current_tenant = :tenant"),
                    {"tenant": tenant_id or ""},
                )
            
            return response
        finally:
            self.tenant_context.reset(token)
    
    @classmethod
    def get_current_tenant(cls) -> str | None:
        return cls.tenant_context.get()
```

### 11.2 PostgreSQL Session Variable Setting

```python
# Set tenant for RLS on every request
from sqlalchemy import event

@event.listens_for(AsyncSession, "after_begin")
async def set_tenant_session_variable(session, transaction, connection):
    """Automatically SET LOCAL app.current_tenant before every query."""
    tenant = TenantMiddleware.get_current_tenant()
    if tenant:
        await connection.execute(
            text("SET LOCAL app.current_tenant = :tenant"),
            {"tenant": tenant},
        )
```

### 11.3 Row-Level Security (RLS) Enforcement

```sql
-- Database migration: Enable RLS on all tenant-scoped tables
ALTER TABLE ceremonies ENABLE ROW LEVEL SECURITY;

-- Policy: Rows are visible only to their tenant
CREATE POLICY tenant_ceremony_policy ON ceremonies
    USING (tenant_id = current_setting('app.current_tenant')::text);

-- Policy: Rows can only be modified by their tenant
CREATE POLICY tenant_ceremony_insert ON ceremonies
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::text);
```

---

## 12. Database Migrations

### 12.1 Alembic Configuration

```python
# alembic/env.py
from app.models.base import Base
from app.config import settings

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(settings.DATABASE_URL)
    
    async with connectable.connect() as connection:
        await connection.run_migrations_online()

# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/scrum_db
```

### 12.2 Migration Script Naming Convention

**Naming convention:** `{sequence}_{description}.py`

Examples:
- `001_initial_schema.py`
- `002_add_ceremony_voting.py`
- `003_add_ai_embeddings.py`
- `004_add_rls_policies.py`
- `005_create_action_overdue_idx.py`

### 12.3 Zero-Downtime Migration Strategy

```python
# IMPORTANT: avoid locked tables during migration
# - Large table changes use `pt-online-schema-change`
# - New columns must be DEFAULT or NULL initially
# - Old columns removed in a SEPARATE deploy after code no longer uses them

# Example: Adding a new nullable column (safe)
def upgrade():
    op.add_column(
        "ceremonies",
        sa.Column("new_config", sa.JSONB, nullable=True, server_default="{}"),
    )

# NEVER do this in single transaction on production:
# op.alter_column("ceremonies", "existing_col", nullable=False)

# INSTEAD: multi-step deploy
# PR 1: Add column as nullable
# Deploy: code writes to both old and new columns
# PR 2: Backfill data
# PR 3: Make column non-nullable
# Deploy: code reads from new column only
# Future PR: Drop old column
```

### 12.4 RLS Policy Migrations

```python
# alembic/versions/004_add_rls_policies.py
"""Add row-level security policies

Revision ID: 004
Revises: 003
Create Date: 2026-03-01 10:00:00.000000
"""

def upgrade():
    # Enable RLS on tables
    op.execute("ALTER TABLE ceremonies ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE action_items ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE boards ENABLE ROW LEVEL SECURITY")
    
    # Create policies
    op.execute("""
        CREATE POLICY tenant_isolation ON ceremonies
            USING (tenant_id = current_setting('app.current_tenant')::text)
            WITH CHECK (tenant_id = current_setting('app.current_tenant')::text)
    """)
    op.execute("""
        CREATE POLICY tenant_isolation ON action_items
            USING (tenant_id = current_setting('app.current_tenant')::text)
            WITH CHECK (tenant_id = current_setting('app.current_tenant')::text)
    """)
    op.execute("""
        CREATE POLICY tenant_isolation ON boards
            USING (tenant_id = current_setting('app.current_tenant')::text)
            WITH CHECK (tenant_id = current_setting('app.current_tenant')::text)
    """)

def downgrade():
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON ceremonies")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON action_items")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON boards")
    op.execute("ALTER TABLE ceremonies DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE action_items DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE boards DISABLE ROW LEVEL SECURITY")
```

---

## 13. Auth Middleware

### 13.1 Clerk JWT Validation

```python
# middleware/auth.py
import jwt
from jwt import PyJWKClient
from starlette.middleware.base import BaseHTTPMiddleware

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Validates Clerk JWT tokens via JWKS endpoint.
    Injects UserContext into request state.
    """
    
    JWKS_URL = "https://your-app.clerk.accounts.dev/.well-known/jwks.json"
    
    def __init__(self, app):
        super().__init__(app)
        self.jwks_client = PyJWKClient(self.JWKS_URL, cache_keys=True)
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes
        if self._is_public_route(request):
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.CLERK_AUDIENCE,
                issuer=settings.CLERK_ISSUER,
            )
            
            # Build user context
            user = UserContext(
                user_id=payload["sub"],
                email=payload.get("email", ""),
                name=payload.get("name", payload.get("email", "")),
                tenant_id=payload.get("org_id", payload.get("tenant_id", "")),
                role=payload.get("role", "member"),
                permissions=payload.get("permissions", []),
            )
            
            # Inject into request state
            request.state.user = user
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired", code="token_expired")
        except jwt.InvalidAudienceError:
            raise AuthenticationError("Invalid audience", code="invalid_audience")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}", code="invalid_token")
        
        return await call_next(request)
    
    PUBLIC_ROUTES = {"/health", "/api/docs", "/api/redoc", "/api/openapi.json", "/api/v1/webhooks/"}
    
    def _is_public_route(self, request: Request) -> bool:
        return request.url.path in self.PUBLIC_ROUTES
```

### 13.2 Role Extraction and Permission Enforcement

```python
# models/auth.py
from enum import Enum
from pydantic import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    SCRUM_MASTER = "scrum_master"
    MEMBER = "member"
    VIEWER = "viewer"

class UserContext(BaseModel):
    user_id: str
    email: str
    name: str
    tenant_id: str
    role: UserRole
    permissions: list[str] = []
```

### 13.3 Permission Enforcement Decorator

```python
# api/dependencies.py
from functools import wraps
from fastapi import HTTPException, status

def require_permission(permission: str):
    """Decorator to enforce permission at the endpoint level."""
    async def dependency(
        user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if permission not in user.permissions and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
                headers={"X-Required-Permission": permission},
            )
        return user
    return dependency


# Usage in endpoint
@router.post(
    "/ceremonies/{ceremony_id}/transition",
    dependencies=[Depends(require_permission("ceremony:transition"))],
)
async def transition_phase(
    ceremony_id: str,
    request: TransitionRequest,
    service: CeremonyService = Depends(get_ceremony_service),
):
    ...
```

---

## 14. Error Handling

### 14.1 Structured Error Responses

```python
# middleware/error_handling.py
from starlette.middleware.base import BaseHTTPMiddleware

class StructuredErrorMiddleware(BaseHTTPMiddleware):
    """Ensures all error responses follow a consistent JSON envelope."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppException as e:
            return JSONResponse(
                status_code=e.status_code,
                content=ApiResponse(
                    error=ApiError(
                        code=e.error_code,
                        message=e.message,
                        details=e.details,
                        correlation_id=getattr(request.state, "correlation_id", "unknown"),
                    ),
                ).model_dump(),
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content=ApiResponse(
                    error=ApiError(
                        code=f"HTTP_{e.status_code}",
                        message=str(e.detail),
                        correlation_id=getattr(request.state, "correlation_id", "unknown"),
                    ),
                ).model_dump(),
            )
        except Exception as e:
            # Unexpected error → log full traceback, return generic 500
            logger.exception("Unhandled exception", exc_info=True)
            sentry_sdk.capture_exception(e)
            return JSONResponse(
                status_code=500,
                content=ApiResponse(
                    error=ApiError(
                        code="INTERNAL_ERROR",
                        message="An unexpected error occurred. Please try again later.",
                        correlation_id=getattr(request.state, "correlation_id", "unknown"),
                    ),
                ).model_dump(),
            )
```

### 14.2 Custom Exception Hierarchy

```python
# exceptions.py
class AppException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


# Domain-specific exceptions
class CeremonyNotFoundError(AppException):
    def __init__(self, ceremony_id: str):
        super().__init__("CEREMONY_NOT_FOUND", f"Ceremony '{ceremony_id}' not found", 404)

class PhaseTransitionError(AppException):
    def __init__(self, current_phase: str, target_phase: str):
        super().__init__("INVALID_TRANSITION", f"Cannot transition from {current_phase} to {target_phase}", 422)

class GuardConditionFailedError(AppException):
    def __init__(self, guard: str, description: str, **kwargs):
        super().__init__("GUARD_CONDITION_FAILED", description, 422, {"guard": guard, **kwargs})

class FacilitatorOnlyError(AppException):
    def __init__(self):
        super().__init__("FACILITATOR_ONLY", "This action is restricted to the Scrum Master", 403)

class RateLimitExceededError(AppException):
    def __init__(self, retry_after: int):
        super().__init__("RATE_LIMIT_EXCEEDED", "Too many requests", 429, {"retry_after_seconds": retry_after})
```

### 14.3 Error Codes by Domain

| Domain | Code Prefix | Example |
|---|---|---|
| Ceremony | `CEREMONY_` | `CEREMONY_NOT_FOUND`, `CEREMONY_ALREADY_COMPLETED` |
| Phase | `PHASE_` | `PHASE_INVALID_TRANSITION`, `PHASE_GUARD_FAILED` |
| Action | `ACTION_` | `ACTION_ASSIGNEE_NOT_MEMBER`, `ACTION_OVERDUE` |
| Integration | `INTEGRATION_` | `INTEGRATION_JIRA_AUTH_FAILED`, `INTEGRATION_ERP_TIMEOUT` |
| AI | `AI_` | `AI_MODEL_UNAVAILABLE`, `AI_CLUSTERING_FAILED` |
| Auth | `AUTH_` | `AUTH_TOKEN_EXPIRED`, `AUTH_INSUFFICIENT_PERMISSIONS` |
| Tenant | `TENANT_` | `TENANT_NOT_SET`, `TENANT_ACCESS_DENIED` |
| General | `INTERNAL_`, `HTTP_` | `INTERNAL_ERROR`, `HTTP_422` |

### 14.4 Correlation ID Middleware

```python
# middleware/correlation.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Adds a unique correlation ID to every request.
    Propagated through logs for distributed tracing.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Use client-provided or generate new
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Inject into structlog context
        with structlog.contextvars.bound_contextvars(correlation_id=correlation_id):
            response = await call_next(request)
        
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

### 14.5 Sentry Integration

```python
# app/sentry_config.py
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENV,
        traces_sample_rate=0.1,               # 10% trace sampling
        profiles_sample_rate=0.05,            # 5% profile sampling
        send_default_pii=False,                # Never send PII
        integrations=[
            SqlalchemyIntegration(),
        ],
        before_send=filter_sensitive_events,
    )

def filter_sensitive_events(event, hint):
    """Strip PII from events before sending to Sentry."""
    if "exception" in event:
        exc = event["exception"]
        for value in exc.get("values", []):
            if value.get("type") == "AuthenticationError":
                return None  # Don't track auth failures in Sentry
    return event
```

---

## 15. Testing Strategy

### 15.1 Testing Pyramid

```mermaid
graph TD
    A["E2E Tests (pytest-httpx)<br/>~5% of tests<br/>Full ceremony flows"]
    B["Integration Tests<br/>~25% of tests<br/>API → Service → DB"]
    C["Unit Tests (pytest)<br/>~70% of tests<br/>Services, models, guards"]
    
    C --> B --> A
```

### 15.2 Unit Testing — pytest

```python
# tests/unit/services/test_ceremony_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.ceremony_service import CeremonyService

@pytest.fixture
def ceremony_service():
    db = AsyncMock()
    redis = AsyncMock()
    user = UserContext(user_id="user_001", role="scrum_master")
    return CeremonyService(db, redis, user)


@pytest.mark.asyncio
async def test_create_ceremony_persists_to_db(ceremony_service):
    """Test that ceremony is persisted with correct initial state."""
    config = CeremonyCreateConfig(
        name="Test Retro",
        type=CeremonyType.RETRO,
        team_id="team_001",
    )
    
    with patch('app.services.ceremony_service.generate_id', return_value="cer_001"):
        result = await ceremony_service.create(config)
    
    assert result.id == "cer_001"
    assert result.status == "idle"
    assert result.team_id == "team_001"
    ceremony_service.db.add.assert_called()
    ceremony_service.redis.hset.assert_called_once()


@pytest.mark.asyncio
async def test_transition_phase_guard_blocks_non_facilitator(ceremony_service):
    """Test that guard condition prevents non-facilitator from transitioning."""
    ceremony = AsyncMock()
    ceremony.facilitator_id = "other_user"
    ceremony.phase = "brainstorm"
    ceremony.status = "active"
    ceremony_service.get_ceremony = AsyncMock(return_value=ceremony)
    ceremony_service.user = UserContext(user_id="non_facilitator", role="member")
    
    with pytest.raises(GuardConditionFailedError) as exc_info:
        await ceremony_service.transition_phase("cer_001", PhaseEvent.START_GROUPING)
    
    assert exc_info.value.error_code == "GUARD_CONDITION_FAILED"
    assert exc_info.value.details["guard"] == "must_be_facilitator"


@pytest.mark.asyncio
async def test_transition_phase_broadcasts_via_redis(ceremony_service):
    """Test that phase changes are published to Redis pub/sub."""
    ceremony = AsyncMock()
    ceremony.facilitator_id = ceremony_service.user.user_id
    ceremony.phase = "brainstorm"
    ceremony.status = "active"
    ceremony_service.get_ceremony = AsyncMock(return_value=ceremony)
    ceremony_service.compute_next_phase = AsyncMock(return_value="grouping")
    
    await ceremony_service.transition_phase("cer_001", PhaseEvent.START_GROUPING)
    
    ceremony_service.redis.publish.assert_called_once()
    args = ceremony_service.redis.publish.call_args[0]
    assert args[0] == "ceremony:cer_001:state_changed"
```

### 15.3 Integration Testing — pytest + httpx + Test DB

```python
# tests/integration/api/test_ceremonies.py
import pytest
from httpx import AsyncClient
from app.main import create_app
from app.database import get_test_async_session

@pytest.fixture
async def client():
    app = create_app()
    app.dependency_overrides[get_db] = get_test_async_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(client: AsyncClient):
    """Client with valid JWT token."""
    token = create_test_token(user_id="test_sm_001", role="scrum_master")
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
async def test_create_and_transition_ceremony(authenticated_client: AsyncClient):
    """Full integration test: create ceremony and transition phase."""
    # Create
    resp = await authenticated_client.post("/api/v1/ceremonies", json={
        "name": "Integration Test Retro",
        "type": "retro",
        "team_id": "team_test_001",
    })
    
    assert resp.status_code == 201
    ceremony_id = resp.json()["data"]["id"]
    
    # Transition
    resp = await authenticated_client.post(
        f"/api/v1/ceremonies/{ceremony_id}/transition",
        json={"event": "start_brainstorm"},
    )
    
    assert resp.status_code == 200
    assert resp.json()["data"]["phase"] == "brainstorm"
    
    # Verify in DB
    async with get_test_async_session() as session:
        ceremony = await session.get(Ceremony, ceremony_id)
        assert ceremony.phase == "brainstorm"


@pytest.mark.asyncio
async def test_unauthenticated_request_returns_401(client: AsyncClient):
    """Test that unauthenticated requests are rejected."""
    resp = await client.post("/api/v1/ceremonies", json={
        "name": "Unauthorized Retro",
        "type": "retro",
        "team_id": "team_001",
    })
    
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "AUTHENTICATION_ERROR"
```

### 15.4 Test Data — factory_boy

```python
# tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from app.models import Ceremony, ActionItem, Team

class TeamFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Team
        sqlalchemy_session = lambda: get_test_session()
    
    id = factory.Sequence(lambda n: f"team_{n:03d}")
    name = factory.Faker("company")
    tenant_id = "tenant_test"


class CeremonyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Ceremony
        sqlalchemy_session = lambda: get_test_session()
    
    id = factory.Sequence(lambda n: f"cer_{n:03d}")
    name = factory.LazyAttribute(lambda o: f"Ceremony {o.id}")
    type = CeremonyType.RETRO
    status = "active"
    phase = "brainstorm"
    team_id = factory.LazyAttribute(lambda o: TeamFactory().id)


class ActionItemFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ActionItem
        sqlalchemy_session = lambda: get_test_session()
    
    id = factory.Sequence(lambda n: f"action_{n:03d}")
    title = factory.Faker("sentence", nb_words=4)
    status = "open"
    priority = "medium"


# Usage in tests
async def test_overdue_actions():
    team = await TeamFactory.create()
    overdue = await ActionItemFactory.create(
        team_id=team.id,
        due_date=datetime.now(UTC) - timedelta(days=3),
        status="open",
    )
    
    result = await action_service.get_overdue_actions(team.id)
    assert overdue.id in [a.id for a in result]
```

### 15.5 Test Database Isolation

```python
# tests/conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.models.base import Base

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/scrum_test"

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db(engine):
    """Provide a transactional scope for each test."""
    connection = await engine.connect()
    transaction = await connection.begin()
    
    session_factory = sessionmaker(connection, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def clean_tables(db):
    """Ensure each test starts with clean tables."""
    for table in reversed(Base.metadata.sorted_tables):
        await db.execute(table.delete())
    await db.commit()
    return db
```

### 15.6 Integration Test Marks

```python
# Use pytest marks for selective test running
import pytest

@pytest.mark.integration
@pytest.mark.jira
async def test_jira_sync_creates_issue():
    """Only runs when --run-integration and --run-jira flags are set."""
    ...

@pytest.mark.integration  
@pytest.mark.ai
async def test_embedding_generation():
    """Only runs when --run-integration and --run-ai flags are set."""
    ...

# pytest.ini configuration
# [pytest]
# markers =
#     integration: marks tests requiring external services (deselect with '-m "not integration"')
#     jira: marks tests requiring Jira credentials
#     ai: marks tests requiring Ollama server
# addopts = -m "not integration"  # Skip integration tests by default
```

### 15.7 Test Coverage Targets

| Layer | Coverage Target | Enforcement |
|---|---|---|
| Services (business logic) | ≥ 90% | CI fails below 85% |
| Models & schemas | ≥ 80% | Warning below 75% |
| Integrations | ≥ 70% | Warning below 60% |
| API endpoints | ≥ 85% | CI fails below 80% |
| Overall | ≥ 85% | CI fails below 80% |

```bash
# Run unit tests only (fast, no external dependencies)
pytest -m "not integration" --cov=app --cov-report=term-missing

# Run integration tests (requires test DB + Redis)
pytest -m integration --cov=app --cov-append

# Run specific integration subset
pytest -m "integration and ai" --cov=app
```

---

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | June 2026 | Backend Architecture Team | Initial document |
