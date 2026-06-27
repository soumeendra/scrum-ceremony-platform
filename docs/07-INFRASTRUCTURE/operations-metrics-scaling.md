# Operations, Metrics & Scaling

**Document ID:** SCP-DOC-013  
**Version:** 1.0  
**Date:** 2026-06-26  

---

## 1. Operational Model

### Team Structure (Phase 1 — MVP)

```
┌─────────────────────────────────────────────────────────────┐
│                     On-Call Rotation                         │
│                                                             │
│  Primary:  Backend Engineer (weekdays)                     │
│  Secondary: Founder/PO (weekdays, escalations only)        │
│  Weekend:  Auto-alerting → Monday triage                   │
│                                                             │
│  Response SLA:                                              │
│    P1 (site down):        30 min acknowledge, 2 hr resolve │
│    P2 (feature broken):   4 hr acknowledge, 24 hr resolve  │
│    P3 (degraded):         Next business day                │
└─────────────────────────────────────────────────────────────┘
```

### Operational Runbooks (Required by Phase 1)

| Runbook | Trigger | Owner |
|---------|---------|-------|
| Database migration failure | Alembic upgrade returns error | Backend |
| WebSocket server disconnect flood | >50% connections drop in 5 min | Backend |
| Jira sync dead-letter overflow | DLQ depth >100 | Backend |
| Ollama GPU OOM | Ollama returns 500 or ENOMEM | DevOps |
| ERPNext sync failure | Circuit breaker opens | DevOps |
| Stripe webhook verification failure | Signature mismatch | Backend |
| Tenant isolation violation detected | CI guardrail or runtime alert | Security |
| Anonymous author map access | Break-glass query executed | Security |

---

## 2. Observability Stack

### Three Pillars

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│   LOGS          METRICS           TRACES                   │
│   (What happened)  (How much)     (Where & why)           │
│                                                            │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────┐       │
│   │  Sentry   │  │  Prometheus   │  │  OpenTelemetry│       │
│   │  (errors) │  │  + Grafana    │  │  → Jaeger    │       │
│   └──────────┘  └──────────────┘  └──────────────┘       │
│                                                            │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────┐       │
│   │ PostHog  │  │  pg_stat_*   │  │  Yjs doc     │       │
│   │ (product │  │  (DB stats)  │  │  history     │       │
│   │  events) │  │              │  │  (board ops) │       │
│   └──────────┘  └──────────────┘  └──────────────┘       │
│                                                            │
│   ┌──────────────────────────────────────────────┐        │
│   │         Alerting → PagerDuty / Opsgenie      │        │
│   └──────────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────────┘
```

### Key Dashboards

| Dashboard | Audience | Key Widgets |
|-----------|----------|-------------|
| **Platform Health** | DevOps | Uptime %, error rate, p95 latency, active WebSocket connections, DB connections, Redis memory |
| **Product Engagement** | Product Owner | DAU/MAU, ceremonies started/day, action completion rate, AI feature adoption, signup→activation funnel |
| **Revenue** | Founder | MRR, churn rate, trial→paid conversion, plan distribution, dunning queue depth |
| **Integration Health** | Backend | Jira sync success rate, ERPNext sync lag, DLQ depth, webhook processing time, circuit breaker state |
| **AI Infrastructure** | DevOps | Ollama uptime, inference latency p95, embedding throughput, GPU utilization, fallback triggers |

---

## 3. Product Metrics (AARRR Framework)

### Acquisition

| Metric | Definition | Target (Month 6) | Target (Year 1) |
|--------|-----------|-------------------|------------------|
| Website visitors | Unique monthly visitors | 5,000 | 50,000 |
| Signups | New user registrations | 100 | 1,000 |
| Signup→Team creation rate | % of signups that create a team | 60% | 70% |
| Team creation→First retro rate | % of teams that start a retro | 40% | 50% |
| CAC (Customer Acquisition Cost) | Marketing spend / new paid teams | <$50 | <$100 |
| Organic signup ratio | % signups from non-paid channels | 30% | 50% |

### Activation

| Metric | Definition | Target (Month 6) | Target (Year 1) |
|--------|-----------|-------------------|------------------|
| Time to first retro | Minutes from signup to first retro started | <10 min | <5 min |
| 3-retro completion rate | % of teams completing 3 retros in 6 weeks | 40% | 70% |
| Onboarding completion | % completing setup wizard | 70% | 85% |
| Template used on first retro | % using template (not blank board) | 80% | 90% |
| AI features tried | % using AI clustering or summary in first 3 retros | 30% | 50% |

### Retention

| Metric | Definition | Target (Month 6) | Target (Year 1) |
|--------|-----------|-------------------|------------------|
| WAU/MAU | Weekly active users / monthly active users | 30% | 45% |
| Day-30 retention | % of teams active 30 days after signup | 40% | 55% |
| Day-90 retention | % of teams active 90 days after signup | 25% | 40% |
| Retro cadence adherence | % of teams running retros at scheduled cadence | 50% | 70% |
| NPS | Net Promoter Score (quarterly survey) | 30 | 45 |
| Churn rate (paid) | Monthly paid team churn | 8% | 4% |

### Revenue

| Metric | Definition | Target (Month 6) | Target (Year 1) |
|--------|-----------|-------------------|------------------|
| MRR | Monthly recurring revenue | $2K | $5K |
| Trial→Paid conversion | % of trials converting to paid | 5% | 15% |
| ARPU | Average revenue per team per month | $0 (mostly free) | $35 |
| Net revenue retention | Including expansion + contraction | 90% | 110% |
| Plan distribution | Free:Paid:Business ratio | 90:9:1 | 70:22:8 |
| Expansion revenue | Revenue from plan upgrades | $0 | 20% of new MRR |

### Referral

| Metric | Definition | Target (Month 6) | Target (Year 1) |
|--------|-----------|-------------------|------------------|
| Viral coefficient | Teams invited per active team | 0.1 | 0.3 |
| In-app invite sent rate | % of facilitators sending team invites | 60% | 75% |
| Community contributions | Templates shared, blog posts, conference talks | 5 | 30 |

---

## 4. Scaling Strategy

### Phase 1: Single Server (Up to 500 teams)

```
┌─────────────────────────────────────────────┐
│           Single Server / Small Cluster      │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Next.js  │  │ FastAPI  │  │ PostgreSQL│  │
│  │ (Vercel) │  │ (2 vCPU) │  │ (4 vCPU) │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Redis   │  │  Ollama  │  │ ERPNext  │  │
│  │ (cache)  │  │ (GPU)   │  │ (2 vCPU) │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  Capacity: ~500 teams, ~100 concurrent boards│
│  Monthly cost: ~$200-300 (cloud)             │
└─────────────────────────────────────────────┘
```

### Phase 2: Horizontal Scaling (500-5,000 teams)

| Component | Scaling Action | Trigger |
|-----------|---------------|---------|
| FastAPI | Add replicas behind load balancer | CPU >70% or p95 latency >500ms |
| PostgreSQL | Add read replica for analytics queries | DB CPU >60% or slow queries |
| Redis | Add Redis Cluster | Memory >80% or connection count >limit |
| WebSocket server | Partition by team (consistent hashing) | >500 concurrent WebSocket connections |
| Ollama | Add second GPU replica | Inference queue depth >10 |
| Background worker | Add worker processes | DLQ growing or job latency >5min |
| ERPNext | Vertical scale (add CPU/RAM) | ERPNext response time >2s |

### Phase 3: Kubernetes + Multi-Region (5,000+ teams)

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│                                                         │
│  ┌─── Ingress ──────────────────────────────────────┐  │
│  │  nginx-ingress + CloudFlare WAF                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─── Namespace: platform ──────────────────────────┐  │
│  │  nextjs-frontend  (3 replicas, HPA)              │  │
│  │  fastapi-backend  (5 replicas, HPA)              │  │
│  │  ws-server        (3 replicas, sticky sessions)  │  │
│  │  celery-worker    (5 replicas, HPA by queue)     │  │
│  │  ai-service       (2 replicas, GPU node pool)    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─── Namespace: data ──────────────────────────────┐  │
│  │  postgres-primary  (StatefulSet)                 │  │
│  │  postgres-replica  (2 replicas, read traffic)    │  │
│  │  redis-cluster     (3 masters + 3 replicas)     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─── Namespace: integrations ──────────────────────┐  │
│  │  erpnext           (1 replica, burst to 2)      │  │
│  │  jira-sync-worker  (2 replicas)                  │  │
│  │  stripe-webhook    (2 replicas)                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─── Node Pools ───────────────────────────────────┐  │
│  │  general:    3× n2d-standard-4  (CPU workloads) │  │
│  │  memory:     2× n2d-standard-8  (DB, Redis)     │  │
│  │  gpu:        2× g2-standard-4   (Ollama, L4 GPU)│  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Capacity Planning

### Concurrent Users Model

| Scenario | Teams | Est. Concurrent Users | WebSocket Connections | Server Requirements |
|----------|-------|----------------------|---------------------|-------------------|
| Alpha | 5 | 25 | 25 | 1 server (dev) |
| Beta | 30 | 150 | 150 | 1 server (small) |
| GA launch | 200 | 500 | 500 | 2 FastAPI replicas + 2 WS servers |
| Year 1 | 500 | 1,500 | 1,500 | 3 FastAPI + 3 WS + read replica |
| Year 2 | 2,000 | 5,000 | 5,000 | 5 FastAPI + 5 WS + 2 read replicas + WS partition |
| Year 3 | 5,000 | 15,000 | 15,000 | K8s with HPA + multi-region |

### Database Growth Model

| At | Teams | Ceremonies | Board Items | Embeddings | DB Size |
|----|-------|-----------|-------------|------------|---------|
| Month 6 | 150 | 3,000 | 30,000 | 30,000 | ~300 MB |
| Year 1 | 500 | 50,000 | 500,000 | 500,000 | ~4.5 GB |
| Year 2 | 2,000 | 400,000 | 4,000,000 | 4,000,000 | ~35 GB |
| Year 3 | 5,000 | 2,000,000 | 20,000,000 | 20,000,000 | ~175 GB |

### Connection Pooling

```python
# FastAPI SQLAlchemy async session with pool sizing
# Rule of thumb: pool_size = (core_count * 2) + effective_sparkle

DATABASE_CONFIG = {
    "pool_size": 20,          # Concurrent persistent connections
    "max_overflow": 10,       # Additional connections under load
    "pool_timeout": 30,       # Seconds to wait for available connection
    "pool_recycle": 3600,     # Recycle connections hourly (PG default)
    "pool_pre_ping": True,    # Verify connection before use
}
```

---

## 6. Cost Model by Scale

| Cost Category | 500 teams/mo | 2,000 teams/mo | 5,000 teams/mo |
|---------------|-------------|----------------|----------------|
| Frontend (Vercel) | $20 | $20 | $40 |
| FastAPI backend | $50 (1 server) | $150 (3 servers) | $400 (K8s) |
| PostgreSQL | $50 (db.t3.medium) | $200 (db.r6g.large + replica) | $500 (multi-replica) |
| Redis | $15 | $50 | $150 |
| Ollama GPU | $100 (1× L4 spot) | $200 (2× L4) | $400 (3× L4) |
| ERPNext | $30 (1 server) | $60 (2 servers) | $100 |
| Monitoring (Sentry+PostHog) | $50 | $100 | $200 |
| CDN + WAF | $20 | $30 | $50 |
| CI/CD | $20 | $30 | $50 |
| **Total** | **~$355/mo** | **~$840/mo** | **~$1,890/mo** |

**Revenue at 500 teams (10% paid, $35/mo avg): $1,750/mo → covers infra costs.**

---

## 7. SLA Targets

| Metric | Phase 1 (MVP) | Phase 2 | Phase 3 (Enterprise) |
|--------|---------------|---------|----------------------|
| Uptime | 99% (3.6 hr/mo downtime) | 99.5% (1.8 hr/mo) | 99.9% (43 min/mo) |
| Board interaction latency | <1s p95 | <500ms p95 | <200ms p95 |
| API response latency | <2s p95 | <1s p95 | <500ms p95 |
| AI summary generation | <15s | <10s | <5s |
| Jira sync latency | <60s | <30s | <10s |
| Deployment frequency | Weekly | Daily | Continuous |
| RTO (Recovery Time Objective) | 4 hours | 2 hours | 30 min |
| RPO (Recovery Point Objective) | 1 hour | 15 min | 5 min |

---

## 8. Incident Management

### Severity Levels

| Severity | Definition | Example | Response |
|----------|-----------|---------|----------|
| **SEV1** | Complete service outage or data corruption | All ceremonies inaccessible; cross-tenant data leak detected | Page on-call → 30 min ack → war room → 2 hr resolution target |
| **SEV2** | Major feature degraded | Board sync failing; Jira integration down; AI service returning errors | Page on-call → 4 hr ack → 24 hr resolution |
| **SEV3** | Minor feature issue | Export failing; health check results delayed; dashboard slow | Slack alert → next business day |
| **SEV4** | Cosmetic / low impact | UI glitch; wrong chart label; notification text typo | Add to backlog |

### Incident Response Flow

```
Detect → Triage → Communicate → Mitigate → Resolve → Post-mortem
   │         │          │            │          │          │
   ▼         ▼          ▼            ▼          ▼          ▼
 Sentry   Assign    Status page   Workaround  Fix +     Blameless
 alert    SEV level  update       or config   deploy    review
                     + customer               change
                     notification
```

### Post-Mortem Template

```
- Date:
- Severity: SEV1/2/3
- Duration: X hours Y minutes
- Impact: N teams, N ceremonies affected
- Root cause:
- Timeline:
- What went well:
- What went wrong:
- Action items (with owners + deadlines):
```

---

## 9. Deployment Strategy

### Phase 1: Simple Rolling Deploy

```bash
# Pull latest, restart containers with health check
docker-compose pull
docker-compose up -d --remove-orphans
./scripts/health-check.sh  # Verify all services respond
```

### Phase 2: Blue-Green Deployment

```
1. Deploy new version to "green" environment
2. Run smoke tests against green
3. If pass: switch load balancer from blue → green
4. Monitor error rate for 15 minutes
5. If error rate >threshold: switch back to blue (rollback)
6. If stable: decommission blue
```

### Phase 3: Canary Deployment (K8s)

```yaml
# canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
      - setWeight: 5        # 5% traffic to new version
      - pause: {duration: 5m}
      - setWeight: 25       # 25% traffic
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100      # Full rollout
      canaryService: canary-svc
      stableService: stable-svc
```

---

## 10. Data Lifecycle Management

### Retention Policies

| Data Type | Retention | Purge Mechanism | Rationale |
|-----------|-----------|-----------------|-----------|
| Active ceremony data | Until org deletes | N/A | Operational data |
| Anonymous author map | 90 days | Daily Celery job | PII minimization |
| Audit events | 7 years | Manual (compliance) | SOC 2 / legal |
| Board item embeddings (pgvector) | Same as board items | Cascade delete | AI feature data |
| Redis voter tokens | Ceremony end + 1 hr | TTL expiry | Ephemeral by design |
| Webhook processing logs | 30 days | Daily purge | Debug window only |
| DLQ messages | 30 days or resolved | Purge on resolve + 7 days | Error tracking |
| Analytics aggregations | 2 years | Annual archive | Long-term trends |
| ERPNext sync logs | 90 days | ERPNext auto-purge | Integration audit |

### Backup Strategy

| What | Method | Frequency | Retention | RTO | RPO |
|------|--------|-----------|-----------|-----|-----|
| PostgreSQL | pg_basebackup + WAL archiving | Continuous | 30 days | 1 hr | <5 min |
| ERPNext MariaDB | Mariabackup | Daily | 14 days | 4 hr | 24 hr |
| Redis | RDB snapshots | Every 15 min | 7 days | 15 min | 15 min |
| Configuration | Git (versioned) | Every commit | Infinite | Minutes | 0 |

---

## 11. Scaling Playbooks

### When Board Sync Gets Slow

```
1. Check WebSocket connection count → redis-cli INFO clients
2. If >500 concurrent: add WS server replica
3. Check Yjs document size → if >1000 items, paginate stale items
4. Check network latency → if cross-region, add regional WS endpoint
5. Check client-side render time → if >100ms, enable React.memo + virtualization
```

### When Database Queries Slow Down

```
1. Check pg_stat_statements for slow queries
2. Common culprit: analytics queries on large ceremony tables
3. Fix: add read replica, route analytics to replica
4. Check missing indexes: EXPLAIN ANALYZE on slow queries
5. Check connection pool exhaustion: pg_stat_activity count vs pool_size
6. If embeddings table large: check HNSW index parameters, consider IVFFlat
```

### When AI Inference Queue Backs Up

```
1. Check Ollama GPU utilization → nvidia-smi
2. If >95%: add second Ollama replica
3. Check inference latency: if p95 >10s, consider smaller context window
4. Check if fallback to cloud LLM is configured and working
5. Rate limit AI requests per team if queue depth >50
```

---

*This document should be reviewed quarterly and updated as the platform scales through phases. Operational SLA targets become contractual in Phase 4 (Enterprise).*
