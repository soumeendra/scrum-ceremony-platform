# Hosting Infrastructure Setup

## Scrum Ceremony Platform

---

**Document Version:** 1.0.0  
**Status:** Draft  
**Author:** Infrastructure Engineering Team  
**Last Updated:** June 2026  
**Audience:** DevOps, SRE, Platform Engineering, Security Team  
**Classification:** Internal

---

## Table of Contents

1. [Hosting Strategy Overview](#1-hosting-strategy-overview)
2. [Development Environment](#2-development-environment)
3. [Staging Environment](#3-staging-environment)
4. [Production Architecture](#4-production-architecture)
5. [Cloud Provider Evaluation](#5-cloud-provider-evaluation)
6. [Kubernetes Configuration](#6-kubernetes-configuration)
7. [Database Infrastructure](#7-database-infrastructure)
8. [Ollama/AI Infrastructure](#8-ollamai-infrastructure)
9. [ERPNext Hosting](#9-erpnext-hosting)
10. [CDN & Edge](#10-cdn--edge)
11. [Monitoring Stack](#11-monitoring-stack)
12. [CI/CD Pipeline](#12-cicd-pipeline)
13. [Disaster Recovery](#13-disaster-recovery)
14. [Cost Estimates](#14-cost-estimates)
15. [Security Infrastructure](#15-security-infrastructure)

---

## 1. Hosting Strategy Overview

### 1.1 Philosophy

The infrastructure strategy follows a **progressive delivery** model — investing in operational maturity proportionally to actual adoption. We avoid premature optimization while ensuring the platform can scale from 10 teams to 500+ teams without architectural rewrites.

### 1.2 Phased Progression

| Phase | Scale | Infrastructure | Deployment Model | Availability Target |
|-------|-------|---------------|------------------|---------------------|
| **Phase 0 — Dev** | 1–3 devs, no external users | Local Docker Compose + single cloud VM for staging | Manual / simple CI runs | N/A |
| **Phase 1 — MVP/Launch** | 10–50 teams (alpha/beta) | Managed Kubernetes (GKE/EKS), RDS PostgreSQL, ElastiCache Redis, 1 GPU node | GitHub Actions → ArgoCD | 99.5% |
| **Phase 2 — Growth** | 50–200 teams | HA Kubernetes (multi-AZ), read replicas, GPU node pool (2 replicas), CDN for static | GitOps (ArgoCD) with progressive delivery | 99.9% |
| **Phase 3 — Scale** | 200–500+ teams | Multi-region active-active, dedicated DB cluster, HPA on all services, edge caching | Full GitOps + Flagger canary | 99.95% |

### 1.3 Infrastructure as Code Strategy

| Layer | Tool | Repository |
|-------|------|-----------|
| Cloud Resources | Terraform / OpenTofu | `infra/terraform/` |
| Kubernetes Manifests | Helm + Kustomize | `infra/k8s/` |
| Configuration | Sealed Secrets + External Secrets Operator | `infra/secrets/` |
| Policy | OPA/Gatekeeper | `infra/policies/` |

All infrastructure changes go through PR review. Production changes require approval from the infrastructure lead.

---

## 2. Development Environment

### 2.1 Local Docker Compose Setup

Every full stack locally via Docker Compose. The setup includes hot-reload for frontend and backend services.

```yaml
# docker-compose.dev.yml (abbreviated)
version: "3.9"
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: scrum_dev
      POSTGRES_USER: scrum
      POSTGRES_PASSWORD: scrum_dev_password
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    command: redis-server --appendonly yes --maxmemory 256mb

  backend:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports: ["8000:8000"]
    env_file: .env.local
    volumes:
      - ./backend:/app
    depends_on: [postgres, redis]

  websocket:
    build: ./backend
    command: python -m websocket_server
    ports: ["8001:8001"]
    env_file: .env.local
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    command: pnpm dev
    ports: ["3000:3000"]
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next

  worker:
    build: ./backend
    command: arq worker.settings.WorkerSettings
    env_file: .env.local
    volumes:
      - ./backend:/app
    depends_on: [redis]

  erpnext:
    image: frappe/erpnext:v15
    ports: ["8080:8080"]
    volumes:
      - erpnext_data:/home/frappe/frappe-bench/sites

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ollama_data:/root/.ollama
    # GPU access requires nvidia-container-toolkit
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

### 2.2 Developer Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 8 cores (Intel i7 / AMD Ryzen 7) | 12+ cores (Intel i9 / AMD Ryzen 9) | FastAPI + Next.js dev server + workers are CPU-heavy |
| **RAM** | 32 GB | 64 GB | Docker (8GB) + Next.js (4GB) + FastAPI (2GB) + Ollama (8-16GBNext (4GB) |
| **Storage** | 512 GB NVMe SSD | 1 TB NVMe SSD | Docker images + node_modules + model files (~20GB for Gemma 3 9B) |
| **GPU** | NVIDIA RTX 3060 (12GB VRAM) | NVIDIA RTX 4090 (24GB VRAM) or A5000 | Required for running Ollama locally with Gemma 3 9B |
| **OS** | Ubuntu 22.04 / macOS Sonoma / Windows 11+WSL2 | Ubuntu 24.04 LTS or macOS Sonoma | WSL2 requires nested virtualization enabled |

### 2.3 Local Development Workflow

```mermaid
graph LR
    DEV[Developer Machine] -->|docker compose up|
    DEV --> LOCAL_OLLAMA[Ollama<br>localhost:11434]
    DEV --> LOCAL_PG[PostgreSQL<br>localhost:5432]
    DEV --> LOCAL_REDIS[Redis<br>localhost:6379]
    DEV --> LOCAL_FE[Next.js<br>localhost:3000]
    DEV --> LOCAL_API[FastAPI<br>localhost:8000]
    DEV --> LOCAL_WS[WebSocket<br>localhost:8001]
    DEV --> LOCAL_WORKER[ARQ Worker]
    DEV --> LOCAL_ERP[ERPNext<br>localhost:8080]
    
    LOCAL_FE -->|REST| LOCAL_API
    LOCAL_FE -->|WSS| LOCAL_WS
    LOCAL_API --> LOCAL_PG
    LOCAL_API --> LOCAL_REDIS
    LOCAL_API --> LOCAL_OLLAMA
    LOCAL_API --> LOCAL_ERP
    LOCAL_WS --> LOCAL_REDIS
    LOCAL_WORKER --> LOCAL_REDIS
```

### 2.4 Environment Variables (Development)

```bash
# .env.local
DATABASE_URL=postgresql://scrum:scrum_dev_password@localhost:5432/scrum_dev
REDIS_URL=redis://localhost:6379/0
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:9b
ERPNEXT_URL=http://localhost:8080
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SENTRY_DSN=https://...
POSTHOG_API_KEY=phc_...
```

---

## 3. Staging Environment

### 3.1 Cloud Staging Setup

Staging mirrors production architecture at a smaller scale. It uses a dedicated Kubernetes cluster (or namespace in a shared cluster) with production-equivalent configuration to catch issues before production deployment.

| Resource | Configuration | Purpose |
|----------|--------------|---------|
| **Kubernetes** | 1 cluster, 3 nodes (2 vCPU, 8GB each) | Run all services |
| **PostgreSQL** | db.t3.medium, 50GB GP3 | Production-like DB instance |
| **Redis** | cache.t3.micro | Cache + pub/sub + task broker |
| **Ollama** | 1× g4dn.xlarge (spot) | AI inference testing |
| **ERPNext** | Docker on same namespace | Integration testing |

### 3.2 CI/CD Pipeline Targets

```mermaid
graph TB
    subgraph CI[CI Phase]
        PUSH[Git Push / PR] --> LINT[Lint & Type Check]
        LINT --> TEST[Unit & Integration Tests]
        TEST --> BUILD[Build Docker Images]
        BUILD --> SCAN[Trivy Security Scan]
        SCAN --> PUSH_IMG[Push to Registry]
    end
    
    subgraph CD[CD Phase]
        PUSH_IMG --> DEPLOY_STG[Deploy to Staging]
        DEPLOY_STG --> E2E[Playwright E2E Tests]
        E2E --> SMOKE[Smoke Tests]
        SMOKE -->{Manual Gate}
        MANUAL_OK[Approve] --> DEPLOY_PROD[Deploy to Production]
        MANUAL_REJ[Reject] --> NOTIFY[Notify Team]
    end
```

### 3.3 Staging Configuration Differences

| Parameter | Staging | Production |
|-----------|---------|------------|
| Replicas (frontend) | 1 | 3+ (HPA) |
| Replicas (backend) | 1 | 2+ (HPA) |
| Replicas (websocket) | 1 | 2 (sticky sessions) |
| Replicas (worker) | 1 | 2+ (HPA) |
| Database | db.t3.medium, no replica | db.r6g.large, 1 read replica |
| Redis | cache.t3.micro, standalone | cache.r6g.large, cluster |
| Ollama | g4dn.xlarge (spot) | g5.xlarge × 2 (on-demand + spot) |
| Stripe | Test mode | Live mode |
| Clerk | Development instance | Production instance |
| Log Level | DEBUG | WARN |

### 3.4 Data Seeding

Staging is seeded with anonymized production-like data weekly using a sanitized pg_dump:

```bash
# Weekly staging refresh
pg_dump -h $PROD_HOST -U scrum --no-owner \
  --exclude-table='audit_log' \
  --exclude-table='session' \
  scrum_prod | \
  psql -h $STG_HOST -U scrum scrum_staging

# Anonymize PII
psql -h $STG_HOST -U scrum scrum_staging -c "
  UPDATE users SET email = 'user' || id || '@example.com';
  UPDATE users SET name = 'Test User ' || id;
"
```

---

## 4. Production Architecture

### 4.1 Initial Production Setup (Phase 1 — MVP Launch)

```mermaid
graph TB
    subgraph Edge[Edge Layer]
        CF[CloudFlare<br>WAF + CDN + DNS]
        VERCEL[Vercel<br>Next.js Frontend]
    end
    
    subgraph K8s[Kubernetes Cluster - us-east-1]
        subgraph Public[Public Subnet]
            INGRESS[NGINX Ingress Controller<br>TLS Termination]
        end
        
        subgraph Private[Private Subnet]
            FE[Next.js SSR Pods<br>3 replicas]
            API[FastAPI Pods<br>2 replicas]
            WS[WebSocket Pods<br>2 replicas]
            WORKER[Worker Pods<br>2 replicas]
        end
        
        subnet Isolated[Isolated Subnet - Data]
            OLLAMA[Ollama GPU Node<br>1 replica]
        end
    end
    
    subgraph Managed[Managed Services]
        RDS[RDS PostgreSQL<br>Multi-AZ]
        REDIS[ElastiCache Redis<br>Cluster Mode]
    end
    
    subgraph External[External Services]
        CLERK[Clerk Auth]
        STRIPE[Stripe]
        ERP[ERPNext<br>Self-hosted]
    end
    
    CF --> VERCEL
    CF --> INGRESS
    VERCEL --> INGRESS
    INGRESS --> FE
    INGRESS --> API
    INGRESS --> WS
    
    API --> RDS
    API --> REDIS
    API --> OLLAMA
    API --> ERP
    
    WS --> REDIS
    WORKER --> REDIS
    WORKER --> RDS
```

### 4.2 Scaling Path

```
Phase 1 (MVP):  Single region, single AZ for, static replicas
       ↓
Phase 2:        Multi-AZ, read replicas, HPA enabled, CDN for assets
       ↓
Phase 3:        Multi-region active-passive, read replicas in DR region
       ↓
Phase 4:        Multi-region active-active, CockroachDB or PlanetScale 
                evaluation for global DB (if needed beyond 500 teams)
```

### 4.3 Service Resource Requirements (Production)

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit | Max Replicas |
|---------|------------|-----------|----------------|-------------|-------------|
| **Frontend (Next.js)** | 250m | 1000m | 256Mi | 1Gi | 10 |
| **Backend (FastAPI)** | 500m | 2000m | 512Mi | 2Gi | 20 |
| **WebSocket (Yjs)** | 500m | 2000m | 512Mi | 2Gi | 10 |
| **Worker (ARQ)** | 250m | 1000m | 256Mi | 1Gi | 10 |
| **Ollama** | 4000m | 8000m | 16Gi | 24Gi | 3 |
| **ERPNext** | 1000m | 4000m | 2Gi | 4Gi | 2 |

---

## 5. Cloud Provider Evaluation

### 5.1 Provider Comparison (India-Based Team)

| Criteria | **AWS** | **GCP** | **Azure** | **Hetzner** |
|----------|---------|---------|-----------|-------------|
| **Closest Region** | Mumbai (ap-south-1) | Mumbai (asia-south1) | Pune (centralindia) | Frankfurt (EU) |
| **Latency (from India)** | ~5ms | ~3ms | ~8ms | ~90ms |
| **GPU Instance Availability** | ✅ g5, p3, p4d | ✅ G2, A2, A3 | ✅ NC, NV series | ✅ CC600+ |
| **Kubernetes (Managed)** | EKS ($0.10/hr/cluster) | GKE (free control plane) | AKS (free control plane) | None (self-managed) |
| **PostgreSQL (Managed)** | RDS ($0.023/hr/GB) | Cloud SQL ($0.015/hr/GB) | Azure DB ($0.018/hr/GB) | None (self-hosted) |
| **Redis (Managed)** | ElastiCache | Memorystore | Azure Cache | None |
| **Pricing Competitiveness** | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★★ (but EU-only) |
| **Compliance (India)** | Meets RBI, IT Act | Meets RBI, IT Act | Meets RBI, IT Act | GDPR only |
| **CDN Integration** | CloudFront | Cloud CDN | Azure CDN | CloudFlare (recommended) |
| **Local Support (India)** | Strong (AWS India) | Strong (GCP India) | Strong (MS India) | Limited |
| **Startup Credits** | $100K (AWS Activate) | $20K (Google for Startups) | $150K (Microsoft) | $20K |

### 5.2 Cost Comparison — Production Environment (100 teams)

| Service | AWS (Monthly) | GCP (Monthly) | Azure (Monthly) | Hetzner (Monthly) |
|---------|--------------|---------------|-----------------|-------------------|
| **Kubernetes (3 nodes)** | $520 (m6i.xlarge) | $480 (e2-standard-4) | $560 (D4s_v3) | $180 (CC4300 × 3) |
| **PostgreSQL** | $180 (db.r6g.large) | $150 (db-n1-standard-4) | $190 (General Purpose) | $0 (self-hosted on nodes) |
| **Redis** | $80 (cache.r6g.large) | $65 (M3 standard) | $85 (C2) | $0 (self-hosted on nodes) |
| **GPU (Ollama)** | $400 (g5.xlarge spot) | $350 (g2-standard-4 spot) | $420 (NC4as_T4_v3) | $120 (CC600 GPU) |
| **Load Balancer** | $25 (ALB) | $18 (GLB) | $22 (LB) | $10 |
| **CDN** | $30 (CloudFront) | $25 (Cloud CDN) | $28 (Azure CDN) | $0 (CloudFlare free) |
| **Managed Services Premium** | +15% | +0% (included) | +10% | N/A |
| **Total Estimated** | **~$1,235** | **~$1,088** | **~$1,305** | **~$310** |

### 5.3 Recommendation

**Primary: GCP (Mumbai Region)**

Rationale:
- Lowest latency from India (3ms)
- Best GPU availability (G2 instances for Ollama)
- GKE is the most mature managed Kubernetes with free control plane
- Competitive pricing with sustained use discounts
- Strong India compliance posture

**Secondary consideration: AWS (Mumbai Region)** for teams requiring broader compliance certifications or specific AWS services.

**Hetzner for non-production workloads only** — accept ~90ms latency for dev/staging to save costs during early phases.

---

## 6. Kubernetes Configuration

### 6.1 Namespace Strategy

```yaml
# Namespace structure
apiVersion: v1
kind: Namespace
metadata:
  name: scrum-prod
  labels:
    environment: production
    team: platform
---
apiVersion: v1
kind: Namespace
metadata:
  name: scrum-staging
  labels:
    environment: staging
    team: platform
---
apiVersion: v1
kind: Namespace
metadata:
  name: scrum-monitoring
  labels:
    purpose: observability
---
apiVersion: v1
kind: Namespace
metadata:
  name: scrum-gpu
  labels:
    purpose: ai-inference
```

| Namespace | Purpose | Network Policy |
|-----------|---------|---------------|
| `scrum-prod` | Production services | Deny-all default, allow explicit |
| `scrum-staging` | Staging services | Deny-all default, allow explicit |
| `scrum-monitoring` | Prometheus, Grafana, Loki | Allow scraping from all namespaces |
| `scrum-gpu` | Ollama and AI workloads | Allow from API pods only |

### 6.2 Resource Limits

```yaml
# Resource Quota for production namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: scrum-prod-quota
  namespace: scrum-prod
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "50"

---
# Limit Range for default resource allocation
apiVersion: v1
kind: LimitRange
metadata:
  name: scrum-prod-limits
  namespace: scrum-prod
spec:
  limits:
    - default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 250m
        memory: 256Mi
      type: Container
    - max:
        cpu: "8"
        memory: 32Gi
      type: Pod
```

### 6.3 Horizontal Pod Autoscaling

```yaml
# Backend HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: scrum-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75
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
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

### 6.4 Node Pools

```yaml
# Node pool definitions (Terraform-style)
node_pools = {
  "general": {
    machine_type = "e2-standard-4"  # 4 vCPU, 16GB
    min_count    = 2
    max_count    = 6
    disk_size    = 100  # GB
    labels = {
      workload = "general"
    }
  },
  
  "compute-optimized": {
    machine_type = "c2-standard-8"  # 8 vCPU, 32GB
    min_count    = 0
    max_count    = 4
    disk_size    = 100
    labels = {
      workload = "compute"
    }
    taint = [{
      key    = "dedicated"
      value  = "compute"
      effect = "NO_SCHEDULE"
    }]
  },
  
  "gpu-pool": {
    machine_type = "g2-standard-4"  # 4 vCPU, 16GB + 1x L4 GPU
    min_count    = 0
    max_count    = 3
    disk_size    = 200
    gpu = {
      type  = "nvidia-l4"
      count = 1
    }
    labels = {
      workload = "ai"
    }
    taint = [{
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NO_SCHEDULE"
    }]
  },
  
  "database": {
    machine_type = "e2-highmem-4"  # 4 vCPU, 32GB
    min_count    = 1
    max_count    = 3
    disk_size    = 500
    labels = {
      workload = "database"
    }
    taint = [{
      key    = "dedicated"
      value  = "database"
      effect = "NO_SCHEDULE"
    }]
  }
}
```

### 6.5 Network Policies

```yaml
# Default deny all ingress/egress in production
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: scrum-prod
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress

---
# Allow backend to talk to database namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: scrum-prod
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              purpose: database
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - namespaceSelector:
            matchLabels:
              purpose: database
      ports:
        - protocol: TCP
          port: 6379
```

---

## 7. Database Infrastructure

### 7.1 PostgreSQL — Managed vs Self-Hosted

| Criteria | **Cloud SQL (GCP)** | **RDS (AWS)** | **Self-Hosted (Patroni)** |
|----------|-------------------|---------------|--------------------------|
| Management Overhead | Low | Low | High |
| Cost (db.r6g.large equiv) | ~$150/mo | ~$180/mo | ~$120/mo (compute only) |
| Extension Support | ✅ pgvector, pg_trgm | ✅ pgvector, pgtrgm | ✅ Any |
| Multi-AZ Failover | Automatic (30s) | Automatic (60s) | Manual config |
| Max Connections | 4,000 | 5,000 | Configurable |
| Read Replicas | Up to 10 | Up to 15 | Via Patroni |
| Backup Retention | 1–365 days | 1–35 days | Custom |
| Point-in-time Recovery | ✅ (7 days) | ✅ (7 days) | ✅ (WAL archiving) |

**Recommendation:** Managed (Cloud SQL) for staging + production. Self-hosted for development via Docker Compose to reduce costs.

### 7.2 PostgreSQL Configuration

```sql
-- Database setup script
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Connection pooling via PgBouncer (deployed alongside backend)
-- pgbouncer.ini:
-- pool_mode = transaction
-- max_client_conn = 1000
-- default_pool_size = 50
-- reserve_pool_size = 25

-- PostgreSQL tuning (db.r6g.large / 4 vCPU, 32GB RAM)
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET work_mem = '32MB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET wal_buffers = '128MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
```

### 7.3 pgvector Configuration

```sql
-- Index strategy for embeddings table
CREATE TABLE ceremony_embeddings (
    id BIGSERIAL PRIMARY KEY,
    ceremony_id UUID REFERENCES ceremonies(id),
    embedding vector(1024),  -- mxbai-embed-large output
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for approximate nearest neighbor search
CREATE INDEX ON ceremony_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- IVFFlat as fallback for large datasets (>100K rows)
-- CREATE INDEX ON ceremony_embeddings 
-- USING ivfflat (embedding vector_cosinelists = 1000);
```

### 7.4 Redis Configuration

| Setting | Development | Staging | Production |
|---------|------------|---------|------------|
| Version | 7.0 (Docker) | 7.2 (Managed) | 7.2 (Managed) |
| Mode | Standalone | Standalone | Cluster (3 shards, 1 replica) |
| Memory | 256MB | 1GB | 6GB |
| Persistence | AOF | AOF + RDB | AOF always |
| Eviction Policy | noeviction | allkeys-lru | allkeys-lru |
| Max Memory Policy | noeviction | volatile-lru | volatile-ttl |

### 7.5 Backup Strategy

```mermaid
graph LR
    subgraph Backup_Types
        WAL[WAL Archiving<br/>Continuous → GCS/S3]
        PGBASE[pg_basebackup<br/>Daily Full Backup]
        MANUAL[Manual Snapshots<br/>Before major deploys]
    end
    
    subgraph Retention
        WAL_R[WAL: 7 days<br/>PITR baseline]
        PGBASE_R[Full: 30 days<br/>Daily snapshots]
        MANUAL_R[Manual: 90 days<br/>On-demand]
    end
    
    subgraph Restore
        PITR[Point-in-Time Recovery<br/>WAL replay to any second]
        FULL[Full Restore<br/>pg_basebackup restore]
    end
    
    WAL --> WAL_R
    PGBASE --> PGBASE_R
    MANUAL --> MANUAL_R
    WAL_R --> PITR
    PGBASE_R --> FULL
```

| Backup Type | Frequency | Storage | Retention | RPO |
|------------|-----------|---------|-----------|-----|
| WAL Archiving | Continuous | GCS bucket | 7 days | < 1 minute |
| Full Backup | Daily (02:00 UTC) | GCS bucket | 30 days | 24 hours |
| Long-term Snapshots | Weekly | Cold storage | 90 days | 7 days |
| Pre-deploy Snapshots | On-demand | GCS bucket | 90 days | N/A |

---

## 8. Ollama/AI Infrastructure

### 8.1 GPU Instance Types Across Providers

| Provider | Instance | GPU | VRAM | On-Demand Price/hr | Spot Price/hr | Suitable |
|----------|----------|-----|------|-------------------|---------------|----------|
| **GCP** | g2-standard-4 | NVIDIA L4 | 24GB | $0.85 | $0.30 | ✅ Best price/perf |
| **GCP** | a2-highgpu-1g | NVIDIA A100 | 40GB | $3.60 | $1.20 | ✅ For batch processing |
| **AWS** | g5.xlarge | NVIDIA A10G | 24GB | $1.42 | $0.50 | ✅ Good alternative |
| **AWS** | p3.2xlarge | NVIDIA V100 | 16GB | $3.82 | $1.20 | ⚠️ Older gen |
| **Azure** | NC4as_T4_v3 | NVIDIA T4 | 16GB | $0.90 | $0.30 | ⚠️ Limited VRAM |
| **Hetzner** | CC600 | NVIDIA A100 | 40GB | €1.80 | N/A | ✅ If EU-based |

### 8.2 Spot/Preemptible Instance Strategy

```yaml
# GPU node pool with spot priority
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: scrum-gpu
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ollama
  template:
    spec:
      containers:
        - name: ollama
          image: ollama/ollama:latest
          resources:
            limits:
              nvidia.com/gpu: 1
              memory: "16Gi"
              cpu: "4"
            requests:
              memory: "8Gi"
              cpu: "2"
          ports:
            - containerPort: 11434
          env:
            - name: OLLAMA_MODEL
              value: "gemma3:9b"
      # Primary: spot instances (70% cost savings)
      nodeSelector:
        cloud.google.com/gke-spot: "true"
      # Fallback: on-demand if spot unavailable
      tolerations:
        - key: "spot"
          operator: "Equal"
          value: "true"
          effect: "NoSchedule"
```

**Cost Optimization Strategy:**
- **Primary replica:** Spot/preemptible instances (70% savings)
- **Fallback replica:** On-demand (ensures availability during spot interruptions)
- **Model preloading:** Keep model loaded in memory; use `ollama pull` on startup with health check
- **Request queue:** If all GPU replicas are busy, queue requests in Redis with exponential backoff

### 8.3 Multi-Replica Strategy

```mermaid
graph TB
    subgraph Load_B INGRESS[Ingress / API Gateway] --> LB[Load Balancer<br/>Round-robin + queue depth]
        LB --> GPU1[Ollama Replica 1<br/>Spot - g2-standard-4]
        LB --> GPU2[Ollama Replica 2<br/>On-Demand - g2-standard-4]
        LB --> GPU3[Ollama Replica 3<br/>Spot - g2-standard-4]
    end
    
    subgraph Queue
        API[Backend API] --> REDIS_QUEUE[Redis Queue<br/>AI Jobs]
        REDIS_QUEUE --> GPU1
        REDIS_QUEUE --> GPU2
        REDIS_QUEUE --> GPU3
    end
    
    subgraph Health
        GPU1 --> HEALTH[/api/tags Health Check]
        GPU2 --> HEALTH
        GPU3 --> HEALTH
        HEALTH -->
```

### 8.4 Model Loading Optimization

```bash
#!/bin/bash
# ollama-entrypoint.sh - Optimized model loading

# Pre-pull model on container start
ollama pull gemma3:9b &
ollama pull mxbai-embed-large &
wait

# Keep)
curl -s http://localhost:11434/api/generate -d '": "gemma3:9b",
  "prompt": "",
  "keep_alive": -1
}' > /dev/null &

# Health check endpoint
while true; do
  if curl -s http://localhost:11434/api/tags | grep -q "gemma3:9b"; then
    echo "Model loaded and ready"
    exit 0
  fi
  sleep 5
done
```

** Implementation |
|-----------|--------|---------------|
| Model preloading | Elim init |
| ` models (Q4_K_M) | 50% VRAM reduction, 10% speed loss | `ollama pull gemma3:9 Streaming responses | Better UX | Use `/api/generate?stream=true` |

---

## 9. ERPNext Hosting

### 9.1 Deployment Options Comparison

| Criteria | **Docker (Self-Hosted)** | **Frappe Cloud** | **Managed (Cloud VM)** |
|----------|------------------------|------------------|----------------------|
| Cost | ~$80/mo (compute) | $500/mo (10 users) | ~$120/mo (dedicated VM) |
| Control | Full | Limited | Full |
| Updates | Manual | Automatic | Manual |
| Customization | Full | Limited (managed) | Full |
| Scaling | Manual | Automatic | Manual |
| Backup Responsibility | Self | Frappe | Self |
| Data Residency | Your choice | Frappe's choice | Your choice |

**Recommendation:** Docker self-hosted alongside the platform for maximum control and cost efficiency.

### 9.2 Resource Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **ERPNext App** | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | Frappe framework is memory-hungry |
| **MariaDB** | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | Separate from PostgreSQL |
| **Redis (ERPNext)** | 512MB RAM | 1GB RAM | Cache + queue |
| **Worker (ERPNext)** | 2 vCPU, 2GB RAM | 2 vCPU, 4GB RAM | Background jobs |
| **Storage** | 50GB SSD | 100GB SSD | Documents, attachments, backups |
| **Total** | 4 vCPU, 8GB RAM | 8 vCPU, 16GB RAM | For up to 50 concurrent users |

### 9.3 Database Sizing Estimate

| Data Category | Growth Rate | 1-Year Estimate (100 teams) |
|--------------|-------------|---------------------------|
| CRM (leads, contacts, deals) | ~500 records/month | ~6,000 records, ~500MB |
| Finance (invoices, GL entries) | ~2,000 entries/month | ~24,000 entries, ~2GB |
| HR (employees, leave) | ~100 records/month | ~1,200 records, ~100MB |
| Attachments (scanned docs) | ~50 files/month | ~600 files, ~5GB |
| **Total** | | **~7.6GB** |

### 9.4 ERPNext Docker Compose (Production)

```yaml
# erpnext-compose.yml
version: "3.8"
services:
  mariadb:
    image: mariadb:10.11
    environment:
      MYSQL_ROOT_PASSWORD: ${ERPNEXT_DB_PASSWORD}
      MYSQL_DATABASE: site1
    volumes:
      - erpnext_db:/var/lib/mysql
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --innodb-buffer-pool-size=2G
      --max-connections=200

  redis-cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

  redis-queue:
    image: redis:7-alpine

  redis-socketio:
    image: redis:7-alpine

  backend:
    image: frappe/erpnext:v15
    environment:
      DB_HOST: mariadb
      REDIS_CACHE: redis-cache
      REDIS_QUEUE: redis-queue
      REDIS_SOCKETIO: redis-socketio
    volumes:
      - erpnext_sites:/home/frappe/frappe-bench/sites

  frontend:
    image: frappe/erpnext:v15
    command: nginx
    ports:
      - "8080:8080"

  worker-default:
    image: frappe/erpnext:v15
    command: bench worker
    deploy:
      replicas: 2

  scheduler:
    image: frappe/erpnext:v15
    command: bench scheduler
```

---

## 10. CDN & Edge

### 10.1 Vercel for Next.js Frontend

The Next.js frontend is deployed to **Vercel** for optimal performance:

| Feature | Vercel Benefit |
|---------|---------------|
| Edge Network | 70+ PoPs globally, automatic edge caching |
| ISR | Incremental Static Regeneration for dashboard pages |
| Image Optimization | Automatic next/image optimization |
| Preview Deployments | Every PR gets a unique preview URL |
| Analytics | Built-in web vitals monitoring |
| Serverless Functions | API routes for webhooks (Stripe, Clerk) |

**Vercel Configuration:**
```json
// vercel.json
{
  "framework": "nextjs",
  "regions": ["bom1", "iad1"],  // Mumbai + US East
  "crons": [],
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.scrumplatform.com/:path*" }
  ],
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

### 10.2 CloudFlare for API

| Service | Configuration |
|---------|--------------|
| **DNS** | Primary DNS provider, CNAME flattening for root domain |
| **WAF** | Managed rulesets: OWASP, CloudFlare Free Managed Rules |
| **DDoS** | Always-on L3/L4 + L7 rate limiting |
| **Rate Limiting** | 100 req/min per IP for API, 1000 req/min per user |
| **SSL/TLS** | Full (strict), minimum TLS 1.2, automatic cert rotation |
| **Caching** | API responses not cached (dynamic); static assets cached 1 year |
| **Workers** | Edge middleware for geo-routing, A/B testing |

### 10.3 Static Asset Strategy

```mermaid
graph LR
    subgraph Origin
        S3[GCS/S3 Bucket<br/>Static Assets]
    end
    
    subgraph CDN
        CF[CloudFlare CDN<br/>Global Edge Cache]
        VERCEL_CDN[Vercel Edge<br/>Next.js Static]
    end
    
    subgraph Client
        BROWSER[Browser]
    end
    
    S3 --> CF
    VERCEL_CDN --> BROWSER
    CF --> BROWSER
    
    style S3 fill:#f96,stroke:#333
    style CF fill:#f96,stroke:#333
```

| Asset Type | Storage | CDN | Cache Duration |
|-----------|---------|-----|---------------|
| Next.js static chunks | Vercel | Vercel Edge | 1 year (immutable) |
| User uploads | GCS bucket | CloudFlare | 30 days |
| Ceremony exports (PDF) | GCS bucket | CloudFlare | 1 hour (signed URLs) |
| Favicon, manifest | Vercel | Vercel Edge | 1 year |

---

## 11. Monitoring Stack

### 11.1 Monitoring Architecture

```mermaid
graph TB
    subgraph Application
        FE[Next.js] -->|Sentry SDK| SENTRY[Sentry<br/>Error Tracking]
        API[FastAPI] -->|Sentry SDK| SENTRY
        API -->|PostHog Events| POSTHOG[PostHog<br/>Product Analytics]
        WS[WebSocket] -->|Sentry SDK| SENTRY
    end
    
    subgraph Infrastructure
        K8s[Kubernetes] -->|Prometheus| PROM[Prometheus<br/>Metrics]
        K8s -->|Logs| LOKI[Loki<br/>Log Aggregation]
        DB[PostgreSQL] -->|postgres_exporter| PROM
        REDIS[Redis] -->|redis_exporter| PROM
        GPU[Ollama] -->|nvidia_s| PROM
    end
    
    subgraph Visualization
        PROM --> GRAFANA[Grafana<br/>Dashboards]
        LOKI --> GRAFANA
        SENTRY --> GRAFANA
    end
    
    subgraph Alerting
        PROM --> ALERT[Alertmanager]
        SENTRY --> ALERT
        ALERT --> PAGER[PagerDuty<br/>On-Call]
        ALERT --> SLACK[#infra-alerts<br/>Slack]
    end
```

### 11.2 Tool Configuration

| Tool | Purpose | Plan/Cost | Integration |
|------|---------|-----------|-------------|
| **Sentry** | Error tracking, performance monitoring | Team plan ($26/mo) | SDK in Next.js, FastAPI, WebSocket |
| **PostHog** | Product analytics, session replay | 1M events/mo free | `posthog-js` in frontend, `posthog-python` in backend |
| **Prometheus** | Infrastructure metrics | Self-hosted (free) | ServiceMonitor CRDs |
| **Grafana** | Dashboards, visualization | Self-hosted (free) | Connected to Prometheus, Loki, Sentry |
| **Loki** | Log aggregation | Self-hosted (free) | Promtail on each node |
| **PagerDuty** | Incident management, on-call | Team plan ($19/user/mo) | Alertmanager webhook |
| **Opsgenie** | Alternative to PagerDuty | Free tier available | Alertmanager webhook |

### 11.3 Key Dashboards

| Dashboard | Data Source | Key Metrics |
|-----------|------------|-------------|
| **API Health** | Prometheus | Request rate, P95 latency, error rate, saturation |
| **Database** | postgres_exporter | Connections, replication lag, cache hit ratio, deadlocks |
| **Redis** | redis_exporter | Memory usage, hit rate, connected clients, evictions |
| **GPU/Ollama** | nvidia_smi_exporter | GPU utilization, VRAM usage, inference queue depth |
| **WebSocket** | Custom metrics | Active connections, message rate, reconnection rate |
| **Business** | PostHog | DAU/MAU, ceremony completion rate, AI feature adoption |
| **Cost** | Cloud provider API | Daily spend by service, GPU hours, egress costs |

### 11.4 Alert Rules

```yaml
# Critical alerts → PagerDuty
groups:
  - name: critical
    rules:
      - alert: APIHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API error rate > 5%"
          
      - alert: DatabaseDown
        expr: pg_up == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is unreachable"
          
      - alert: OllamaDown
        expr: ollama_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Ollama AI service is down"

  - name: warning
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency > 500ms"
          
      - alert: GPUMemoryHigh
        expr: nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU VRAM usage > 90%"
```

---

## 12. CI/CD Pipeline

### 12.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build, Test, Deploy

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: gcr.io
  PROJECT_ID: scrum-platform

jobs:
  # ─── LINT & TEST ───────────────────────────────────
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    
    steps:
      - uses: actions/checkout@v4
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov=app --cov-report=xml
      - name: Run frontend tests
        run: |
          cd frontend
          pnpm install
          pnpm test --coverage
      - name: Run E2E tests
        run: |
          cd frontend
          pnpm playwright test

  # ─── BUILD & PUSH ─────────────────────────────────
  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [frontend, backend, websocket, worker]
    
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./${{ matrix.service }}
          push: true
          tags: |
            $REGISTRY/$PROJECT_ID/${{ matrix.service }}:${{ github.sha }}
            $REGISTRY/$PROJECT_ID/${{ matrix.service }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ─── SECURITY SCAN ────────────────────────────────
  security:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.PROJECT_ID }}/backend:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  # ─── DEPLOY TO STAGING ────────────────────────────
  deploy-staging:
    needs: [build, security]
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - name: Deploy to GKE staging
        run: |
          gcloud container clusters get-credentials staging --zone asia-south1-a
          kubectl set image deployment/backend \
            backend=$REGISTRY/$PROJECT_ID/backend:${{ github.sha }} \
            --namespace=scrum-staging
          kubectl rollout status deployment/backend -n scrum-staging --timeout=300s

  # ─── DEPLOY TO PRODUCTION ─────────────────────────
  deploy-production:
    needs: [build, security]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - name: Deploy to GKE production (Canary)
        run: |
          gcloud container clusters get-credentials production --zone asia-south1-a
          # Flagger handles canary progression
          kubectl apply -f k8s/production/
          kubectl wait --for=condition=promoted canary/backend -n scrum-prod --timeout=600s
```

### 12.2 Deployment Strategy — Canary with Flagger

```mermaid
graph LR
    subgraph Canary_Flow
        NEW[New Version<br/>Deployed] --> CANARY[Canary Pod<br/>5% Traffic]
        CANARY --> METRICS{Metrics Check<br/>Error Rate < 1%<br/>Latency < 200ms}
        METRICS -->|PASS| RAMP1[20% Traffic<br/>2 min]
        RAMP1 --> METRICS
        METRICS -->|PASS| RAMP2[50% Traffic<br/>2 min]
        RAMP2 --> METRICS
        METRICS -->|PASS| PROMOTE[100% Traffic<br/>Promote]
        METRICS -->|FAIL| ROLLBACK[Rollback<br/>to Previous]
    end
```

### 12.3 Rollback Procedures

| Scenario | Detection | Automated Response | Manual Intervention |
|----------|-----------|-------------------|-------------------|
| Canary fails metrics | Flagger (Prometheus) | Auto-rollback within 30s | Review logs, fix, redeploy |
| Post-deploy error spike | Sentry alert | Auto-rollback via ArgoCD | Incident response |
| Database migration failure | Migration job fails | Block deployment | Manual DB rollback |
| Complete region outage | Health check failure | Failover to DR region | Activate DR runbook |

```bash
# Manual rollback commands
# 1. Immediate rollback (last known good)
kubectl rollout undo deployment/backend -n scrum-prod

# 2. Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=42 -n scrum-prod

# 3. Rollback database migration
almbic downgrade -1

# 4. Verify rollback
kubectl rollout status deployment/backend -n scrum-prod
```

---

## 13. Disaster Recovery

### 13.1 RPO/RTO Targets

| Component | RPO (Recovery Point Objective) | RTO (Recovery Time Objective) | Strategy |
|-----------|-------------------------------|-------------------------------|----------|
| **PostgreSQL** | < 1 minute | < 5 minutes | WAL archiving + cross-region replica |
| **Redis** | N/A (ephemeral) | < 2 minutes | Rebuild from PostgreSQL state |
| **User uploads (GCS)** | 0 (synchronous) | < 1 minute | Multi-region bucket replication |
| **Ollama models** | N/A | < 10 minutes | Re-pull from registry on startup |
| **ERPNext** | < 1 hour | < 15 minutes | Hourly backups + cross-region copy |
| **Configuration** | 0 | < 5 minutes | GitOps (ArgoCD from GitHub) |

### 13.2 Backup Automation

```mermaid
graph TB
    subgraph Primary_Region [us-east-1 / Mumbai]
        PG[(PostgreSQL<br/>Primary)] -->|WAL Stream| WAL_GCS[GCS WAL Archive<br/>Primary Region]
        PG -->|Daily Backup| FULL_GCS[GCS Full Backup<br/>Primary Region]
        GCS_OBJ[GCS Objects<br/>User Uploads] -->|Dual-region| GCS_DUAL[GCS Multi-region]
    end
    
    subgraph DR_Region [us-west-1 / Hyderabad]
        WAL_GCS_DR[GCS WAL Archive<br/>DR Region]
        FULL_GCS_DR[GCS Full Backup<br/>DR Region]
        PG_DR[(PostgreSQL<br/>Read Replica)]
    end
    
    subgraph DR_Infrastructure
        K8S_DR[Kubernetes<br/>DR Cluster]
        K8S_DR -->|Reads from| PG_DR
    end
    
    WAL_GCS -->|Cross-region replication| WAL_GCS_DR
    FULL_GCS -->|Cross-region copy| FULL_GCS_DR
    PG_DR -->|Replicates| WAL_GCS_DR
```

### 13.3 DR Runbook

```markdown
# DR Runbook: Activating Disaster Recovery

## Trigger Conditions
- Primary region unavailable for > 5 minutes
- Data corruption detected in primary database
- Security incident requiring region isolation

## Activation Steps

### 1. Declare Incident (0–2 min)
- Page on-call engineer via PagerDuty
- Open #incident channel in Slack
- Notify engineering lead

### 2. Promote DR Region (2–5 min)
```bash
# Promote PostgreSQL read replica to primary
gcloud sql instances promote-replica scrum-db-dr \
  --project=scrum-platform

# Update application to point to DR database
kubectl patch configmap app-config \
  --patch '{"data":{"DATABASE_URL":"postgresql://...@dr-host:5432/scrum"}}' \
  -n scrum-prod

# Restart all pods to pick up new config
kubectl rollout restart deployment -n scrum-prod
```

### 3. Verify Services (5–10 min)
- Check API health: `curl https://api.scrumplatform.com/health`
- Verify database connectivity
- Confirm Ollama models loaded
- Test WebSocket connections

### 4. Update DNS (10–15 min)
- Point api.scrumplatform.com to DR load balancer
- Verify SSL certificates are valid

### 5. Post-Incident
- Document timeline and root cause
- Plan failback to primary region
- Update runbook with lessons learned
```

### 13.4 DR Testing Schedule

| Test Type | Frequency | Scope | Duration |
|-----------|-----------|-------|----------|
| Backup restore test | Monthly | Restore to staging | 2 hours |
| Failover simulation | Quarterly | Full DR activation | 4 hours |
| Game day | Bi-annual | Full DR with team | 8 hours |
| Tabletop exercise | Quarterly | Walkthrough only | 1 hour |

---

## 14. Cost Estimates

### 14.1 Monthly Infrastructure Cost by Phase

| Category | Dev (1 team) | Staging (10 teams) | Production (100 teams) | Production (500 teams) |
|----------|-------------|-------------------|----------------------|----------------------|
| **Kubernetes** | $0 (local) | $150 | $500 | $1,500 |
| **PostgreSQL** | $0 (local) | $50 | $200 | $800 |
| **Redis** | $0 (local) | $20 | $100 | $400 |
| **GPU (Ollama)** | $0 (local) | $100 (spot) | $400 (2 spot + 1 OD) | $1,500 |
| **ERPNext** | $0 (local) | $30 | $120 | $400 |
| **CDN & DNS** | $0 | $10 | $50 | $200 |
| **Monitoring** | $0 | $25 | $100 | $300 |
| **Vercel** | $0 (free) | $20 (Pro) | $20 (Pro) | $20 (Pro) |
| **CloudFlare** | $0 (free) | $20 (Pro) | $200 (Business) | $200 (Business) |
| **Secrets/SSL** | $0 | $10 | $50 | $100 |
| **External Services** | $0 | $50 | $300 | $800 |
| **Contingency (15%)** | $0 | $70 | $290 | $870 |
| **TOTAL** | **$0** | **$555** | **$2,330** | **$7,090** |

### 14.2 External Service Costs (Monthly)

| Service | Tier | Paid Tier | 100 Teams | 500 Teams |
|---------|-----------|-----------|-----------|-----------|
| **Clerk** | 10K MAU | $0.02/MAU | $50 (2.5K users) | $250 (12.5K users) |
| **Stripe** | N/A | 2.9% + $0.30/txn | Variable | Variable |
| **Sentry** | 5K errors | $26/mo (Team) | $26 | $80 |
| **PostHog** | 1M events | $0.00031/event | $30 | $150 |
| **PagerDuty** | N/A | $19/user/mo | $57 (3 users) | $95 (5 users) |
| **GitHub Actions** | 2K min/mo | $0.008/min | $30 | $100 |
| **Vercel** | Free (hobby) | $20/mo (Pro) | $20 | $20 |

### 14.3 Cost Optimization Strategies

| Strategy | Savings | Implementation |
|----------|---------|---------------|
| Spot/preemptible for GPU | 60-70% on GPU costs | Node pool with spot priority |
| Sustained use discounts (GCP) | 20-30% on compute | Automatic for running >25% of month |
| Committed use (1-year) | 30-40% on stable workloads | For baseline Kubernetes nodes |
| Autoscaling to zero (GPU) | 50-80% at low usage | Scale GPU pool to 0 when idle >15 min |
| Reserved instances (DB) | 25-30% on RDS/Cloud SQL | 1-year reservation for production DB |
| CloudFlare over CloudFront | 50-80% on CDN egress | CloudFlare free tier for most workloads |

### 14.4 Cost Per Team Analysis

| Scale | Monthly Cost | Cost Per Team/Month | Cost Per Team/Year |
|-------|-------------|--------------------|--------------------|
| 10 teams | $555 | $55.50 | $666 |
| 100 teams | $2,330 | $23.30 | $280 |
| 500 teams | $7,090 | $14.18 | $170 |

**Target:** Infrastructure cost should remain below 15% of revenue per team ($35/team/mo × 15% = $5.25/team/mo). At 500 teams, we achieve $14.18/team/mo — within acceptable range. At scale beyond 500 teams, dedicated infrastructure and multi-region will be required.

---

## 15. Security Infrastructure

### 15.1 Network Architecture

```mermaid
graph TB
    subgraph Internet
        USERS[Users]
    end
    
    subgraph Edge_Security
        CF[CloudFlare<br/>WAF + DDoS + Bot Management]
    end
    
    subgraph VPC[Virtual Private Cloud - Mumbai]
        subgraph Public_Subnet
            LB[Cloud Load Balancer<br/>TLS 1.3 Termination]
            BASTION[Bastion Host<br/>SSH Access Only]
        end
        
        subgraph Private_Subnet
            INGRESS[NGINX Ingress<br/>Rate Limiting]
            FE[Frontend Pods]
            API[Backend Pods]
            WS[WebSocket Pods]
            WORKER[Worker Pods]
        end
        
        subgraph Data_Subnet
            PG[(PostgreSQL<br/>Private IP Only)]
            REDIS[(Redis<br/>Private IP Only)]
        end
        
        subgraph GPU_Subnet
            OLLAMA[Ollama GPU Node<br/>No Internet Egress]
        end
    end
    
    USERS --> CF
    CF --> LB
    LB --> INGRESS
    INGRESS --> FE
    INGRESS --> API
    INGRESS --> WS
    API --> PG
    API --> REDIS
    API --> OLLAMA
    WORKER --> PG
    WORKER --> REDIS
    BASTION -->|SSH Tunnel| API
```

### 15.2 Security Groups / Firewall Rules

| Source | Destination | Port | Protocol | Purpose |
|--------|------------|------|----------|---------|
| CloudFlare IPs | Load Balancer | 443 | HTTPS | User traffic |
| Load Balancer | Ingress | 80 | HTTP | Internal routing |
| Ingress | Backend pods | 8000 | HTTP | API requests |
| Ingress | WebSocket pods | 8001 | HTTP | WebSocket upgrade |
| Backend pods | PostgreSQL | 5432 | TCP | Database queries |
| Backend pods | Redis | 6379 | TCP | Cache/pub-sub |
| Backend pods | Ollama | 11434 | HTTP | AI inference |
| Bastion | All private | 22 | SSH | Admin access (key only) |
| Monitoring | All pods | Various | TCP | Metrics scraping |
| **Any** | **Any** | **Any** | **Any** | **DENY ALL** |

### 15.3 Secrets Management

| Approach | Tool | Use Case |
|----------|------|----------|
| **Development** | `.env.local` (gitignored) | Local development |
| **Staging/Production** | External Secrets Operator + GCP Secret Manager | Kubernetes secrets |
| **CI/CD** | GitHub Actions Secrets | Build/deploy secrets |
| **Infrastructure** | Terraform variables + encrypted state | Cloud resources |
| **Database credentials** | Automatic rotation via Cloud SQL | DB passwords |

```yaml
# External Secrets Operator configuration
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: scrum-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: gcp-secret-store
    kind: ClusterSecretStore
  target:
    name: database-secret
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: projects/scrum-platform/secrets/prod-database-url/versions/latest
    - secretKey: REDIS_URL
      remoteRef:
        key: projects/scrum-platform/secrets/prod-redis-url/versions/latest
```

### 15.4 SSL/TLS Configuration

| Layer | Certificate | Provider | Renewal |
|-------|------------|----------|---------|
| CloudFlare → User | Universal SSL (auto) | CloudFlare | Automatic (90-day rotation) |
| Load Balancer → Ingress | Google-managed or Let's Encrypt | GCP / cert-manager | Automatic (60-day rotation) |
| Internal (pod-to-pod) | mTLS via Istio (optional) | cert-manager | Automatic (24-hour rotation) |
| Database | SSL enforced | Cloud SQL / RDS | Managed |
| API → External services | System CA bundle | OS-level | Managed |

### 15.5 WAF & DDoS Protection

| Threat | Protection | Configuration |
|--------|-----------|---------------|
| **SQL Injection** | CloudFlare WAF (OWASP ruleset) | Block on match |
| **XSS** | CloudFlare WAF + CSP headers | Block on match |
| **DDoS L3/L4** | CloudFlare Always-On | Automatic mitigation |
| **DDoS L7** | Rate limiting rules | 100 req/min/IP, 1000 req/min/user |
| **Bot abuse** | CloudFlare Bot Management | Challenge suspicious bots |
| **Credential stuffing** | Clerk (built-in brute force protection) | Enabled by default |
| **API abuse** | Custom WAF rules | Geo-blocking, user-agent filtering |

### 15.6 Security Compliance Checklist

| Control | Implementation | Status |
|---------|---------------|--------|
| Encryption at rest | Cloud SQL encryption (AES-256), GCS bucket encryption | ✅ |
| Encryption in transit | TLS 1.3 everywhere, mTLS for internal (optional) | ✅ |
| Access control | RBAC (K8s), IAM (Cloud), least privilege | ✅ |
| Audit logging | Cloud Audit Logs, Kubernetes audit logs | ✅ |
| Vulnerability scanning | Trivy in CI, CloudFlare security scan | ✅ |
| Dependency scanning | Dependabot, Snyk | ✅ |
| Secret rotation | 90-day automatic rotation for DB creds | ✅ |
| Network segmentation | VPC with private subnets, security groups | ✅ |
| Incident response | PagerDuty on-call, DR runbook | ✅ |
| Data retention | 90-day log retention, 7-day WAL, 30-day backups | ✅ |
| SOC 2 readiness | Audit logging, access controls, change management | � In progress |

---

## Appendix A: Infrastructure Decision Log

| Decision | Decision | Rationale | Date |
|----------|----------|-----------|------|
| Cloud Provider | GCP (Mumbai) | Best latency, GPU availability, pricing for India team | June 2026 |
| Container Orchestration | GKE | Most mature managed K8s, free control plane | June 2026 |
| Database | Cloud SQL PostgreSQL | Managed backups, pgvector support, low ops overhead | June 2026 |
| AI Inference | Self-hosted Ollama | Cost control, data privacy, no egress for AI | June 2026 |
| Frontend Hosting | Vercel | Optimal Next.js performance, preview deployments | June 2026 |
| CDN/WAF | CloudFlare | Cost-effective, strong DDoS protection | June 2026 |
| Monitoring | Prometheus + Grafana + Sentry + PostHog | Best-in-class open source + managed where appropriate | June 2026 |
| CI/CD | GitHub Actions + ArgoCD | Familiar tooling, GitOps for K8s | June 2026 |
| Secrets | External Secrets Operator + GCP Secret Manager | Native K8s integration, automatic rotation | June 2026 |

## Appendix B: Contact & Escalation

| Role | Contact | Escalation |
|------|---------|-----------|
| Infrastructure Lead | infra@scrumplatform.com | PagerDuty primary |
| Security Lead | security@scrumplatform.com | security@ + infra@ |
| On-Call Engineer | PagerDuty rotation | Escalate to Lead after 15 min |
| Cloud Support | GCP Support (Business) | Critical: +1-855-814-6675 |

---

**Document Status:** Draft — Pending review by Infrastructure and Security teams.  
**Next Review Date:** July 2026
