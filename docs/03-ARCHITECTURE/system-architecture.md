# System Architecture Document
## Scrum Ceremony Platform

---

**Document Version:** 1.0.0  
**Status:** Draft  
**Author:** Solution Architecture Team  
**Last Updated:** June 2026  
**Audience:** Solution Architects, Engineering Leadership, DevOps, Security Reviewers  
**Classification:** Internal

---

## Table of Contents

1. [Introduction & Purpose](#1-introduction--purpose)
2. [Architecture Overview](#2-architecture-overview)
3. [C4 Level 1 — System Context](#3-c4-level-1--system-context)
4. [C4 Level 2 — Containers](#4-c4-level-2--containers)
5. [C4 Level 3 — Components (FastAPI Backend)](#5-c4-level-3--components-fastapi-backend)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Technology Decision Rationale](#8-technology-decision-rationale)
9. [Scalability Considerations](#9-scalability-considerations)
10. [Security Architecture](#10-security-architecture)
11. [Observability](#11-observability)
12. [Appendix](#12-appendix)

---

## 1. Introduction & Purpose

### 1.1 Scope

This document describes the system architecture of the **Scrum Ceremony Platform** — a purpose-built application that facilitates agile ceremonies (Daily Standup, Sprint Planning, Sprint Review, Sprint Retrospective, and Backlog Refinement) with real-time collaboration, AI-powered insights, and enterprise integrations.

### 1.2 Design Principles

| Principle | Description |
|-----------|-------------|
| **Event-Driven Collaboration** | All ceremony state changes propagate as events; real-time sync via CRDTs |
| **Domain Isolation** | Bounded contexts map to independent services with explicit APIs |
| **Progressive Enhancement** | Core ceremony experience works without AI; AI enhances but is not required |
| **Enterprise-Ready** | SSO (SAML/OIDC), SCIM, audit logging, and ERP integration from day one |
| **Observability-First** | Every service emits structured traces, metrics, and events |

### 1.3 Key Quality Attributes

| Quality Attribute | Target |
|-------------------|--------|
| Availability | 99.9% (8.76 hrs downtime/year) |
| Latency (P95) | < 200ms API, < 50ms WebSocket round-trip |
| Throughput | 10,000 concurrent ceremonies, 100,000 simultaneous WebSocket connections |
| Data Durability | RPO < 1 minute, RTO < 5 minutes |
| Scalability | Horizontal scaling to 10x peak load with < 2x infrastructure cost |

---

## 2. Architecture Overview

The platform follows a **modular monolith** architecture at the service level, with clear boundaries that allow extraction to microservices as scale demands. The backend is organized around domain services within a single FastAPI application, communicating synchronously via internal calls and asynchronously via Redis Streams / Celery tasks.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Scrum Ceremony Platform                       │
│                                                                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Frontend │──│   Backend    │──│   AI     │──│  Integrations  │  │
│  │ Next.js  │  │   FastAPI    │  │  Ollama  │  │  Jira/Slack    │  │
│  └──────────┘  └──────────────┘  └──────────┘  └────────────────┘  │
│       │              │                │               │              │
│       └──────────────┴────────────────┴───────────────┘              │
│                              │                                        │
│                    ┌─────────┴─────────┐                             │
│                    │  Infrastructure   │                             │
│                    │  PostgreSQL/Redis │                             │
│                    └───────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. C4 Level 1 — System Context

The System Context diagram shows the platform as a black box, its human actors, and external systems.

### 3.1 System Context Diagram

```mermaid
C4Context
    title System Context Diagram — Scrum Ceremony Platform

    Person(scrum_master, "Scrum Master", "Facilitates ceremonies, configures templates, reviews team health metrics")
    Person(team_member, "Team Member", "Participates in ceremonies, contributes to boards, tracks action items")
    Person(agile_coach, "Agile Coach", "Analyzes cross-team patterns, configures advanced templates, reviews org-wide metrics")
    Person(eng_manager, "Engineering Manager", "Reviews team performance, approves actions, monitors delivery metrics")
    Person(it_admin, "IT Admin", "Manages SSO/SCIM configuration, audit logs, platform settings")

    System(scrum_platform, "Scrum Ceremony Platform", "Facilitates agile ceremonies with real-time collaboration, AI-powered insights, and enterprise integrations")

    System_Ext(jira, "Jira Cloud", "Project management tool — syncs epics, stories, sprints, and issues")
    System_Ext(slack, "Slack", "Team communication — sends notifications, ceremony reminders")
    System_Ext(teams, "Microsoft Teams", "Enterprise communication — sends notifications, calendar invites")
    System_Ext(erpnext, "ERPNext", "Self-hosted ERP — CRM, finance, resource management")
    System_Ext(stripe, "Stripe", "Payment processing and subscription billing")
    System_Ext(ollama, "Ollama Server", "Self-hosted LLM inference — clustering, summarization, insights")
    System_Ext(clerk, "Clerk", "Authentication provider — SSO, SAML, SCIM, user management")

    Rel(scrum_master, scrum_platform, "Configures ceremonies, facilitates retros, reviews insights", "HTTPS/WSS")
    Rel(team_member, scrum_platform, "Participates in ceremonies, tracks actions", "HTTPS/WSS")
    Rel(agile_coach, scrum_platform, "Analyzes patterns, configures templates", "HTTPS")
    Rel(eng_manager, scrum_platform, "Reviews metrics, approves actions", "HTTPS")
    Rel(it_admin, scrum_platform, "Manages platform config, SSO, audit", "HTTPS")

    Rel(scrum_platform, jira, "Syncs issues, sprints, epics bidirectionally", "HTTPS/REST Webhooks")
    Rel(scrum_platform, slack, "Sends notifications, reminders, action updates", "HTTPS/REST")
    Rel(scrum_platform, teams, "Sends notifications, calendar invites", "HTTPS/REST")
    Rel(scrum_platform, erpnext, "Pulls team/resource data, pushes billing events", "HTTPS/REST")
    Rel(scrum_platform, stripe, "Manages subscriptions, processes payments", "HTTPS/REST + Webhooks")
    Rel(scrum_platform, ollama, "Sends prompts for clustering, summarization, insights", "HTTPS/REST")
    Rel(scrum_platform, clerk, "Authenticates users, manages sessions, provisions SCIM", "HTTPS/REST + JWT")
    Rel(clerk, scrum_platform, "Sends webhooks for user provisioning events", "HTTPS/Webhooks")

    UpdateRelStyle(scrum_master, scrum_platform, $offsetY="-40", $offsetX="20")
    UpdateRelStyle(team_member, scrum_platform, $offsetY="-20", $offsetX="-20")
    UpdateRelStyle(it_admin, scrum_platform, $offsetY="40", $offsetX="0")
```

### 3.2 External Actor Descriptions

| Actor | Role | Primary Interactions | Authentication |
|-------|------|---------------------|----------------|
| **Scrum Master** | Ceremony facilitator | Create/configure ceremonies, manage templates, review team health, moderate boards | Clerk SSO |
| **Team Member** | Participant | Join ceremonies, contribute to boards, vote, track personal action items | Clerk SSO |
| **Agile Coach** | Organizational coach | Cross-team analytics, advanced template design, org-wide metrics | Clerk SSO |
| **Engineering Manager** | Delivery oversight | Sprint metrics, team performance, approval workflows | Clerk SSO |
| **IT Admin** | Platform administration | SSO/SCIM config, audit log review, tenant management | Clerk SSO + Admin Role |

### 3.3 External System Integration Details

| System | Integration Pattern | Data Direction | Protocol | Frequency |
|--------|-------------------|----------------|----------|-----------|
| **Jira Cloud** | Webhook + REST polling | Bidirectional | HTTPS/REST | Real-time (webhook) + 5min sync |
| **Slack** | Outgoing webhooks + Bot | Outbound (platform → Slack) | HTTPS/REST | Event-driven |
| **Microsoft Teams** | Outgoing webhooks + Graph API | Outbound (platform → Teams) | HTTPS/REST | Event-driven |
| **ERPNext** | REST API polling | Bidirectional | HTTPS/REST | Hourly sync + on-demand |
| **Stripe** | Webhook + REST | Bidirectional | HTTPS/REST + Webhooks | Event-driven |
| **Ollama** | REST API | Inbound (platform → Ollama) | HTTPS/REST | On-demand (per ceremony) |
| **Clerk** | JWT validation + SCIM | Bidirectional | HTTPS/REST + SCIM | Per-request auth + hourly SCIM |

---

## 4. C4 Level 2 — Containers

The Containers diagram zooms into the platform, showing the major deployable units and their interactions.

### 4.1 Container Diagram

```mermaid
C4Container
    title Container Diagram — Scrum Ceremony Platform

    Person(users, "Users", "Scrum Masters, Team Members, Coaches, Managers")
    Person(devops, "DevOps", "Deployment, monitoring, infrastructure management")

    System_Boundary(scrum_platform, "Scrum Ceremony Platform") {
        Container(frontend, "Next.js Frontend", "Next.js 15 + React + TailwindCSS + Radix UI", "Single-page application providing ceremony UI, real-time boards, dashboards, and configuration interfaces")
        
        Container(backend, "FastAPI Backend", "Python 3.12 + FastAPI + SQLAlchemy + Alembic", "Core business logic: ceremony orchestration, team management, templates, analytics, integrations")
        
        ContainerDb(pgdb, "PostgreSQL Database", "PostgreSQL 16 + pgvector", "Primary data store: ceremonies, teams, boards, actions, templates, audit logs, vector embeddings")
        
        ContainerDb(redis, "Redis Cache/Presence", "Redis 7", "Session cache, WebSocket presence, rate limiting, pub/sub, task queue broker")
        
        Container(ws_server, "WebSocket Server", "Python + Yjs Protocol + WebSocket", "Real-time collaboration server handling CRDT sync, cursor presence, and ceremony state broadcast")
        
        Container(ai_service, "AI Service", "Ollama + Gemma 3 9B + mxbai-embed-large", "AI inference: retro clustering, summarization, sentiment analysis, action extraction")
        
        Container(erpnext, "ERPNext Backend", "ERPNext (Docker, self-hosted)", "Enterprise resource planning: CRM, finance, HR, resource allocation")
        
        Container(worker, "Background Worker", "Celery/ARQ + Python", "Async task processing: Jira sync, notifications, report generation, AI job execution")
    }

    System_Ext(jira, "Jira Cloud", "External project management")
    System_Ext(slack, "Slack", "External communication")
    System_Ext(teams, "Microsoft Teams", "External communication")
    System_Ext(stripe, "Stripe", "External billing")
    System_Ext(clerk, "Clerk", "External authentication")

    Rel(users, frontend, "Interacts with ceremony UI, dashboards", "HTTPS")
    Rel(devops, frontend, "Deploys, monitors", "HTTPS")
    Rel(devops, backend, "Deploys, monitors", "HTTPS")
    
    Rel(frontend, backend, "API calls: ceremony CRUD, team management, analytics", "HTTPS/REST + JSON")
    Rel(frontend, ws_server, "Real-time collaboration: board edits, cursor sync, presence", "WSS/WebSocket + Yjs Protocol")
    Rel(backend, pgdb, "Read/write domain data", "TCP/PostgreSQL Wire Protocol")
    Rel(backend, redis, "Cache reads, session management, pub/sub", "TCP/Redis Protocol")
    Rel(backend, ws_server, "Broadcast ceremony state changes", "Redis Pub/Sub → WebSocket")
    Rel(backend, ai_service, "Submit AI jobs: clustering, summarization", "HTTPS/REST + JSON")
    Rel(backend, erpnext, "Sync team/resource data, billing events", "HTTPS/REST + JSON")
    Rel(backend, worker, "Enqueue background tasks", "Redis Streams / AMQP")
    Rel(worker, pgdb, "Read/write job results, sync state", "TCP/PostgreSQL Wire Protocol")
    Rel(worker, jira, "Sync issues, sprints, epics", "HTTPS/REST")
    Rel(worker, slack, "Send notifications", "HTTPS/REST")
    Rel(worker, teams, "Send notifications, calendar invites", "HTTPS/REST")
    Rel(worker, stripe, "Process billing events", "HTTPS/REST")
    Rel(backend, clerk, "Validate JWT tokens, SCIM provisioning", "HTTPS/REST")
    Rel(clerk, backend, "User provisioning webhooks", "HTTPS/Webhooks")
    Rel(ws_server, redis, "Presence tracking, pub/sub fan-out", "TCP/Redis Protocol")
    Rel(ai_service, pgdb, "Read embeddings, write inference results", "TCP/PostgreSQL Wire Protocol")

    UpdateRelStyle(frontend, backend, $offsetY="-30", $offsetX="0")
    UpdateRelStyle(backend, pgdb, $offsetY="0", $offsetX="-40")
    UpdateRelStyle(backend, redis, $offsetY="20", $offsetX="-20")
    UpdateRelStyle(worker, jira, $offsetY="20", $offsetX="0")
```

### 4.2 Container Specifications

#### 4.2.1 Next.js Frontend

| Attribute | Detail |
|-----------|--------|
| **Technology** | Next.js 15, React 19, TailwindCSS 4, Radix UI, Yjs |
| **Responsibility** | Ceremony UI, real-time collaborative boards, dashboards, admin configuration |
| **Build Output** | Static assets (CDN) + Server-Side Rendering (SSR) via Next.js server |
| **State Management** | React Query (server state) + Zustand (client state) + Yjs (collaborative state) |
| **Authentication** | Clerk SDK, JWT-based session management |
| **Scaling** | Horizontal via stateless deployment; CDN for static assets |

#### 4.2.2 FastAPI Backend

| Attribute | Detail |
|-----------|--------|
| **Technology** | Python 3.12, FastAPI 0.115, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| **Responsibility** | Core business logic, REST API, authentication middleware, integration orchestration |
| **API Design** | RESTful with OpenAPI 3.1 spec, JSON:API compatible |
| **Authentication** | Clerk JWT validation via middleware, role-based access control (RBAC) |
| **Scaling** | Horizontal via Uvicorn workers behind load balancer; stateless design |

#### 4.2.3 PostgreSQL Database

| Attribute | Detail |
|-----------|--------|
| **Technology** | PostgreSQL 16 + pgvector extension |
| **Responsibility** | Primary persistent storage for all domain entities, vector embeddings for AI |
| **Data Volume Estimate** | 50GB/year at 1000 active teams |
| **High Availability** | Primary + synchronous replica; automated failover via Patroni |
| **Backup** | Continuous WAL archiving + daily pg_basebackup |
| **Extensions** | pgvector (AI embeddings), pg_trgm (text search), pg_stat_statements |

#### 4.2.4 Redis Cache/Presence

| Attribute | Detail |
|-----------|--------|
| **Technology** | Redis 7 (cluster mode in production) |
| **Responsibility** | Session cache, WebSocket presence, rate limiting, pub/sub broker, Celery broker |
| **Memory Estimate** | 8GB for cache + presence at 10K concurrent users |
| **Persistence** | AOF + RDB snapshots for cache; presence data is ephemeral |
| **High Availability** | Redis Sentinel (dev) → Redis Cluster (prod) |

#### 4.2.5 WebSocket Server

| Attribute | Detail |
|-----------|--------|
| **Technology** | Python 3.12, ypy-websocket, WebSocket (RFC 6455) |
| **Responsibility** | Real-time CRDT synchronization, cursor presence, ceremony state broadcast |
| **Protocol** | Yjs sync protocol over WebSocket (binary frames) |
| **Scaling** | Horizontal with Redis pub/sub for cross-node broadcast; sticky sessions required |
| **Connection Limit** | ~10,000 concurrent connections per node (4 vCPU, 8GB RAM) |

#### 4.2.6 AI Service (Ollama)

| Attribute | Detail |
|-----------|--------|
| **Technology** | Ollama server, Gemma 3 9B (instruct), mxbai-embed-large (334M) |
| **Responsibility** | LLM inference for retro clustering, summarization, action extraction, sentiment |
| **API** | Ollama REST API (`/api/generate`, `/api/embeddings`) |
| **Hardware** | GPU node (NVIDIA A10G or equivalent) in production |
| **Scaling** | Model sharding across GPU nodes; request queue with worker pool |

#### 4.2.7 ERPNext Backend

| Attribute | Detail |
|-----------|--------|
| **Technology** | ERPNext v15, Python, Frappe framework, MariaDB |
| **Responsibility** | CRM, finance, HR, resource allocation, billing records |
| **Deployment** | Self-hosted Docker Compose alongside platform |
| **Integration** | REST API with API key authentication |
| **Scaling** | Separate scaling path from core platform; shared Docker network |

#### 4.2.8 Background Worker (Celery/ARQ)

| Attribute | Detail |
|-----------|--------|
| **Technology** | ARQ (async Redis queue) or Celery with Redis broker |
| **Responsibility** | Async task execution: Jira sync, notification dispatch, report generation, AI job orchestration |
| **Concurrency** | 20-50 worker processes per node |
| **Scaling** | Horizontal via additional worker nodes consuming from shared Redis |
| **Retry Policy** | Exponential backoff (1s, 2s, 4s, 8s, 30s max); dead letter queue after 5 failures |

---

## 5. C4 Level 3 — Components (FastAPI Backend)

The Components diagram zooms into the FastAPI Backend container, showing the major logical components and their interactions.

### 5.1 Component Diagram

```mermaid
C4Component
    title Component Diagram — FastAPI Backend

    Container_Boundary(backend_container, "FastAPI Backend") {
        Component(identity_svc, "Identity Service", "Clerk integration + JWT validation + RBAC", "Authenticates requests, manages user context, handles SCIM provisioning")
        
        Component(team_svc, "Team & Workspace Service", "Team CRUD + workspace management + membership", "Manages teams, workspaces, member roles, and permissions")
        
        Component(template_svc, "Template Service", "Ceremony template CRUD + versioning", "Manages retro templates, standup formats, and custom board layouts")
        
        Component(ceremony_svc, "Ceremony Orchestration Service", "XState phase machine + scheduling + state transitions", "Core ceremony lifecycle: create, start, transition phases, complete, archive")
        
        Component(collab_svc, "Collaboration/Board Service", "Yjs CRDT management + board state + voting", "Manages collaborative boards, sticky notes, voting, and real-time sync coordination")
        
        Component(action_svc, "Action Service", "Action item CRUD + tracking + reminders", "Manages action items from ceremonies: assignment, due dates, status tracking")
        
        Component(integration_svc, "Integration Service", "Jira/Slack/Teams adapters + webhook management", "Handles all external system integrations with circuit breakers and retry logic")
        
        Component(analytics_svc, "Analytics Service", "Metrics aggregation + report generation + dashboards", "Computes team health metrics, velocity, burndown, and generates reports")
        
        Component(ai_orch, "AI Orchestrator", "Ollama client + prompt engineering + job queuing", "Manages AI inference jobs: clustering, summarization, sentiment, embeddings")
        
        Component(notification_svc, "Notification Service", "Email + Slack + Teams + in-app notifications", "Multi-channel notification delivery with preference management")
    }

    ContainerDb(pgdb, "PostgreSQL", "Primary data store")
    ContainerDb(redis, "Redis", "Cache + pub/sub + task queue")
    Container(ws_server, "WebSocket Server", "Real-time broadcast")
    Container(ai_service, "AI Service (Ollama)", "LLM inference")
    Container(worker, "Background Worker", "Async task execution")

    System_Ext(jira, "Jira Cloud")
    System_Ext(slack, "Slack")
    System_Ext(teams, "Microsoft Teams")
    System_Ext(clerk, "Clerk Auth")

    Rel(identity_svc, clerk, "Validates JWT, provisions users via SCIM", "HTTPS/REST")
    Rel(identity_svc, pgdb, "Read/write user profiles, roles", "SQL")
    
    Rel(team_svc, identity_svc, "Resolves user permissions for team actions", "Internal")
    Rel(team_svc, pgdb, "CRUD teams, workspaces, memberships", "SQL")
    Rel(team_svc, redis, "Cache team/permission lookups", "Redis Protocol")
    
    Rel(template_svc, team_svc, "Validates team context for templates", "Internal")
    Rel(template_svc, pgdb, "CRUD templates with versioning", "SQL")
    
    Rel(ceremony_svc, team_svc, "Validates team membership for ceremony access", "Internal")
    Rel(ceremony_svc, template_svc, "Loads ceremony template configuration", "Internal")
    Rel(ceremony_svc, collab_svc, "Initializes collaboration board for ceremony", "Internal")
    Rel(ceremony_svc, action_svc, "Creates action items on ceremony completion", "Internal")
    Rel(ceremony_svc, pgdb, "CRUD ceremony entities, phase state", "SQL")
    Rel(ceremony_svc, redis, "Cache active ceremony state, pub/sub events", "Redis Protocol")
    Rel(ceremony_svc, ws_server, "Broadcasts phase transitions to connected clients", "Redis Pub/Sub")
    
    Rel(collab_svc, ceremony_svc, "Validates ceremony context for board operations", "Internal")
    Rel(collab_svc, ws_server, "Syncs CRDT updates, manages board state", "Redis Pub/Sub")
    Rel(collab_svc, pgdb, "Persist board snapshots, voting results", "SQL")
    Rel(collab_svc, redis, "Cache active board state, presence", "Redis Protocol")
    
    Rel(action_svc, ceremony_svc, "Links actions to source ceremony", "Internal")
    Rel(action_svc, pgdb, "CRUD action items, status history", "SQL")
    Rel(action_svc, notification_svc, "Triggers reminders on due date proximity", "Internal")
    
    Rel(integration_svc, pgdb, "Store integration configs, sync state", "SQL")
    Rel(integration_svc, jira, "Sync issues, sprints, epics", "HTTPS/REST")
    Rel(integration_svc, slack, "Send messages, handle interactions", "HTTPS/REST")
    Rel(integration_svc, teams, "Send messages, calendar events", "HTTPS/REST")
    Rel(integration_svc, worker, "Enqueue sync jobs", "Redis Streams")
    
    Rel(analytics_svc, pgdb, "Read ceremony data, compute metrics", "SQL")
    Rel(analytics_svc, redis, "Cache computed metrics", "Redis Protocol")
    Rel(analytics_svc, worker, "Trigger heavy report generation", "Redis Streams")
    
    Rel(ai_orch, ceremony_svc, "Receives AI job requests from ceremonies", "Internal")
    Rel(ai_orch, ai_service, "Submit inference requests to Ollama", "HTTPS/REST")
    Rel(ai_orch, pgdb, "Read embeddings, store inference results", "SQL")
    Rel(ai_orch, worker, "Queue long-running AI jobs", "Redis Streams")
    
    Rel(notification_svc, pgdb, "Read notification preferences, log delivery", "SQL")
    Rel(notification_svc, redis, "Rate limit notifications, cache preferences", "Redis Protocol")
    Rel(notification_svc, slack, "Send Slack messages", "HTTPS/REST")
    Rel(notification_svc, teams, "Send Teams messages", "HTTPS/REST")
    Rel(notification_svc, worker, "Queue notification delivery", "Redis Streams")

    UpdateRelStyle(ceremony_svc, collab_svc, $offsetY="-20", $offsetX="0")
    UpdateRelStyle(ai_orch, ai_service, $offsetY="0", $offsetX="30")
    UpdateRelStyle(integration_svc, jira, $offsetY="-10", $offsetX="20")
```

### 5.2 Component Descriptions

#### 5.2.1 Identity Service

**Responsibilities:**
- JWT token validation from Clerk
- User context injection into request lifecycle
- Role-Based Access Control (RBAC) enforcement
- SCIM user provisioning/deprovisioning
- Session management and token refresh

**Key Interfaces:**
```python
class IdentityService:
    async def validate_token(self, token: str) -> UserContext
    async def check_permission(self, user: UserContext, resource: str, action: str) -> bool
    async def provision_user(self, clerk_event: WebhookEvent) -> User
    async def sync_scim_users(self) -> list[User]
```

**Dependencies:** Clerk (external), PostgreSQL

#### 5.2.2 Team & Workspace Service

**Responsibilities:**
- Team creation, configuration, and archival
- Workspace management (multi-team groupings)
- Member invitation, role assignment, and removal
- Permission resolution and caching

**Key Interfaces:**
```python
class TeamService:
    async def create_team(self, name: str, workspace_id: str, owner: UserContext) -> Team
    async def add_member(self, team_id: str, user_id: str, role: TeamRole) -> Membership
    async def get_user_teams(self, user_id: str) -> list[Team]
    async def resolve_permissions(self, user_id: str, team_id: str) -> PermissionSet
```

**Dependencies:** Identity Service, PostgreSQL, Redis

#### 5.2.3 Template Service

**Responsibilities:**
- Ceremony template CRUD operations
- Template versioning and inheritance
- Default template seeding
- Template sharing across workspaces

**Key Interfaces:**
```python
class TemplateService:
    async def create_template(self, team_id: str, config: TemplateConfig) -> Template
    async def get_template(self, template_id: str) -> Template
    async def fork_template(self, source_id: str, team_id: str) -> Template
    async def list_templates(self, workspace_id: str, type: CeremonyType) -> list[Template]
```

**Dependencies:** Team Service, PostgreSQL

#### 5.2.4 Ceremony Orchestration Service

**Responsibilities:**
- Ceremony lifecycle management (create → schedule → start → phases → complete → archive)
- XState-powered phase transition machine
- Ceremony state persistence and recovery
- Integration with collaboration board initialization
- Action item generation on ceremony completion

**State Machine (XState):**
```
idle → scheduled → active → [brainstorm → group → vote → discuss → actions] → completed → archived
                                    ↑__________________________________________|
```

**Key Interfaces:**
```python
class CeremonyOrchestrationService:
    async def create_ceremony(self, config: CeremonyCreateConfig) -> Ceremony
    async def start_ceremony(self, ceremony_id: str, user: UserContext) -> Ceremony
    async def transition_phase(self, ceremony_id: str, event: PhaseEvent) -> Ceremony
    async def complete_ceremony(self, ceremony_id: str) -> Ceremony
    async def get_ceremony_state(self, ceremony_id: str) -> CeremonyState
```

**Dependencies:** Team Service, Template Service, Collaboration Service, Action Service, PostgreSQL, Redis, WebSocket Server

#### 5.2.5 Collaboration/Board Service

**Responsibilities:**
- Collaborative board management (create, update, lock)
- Yjs CRDT document lifecycle
- Voting mechanics (allocate, cast, reveal)
- Sticky note operations (add, move, edit, group)
- Board snapshot persistence

**Key Interfaces:**
```python
class CollaborationService:
    async def create_board(self, ceremony_id: str, config: BoardConfig) -> Board
    async def apply_operation(self, board_id: str, operation: BoardOperation) -> Board
    async def cast_vote(self, board_id: str, user_id: str, vote: Vote) -> VoteResult
    async def get_board_state(self, board_id: str) -> BoardState
    async def snapshot_board(self, board_id: str) -> BoardSnapshot
```

**Dependencies:** Ceremony Service, WebSocket Server, PostgreSQL, Redis

#### 5.2.6 Action Service

**Responsibilities:**
- Action item CRUD with ceremony lineage
- Assignment and due date management
- Status tracking and transitions
- Reminder scheduling and escalation
- Integration with Jira issue creation

**Key Interfaces:**
```python
class ActionService:
    async def create_action(self, ceremony_id: str, config: ActionConfig) -> ActionItem
    async def update_status(self, action_id: str, status: ActionStatus) -> ActionItem
    async def assign_action(self, action_id: str, assignee_id: str) -> ActionItem
    async def get_overdue_actions(self, team_id: str) -> list[ActionItem]
    async def bulk_create_from_ceremony(self, ceremony_id: str, items: list[ActionConfig]) -> list[ActionItem]
```

**Dependencies:** Ceremony Service, PostgreSQL, Notification Service

#### 5.2.7 Integration Service

**Responsibilities:**
- Jira Cloud bidirectional sync (issues, sprints, epics, statuses)
- Slack notification delivery and interactive message handling
- Microsoft Teams notification and calendar event creation
- Webhook registration and event routing
- Circuit breaker and retry logic for external APIs

**Key Interfaces:**
```python
class IntegrationService:
    async def sync_to_jira(self, action: ActionItem) -> JiraIssue
    async def sync_from_jira(self, team_id: str, since: datetime) -> list[SyncResult]
    async def send_slack_notification(self, channel: str, message: Message) -> DeliveryResult
    async def register_webhook(self, system: ExternalSystem, events: list[str]) -> Webhook
    async def handle_incoming_webhook(self, system: ExternalSystem, payload: dict) -> None
```

**Dependencies:** PostgreSQL, Worker, External Systems (Jira, Slack, Teams)

#### 5.2.8 Analytics Service

**Responsibilities:**
- Team health metrics computation (velocity, happiness, engagement)
- Sprint burndown/burnup chart data
- Retro trend analysis (recurring themes, sentiment trends)
- Cross-team comparison dashboards
- Report generation (PDF/CSV export)

**Key Interfaces:**
```python
class AnalyticsService:
    async def get_team_health(self, team_id: str, period: DateRange) -> TeamHealth
    async def get_sprint_metrics(self, team_id: str, sprint_id: str) -> SprintMetrics
    async def get_retro_trends(self, team_id: str, window: int) -> RetroTrends
    async def generate_report(self, team_id: str, type: ReportType) -> Report
    async def get_dashboard_data(self, user_id: str) -> Dashboard
```

**Dependencies:** PostgreSQL, Redis, Worker

#### 5.2.9 AI Orchestrator

**Responsibilities:**
- Retro item clustering (semantic grouping via embeddings + LLM)
- Ceremony summarization (meeting notes, key themes)
- Sentiment analysis on retro feedback
- Action item extraction from free-text
- Embedding generation and storage (pgvector)
- Prompt template management and versioning

**Key Interfaces:**
```python
class AIOrchestrator:
    async def cluster_retro_items(self, items: list[str]) -> list[Cluster]
    async def summarize_ceremony(self, ceremony_id: str) -> Summary
    async def analyze_sentiment(self, texts: list[str]) -> SentimentResult
    async def extract_actions(self, text: str) -> list[ExtractedAction]
    async def generate_embedding(self, text: str) -> list[float]
    async def find_similar_items(self, embedding: list[float], top_k: int) -> list[SimilarItem]
```

**Dependencies:** AI Service (Ollama), PostgreSQL, Worker

#### 5.2.10 Notification Service

**Responsibilities:**
- Multi-channel notification delivery (in-app, email, Slack, Teams)
- User notification preference management
- Rate limiting and deduplication
- Notification history and read status
- Scheduled notification delivery

**Key Interfaces:**
```python
class NotificationService:
    async def send_notification(self, notification: Notification) -> DeliveryResult
    async def get_user_preferences(self, user_id: str) -> NotificationPreferences
    async def mark_read(self, notification_id: str, user_id: str) -> None
    async def get_unread(self, user_id: str) -> list[Notification]
    async def schedule_notification(self, notification: Notification, deliver_at: datetime) -> ScheduledNotification
```

**Dependencies:** PostgreSQL, Redis, Worker, Slack, Teams

---

## 6. Data Flow Diagrams

### 6.1 Scenario 1: Retrospective Execution

This flow describes a complete retrospective ceremony from creation to action item generation.

```mermaid
sequenceDiagram
    participant SM as Scrum Master (Browser)
    participant FE as Next.js Frontend
    participant API as FastAPI Backend
    participant Auth as Identity Service
    participant Ceremony as Ceremony Orchestration
    participant Collab as Collaboration Service
    participant WS as WebSocket Server
    participant DB as PostgreSQL
    participant Cache as Redis
    participant AI as AI Orchestrator
    participant Ollama as Ollama Server
    participant Worker as Background Worker
    participant Notify as Notification Service

    SM->>FE: Create new retrospective
    FE->>API: POST /api/ceremonies {type: "retro", team_id, template_id}
    API->>Auth: Validate JWT + check permission
    Auth-->>API: UserContext {user_id, team_id, role}
    API->>Ceremony: create_ceremony(config)
    Ceremony->>DB: INSERT ceremony, phases, board
    DB-->>Ceremony: ceremony_id, board_id
    Ceremony->>Cache: Cache ceremony state
    Ceremony->>Collab: initialize_board(ceremony_id, template)
    Collab->>DB: INSERT board_config, sticky_note_groups
    Collab-->>Ceremony: board_id
    Ceremony-->>API: Ceremony created
    API-->>FE: 201 {ceremony_id, board_url}
    FE-->>SM: Retro created, share link

    Note over SM: Team joins ceremony
    FE->>WS: WSS connect {ceremony_id, auth_token}
    WS->>Auth: Validate connection token
    Auth-->>WS: UserContext
    WS->>Cache: SET presence:{ceremony_id}:{user_id}
    WS->>WS: Broadcast participant_joined event

    Note over SM: Phase 1: Brainstorm
    SM->>FE: Click "Start Brainstorm"
    FE->>API: POST /api/ceremonies/{id}/transition {event: "START_BRAINSTORM"}
    API->>Ceremony: transition_phase("START_BRAINSTORM")
    Ceremony->>Ceremony: XState: idle → brainstorm
    Ceremony->>DB: UPDATE ceremony SET phase='brainstorm'
    Ceremony->>Cache: PUBLISH ceremony:state:changed
    Cache->>WS: State change event
    WS-->>FE: Broadcast phase_change {phase: "brainstorm"}

    Note over SM: Team adds sticky notes (real-time)
    FE->>WS: Yjs sync: add_sticky_note {content, color, column}
    WS->>Collab: apply_operation(board_id, op)
    Collab->>Collab: Apply to Yjs CRDT doc
    Collab->>WS: Broadcast CRDT update to room
    WS->>FE: Binary Yjs update (all participants)
    Collab->>Cache: Cache board state (debounced)

    Note over SM: Phase 2: Group & Vote
    SM->>FE: Click "Move to Grouping"
    FE->>API: POST /api/ceremonies/{id}/transition {event: "START_GROUPING"}
    API->>Ceremony: transition_phase("START_GROUPING")
    Ceremony->>Ceremony: XState: brainstorm → group
    Ceremony->>DB: UPDATE ceremony SET phase='group'
    Ceremony->>Cache: PUBLISH ceremony:state:changed

    Note over SM: AI Clustering triggered
    SM->>FE: Click "AI Cluster"
    FE->>API: POST /api/ceremonies/{id}/ai/cluster
    API->>AI: cluster_retro_items(sticky_note_texts)
    AI->>Ollama: POST /api/embeddings {texts}
    Ollama-->>AI: embeddings[]
    AI->>AI: DBSCAN clustering on embeddings
    AI->>Ollama: POST /api/generate {prompt: "Name these clusters"}
    Ollama-->>AI: cluster_labels
    AI->>DB: INSERT INTO clusters (labels, items)
    AI-->>API: clusters[]
    API-->>FE: Cluster suggestions
    FE-->>SM: Display AI-suggested groupings

    Note over SM: Phase 3: Actions
    SM->>FE: Click "Create Actions"
    FE->>API: POST /api/ceremonies/{id}/transition {event: "CREATE_ACTIONS"}
    API->>Ceremony: transition_phase("CREATE_ACTIONS")
    Ceremony->>Ceremony: XState: vote → actions
    Ceremony->>Worker: enqueue(ai_summarize_ceremony)
    Worker->>AI: summarize_ceremony(ceremony_id)
    AI->>Ollama: POST /api/generate {prompt: "Summarize retro"}
    Ollama-->>AI: summary_text
    AI->>DB: INSERT INTO ceremony_summaries

    Note over SM: Complete ceremony
    SM->>FE: Click "Complete Retro"
    FE->>API: POST /api/ceremonies/{id}/complete
    API->>Ceremony: complete_ceremony(ceremony_id)
    Ceremony->>Ceremony: XState: actions → completed
    Ceremony->>DB: UPDATE ceremony SET status='completed', ended_at=NOW()
    Ceremony->>Worker: enqueue(generate_action_items)
    Worker->>Worker: Extract actions from board
    Worker->>DB: INSERT action_items (multiple)
    Worker->>Notify: send_notification(type="retro_completed", team_id)
    Notify->>Cache: Check notification preferences
    Notify->>Worker: enqueue(slack_notification) if enabled
    Ceremony-->>API: Ceremony completed
    API-->>FE: 200 {ceremony_id, summary_url}
    FE-->>SM: Retro completed, view summary
```

### 6.2 Scenario 2: Jira Synchronization

This flow describes bidirectional synchronization between the platform and Jira Cloud.

```mermaid
sequenceDiagram
    participant Ext as External Trigger
    participant Worker as Background Worker
    participant IntSvc as Integration Service
    participant Cache as Redis
    participant DB as PostgreSQL
    participant Jira as Jira Cloud
    participant ActionSvc as Action Service
    participant Notify as Notification Service

    Note over Worker: Polling Sync (every 5 minutes)
    Worker->>Cache: GET jira:sync:cursor:{team_id}
    Cache-->>Worker: last_sync_timestamp
    Worker->>IntSvc: sync_from_jira(team_id, since)
    IntSvc->>Jira: GET /rest/api/3/search?updatedSince={since}
    Jira-->>IntSvc: {issues: [...], changelog: [...]}
    loop For each changed issue
        IntSvc->>DB: UPSERT INTO jira_issue_mappings
        IntSvc->>ActionSvc: update_linked_action(issue)
        ActionSvc->>DB: UPDATE action_items SET status=jira_status
        ActionSvc->>Notify: notify_action_updated(action)
    end
    Worker->>Cache: SET jira:sync:cursor:{team_id} = new_timestamp

    Note over Ext: Outbound Sync (action created in platform)
    Ext->>Worker: enqueue(sync_to_jira, action_id)
    Worker->>IntSvc: sync_to_jira(action_id)
    IntSvc->>DB: SELECT action_item, jira_config
    IntSvc->>Jira: POST /rest/api/3/issue {summary, description, project}
    Jira-->>IntSvc: {issue_key: "PROJ-123", id: "10001"}
    IntSvc->>DB: UPDATE action_items SET jira_issue_key='PROJ-123'
    IntSvc->>Cache: SET jira:issue:PROJ-123 -> action_id

    Note over Ext: Inbound Webhook (Jira issue updated externally)
    Ext->>Worker: POST /webhooks/jira {issue_key, event}
    Worker->>Cache: GET jira:issue:PROJ-123
    Cache-->>Worker: action_id
    Worker->>IntSvc: handle_jira_webhook(issue_key, event)
    IntSvc->>Jira: GET /rest/api/3/issue/PROJ-123
    Jira-->>IntSvc: {status, assignee, comments}
    IntSvc->>ActionSvc: update_action_from_jira(action_id, jira_data)
    ActionSvc->>DB: UPDATE action_items SET status, assignee, updated_at
    ActionSvc->>Notify: notify_action_updated(action)
    Notify->>Worker: enqueue(send_slack_notification)

    Note over Worker: Circuit Breaker Pattern
    Worker->>IntSvc: sync_from_jira (fails)
    IntSvc->>Jira: GET /rest/api/3/search
    Jira-->>IntSvc: 503 Service Unavailable
    IntSvc->>IntSvc: circuit_breaker.record_failure()
    Note over IntSvc: After 5 failures: OPEN state
    IntSvc-->>Worker: CircuitOpenError
    Worker->>Worker: backoff_retry(30s)
    Note over Worker: After 60s: HALF_OPEN probe
    Worker->>IntSvc: sync_from_jira (probe)
    IntSvc->>Jira: GET /rest/api/3/search
    Jira-->>IntSvc: 200 OK
    IntSvc->>IntSvc: circuit_breaker.reset()
    IntSvc-->>Worker: Success
```

### 6.3 Scenario 3: AI Clustering (Retro Items)

This flow describes the AI-powered clustering of retrospective feedback items.

```mermaid
sequenceDiagram
    participant SM as Scrum Master
    participant FE as Next.js Frontend
    participant API as FastAPI Backend
    participant AIOrch as AI Orchestrator
    participant DB as PostgreSQL (pgvector)
    participant Ollama as Ollama Server
    participant Cache as Redis
    participant Worker as Background Worker

    SM->>FE: Click "AI Cluster" on retro board
    FE->>API: POST /api/ceremonies/{id}/ai/cluster
    API->>API: Validate ceremony phase = "group"
    API->>AIOrch: cluster_retro_items(ceremony_id)
    AIOrch->>DB: SELECT sticky_note_texts WHERE ceremony_id = ?
    DB-->>AIOrch: ["Deploy took too long", "CI pipeline flaky", "Need better monitoring", "Tests are slow", "Deployment rollback failed"]

    Note over AIOrch: Step 1: Generate embeddings
    AIOrch->>Ollama: POST /api/embeddings {model: "mxbai-embed-large", input: [texts]}
    Ollama-->>AIOrch: [[0.023, -0.118, ...], [0.041, -0.092, ...], ...] (5 vectors × 1024d)

    Note over AIOrch: Step 2: Store embeddings
    AIOrch->>DB: INSERT INTO embeddings (text, vector, ceremony_id) VALUES ...
    Note over DB: pgvector stores 1024-dimension vectors

    Note over AIOrch: Step 3: Cluster algorithm
    AIOrch->>AIOrch: DBSCAN(eps=0.3, min_samples=2) on embeddings
    Note over AIOrch: Cluster 0: ["Deploy took too long", "CI pipeline flaky", "Deployment rollback failed"]
    Note over AIOrch: Cluster 1: ["Need better monitoring", "Tests are slow"]

    Note over AIOrch: Step 4: Generate labels via LLM
    AIOrch->>Ollama: POST /api/generate {model: "gemma-3-9b-instruct", prompt: "Given these items: [...], suggest a short cluster name"}
    Ollama-->>AIOrch: "Deployment & CI Pipeline Issues"
    AIOrch->>Ollama: POST /api/generate {model: "gemma-3-9b-instruct", prompt: "Given these items: [...], suggest a short cluster name"}
    Ollama-->>AIOrCH: "Quality & Observability"

    Note over AIOrch: Step 5: Store results
    AIOrch->>DB: INSERT INTO ai_clusters (ceremony_id, label, items, embeddings)
    AIOrch->>Cache: SET ai:cluster:{ceremony_id} (TTL: 1hr)
    AIOrch-->>API: {clusters: [{label, items, confidence}]}
    API-->>FE: 200 {clusters}
    FE-->>SM: Display clustered groups with labels

    Note over SM: SM accepts/modifies clusters
    SM->>FE: Drag item between clusters
    FE->>API: PUT /api/ceremonies/{id}/ai/clusters/{cluster_id}
    API->>DB: UPDATE ai_clusters SET items = ...
    API->>AIOrch: recompute_centroid(cluster_id)
    AIOrch->>Ollama: POST /api/embeddings {input: [updated_items]}
    Ollama-->>AIOrch: new_centroid_embedding
    AIOrch->>DB: UPDATE embeddings SET vector = ? WHERE cluster_id = ?
    API-->>FE: 200 {updated_cluster}

    Note over Worker: Background: Similarity search for future retros
    Worker->>AIOrch: find_similar_clusters(team_id, current_cluster)
    AIOrch->>DB: SELECT * FROM embeddings ORDER BY vector <=> ? LIMIT 5
    DB-->>AIOrch: [similar_items from past retros]
    AIOrch->>DB: INSERT INTO cluster_similarities
```

---

## 7. Deployment Architecture

### 7.1 Docker Compose (Development)

```mermaid
graph TB
    subgraph dev["Docker Compose — Development Environment"]
        direction TB
        
        subgraph frontend["Frontend Container"]
            FE[Next.js 15<br/>Node.js 20 LTS<br/>Port: 3000]
        end
        
        subgraph backend["Backend Container"]
            API[FastAPI<br/>Uvicorn<br/>Port: 8000]
        end
        
        subgraph ws["WebSocket Container"]
            WS[ypy-websocket<br/>WebSocket Server<br/>Port: 8001]
        end
        
        subgraph worker["Worker Container"]
            CELERY[Celery/ARQ Worker<br/>Port: N/A]
        end
        
        subgraph ai["AI Container"]
            OLLAMA[Ollama Server<br/>GPU Runtime<br/>Port: 11434]
        end
        
        subgraph erp["ERPNext Stack"]
            ERP_APP[ERPNext App<br/>Port: 8000]
            ERP_DB[(MariaDB<br/>ERPNext DB)]
        end
        
        subgraph data["Data Layer"]
            PG[(PostgreSQL 16<br/>+ pgvector<br/>Port: 5432)]
            RD[(Redis 7<br/>Port: 6379)]
        end
        
        subgraph infra["Infrastructure"]
            MINIO[MinIO<br/>S3-compatible<br/>Port: 9000]
            SMTP[Mailpit<br/>SMTP Testing<br/>Port: 1025]
        end
    end
    
    FE -->|HTTP| API
    FE -->|WSS| WS
    API -->|SQL| PG
    API -->|Redis Protocol| RD
    WS -->|Redis Protocol| RD
    API -->|HTTP| OLLAMA
    API -->|HTTP| ERP_APP
    CELERY -->|Redis Protocol| RD
    CELERY -->|SQL| PG
    CELERY -->|HTTP| OLLAMA
    ERP_APP -->|SQL| ERP_DB
    
    style dev fill:#f9f9f9,stroke:#ccc
```

**docker-compose.yml (Development):**

```yaml
version: "3.9"

services:
  # ─── Frontend ───────────────────────────────────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_WS_URL=ws://ws-server:8001
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${CLERK_PUBLISHABLE_KEY}
    depends_on:
      - backend
      - ws-server

  # ─── Backend API ────────────────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://scrum:scrum@postgres:5432/scrum_platform
      - REDIS_URL=redis://redis:6379/0
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - CLERK_JWKS_URL=${CLERK_JWKS_URL}
      - OLLAMA_BASE_URL=http://ollama:11434
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - JIRA_API_TOKEN=${JIRA_API_TOKEN}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - ERPNEXT_API_KEY=${ERPNEXT_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      ollama:
        condition: service_started

  # ─── WebSocket Server ───────────────────────────────────
  ws-server:
    build:
      context: ./ws-server
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379/1
      - DATABASE_URL=postgresql+asyncpg://scrum:scrum@postgres:5432/scrum_platform
      - CLERK_JWKS_URL=${CLERK_JWKS_URL}
    depends_on:
      - redis
      - postgres

  # ─── Background Worker ──────────────────────────────────
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: arq worker.settings.WorkerSettings
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://scrum:scrum@postgres:5432/scrum_platform
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_BASE_URL=http://ollama:11434
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - JIRA_API_TOKEN=${JIRA_API_TOKEN}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
    depends_on:
      - redis
      - postgres

  # ─── PostgreSQL ─────────────────────────────────────────
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_DB=scrum_platform
      - POSTGRES_USER=scrum
      - POSTGRES_PASSWORD=scrum
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U scrum"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ─── Redis ──────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ─── Ollama (AI) ────────────────────────────────────────
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ─── ERPNext ────────────────────────────────────────────
  erpnext:
    image: frappe/erpnext:v15
    ports:
      - "8001:8000"
    volumes:
      - erpnext_data:/home/frappe/frappe-bench/sites
    depends_on:
      - erpnext-db

  erpnext-db:
    image: mariadb:10.6
    volumes:
      - erpnext_db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=erpnext
      - MYSQL_DATABASE=erpnext

  # ─── Object Storage (Dev) ───────────────────────────────
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin

  # ─── SMTP Testing ───────────────────────────────────────
  mailpit:
    image: axllent/mailpit:latest
    ports:
      - "1025:1025"
      - "8025:8025"

volumes:
  postgres_data:
  redis_data:
  ollama_models:
  erpnext_data:
  erpnext_db_data:
  minio_data:
```

### 7.2 Kubernetes (Production)

```mermaid
graph TB
    subgraph k8s["Kubernetes Cluster — Production"]
        direction TB
        
        subgraph ingress["Ingress Layer"]
            INGRESS[NGINX Ingress Controller<br/>TLS Termination<br/>Rate Limiting]
            WAF[WAF / CloudFlare]
        end
        
        subgraph frontend["Frontend Tier"]
            HPA_FE[HPA: 3-20 pods]
            FE_POD[Next.js Pods<br/>Resources: 256Mi RAM, 250m CPU]
        end
        
        subgraph backend["Backend Tier"]
            HPA_API[HPA: 3-15 pods]
            API_POD[FastAPI Pods<br/>Uvicorn Workers<br/>Resources: 512Mi RAM, 500m CPU]
        end
        
        subgraph ws_tier["WebSocket Tier"]
            HPA_WS[HPA: 2-10 pods]
            WS_POD[WebSocket Pods<br/>Sticky Sessions<br/>Resources: 512Mi RAM, 500m CPU]
        end
        
        subgraph worker_tier["Worker Tier"]
            HPA_WORKER[HPA: 2-8 pods]
            WORKER_POD[ARQ Worker Pods<br/>Resources: 1Gi RAM, 1000m CPU]
        end
        
        subgraph ai_tier["AI Tier"]
            GPU_NODE[GPU Node Pool<br/>NVIDIA A10G<br/>1-3 nodes]
            OLLAMA_POD[Ollama Pod<br/>Gemma 3 9B + mxbai-embed]
        end
        
        subgraph data["Data Subsystem"]
            PG_PRIMARY[PostgreSQL Primary<br/>Patroni Managed]
            PG_REPLICA[PostgreSQL Replica<br/>Synchronous]
            RD_CLUSTER[Redis Cluster<br/>6 nodes<br/>3 masters + 3 replicas]
        end
        
        subgraph external["External Services"]
            S3[Object Storage<br/>S3 / GCS]
            SES[Email Service<br/>SES / SendGrid]
        end
    end
    
    WAF --> INGRESS
    INGRESS --> FE_POD
    INGRESS --> API_POD
    INGRESS --> WS_POD
    API_POD --> PG_PRIMARY
    API_POD --> RD_CLUSTER
    WS_POD --> RD_CLUSTER
    WS_POD --> PG_PRIMARY
    WORKER_POD --> RD_CLUSTER
    WORKER_POD --> PG_PRIMARY
    API_POD --> OLLAMA_POD
    WORKER_POD --> OLLAMA_POD
    PG_PRIMARY --> PG_REPLICA
    API_POD --> S3
    WORKER_POD --> S3
    WORKER_POD --> SES
    
    style k8s fill:#f0f4ff,stroke:#4a90d9
    style data fill:#f0fff0,stroke:#32cd32
    style ai_tier fill:#fff0f0,stroke:#ff6347
```

### 7.3 Kubernetes Migration Path

| Phase | Environment | Infrastructure | Database | Scaling |
|-------|-------------|----------------|----------|---------|
| **Phase 1** | Development | Docker Compose (local) | Single PostgreSQL | Single container each |
| **Phase 2** | Staging | Docker Compose (VPS) | Managed PostgreSQL (RDS) | 2 backend replicas |
| **Phase 3** | Production (initial) | K8s (managed, single region) | RDS PostgreSQL + ElastiCache Redis | HPA enabled, 3-5 backend pods |
| **Phase 4** | Production (scale) | K8s (multi-AZ, single region) | RDS Multi-AZ + Read Replicas | Full HPA, GPU node pool |
| **Phase 5** | Enterprise (multi-region) | K8s (multi-region, active-active) | CockroachDB or Aurora Global | Global load balancing |

### 7.4 Kubernetes Resource Manifests (Key Resources)

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scrum-backend
  namespace: scrum-platform
  labels:
    app: scrum-backend
    tier: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: scrum-backend
  template:
    metadata:
      labels:
        app: scrum-backend
        tier: api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
    spec:
      serviceAccountName: scrum-backend
      containers:
        - name: backend
          image: registry.scrum-platform.io/backend:latest
          ports:
            - containerPort: 8000
              name: http
          envFrom:
            - configMapRef:
                name: scrum-backend-config
            - secretRef:
                name: scrum-backend-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          startupProbe:
            httpGet:
              path: /health/startup
              port: 8000
            failureThreshold: 30
            periodSeconds: 10
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scrum-backend-hpa
  namespace: scrum-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scrum-backend
  minReplicas: 3
  maxReplicas: 15
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
```

---

## 8. Technology Decision Rationale

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| **Frontend Framework** | Next.js 15 | Remix, SvelteKit, Nuxt | React ecosystem maturity, SSR/SSG flexibility, App Router for streaming, Vercel deployment option |
| **UI Components** | Radix UI + TailwindCSS | Material UI, Ant Design, Chakra | Headless primitives = full styling control, Tailwind for rapid iteration, accessibility built-in |
| **Real-time Collaboration** | Yjs CRDT | Operational Transform (ShareDB), Socket.io rooms | CRDTs handle offline/conflict resolution natively, no central server required for merge, mature ecosystem |
| **State Machine** | XState | custom FSM, Machina.js, Zag | Visual statechart tooling, inspectable state, guards/actors/invariants built-in, ceremony phases are naturally modeled as statecharts |
| **Backend Framework** | FastAPI | Django, Flask, NestJS (Node) | Native async, automatic OpenAPI docs, Pydantic validation, performance comparable to Go for I/O-bound workloads |
| **ORM** | SQLAlchemy 2.0 | Prisma, Drizzle, raw SQL | Mature async support, Alembic integration, type-annotated queries, flexible relationship loading |
| **Database** | PostgreSQL 16 | MySQL, MongoDB, CockroachDB | pgvector extension for AI embeddings, JSONB for flexible data, mature replication, ACID compliance |
| **Cache** | Redis 7 | Memcached, Dragonfly | Pub/sub for WebSocket fan-out, sorted sets for presence, streams for task queue, cluster mode |
| **Authentication** | Clerk | Auth0, Keycloak, Firebase Auth | SAML/SCIM out-of-the-box, React-native SDKs, webhook-based provisioning, competitive pricing |
| **AI Inference** | Ollama (self-hosted) | OpenAI API, Anthropic, HuggingFace TGI | Data sovereignty, no egress costs, predictable latency, Gemma 3 9B sufficient for clustering/summarization |
| **LLM Model** | Gemma 3 9B Instruct | Llama 3 70B, Mixtral, GPT-4o mini | 9B params fit single GPU, strong instruction following, fine-tunable, Apache 2.0 license |
| **Embedding Model** | mxbai-embed-large (334M) | OpenAI text-embedding-3, GTE-large | 1024 dimensions, strong retrieval quality, small enough for self-hosting, Apache 2.0 |
| **Billing** | Stripe | Paddle, Chargebee | Billing + invoicing + tax in one, excellent API, webhook ecosystem, global coverage |
| **ERP** | ERPNext (self-hosted) | SAP, Odoo, NetSuite | Open-source, Docker-deployable, REST API, no per-user licensing for self-hosted |
| **Task Queue** | ARQ (async redis queue) | Celery, Bull (Node), RQ | Native async/await, Redis-based (no extra broker), type-safe, simpler than Celery |
| **Observability** | Sentry + PostHog + Prometheus | Datadog, Grafana Cloud, New Relic | Cost-effective at scale, self-hosted option, best-in-class for each concern (errors, analytics, metrics) |
| **Deployment (Dev)** | Docker Compose | Vagrant, Nix, bare metal | Industry standard, easy onboarding, parity with production K8s networking |
| **Deployment (Prod)** | Kubernetes | ECS, Nomad, serverless | Industry standard, HPA, ecosystem maturity, multi-cloud portability |

---

## 9. Scalability Considerations

### 9.1 Horizontal Scaling Strategy

| Component | Scaling Mechanism | Bottleneck | Mitigation |
|-----------|------------------|------------|------------|
| **Next.js Frontend** | HPA (CPU/memory), CDN for static | SSR compute | Cache SSR at edge, use ISR where possible |
| **FastAPI Backend** | HPA (CPU/memory/custom metrics) | Database connection pool | PgBouncer, connection multiplexing |
| **WebSocket Server** | HPA (connection count), sticky sessions | Memory per connection | Connection limits per node, Redis pub/sub for fan-out |
| **PostgreSQL** | Vertical + Read Replicas | Write throughput | Connection pooling, query optimization, eventual consistency for analytics |
| **Redis** | Redis Cluster (sharding) | Memory per node | Key eviction policies, shard by tenant |
| **Ollama** | GPU node pool, request queue | GPU memory/vRAM | Model quantization (Q4_K_M), batching, request queuing |
| **Background Workers** | HPA (queue depth) | Downstream API rate limits | Rate limiters, circuit breakers, backoff |

### 9.2 Database Scaling Path

```
Phase 1: Single PostgreSQL (vertical)
    ↓
Phase 2: Primary + 1 Read Replica (read scaling)
    ↓
Phase 3: Primary + 2 Read Replicas + PgBouncer (connection pooling)
    ↓
Phase 4: Table partitioning (by tenant_id for ceremonies, actions)
    ↓
Phase 5: Citus extension (distributed tables) or migration to CockroachDB
```

### 9.3 WebSocket Scaling

The WebSocket server uses Redis Pub/Sub for cross-node message fan-out:

```
Client A → WebSocket Node 1 → Redis PUBLISH "ceremony:123:updates"
                                              ↓
                                    Redis SUBSCRIBE on all WS nodes
                                              ↓
Client B ← WebSocket Node 2 ← Redis message delivered
```

**Connection Distribution:**
- Load balancer with `ip_hash` sticky routing
- Each node handles ~10K connections
- Redis pub/sub ensures all nodes broadcast to their local subscribers
- Presence data in Redis with TTL-based expiry

### 9.4 Multi-Tenancy Strategy

| Layer | Isolation Level | Implementation |
|-------|----------------|----------------|
| **Database** | Row-level security (RLS) | PostgreSQL RLS policies on all tables, `tenant_id` column |
| **Cache** | Key prefixing | `:{tenant_id}:` prefix on all Redis keys |
| **WebSocket** | Room-based | Each ceremony is a room; auth check on join |
| **AI** | Queue isolation | Per-tenant rate limits, separate model instances if needed |
| **Background Jobs** | Tenant context in payload | All tasks carry `tenant_id` for RLS compliance |

### 9.5 Performance Budgets

| Operation | P50 Target | P95 Target | P99 Target |
|-----------|-----------|-----------|-----------|
| API response (simple query) | 20ms | 80ms | 200ms |
| API response (complex aggregation) | 100ms | 500ms | 2s |
| WebSocket message delivery | 10ms | 50ms | 100ms |
| AI clustering (50 items) | 2s | 5s | 15s |
| AI summarization | 3s | 10s | 30s |
| Jira sync (100 issues) | 5s | 15s | 30s |
| Page load (SSR) | 200ms | 500ms | 1s |

### 9.6 Capacity Planning (1000 Active Teams)

| Resource | Specification | Count | Monthly Cost (est.) |
|----------|--------------|-------|-------------------|
| Backend pods | 4 vCPU, 8GB RAM | 5-10 | $500-1000 |
| Frontend pods | 1 vCPU, 512MB RAM | 3-6 | $150-300 |
| WebSocket pods | 2 vCPU, 4GB RAM | 2-4 | $200-400 |
| Worker pods | 4 vCPU, 8GB RAM | 2-4 | $200-400 |
| PostgreSQL | 8 vCPU, 32GB RAM, 500GB SSD | 1 primary + 1 replica | $600 |
| Redis | 4GB RAM | 3 nodes (cluster) | $300 |
| GPU node (A10G) | 24 vCPU, 100GB RAM, 1×A10G | 1-2 | $800-1600 |
| **Total** | | | **$2,750-4,600/mo** |

---

## 10. Security Architecture

### 10.1 Authentication & Authorization Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │────▶│  Clerk   │────▶│  FastAPI  │────▶│   JWT    │
│          │     │  (SSO)   │     │  Backend  │     │  Claims  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     │  1. Login      │                │                │
     │───────────────▶│                │                │
     │                │                │                │
     │  2. SAML/OIDC  │                │                │
     │    callback    │                │                │
     │◀───────────────│                │                │
     │                │                │                │
     │  3. JWT token  │                │                │
     │────────────────────────────────▶│               │
     │                │                │                │
     │                │  4. Validate   │                │
     │                │    JWKS        │                │
     │                │───────────────▶│               │
     │                │                │                │
     │                │  5. UserContext │               │
     │                │    + RBAC      │                │
     │                │◀───────────────│               │
     │                │                │                │
     │  6. Response   │                │                │
     │◀────────────────────────────────│               │
```

### 10.2 Security Controls

| Control | Implementation |
|---------|---------------|
| **Authentication** | Clerk (SAML 2.0, OIDC, OAuth 2.0, magic links, MFA) |
| **Authorization** | RBAC with 5 roles (Admin, Manager, Scrum Master, Member, Viewer) |
| **API Security** | JWT validation, CORS, rate limiting (100 req/min per user), input validation (Pydantic) |
| **Data at Rest** | PostgreSQL TDE, Redis AOF encryption, S3 SSE-S3 |
| **Data in Transit** | TLS 1.3 everywhere, mTLS between services in K8s |
| **Secrets Management** | Kubernetes Secrets + External Secrets Operator (AWS Secrets Manager) |
| **Audit Logging** | Immutable audit log table, shipped to S3 for long-term retention |
| **Row-Level Security** | PostgreSQL RLS policies enforce tenant isolation |
| **WebSocket Auth** | Token validation on connection upgrade, room-level authorization |
| **AI Data Privacy** | No PII sent to Ollama; data anonymization before embedding |

---

## 11. Observability

### 11.1 Observability Stack

```mermaid
graph LR
    subgraph apps["Application Services"]
        FE[Frontend]
        API[Backend]
        WS[WebSocket]
        WORKER[Worker]
    end
    
    subgraph observability["Observability Platform"]
        SENTRY[Sentry<br/>Error Tracking]
        POSTHOG[PostHog<br/>Product Analytics]
        PROM[Prometheus<br/>Metrics]
        GRAF[Grafana<br/>Dashboards]
        JAEGER[Jaeger<br/>Distributed Tracing]
        LOKI[Loki<br/>Log Aggregation]
    end
    
    FE -->|Error events| SENTRY
    FE -->|Custom events| POSTHOG
    API -->|Metrics| PROM
    API -->|Traces| JAEGER
    API -->|Logs| LOKI
    WS -->|Metrics| PROM
    WS -->|Traces| JAEGER
    WORKER -->|Metrics| PROM
    WORKER -->|Traces| JAEGER
    PROM --> GRAF
    JAEGER --> GRAF
    LOKI --> GRAF
    SENTRY -->|Alert| PagerDuty
    PROM -->|Alert| PagerDuty
```

### 11.2 Key Metrics & SLIs

| SLI | Measurement | SLO | Alert Threshold |
|-----|-------------|-----|-----------------|
| **API Availability** | Successful requests / Total requests | 99.9% | < 99.95% over 5min |
| **API Latency** | P95 response time | < 200ms | > 300ms over 5min |
| **WebSocket Delivery** | Message delivery time P95 | < 50ms | > 100ms over 5min |
| **AI Inference** | Clustering job P95 | < 10s | > 15s over 5min |
| **Error Rate** | 5xx responses / Total | < 0.1% | > 0.5% over 5min |
| **DB Connection Pool** | Active connections / Max | < 80% | > 90% |

### 11.3 Product Analytics Events (PostHog)

| Event Name | Trigger | Properties |
|-----------|---------|------------|
| `ceremony_created` | New ceremony created | `type`, `team_id`, `template_id` |
| `ceremony_started` | Ceremony phase transitions to active | `ceremony_id`, `type`, `participant_count` |
| `board_operation` | Sticky note added/edited/moved | `operation_type`, `ceremony_id` |
| `ai_clustering_used` | AI cluster button clicked | `item_count`, `ceremony_id` |
| `action_item_created` | Action item generated | `source`, `assignee`, `due_date` |
| `integration_synced` | Jira/Slack sync completed | `system`, `items_synced`, `duration_ms` |
| `export_generated` | Report exported | `format`, `team_id`, `report_type` |

---

## 12. Appendix

### 12.1 Glossary

| Term | Definition |
|------|-----------|
| **CRDT** | Conflict-free Replicated Data Type — data structure that converges state across nodes without coordination |
| **Yjs** | High-performance CRDT library for shared editing |
| **XState** | Statechart-based state machine library for JavaScript |
| **pgvector** | PostgreSQL extension for vector similarity search |
| **SCIM** | System for Cross-domain Identity Management — protocol for user provisioning |
| **SAML** | Security Assertion Markup Language — XML-based SSO standard |
| **OIDC** | OpenID Connect — identity layer on top of OAuth 2.0 |
| **ARQ** | Async Redis Queue — Python async task queue using Redis |
| **HPA** | Horizontal Pod Autoscaler — Kubernetes scaling mechanism |
| **RLS** | Row-Level Security — PostgreSQL feature for per-row access control |

### 12.2 Architecture Decision Records (ADRs)

| ADR | Title | Status | Summary |
|-----|-------|--------|---------|
| ADR-001 | Use Yjs CRDT for Collaboration | Accepted | CRDTs provide offline-first collaboration without central coordination |
| ADR-002 | Self-hosted Ollama for AI | Accepted | Data sovereignty and cost predictability outweigh managed API convenience |
| ADR-003 | Modular Monolith over Microservices | Accepted | Team size and complexity don't justify microservice overhead at current scale |
| ADR-004 | PostgreSQL over MongoDB | Accepted | ACID transactions, pgvector extension, and SQLAlchemy ecosystem |
| ADR-005 | Clerk for Authentication | Accepted | SAML/SCIM support out-of-the-box reduces auth development by ~3 months |
| ADR-006 | XState for Ceremony State Machine | Accepted | Visual statecharts reduce bugs in ceremony phase transitions |

### 12.3 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Ollama inference latency exceeds SLA | Medium | High | Request queuing, model quantization, fallback to simpler heuristics |
| WebSocket connection limits at scale | Medium | High | Horizontal scaling with Redis pub/sub, connection limits per node |
| Jira API rate limiting | High | Medium | Circuit breaker, exponential backoff, request batching |
| Clerk outage (auth dependency) | Low | Critical | JWT caching with extended TTL, graceful degradation mode |
| PostgreSQL write bottleneck | Low | High | Read replicas, query optimization, eventual consistency for analytics |
| Yjs document corruption | Low | Medium | Periodic snapshots, document validation, rollback capability |

### 12.4 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2026-06-15 | Architecture Team | Initial draft |
| 0.9.0 | 2026-06-25 | Architecture Team | Added deployment diagrams, scalability section |
| 1.0.0 | 2026-06-27 | Architecture Team | Final review, all sections complete |

---

*This document is maintained in the repository at `docs/architecture/system-architecture.md` and is reviewed quarterly or upon significant architectural changes.*
