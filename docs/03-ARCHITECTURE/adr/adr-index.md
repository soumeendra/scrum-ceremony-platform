# Architecture Decision Records (ADRs)

**Document ID:** SCP-DOC-010  
**Date:** 2026-06-26  

---

## ADR-001: Use Yjs for Real-Time Board Collaboration

**Status:** Accepted  
**Context:** We need real-time collaborative editing on the ceremony board. Multiple participants add/move/group notes simultaneously.  
**Decision:** Use Yjs CRDT library over Automerge or custom OT.  
**Rationale:** Yjs has production proof (Notion, Jupyter), mature React bindings (yjs-react), efficient binary encoding, and WebSocket provider built-in. Automerge is slower for large documents. Custom OT is high-risk.  
**Consequences:** Locks us into Yjs document model; Yjs updates are opaque (can't query "who changed what" without Yjs event listeners); team must learn CRDT mental model.

---

## ADR-002: Use XState for Ceremony State Machine

**Status:** Accepted  
**Context:** Ceremonies have strict phase transitions (collect→cluster→vote→decide→action). Invalid transitions must be impossible.  
**Decision:** Model ceremony FSM in XState with formal state definitions.  
**Rationale:** XState provides visualizable, testable state machines. Invalid transitions are structurally impossible (not just runtime-checked). State can be serialized and restored. Alternative (ad-hoc if/else) leads to state bugs.  
**Consequences:** XState adds bundle size (~20KB); team must learn state machine thinking; ceremony types need separate machine definitions.

---

## ADR-003: ERPNext as Back-Office System of Record

**Status:** Accepted  
**Context:** We need CRM, invoicing, and operations backend. Build vs buy vs open-source.  
**Decision:** Use self-hosted ERPNext for CRM/finance/ops. NOT for product runtime.  
**Rationale:** ERPNext is free, open-source, Docker-deployable, has REST API, and covers CRM + sales + accounting + custom doctypes. Avoids building back-office from scratch. ERPNext is NOT suitable for real-time collaboration or ceremony logic (Frappe framework is request/response).  
**Consequences:** Two-database architecture (PostgreSQL + MariaDB); integration service needed; ERPNext maintenance burden; Frappe framework learning curve.

---

## ADR-004: Local Gemma 3 9B via Ollama for AI

**Status:** Accepted  
**Context:** AI features (clustering, summaries, actions, sentiment) needed. Cloud vs local inference.  
**Decision:** Use Gemma 3 9B (instruct, Q4_K_M) via Ollama for local inference, with cloud LLM fallback.  
**Rationale:** Zero per-token cost at scale; data never leaves infrastructure (enterprise requirement); Ollama provides simple REST API; Gemma 3 9B is adequate for summarization and structured extraction. Weak for complex reasoning (adaptive facilitation).  
**Consequences:** Requires GPU hardware (RTX 4060 Ti 16GB minimum); AI quality lower than GPT-4o for complex tasks; need fallback path for Ollama downtime; embedding model (mxbai-embed-large) separate from generative model.

---

## ADR-005: Clerk for Authentication (over Auth0)

**Status:** Accepted  
**Context:** Need auth provider with SSO, SCIM roadmap, and reasonable pricing.  
**Decision:** Use Clerk over Auth0.  
**Rationale:** Clerk has better DX for Next.js, free tier supports 10K MAU, SAML SSO available on Pro ($25/mo) vs Auth0 Enterprise ($240/mo). Built-in user management UI reduces our scope.  
**Consequences:** Vendor lock-in for auth; SAML on paid tier only; SCIM requires Enterprise; if Clerk has outage, all login fails (mitigate with session caching).

---

## ADR-006: Per-Team Pricing Model

**Status:** Accepted  
**Context:** How to price: per-user, per-team, or flat org?  
**Decision:** Per-team pricing with unlimited participants per team.  
**Rationale:** Scrum teams are the natural unit (not individual users). TeamRetro uses per-team pricing successfully. Per-user pricing penalizes team participation (Parabol's weakness). Unlimited participants encourages broad engagement within a team.  
**Consequences:** Revenue scales with team count, not user count; need team-size abuse mitigation; enterprise tier may need per-seat component for admin seats.

---

## ADR-007: pgvector for Embedding Storage

**Status:** Accepted  
**Context:** Need vector storage for AI clustering and similarity search.  
**Decision:** Use pgvector extension in PostgreSQL over Pinecone/Weaviate.  
**Rationale:** Same database as operational data — no new infrastructure. pgvector supports HNSW indexing, cosine similarity, and is well-supported. Sufficient for our scale (500K embeddings Year 1).  
**Consequences:** pgvector slower than Pinecone at >1M vectors; ties AI features to PostgreSQL availability; need to tune HNSW index parameters (ef_construction, m).

---

## ADR-008: FastAPI for Backend (over Node.js/Go)

**Status:** Accepted  
**Context:** Backend API framework choice.  
**Decision:** Python FastAPI over Node.js Express or Go.  
**Rationale:** Python ecosystem for AI (langchain, sentence-transformers if needed later); FastAPI is async, fast, with OpenAPI auto-generation; SQLAlchemy/alembic for ORM+migrations; team can leverage Python ML skills.  
**Consequences:** Python slower than Go for CPU-bound work; GIL means true parallelism needs multiprocessing; FastAPI ecosystem smaller than Express; no native CRDT server (Yjs runs client-side).

---

## ADR-009: Next.js for Frontend (over Remix/Vue)

**Status:** Accepted  
**Context:** Frontend framework choice for the ceremony board UI.  
**Decision:** Next.js 15 (React) over Remix or Vue/Nuxt.  
**Rationale:** Largest ecosystem; Clerk has first-class Next.js SDK; Yjs has yjs-react bindings; TailwindCSS + Radix UI for accessible components; SSR for marketing pages, CSR for interactive board.  
**Consequences:** React bundle size; Next.js App Router complexity; vendor tie to Vercel for optimal SSR (self-hosted possible but harder).

---

## ADR-010: Multi-Tenant Row-Level Security from Day 1

**Status:** Accepted  
**Context:** When to implement multi-tenancy: from start or add later?  
**Decision:** PostgreSQL RLS with tenant_id on every table, enforced from the first commit.  
**Rationale:** Retrofitting multi-tenancy is extremely expensive and error-prone. RLS is the most secure pattern (enforced at database level, not just application level). Every query automatically scoped to tenant — no "forgot to filter" bugs.  
**Consequences:** Every table needs tenant_id column; every query includes tenant_id (enforced by middleware); testing must verify RLS on every deploy; slight query performance overhead (mitigated by indexing tenant_id).
