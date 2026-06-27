# Release Roadmap + Sprint Plan

**Document ID:** SCP-DOC-011  
**Version:** 1.0  
**Date:** 2026-06-26  

---

## Phase Timeline

```
Week  0   4   8   12  16  20  24  28  32  36  40  44  48
      │───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───│
P0:  ████████████                                        Foundation & Guardrails
P1:       ████████████████████████████████               Core MVP
P2:                           ████████████████████████   Differentiation + Billing
P3:                                       ████████████████ Multi-Ceremony
P4:                                               ████████████████████ Enterprise
```

---

## Phase 0: Foundation & Guardrails (Weeks 1–4)

| Sprint | Weeks | Focus | Deliverables |
|--------|-------|-------|-------------|
| Sprint 1 | 1-2 | Project scaffold + infra | Monorepo, Docker Compose, PostgreSQL, Redis, ERPNext, Ollama running locally |
| Sprint 2 | 3-4 | Auth + guardrails + DB schema | Clerk integration, RLS policies, Alembic migrations, `.hermes.md`, CI pipeline |

**Exit Criteria:** `docker compose up` starts all services; CI passes; auth flow works end-to-end.

---

## Phase 1: Core MVP (Weeks 5–14)

| Sprint | Weeks | Focus | Stories | Points |
|--------|-------|-------|---------|--------|
| Sprint 3 | 5-6 | Team CRUD + template library | EPIC-10/S05-S07, EPIC-01/F01/S01-S04 | ~18 |
| Sprint 4 | 7-8 | Board UI + CRDT sync | EPIC-01/F02/S05-S09 | ~23 |
| Sprint 5 | 9-10 | Anonymity + voting + facilitation | EPIC-02/F07/S01-S04, EPIC-01/F03, F04 | ~20 |
| Sprint 6 | 11-12 | Action tracking + Jira sync | EPIC-03/F11/F12, F14/S09-S12 | ~26 |
| Sprint 7 | 13-14 | AI clustering + summaries + analytics basics | EPIC-04/F15/F16/S01-S05, EPIC-05/F19/S01-S02 | ~23 |

**Exit Criteria:** 10 pilot teams complete 3+ retros each; action completion rate >30%; anonymity used in >50% of retros.

---

## Phase 2: Differentiation + Billing (Weeks 15–22)

| Sprint | Weeks | Focus | Stories | Points |
|--------|-------|-------|---------|--------|
| Sprint 8 | 15-16 | Recurring detection + action quality | EPIC-04/F17/F18/S07-S10 | ~18 |
| Sprint 9 | 17-18 | Health checks + participation analytics | EPIC-05/F20, EPIC-02/F09 | ~16 |
| Sprint 10 | 19-20 | ERPNext sync + Stripe billing | EPIC-07/F27/F28, EPIC-09/F35/F36 | ~22 |
| Sprint 11 | 21-22 | Onboarding + export + audit + security review | EPIC-05/F21/S08, EPIC-08/F32/S04 | ~16 |

**Exit Criteria:** 50% of pilot teams use analytics/recurring features; billing flow works end-to-end; audit log operational.

---

## Phase 3: Multi-Ceremony Suite (Weeks 23–32)

| Sprint | Weeks | Focus | Stories | Points |
|--------|-------|-------|---------|--------|
| Sprint 12 | 23-24 | Planning poker ceremony | EPIC-06/F22/S01-S03 | ~13 |
| Sprint 13 | 25-26 | Async standups + blocker flagging | EPIC-06/F23/S04-S06 | ~10 |
| Sprint 14 | 27-28 | Sprint review + decision log + shared actions | EPIC-06/F24/F25/S07-S12 | ~21 |
| Sprint 15 | 29-30 | Slack + Teams integrations | EPIC-07/F29/F30/S13-S16 | ~16 |
| Sprint 16 | 31-32 | API v1 + polish + accessibility | EPIC-08/F34/S09, quality pass | ~12 |

**Exit Criteria:** 30% of active teams use a second ceremony type within 60 days.

---

## Phase 4: Enterprise Scale (Weeks 33–48)

| Sprint | Weeks | Focus | Stories | Points |
|--------|-------|-------|---------|--------|
| Sprint 17 | 33-34 | SSO + SCIM | EPIC-08/F31/S01-S02 | ~8 |
| Sprint 18 | 35-36 | RBAC + template governance | EPIC-08/F31/S03, F33/S06-S07 | ~8 |
| Sprint 19 | 37-38 | Cross-team heatmap + admin console | EPIC-05/F21/S06-S07, EPIC-08/F34/S08 | ~13 |
| Sprint 20 | 39-40 | SOC 2 prep + API v2 | EPIC-08/F32/S05, F34/S09 | ~18 |
| Sprint 21 | 41-42 | Data residency + retention | EPIC-08/F34/S10-S11 | ~8 |
| Sprint 22 | 43-44 | Security audit + pen test prep | External engagement | ~8 |
| Sprint 23 | 45-46 | Performance at scale + load testing | Infrastructure | ~8 |
| Sprint 24 | 47-48 | Final hardening + GA release criteria | Quality | ~5 |

**Exit Criteria:** SOC 2 audit initiated; 3 enterprise accounts; cross-team analytics used by 2+ orgs.

---

## MVP Definition of Done

A feature is "done" when:

- [ ] Code merged to main via PR (with review for RED zone)
- [ ] Unit tests pass (≥80% coverage for RED zone)
- [ ] Integration tests pass
- [ ] CI guardrails pass (tenant isolation, anonymity, FSM, no raw SQL)
- [ ] Feature flag configured (can be toggled off)
- [ ] Product analytics events instrumented
- [ ] Documentation updated (if architecture-changing)
- [ ] Accessibility: keyboard navigable, screen-reader compatible
- [ ] No P1/P2 bugs open

---

## Go-to-Market Timeline

| Milestone | Week | What |
|-----------|------|------|
| **Alpha** (private) | 14 | 3-5 teams using MVP, no billing |
| **Beta** (invited) | 22 | 20-30 teams, billing live, NPS survey |
| **Public launch** | 32 | Self-serve signup, 3 ceremony types |
| **Enterprise GA** | 48 | SOC 2, SSO, full governance |
