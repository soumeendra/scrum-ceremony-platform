# Security & Privacy Design ⚠️ RED ZONE

**Document ID:** SCP-DOC-009  
**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-06-26  
**Classification:** RED ZONE — Security architecture. All implementations require security review.

---

## 1. Threat Model (STRIDE)

| Threat | Target | Severity | Mitigation |
|--------|--------|----------|------------|
| **Spoofing** — Fake user joins ceremony | Board participation | Medium | Auth required for all WebSocket connections; session token validated on connect |
| **Tampering** — Modify another user's notes | Board items | High | CRDT prevents silent overwrites; all edits attributed to authenticated user; audit logged |
| **Repudiation** — User denies writing toxic content | Board items | Medium | Audit log with immutable records; break-glass identity for anonymous items |
| **Info Disclosure** — Cross-tenant data leak | All data | Critical | Row-level security on every table; tenant_id in all queries; API middleware enforcement |
| **Info Disclosure** — Anonymous author identity exposed | Anonymous notes | Critical | Dual-path data model; identity map access-gated; never in API responses |
| **Denial of Service** — Flood board with notes | Board items | Medium | Rate limiting per user per ceremony; max notes per phase configurable |
| **Elevation of Privilege** — Member grants self admin | Roles | High | Role changes require org_admin; all role mutations audited |

---

## 2. Authentication Architecture

### Provider: Clerk

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Browser    │────►│   Clerk     │────►│  Product App │
│  (React)    │     │  (Auth)     │     │  (FastAPI)   │
└─────────────┘     └─────────────┘     └──────────────┘
                           │
                     ┌─────┴──────┐
                     │  Identity  │
                     │  Provider  │
                     │ (Google,   │
                     │  Okta,     │
                     │  Azure AD) │
                     └────────────┘
```

### Flow

1. User authenticates via Clerk (email/magic-link/social/SSO)
2. Clerk issues JWT with custom claims: `org_id`, `role`, `team_ids`
3. Frontend sends JWT in `Authorization: Bearer` header
4. FastAPI middleware validates JWT via Clerk's public key
5. Sets PostgreSQL session variables: `app.current_tenant_id`, `app.user_role`

### Why Clerk (not Auth0)

| Factor | Clerk | Auth0 |
|--------|-------|-------|
| Pricing (free tier) | 10,000 MAU | 7,000 MAU |
| SAML SSO | Free on Pro ($25/mo) | Requires Enterprise ($240/mo) |
| SCIM | Available on Enterprise | Available on Enterprise |
| DX for Next.js | First-class SDK | Good but more config |
| User management UI | Built-in | Requires separate dashboard |

---

## 3. Authorization: Role-Based Access Control

### Role Hierarchy

```
org_admin
  └── workspace_admin
        └── team_facilitator
              └── team_member
                    └── viewer
```

### Permission Matrix

| Action | org_admin | ws_admin | facilitator | member | viewer |
|--------|:---------:|:--------:|:----------:|:------:|:------:|
| Create workspace | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create team | ✅ | ✅ | ❌ | ❌ | ❌ |
| Publish org template | ✅ | ❌ | ❌ | ❌ | ❌ |
| Start ceremony | ✅ | ✅ | ✅ | ❌ | ❌ |
| Advance ceremony phase | ✅ | ✅ | ✅ | ❌ | ❌ |
| Add board item | ✅ | ✅ | ✅ | ✅ | ❌ |
| Vote | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create action | ✅ | ✅ | ✅ | ✅ | ❌ |
| Approve AI summary | ✅ | ✅ | ✅ | ❌ | ❌ |
| View team dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| View cross-team analytics | ✅ | ✅ | ❌ | ❌ | ❌ |
| Break anonymity glass | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage integrations | ✅ | ✅ | ❌ | ❌ | ❌ |
| Invite team member | ✅ | ✅ | ✅ | ❌ | ❌ |
| Export data | ✅ | ✅ | ✅ | ✅ | ❌ |
| Manage billing | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 4. Multi-Tenancy Security

### Row-Level Security (RLS) — Enforcement Layers

| Layer | Mechanism | Failure Mode |
|-------|-----------|-------------|
| **Application** | FastAPI middleware sets `app.current_tenant_id` on every request | 403 if missing |
| **Database** | PostgreSQL RLS policies on ALL tenant-scoped tables | Empty result set if tenant_id mismatch |
| **API** | All endpoints require authenticated user; org_id derived from JWT | 401 if no valid JWT |
| **WebSocket** | Auth on connect; tenant_id in connection metadata; board events filtered | Connection rejected |
| **Integration** | Jira/ERPNext connections scoped per-org; secrets encrypted per-tenant | Sync fails safely |

### RLS Test (Required in CI)

```sql
-- This test MUST pass on every deploy
-- User A in tenant X cannot see tenant Y's data

SET app.current_tenant_id = 'tenant_x';
SELECT count(*) FROM ceremonies WHERE tenant_id = 'tenant_y';
-- Expected: 0 (RLS blocks it)

SET app.current_tenant_id = 'tenant_y';
SELECT count(*) FROM ceremonies WHERE tenant_id = 'tenant_y';
-- Expected: >0 (RLS allows own tenant)
```

---

## 5. Data Encryption

| Data | At Rest | In Transit | Key Management |
|------|---------|------------|----------------|
| PostgreSQL data | AES-256 (TDE) | TLS 1.3 | AWS KMS / Vault |
| Redis | No (ephemeral) | TLS 1.3 | — |
| Integration secrets (Jira tokens, etc.) | AES-256 in `integration_config.encrypted_secrets` | TLS 1.3 | App-level encryption with ENV-stored master key |
| JWT tokens | N/A | TLS 1.3 + HTTPS only | Clerk manages |
| Voter tokens | Redis only (ephemeral, deleted on ceremony end) | TLS 1.3 | — |
| Anonymous author map | AES-256 (TDE) | TLS 1.3 | Same as PG |

### Master Key Rotation

- Integration secret master key stored in `INTEGRATION_SECRET_KEY` env var
- Rotation: decrypt with old key → re-encrypt with new key → atomic swap
- Rotation job runs quarterly, logged in audit trail

---

## 6. API Security

### Rate Limiting

| Endpoint Category | Limit | Window | Key |
|-------------------|-------|--------|-----|
| Board item CRUD | 60 req/min | Per user per ceremony | `user_id + ceremony_id` |
| Vote submission | 30 req/min | Per user per ceremony | `user_id + ceremony_id` |
| Action CRUD | 60 req/min | Per user per team | `user_id + team_id` |
| Auth (login/signup) | 5 req/min | Per IP | `ip_address` |
| Jira sync | 10 req/min | Per team | `team_id` |
| AI requests | 10 req/min | Per user | `user_id` |
| General API | 100 req/min | Per user | `user_id` |

### Input Validation

- All text inputs (board items, actions, templates): max 2000 chars, HTML sanitized
- Template names: max 200 chars, alphanumeric + spaces + hyphens
- Vote weights: integer 0-5
- All IDs: UUID v4 format validation

---

## 7. Privacy Design (GDPR Alignment)

### Data Classification

| Category | Examples | Retention | Deletion |
|----------|----------|-----------|----------|
| **PII** | email, display_name, avatar | Account lifetime | On account deletion |
| **Contribution data** | board item text, vote choices | 2 years (configurable) | On account deletion (including anonymous via identity map) |
| **Behavioral data** | participation timestamps, login events | 90 days | Auto-purged |
| **Analytics** | aggregated metrics, health scores | 2 years | Auto-purged |
| **Audit** | security events, anonymity breaks | 7 years | Compliance-required retention |
| **Integration secrets** | Jira tokens, ERPNext keys | Account lifetime | On disconnect |

### Right to Deletion Flow

```
User requests deletion
    │
    ▼
1. Find all anonymous contributions via anonymous_author_map
2. Delete board_items where id IN (linked board_item_ids)
3. Delete anonymous_author_map entries
4. Delete named board_items where author_id = user_id
5. Delete votes where voter_id = user_id
6. Delete actions where owner_id = user_id (reassign to "Former Team Member")
7. Delete user account from Clerk
8. Delete from PostgreSQL users table
9. Log audit event: "user.account_deleted"
10. Notify ERPNext (mark contact as inactive)
11. Notify Stripe (cancel subscription)
```

### Data Processing Lawfulness

We process user data under:
- **Art. 6(1)(b)** — Contract performance (providing the SaaS service)
- **Art. 6(1)(f)** — Legitimate interest (analytics, security, product improvement)
- **Art. 6(1)(a)** — Consent (marketing communications, optional)

---

## 8. SOC 2 Type 2 Readiness

### Trust Service Criteria Mapping

| Criteria | Control | Evidence | Status |
|----------|---------|----------|--------|
| **CC6.1** — Logical access | Clerk SSO + RLS + RBAC | Auth logs, RLS test results | Phase 4 |
| **CC6.2** — Role management | Permission matrix + role hierarchy | Role assignment audit log | Phase 4 |
| **CC6.3** — Least privilege | Per-role API access + RLS | API access logs | Phase 2 |
| **CC7.1** — Incident detection | Sentry + anomaly alerts | Alert configs, runbooks | Phase 3 |
| **CC7.2** — Incident response | IR runbook + on-call rotation | IR post-mortems | Phase 4 |
| **CC8.1** — Change management | Git PR + CI guardrails + review | PR history, CI results | Phase 0 |
| **CC9.1** — Risk assessment | Annual risk assessment | Threat model updates | Phase 4 |

### SOC 2 Audit Timeline

| Milestone | Date |
|-----------|------|
| Controls implemented | Month 10 |
| Monitoring period begins | Month 10 |
| Monitoring period ends (3 months min) | Month 13 |
| Auditor engagement | Month 13 |
| Audit complete | Month 15 |
| SOC 2 Type 2 report issued | Month 16 |

---

## 9. Infrastructure Security

| Area | Standard | Implementation |
|------|----------|---------------|
| **Network** | Private VPC, no public DB access | PostgreSQL in private subnet; only FastAPI exposed |
| **Container** | Minimal images, no root | Distroless or Alpine base; USER directive in Dockerfile |
| **Dependency scanning** | Snyk/Dependabot | CI step on every PR |
| **Secret scanning** | GitGuardian | Pre-commit hook + CI scan |
| **SAST** | Semgrep | CI step on every PR |
| **Penetration testing** | Annual external pen test | Budget in Phase 4; scope: anonymity, RLS, API auth |
| **Backup** | Daily PG backups, 30-day retention | AWS RDS automated backups |
| **DR** | RPO 1 hour, RTO 4 hours | Cross-region read replica (Phase 4) |

---

*This document must be reviewed by a security engineer before any RED ZONE code is merged. Annual review required to maintain SOC 2 compliance.*
