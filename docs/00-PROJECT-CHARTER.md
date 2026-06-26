# Project Charter — Scrum Ceremony Platform

**Document ID:** SCP-DOC-001  
**Version:** 1.0  
**Status:** Draft  
**Author:** Product Owner  
**Date:** 2026-06-26  
**Jira Project:** SCP  

---

## 1. Vision Statement

Build the **ceremony operating system** for Scrum Masters and Agile coaches — a purpose-built platform that helps teams run better retrospectives, planning poker, standups, and health checks, and **proves they improved the system** over time through longitudinal analytics and action accountability.

This is **not** another whiteboard. This is **not** another retro board. This is the operating layer between team reflection and measurable improvement.

## 2. Mission

To replace the fragmented tool chain (Miro/Mural for boards + Jira for tracking + spreadsheets for analytics + Slack for follow-ups) with a single, ceremony-native platform where:

- Every ceremony is guided, time-boxed, and psychologically safe
- Every discussion converts into tracked actions
- Every action connects back to delivery systems (Jira, Azure DevOps)
- Every team's improvement trajectory is visible over time
- Every organization can see systemic patterns across teams

## 3. Problem Statement

### Current Pain Points

| # | Pain Point | Impact | Who Suffers |
|---|-----------|--------|-------------|
| 1 | Scrum Masters spend 15-30 min setting up each retro in generic tools | Wasted facilitation time, inconsistent ceremony quality | Scrum Master |
| 2 | Action items from retros disappear — no follow-through | Retros become venting sessions, not improvement engines | Team, Engineering Manager |
| 3 | Same blockers recur sprint after sprint with no detection | Teams feel retros are pointless, participation drops | Team, Agile Coach |
| 4 | Anonymity is weak or absent in most tools | Teams don't speak honestly, especially with managers present | Team Members |
| 5 | No cross-team visibility into organizational patterns | Agile CoEs can't identify systemic issues or effective interventions | Agile Coach, VP Engineering |
| 6 | Generic whiteboards lack ceremony-specific workflow | Scrum Masters reinvent process every sprint, fatigue sets in | Scrum Master |
| 7 | MS Whiteboard explicitly tells users to track actions elsewhere | Action loop breaks at the ceremony boundary | Everyone |

### Quantified Opportunity

- Collaborative whiteboard market: $3.17B (2025) → $9.59B (2031)
- Scrum tooling market: $3.57B (2024) → $10.3B (2035)
- Specialist retro tools (TeamRetro, EasyRetro, etc.): $250-900/team/year
- Target niche: **$5M–$20M ARR** as a category specialist

## 4. Product Positioning

### Positioning Statement

> **For** Scrum Masters and Agile coaches **who** run recurring ceremonies, **the** Scrum Ceremony Platform **is** a ceremony operating system **that** guides facilitation, ensures psychological safety, tracks action outcomes, and surfaces organizational improvement patterns — **unlike** Miro/Mural (flexible canvases without ceremony logic), EasyRetro/GoRetro (simple boards without outcome tracking), or Mentimeter (engagement without execution).

### Competitive Positioning Map

```
                    High Structure
                         │
           TeamRetro ●   │   ● YOUR PRODUCT
                         │
         Retrium ●       │       ● Parabol
                         │
    ─────────────────────┼─────────────────────
     Low Intelligence    │    High Intelligence
                         │
       EasyRetro ●       │       ● Mentimeter
                         │
     GoRetro ●           │   ● Miro / Mural
                         │
                    Low Structure
```

### Differentiation Pillars (The Moat)

| Pillar | Why It's a Moat | Competitor Weakness |
|--------|----------------|-------------------|
| Ceremony-native workflow | Recurring, structured, not ad-hoc | Whiteboards: no ceremony logic |
| Action accountability loop | Actions persist, sync to Jira, completion tracked | MS Whiteboard: "track actions elsewhere" |
| Longitudinal improvement intelligence | Recurring blockers, improvement velocity, cross-team patterns | All retro tools: data dies when board closes |
| Psychological safety by design | Phase-aware anonymity, silent brainstorm, participation equity | Most tools: anonymity is binary or absent |
| Enterprise governance | SSO, SCIM, template governance, cross-team insights | Small retro tools: no enterprise posture |

## 5. Target Customers

### Primary Personas

| Persona | Role | Key Need | Buying Pattern |
|---------|------|----------|---------------|
| **Priya** | Scrum Master (3-8 teams) | Run retros faster with better outcomes | Bottoms-up, $20-50/month per team |
| **Alex** | Agile Coach (10-30 teams) | Repeatable ceremonies + cross-team patterns | Influences org purchase |
| **Sarah** | Engineering Manager | Evidence that retros improve delivery | Approves budget for team tools |
| **David** | Agile CoE / Transformation Office | Org-wide standards + systemic insights | Enterprise procurement, $15-40K ACV |
| **Jordan** | Team Member | Safe way to speak up + see follow-through | Free participant, drives adoption |

### Target Segments

| Segment | Teams | Price Sensitivity | Entry Point |
|---------|-------|------------------|-------------|
| Micro/self-serve | 1-5 teams | High ($250-600/yr) | Free trial → 1 team |
| Mid-market | 20-150 teams | Moderate ($2,500-5,000/yr) | Team adoption → org expansion |
| Enterprise | 150+ teams | Low ($15-40K ACV) | Pilot → procurement → rollout |

## 6. Business Objectives

### Year 1 (Months 1-12)
- Launch MVP with retrospective workflow
- Acquire **50 pilot organizations** (avg 3 teams each = 150 teams)
- Achieve **30% WAU/MAU retention** after 3 retros
- Validate pricing: $20-50/team/month
- Revenue target: **$50K ARR**

### Year 2 (Months 13-24)
- Expand to multi-ceremony suite (poker, standups, health checks)
- Convert 20% of free teams to paid
- Acquire **5 mid-market accounts** (20+ teams each)
- Revenue target: **$500K ARR**

### Year 3 (Months 25-36)
- Enterprise governance + cross-team analytics
- SOC 2 Type 2 certification
- Acquire **3 enterprise accounts** ($20K+ ACV)
- Revenue target: **$2M ARR**

## 7. Success Metrics

| Metric | Target (MVP +3 months) | Measurement |
|--------|----------------------|-------------|
| Teams completing 3+ retros in 6 weeks | 70% of activated teams | Product analytics |
| Action creation rate per retro | ≥ 3 actions per retro | Product analytics |
| Action completion rate (30 days) | ≥ 40% | Product analytics |
| Use of anonymity features | ≥ 60% of retros | Feature flag analytics |
| Use of AI clustering/summary | ≥ 40% of retros | Feature flag analytics |
| Recurring blockers detected and reviewed | ≥ 1 per team per month | Analytics service |
| Net Promoter Score | ≥ 40 | Quarterly survey |
| Team expansion (1 team → multiple) | 15% within 90 days | Account analytics |

## 8. Scope

### In Scope — MVP (Phase 1)

- Workspace, organization, and team setup
- Template-driven retrospective boards
- Real-time and asynchronous participation
- Sticky note capture, grouping, voting, timer
- Phase-aware anonymity (anonymous input → named action ownership)
- Facilitator mode with stage controls
- Action item creation, assignment, tracking
- Jira Cloud integration (push actions, sync status)
- Retro history with recurring issue detection
- AI-assisted grouping + summary (Gemma 3 9B via Ollama)
- Basic analytics dashboard

### In Scope — Roadmap (Phases 2-4)

- Planning poker, async standups, health checks, sprint review
- AI recurring theme detection, action quality scoring
- Team health radars and participation equity analytics
- Cross-team heatmaps and executive dashboards
- SSO/SAML, SCIM, SOC 2, template governance
- Slack, Teams, Azure DevOps integrations
- ERPNext CRM/finance backend integration

### Explicitly Out of Scope

- Freeform canvas/whiteboard (we are NOT Miro)
- Project management / sprint tracking (we are NOT Jira)
- Code repository / CI/CD (we are NOT GitHub)
- Video conferencing (we integrate, not replace)
- Mobile native app (responsive web only in Year 1)
- Multi-language UI (English only for MVP)

## 9. Technical Approach

### Architecture Pattern
Two-system model:
1. **Product Application** (system of engagement) — Next.js + FastAPI + PostgreSQL + Redis + Yjs CRDT
2. **ERPNext** (system of record) — CRM, finance, operations

### AI Strategy
- **Local inference**: Gemma 3 9B via Ollama for summarization, action extraction, sentiment
- **Embeddings**: mxbai-embed-large via Ollama for clustering and similarity
- **Storage**: pgvector in product PostgreSQL
- **Philosophy**: All AI outputs are suggestions requiring facilitator approval

### Build Approach
- **Vibe coding** with Hermes for GREEN zone (CRUD, integrations, UI)
- **Spec-first** with human review for RED zone (CRDT, anonymity, state machine, Jira sync)
- Guardrails enforced via `.hermes.md` + CI checks

## 10. Key Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Building a Miro-clone instead of ceremony system | High | High | Ruthless scope: NO freeform canvas |
| Real-time board unreliability | Medium | Critical | Yjs (proven CRDT), extensive reconnect testing |
| Jira integration fragility | High | Medium | Idempotency, retry queues, dead-letter queue |
| Anonymity breach | Low | Existential | Dual-path data model, pen test, CI guardrails |
| AI output quality (Gemma 9B) | Medium | Medium | All AI = suggestions, human approval gate |
| Enterprise SSO needed earlier than planned | Medium | High | Use Clerk/Auth0 — SSO is mostly config |
| CAC inflation in SMB segment | Medium | Medium | Target mid-market; SMBs churn too fast |
| Competitors bundling retro features | Medium | Medium | Moat is data + workflow memory, not features |

## 11. Constraints

- **Budget**: ₹83L (~$100K) for Year 1 (India-based team)
- **Timeline**: 48 weeks to enterprise-ready, 10 weeks to MVP
- **Team**: 1 founder (product) + 1 backend + 1 frontend (hiring in Phase 1)
- **Tech constraint**: ERPNext self-hosted, Ollama on GPU hardware (RTX 4060 Ti 16GB minimum)
- **License**: All product code is proprietary; ERPNext, Ollama, Yjs are open-source dependencies

## 12. Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| Soumeendra | Founder / Product Owner | Vision, business viability, product direction |
| Backend Engineer (TBD) | Technical Lead | Architecture, RED zone implementation |
| Frontend Engineer (TBD) | UI/UX Engineer | Board UX, ceremony flows, accessibility |
| DevOps (TBD) | Infrastructure | ERPNext, Ollama, deployment, monitoring |
| Pilot Teams (TBD) | Early Adopters | Product validation, feedback |
| Enterprise Buyers (TBD) | Customers | Security, compliance, governance |

## 13. Approvals

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Soumeendra | Draft | 2026-06-26 |
| Technical Lead | TBD | Pending | — |
| Stakeholder | TBD | Pending | — |

---

*This document is the authoritative source of project scope and direction. All Jira epics and stories must trace back to this charter. Changes require Product Owner approval.*
