# Scrum Ceremony Platform — Agentic Development Ground Rules

**Version:** 2.0  
**Date:** 2026-06-27  
**Source:** Adapted from Avinya Ground Rules v2.0 + SAW (SAFe Agentic Workflow) best practices

---

## 1. Single Point of Contact

You only talk to me (Orchestrator). I handle all routing, delegation, and reporting.
No separate agents to configure, no context switching for you.
I use `delegate_task` internally to spawn isolated sub-agents per task.

## 2. Three Environments

| Environment | Purpose | URL | DB |
|-------------|---------|-----|-----|
| Development | Active coding, feature branches, local testing | localhost | Local PostgreSQL (Docker) |
| Staging | Integration testing, Playwright regression suite, QA | staging.scp.com | Staging RDS |
| Production | Live platform | scp.com | Production RDS |

### Promotion Flow
```
Feature Branch → Quality Gate → PR → Merge to `develop` → Auto-deploy to STAGING
                                                          → Playwright Tests Pass
                                                          → You give GO → Deploy to PRODUCTION
                                                          → Update Documentation
```

### Branch Strategy
```
master ──────────────────────────────────────────── production deploys
└── develop ──────────────────────────────────── staging deploys
    ├── feat/T-xxx-short-description          feature work
    ├── fix/T-xxx-short-description           bug fixes
    └── arch/T-xxx-short-description          architecture changes
```
- `master` = production-ready, protected, only merged via PR from `develop`
- `develop` = staging branch, auto-deploys to staging on merge
- Feature branches = individual tasks, PR'd into `develop`

## 3. Quality Gates (Pre-Commit)

Every commit must pass these gates before PR is created.

### 3.1 Backend (Python / FastAPI)

| Tool | Purpose | Config |
|------|---------|--------|
| Ruff | Linting + formatting | `backend/pyproject.toml` |
| mypy | Type checking | `backend/pyproject.toml` |
| pytest | Unit tests | `backend/tests/` |
| pytest-cov | Coverage reporting | `backend/pyproject.toml` |

```bash
# Pre-commit hook runs:
ruff check backend/
ruff format --check backend/
mypy backend/
pytest backend/tests/ -v --cov=backend/app --cov-report=xml --cov-fail-under=80
```

### 3.2 Frontend (TypeScript / Next.js)

| Tool | Purpose | Config |
|------|---------|--------|
| Biome | Linting + formatting | `frontend/biome.json` |
| TypeScript | Type checking | `frontend/tsconfig.json` |
| ESLint | Next.js linting | `frontend/eslint.config.mjs` |

```bash
# Pre-commit hook runs:
biome check frontend/
biome format --check frontend/
npx tsc --noEmit -p frontend/
npm run lint --prefix frontend/
```

### 3.3 CodeQL Security Scan (Free, GitHub-Native)

Replaces SonarQube — no subscription needed.
Built into GitHub Actions, free for public repos.
Catches: SQL injection, XSS, hardcoded secrets, insecure deserialization, CWE Top 25.

### 3.4 Coverage Gate

| Metric | Threshold |
|--------|-----------|
| Code Coverage | ≥ 80% |
| No new CodeQL security alerts | Required |

### 3.5 Domain-Specific Guardrails (Ceremony-Specific Validation)

In addition to standard linting, the following ceremony-specific checks MUST pass:

| Guardrail | Script | What It Catches | When It Runs |
|-----------|--------|-----------------|--------------|
| **Anonymity Invariant Check** | `scripts/verify_anonymity.py` | Ensures `board_items` table never contains `author_id` when `is_anonymous=true`; verifies `anonymous_author_map` is the sole identity path | Pre-commit + CI |
| **FSM Transition Validity** | `scripts/verify_fsm.py` | Validates that all ceremony state transitions in code match the spec in `docs/03-ARCHITECTURE/ceremony-state-machine.md`; detects invalid transitions | Pre-commit + CI |
| **Tenant Isolation Check** | `scripts/verify_tenant_isolation.py` | Scans all API endpoints for missing `tenant_id` filters; ensures no cross-tenant query paths exist | CI only |
| **Idempotency Key Verification** | `scripts/verify_idempotency.py` | Ensures all integration sync operations (Jira, ERPNext, Stripe) include idempotency keys | CI only |
| **CRDT Schema Conformance** | `scripts/verify_yjs_schema.py` | Validates Yjs document structure against `data-model.md` schema; ensures no `author_id` in anonymous board items | Pre-commit + CI |
| **Vote Token Uniqueness** | `scripts/verify_vote_tokens.py` | Ensures voter tokens are per-ceremony UUIDs, never user IDs; validates UNIQUE constraint on `(item_id, voter_token)` | CI only |

```bash
# Domain-specific hooks run AFTER standard hooks:
echo "🔬 Running ceremony-specific guardrails..."
python scripts/verify_anonymity.py || exit 1
python scripts/verify_fsm.py || exit 1
python scripts/verify_yjs_schema.py || exit 1
echo "✅ Ceremony guardrails passed!"
```

**Why these matter:**
- **Anonymity breaches** are existential — a single leak destroys trust in the entire product
- **FSM violations** can leave ceremonies stuck in invalid states, losing team data
- **Tenant isolation failures** expose one organization's retros to another
- **Missing idempotency** causes duplicate Jira tickets and billing double-charges
- **CRDT schema drift** causes real-time sync corruption across participants

### 3.6 Quality Gate Flow

```
git commit
┌─────────────────────────────┐
│  Pre-commit hooks (Husky)   │
│  ├─ Ruff (lint + format)    │
│  ├─ Biome (lint + format)   │
│  ├─ TypeScript type check   │
│  ├─ Standard unit tests     │
│  ├─ Anonymity invariant     │  ← Domain-specific
│  ├─ FSM transition validity │  ← Domain-specific
│  └─ CRDT schema conformance │  ← Domain-specific
│                             │
│  ❌ FAIL → Fix & re-commit  │
│  ✅ PASS → Commit succeeds  │
└──────────────┬──────────────┘
┌─────────────────────────────┐
│  Push to feature branch     │
│  CI pipeline (GitHub Actions)│
│  ├─ All pre-commit checks   │
│  ├─ pytest + coverage ≥80%  │
│  ├─ CodeQL security scan    │
│  ├─ Tenant isolation check  │  ← Domain-specific
│  ├─ Idempotency key check   │  ← Domain-specific
│  └─ Vote token validation   │  ← Domain-specific
│                             │
│  ❌ FAIL → PR blocked       │
│  ✅ PASS → PR can be opened │
└──────────────┬──────────────┘
┌─────────────────────────────┐
│  PR to `develop`            │
│  ├─ Code review (you)       │
│  ├─ All CI checks green     │
│  └─ No CodeQL blockers      │
│                             │
│  ✅ Merge → Auto-deploy     │
│     to STAGING              │
└─────────────────────────────┘
```

## 4. Staging & Automated Testing

### 4.1 Auto-Deploy to Staging
- Merge to `develop` → CI deploys to staging automatically
- Staging uses a separate PostgreSQL instance (staging data, refreshed weekly from prod backup)

### 4.2 Playwright Test Suite

| Test Category | What It Covers | Location |
|---------------|---------------|----------|
| Smoke Tests | App loads, key pages render, API health | `tests/playwright/smoke/` |
| Regression Suite | All existing features work end-to-end | `tests/playwright/regression/` |
| API Integration | Backend endpoints return correct data | `tests/playwright/api/` |
| Visual Regression | Screenshot comparison for UI pages | `tests/playwright/visual/` |
| Performance | Page load times, API response times | `tests/playwright/perf/` |
| Anonymity E2E | Anonymous notes never leak author identity | `tests/playwright/security/` |

### 4.3 Staging Test Flow

```
Code merged to develop
  → CI deploys to STAGING
  → Playwright suite runs (30 min)
      ├─ Smoke tests (5 min)
      ├─ Regression suite (15 min)
      ├─ API integration (5 min)
      ├─ Anonymity E2E (5 min)
      └─ Visual regression (5 min)
  → ❌ FAIL → Alert you, block production deploy
  → ✅ PASS → Notify you: "Staging ready for review"
  → You test manually on staging
      → ✅ GO → I deploy to PRODUCTION
      → ❌ NO-GO → I fix issues, re-run cycle
```

## 5. Production Deployment

### 5.1 Deploy Process

You say "Deploy T-001 to production"

```
┌─────────────────────────────────┐
│  1. Verify all tests green      │
│  2. Create release tag          │
│     v{major}.{minor}.{patch}    │
│  3. Merge develop → master      │
│  4. CI deploys to PRODUCTION    │
│  5. Post-deploy smoke test      │
│  6. Update documentation        │
│  7. Notify you: "Live ✅"       │
└─────────────────────────────────┘
```

### 5.2 Rollback Plan
- If post-deploy smoke test fails → automatic rollback to previous release tag
- If you report issues within 24h → one-command rollback

### 5.3 Release Tags
- Format: `v{major}.{minor}.{patch}` (semver)
- `patch` = bug fixes, data updates
- `minor` = new features, new pages
- `major` = breaking API changes, schema migrations

## 6. Documentation

### 6.1 Repo Documentation (Git-tracked)
```
docs/
├── 00-PROJECT-CHARTER.md
├── 01-BUSINESS/
│   ├── market-analysis.md
│   ├── go-to-market.md
│   └── marketing-branding-strategy.md
├── 02-PRODUCT/
│   ├── personas-and-user-journeys.md
│   ├── frontend-architecture.md
│   └── backend-architecture.md
├── 03-ARCHITECTURE/
│   ├── system-architecture.md
│   ├── data-model.md
│   ├── ceremony-state-machine.md
│   ├── anonymity-architecture.md
│   └── adr/
│       └── adr-index.md
├── 04-INTEGRATIONS/
│   ├── erpnext-integration.md
│   ├── jira-integration.md
│   ├── stripe-integration.md
│   └── ollama-integration.md
├── 05-SECURITY/
│   └── security-design.md
├── 07-INFRASTRUCTURE/
│   ├── hosting-infrastructure.md
│   └── operations-metrics-scaling.md
├── 09-RELEASE-PLAN/
│   └── roadmap.md
└── 10-GUARDRAILS/
    ├── ground-rules.md
    └── vibe-coding-zones.md
```

### 6.2 Documentation Rules
- Every production deploy → update relevant docs
- New features → create feature doc + update changelog
- Architecture changes → update system design + create ADR
- Bug fixes → add to troubleshooting runbook if recurring

## 7. Task Intake & Decomposition

### 7.1 Task Lifecycle

```
Your request
  → Orchestrator decomposes into atomic tasks
  → Each task → tracked in Huly (Epic → Feature → Story → Subtask)
  → Implementation (isolated sub-agents per task)
  → PR created → Quality Gate → Staging → Your GO → Production → Docs updated
```

### 7.2 Session Workflows (Start/End Task Protocols)

These protocols are MANDATORY. I must follow them for every task without exception.

#### START TASK PROTOCOL (The `/start-work` equivalent)

When you say "Begin T-001" or assign any task, I MUST complete this checklist BEFORE writing any code:

```
□ 1. READ CONTEXT
     → Read the linked docs (architecture, data model, relevant ADR)
     → Read the Huly story for acceptance criteria
     → Check the ceremony state machine if the task touches ceremony flow

□ 2. SCAN ENVIRONMENT
     → Check current database schema (peek_db.py or Alembic heads)
     → Check existing dependencies (requirements.txt, package.json)
     → Verify no new dependencies needed before inventing them

□ 3. OUTPUT EXECUTION PLAN
     → Present a 3-5 bullet plan: what I'll change, in what order, what could break
     → Identify which zone (GREEN/RED) the work falls into
     → For RED zone: flag that human review will be required before merge
     → WAIT for your approval before proceeding
```

#### END TASK PROTOCOL (The `/pre-pr` equivalent)

Before declaring any task complete and creating a PR, I MUST autonomously run this checklist:

```
□ 1. LOCAL QUALITY GATES
     → ruff check backend/ && ruff format --check backend/
     → biome check frontend/
     → npx tsc --noEmit -p frontend/
     → mypy backend/

□ 2. DOMAIN-SPECIFIC GUARDRAILS
     → python scripts/verify_anonymity.py (if anonymity code touched)
     → python scripts/verify_fsm.py (if ceremony flow touched)
     → python scripts/verify_yjs_schema.py (if board/collaboration code touched)
     → python scripts/verify_tenant_isolation.py (if API code touched)

□ 3. TEST SUITE
     → pytest backend/tests/ -v --cov --cov-fail-under=80
     → If ceremony feature: run specific Playwright tests for that ceremony
     → If integration feature: run idempotency + conflict tests

□ 4. SELF-CORRECTION LOOP
     → If any check fails: fix the issue, re-run, repeat
     → Maximum 3 self-correction attempts
     → If still failing after 3 attempts: STOP, report to you with details

□ 5. PR PREPARATION
     → Fill PR description template completely
     → Link to Huly story (T-xxx)
     → Attach screenshots for UI changes
     → Confirm all checklist items checked
     → Only THEN notify you: "PR ready for review"
```

**Why these protocols exist:**
- Prevents context drift (yesterday's task bleeding into today's)
- Catches errors BEFORE they burn CI minutes or your review time
- Ensures I validate my own work before asking you to
- Makes RED zone code safe through mandatory domain-specific checks

## 8. Approval Gates

| Action | Auto-Execute | Ask First |
|--------|:------------:|:---------:|
| Bug fixes (existing features) | ✅ | |
| Small UI changes | ✅ | |
| Unit tests | ✅ | |
| New feature (single module, GREEN zone) | ✅ | |
| New feature (multi-module or RED zone) | | ✅ |
| Database schema changes | | ✅ |
| API contract changes | | ✅ |
| New third-party integration | | ✅ |
| Deploy to staging | ✅ (auto after merge) | |
| Deploy to production | | ✅ (always) |
| Data deletion/migration | | ✅ |
| Cloud cost changes | | ✅ |

## 9. Git & Commit Conventions

### 9.1 Commit Messages
```
feat: add retrospective board real-time sync
fix: correct action carry-forward logic
arch: implement ceremony state machine with XState
docs: add ADR-004 for Gemma 3 9B choice
test: add Playwright regression suite for retro board
chore: update Ruff config, add pre-commit hooks
```

### 9.2 PR Title Format
```
feat(T-001): Retrospective board with real-time CRDT sync
fix(T-003): Action carry-forward across retros
arch(T-005): Ceremony state machine implementation
```

### 9.3 PR Description Template
```markdown
## What changed
Brief description of changes.

## Why
Link to task: T-xxx

## How to test
1. Steps to verify
2. Expected results

## Screenshots (if UI)

## Checklist
- [ ] Ruff/Biome pass
- [ ] Tests pass (≥80% coverage)
- [ ] CodeQL security scan clean
- [ ] No secrets in code
- [ ] Domain guardrails pass (anonymity, FSM, tenant isolation)
- [ ] Docs updated (if prod-facing)
```

## 10. Communication Protocol

| Event | Response |
|-------|----------|
| Task received | "Working on T-xxx. ETA: ~X hours. Will update when PR is ready." |
| Task blocked | "T-xxx blocked: [reason]. Options: [A/B/C]. Your call." |
| PR created | "PR ready for review: [link]. All quality gates green." |
| Staging deployed | "Staging updated. Playwright running (~30 min). Will report results." |
| Staging tests pass | "Staging ✅. Ready for your GO to deploy to production." |
| Production deployed | "🚀 v1.2.0 is live. Docs updated." |
| Weekly digest | Full status: completed, in-progress, blocked, pipeline health, next week plan |

## 11. Repo Structure (Monorepo)

```
scrum-ceremony-platform/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Quality gates + CodeQL + coverage
│       ├── deploy-staging.yml        # Auto-deploy to staging
│       └── deploy-prod.yml           # Manual trigger, needs approval
├── .husky/                           # Git hooks (pre-commit, pre-push)
│   ├── pre-commit                    # Ruff, Biome, type checks, domain guardrails
│   └── pre-push                      # Full test suite
├── .hermes.md                        # Hermes guardrails (RED/GREEN zones)
├── backend/
│   ├── app/
│   │   ├── api/                      # FastAPI routers
│   │   ├── services/                 # Business logic layer
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── integrations/             # External connectors
│   │   ├── ai/                       # Ollama client, prompts
│   │   └── core/                     # Config, DB, middleware
│   ├── tests/                        # pytest unit tests
│   ├── pyproject.toml                # Ruff, mypy, pytest config
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   ├── components/               # Shared UI components
│   │   ├── features/                 # Feature-specific modules
│   │   │   ├── retro-board/          # Retrospective board feature
│   │   │   ├── planning-poker/       # Planning poker feature
│   │   │   ├── standup/              # Async standup feature
│   │   │   └── health-check/         # Team health check feature
│   │   ├── lib/                      # Utilities, API client
│   │   ├── hooks/                    # React hooks
│   │   └── stores/                   # Zustand stores
│   ├── tests/                        # (future unit tests)
│   ├── biome.json                    # Biome config
│   ├── tsconfig.json
│   └── package.json
├── ai-service/
│   ├── ollama_client.py              # Ollama API wrapper
│   ├── prompts/                      # Prompt templates
│   ├── clustering.py                 # Embedding + DBSCAN clustering
│   └── structured_output.py          # JSON schema enforcement
├── integration-service/
│   ├── connectors/
│   │   ├── base.py                   # Base IntegrationConnector
│   │   ├── jira.py                   # Jira Cloud connector
│   │   ├── erpnext.py                # ERPNext connector
│   │   └── stripe_webhook.py         # Stripe webhook handler
│   ├── dead_letter_queue.py          # Failed sync recovery
│   └── circuit_breaker.py            # Circuit breaker pattern
├── tests/
│   └── playwright/                   # E2E tests
│       ├── smoke/
│       ├── regression/
│       ├── api/
│       ├── visual/
│       ├── security/                 # Anonymity E2E tests
│       └── playwright.config.ts
├── database/
│   └── docker-compose.yml            # Local PostgreSQL + Redis
├── scripts/
│   └── agent_tools/                  # Agent Skills (read-only context gathering)
│       ├── peek_db.py
│       ├── mock_api_response.py
│       ├── test_ceremony_fsm.py
│       ├── check_anonymity.py
│       ├── verify_anonymity.py
│       ├── verify_fsm.py
│       ├── verify_tenant_isolation.py
│       ├── verify_idempotency.py
│       ├── verify_yjs_schema.py
│       └── verify_vote_tokens.py
├── docs/                             # Project documentation (see 6.1)
├── stories/                          # User story backlog
└── README.md
```

## 12. Tooling Setup Summary (100% Free / Open-Source)

| Tool | Scope | Config File | Purpose | Cost |
|------|-------|-------------|---------|------|
| Ruff | Backend | `backend/pyproject.toml` | Python linting + formatting | Free |
| mypy | Backend | `backend/pyproject.toml` | Python type checking | Free |
| pytest | Backend | `backend/pyproject.toml` | Python unit tests | Free |
| pytest-cov | Backend | `backend/pyproject.toml` | Coverage reporting | Free |
| Biome | Frontend | `frontend/biome.json` | TS/JS linting + formatting | Free |
| TypeScript | Frontend | `frontend/tsconfig.json` | Type checking | Free |
| Husky | All | `.husky/` | Git pre-commit/pre-push hooks | Free |
| Playwright | E2E | `tests/playwright/` | Browser automation tests | Free |
| CodeQL | Security | `.github/workflows/ci.yml` | GitHub-native SAST scanning | Free |
| GitHub Actions | CI/CD | `.github/workflows/` | Pipeline orchestration | Free (2,000 min/month) |
| Docker | Infra | `database/docker-compose.yml` | Local dev environment | Free |

**Total cost: $0/month**

## 13. Agent Skills (Autonomous Context Gathering)

I have read-only utility scripts in `scripts/agent_tools/`. I am authorized and encouraged to run these autonomously during development to understand the environment without asking you:

### Context Gathering Skills (Read-Only)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `python scripts/agent_tools/peek_db.py [table]` | Returns schema + 5 sample rows of any table | Before writing queries or models |
| `python scripts/agent_tools/mock_api_response.py [endpoint]` | Returns the exact JSON structure of any API | Before writing API integration code |
| `python scripts/agent_tools/test_ceremony_fsm.py` | Validates current FSM implementation against spec | After any ceremony flow changes |
| `python scripts/agent_tools/check_anonymity.py [ceremony_id]` | Verifies anonymity invariants for a ceremony | After any board/anonymity code changes |
| `python scripts/agent_tools/get_ceremony_state.py [id]` | Returns current ceremony state + phase history | Debugging stuck ceremonies |
| `python scripts/agent_tools/list_active_teams.py` | Returns teams with recent activity | Understanding usage patterns |
| `python scripts/agent_tools/check_sync_status.py [team_id]` | Returns Jira/ERPNext sync status + DLQ depth | Debugging integration issues |
| `python scripts/agent_tools/ollama_benchmark.py` | Runs inference latency benchmark | After AI model or prompt changes |

### Verification Skills (Guardrail Enforcement)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `python scripts/agent_tools/verify_anonymity.py` | Scans all anonymity code paths | Pre-commit + CI |
| `python scripts/agent_tools/verify_fsm.py` | Validates FSM transitions match spec | Pre-commit + CI |
| `python scripts/agent_tools/verify_tenant_isolation.py` | Checks all APIs for tenant_id filters | CI only |
| `python scripts/agent_tools/verify_idempotency.py` | Checks integration sync has idempotency keys | CI only |
| `python scripts/agent_tools/verify_yjs_schema.py` | Validates Yjs document structure | Pre-commit + CI |
| `python scripts/agent_tools/verify_vote_tokens.py` | Validates vote token uniqueness constraints | CI only |

**Why these skills matter:**
- I don't have to copy-paste database schemas into chat — I can look them up myself
- I can verify my own work before declaring a task complete
- Domain-specific guardrails catch errors that standard linters miss (anonymity leaks, FSM violations)
- Reduces your review burden — I catch issues before you see the PR

## 14. Error Handling

| Scenario | Response |
|----------|----------|
| Pre-commit hook fails | Auto-fix what's possible (Ruff format), report what needs manual fix |
| Domain guardrail fails | STOP — do not proceed until resolved. Report specific violation. |
| CI pipeline fails | Analyze logs, create fix task, notify you if blocked |
| CodeQL blocker | Create fix task, don't open PR until resolved |
| Playwright test fails | Analyze screenshot diff, fix or flag for your review |
| Anonymity E2E fails | Treat as SEV1 — immediate fix required, no exceptions |
| Staging deploy fails | Auto-rollback, notify you with error |
| Production deploy fails | Auto-rollback to previous tag, alert you immediately |

## 15. Out of Scope

- ERPNext core modifications (use custom doctypes only)
- Jira plugin development (use REST API + OAuth)
- Mobile app development (responsive web only in Year 1)
- Building a generic whiteboard (we are ceremony-specific, not Miro)
