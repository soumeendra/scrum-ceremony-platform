# Scrum Ceremony Platform — Agentic Development Ground Rules

**Version:** 1.0  
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

```yaml
# In CI workflow
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: python, javascript
- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v3
```

### 3.4 Coverage Gate

| Metric | Threshold |
|--------|-----------|
| Code Coverage | ≥ 80% |
| No new CodeQL security alerts | Required |

### 3.5 Quality Gate Flow

```
git commit
┌─────────────────────────────┐
│  Pre-commit hooks (Husky)   │
│  ├─ Ruff (lint + format)    │
│  ├─ Biome (lint + format)   │
│  ├─ TypeScript type check   │
│  └─ Relevant unit tests     │
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
│  └─ Build verification      │
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

### 4.3 Staging Test Flow

```
Code merged to develop
  → CI deploys to STAGING
  → Playwright suite runs (30 min)
      ├─ Smoke tests (5 min)
      ├─ Regression suite (15 min)
      ├─ API integration (5 min)
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

### 7.2 Agent Session Protocols (Start/End Task)

**Start Task Protocol:**
When you say "Begin T-001", I must automatically:
1. Read the relevant docs for context
2. Scan the active schema of relevant database tables
3. Check existing dependencies before inventing new ones
4. Output a 3-bullet execution plan for your approval BEFORE writing code

**End Task Protocol:**
Before telling you a PR is ready, I must autonomously run:
1. `ruff check` and `biome check` locally
2. The specific `pytest` suite for that module
3. If tests fail, self-correct up to 3 times before asking for help

## 8. Approval Gates

| Action | Auto-Execute | Ask First |
|--------|:------------:|:---------:|
| Bug fixes (existing features) | ✅ | |
| Small UI changes | ✅ | |
| Unit tests | ✅ | |
| New feature (single module) | ✅ | |
| New feature (multi-module) | | ✅ |
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
│   ├── pre-commit                    # Ruff, Biome, type checks
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
│       └── playwright.config.ts
├── database/
│   └── docker-compose.yml            # Local PostgreSQL + Redis
├── docs/                             # Project documentation (see 6.1)
├── scripts/                          # Utility & agent tools
│   └── agent_tools/                  # Read-only context gathering scripts
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

I have read-only utility scripts in `scripts/agent_tools/`. I am authorized and encouraged to run these autonomously during development:

| Script | Purpose |
|--------|---------|
| `python scripts/agent_tools/peek_db.py [table]` | Returns schema + 5 sample rows |
| `python scripts/agent_tools/mock_api.py [endpoint]` | Returns API response structure |
| `python scripts/agent_tools/test_ceremony_fsm.py` | Validates ceremony state machine transitions |
| `python scripts/agent_tools/check_anonymity.py [ceremony_id]` | Verifies anonymity invariants |

## 14. Error Handling

| Scenario | Response |
|----------|----------|
| Pre-commit hook fails | Auto-fix what's possible (Ruff format), report what needs manual fix |
| CI pipeline fails | Analyze logs, create fix task, notify you if blocked |
| CodeQL blocker | Create fix task, don't open PR until resolved |
| Playwright test fails | Analyze screenshot diff, fix or flag for your review |
| Staging deploy fails | Auto-rollback, notify you with error |
| Production deploy fails | Auto-rollback to previous tag, alert you immediately |

## 15. Out of Scope

- ERPNext core modifications (use custom doctypes only)
- Jira plugin development (use REST API + OAuth)
- Mobile app development (responsive web only in Year 1)
- NSE/BSE/exchange API integrations (not applicable)
