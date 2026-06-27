# Go-to-Market Strategy
## Scrum Ceremony Platform — Ceremony Operating System for Agile Teams

---

**Document Version:** 1.0.0  
**Status:** Final  
**Author:** GTM Strategy Team  
**Last Updated:** June 27, 2026  
**Audience:** Executive Team, Board of Directors, Investors, Sales & Marketing Leadership  
**Classification:** Confidential — Internal & Investor Use

---

## Table of Contents

1. [GTM Strategy Overview](#1-gtm-strategy-overview)
2. [Ideal Customer Profile (ICP)](#2-ideal-customer-profile-icp)
3. [Acquisition Channels](#3-acquisition-channels)
4. [Product-Led Growth (PLG) Motion](#4-product-led-growth-plg-motion)
5. [Enterprise Sales Motion](#5-enterprise-sales-motion)
6. [Pricing Strategy](#6-pricing-strategy)
7. [Launch Plan](#7-launch-plan)
8. [Content & Community Strategy](#8-content--community-strategy)
9. [Partnership Strategy](#9-partnership-strategy)
10. [Competitive Response Playbook](#10-competitive-response-playbook)
11. [Key Metrics & KPIs](#11-key-metrics--kpis)
12. [Appendix — Resource Requirements & Budget](#12-appendix--resource-requirements--budget)

---

## 1. GTM Strategy Overview

### 1.1 Positioning Statement

> **For Scrum Masters and Agile Coaches** who are frustrated with generic whiteboards that force them to manually orchestrate ceremonies, the **Scrum Ceremony Platform** is a **ceremony operating system** that runs retrospectives, planning poker, standups, and health checks — with longitudinal improvement tracking, action accountability, and AI-powered facilitation. **Unlike retro boards or whiteboards**, our platform doesn't just capture input; it drives measurable team improvement over time.

### 1.2 Strategic Framework: The "Wedge and Platform" Model

We execute a **three-phase wedge strategy**:

| Phase | Objective | Timeline | Key Metric |
|-------|-----------|----------|------------|
| **Phase 1: Wedge** | Dominate the retro ceremony niche; become the default retrospective tool | Months 1–9 | Team activation rate |
| **Phase 2: Expand** | Cross-sell additional ceremonies (standups, poker, health checks) | Months 6–18 | Ceremonies per team/week |
| **Phase 3: Platform** | Become the ceremony OS — analytics, cross-team insights, AI facilitation | Months 12–36 | Net Revenue Retention (NRR) |

### 1.3 Land-and-Expand Mechanics

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAND-AND-EXPAND FLYWHEEL                     │
│                                                                   │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │  LAND    │───▶│ ACTIVATE │───▶│  EXPAND  │───▶│  RENEW   │  │
│   │          │    │          │    │          │    │          │  │
│   │ Free tier│    │ First    │    │ Add      │    │ Enterprise│  │
│   │ or single│    │ retro    │    │ ceremony │    │ contract │  │
│   │ team     │    │ complete │    │ types +  │    │ + multi- │  │
│   │          │    │          │    │ AI       │    │ team     │  │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│        │                                              │          │
│        └──────────────────────────────────────────────┘          │
│                    Referral Loop (NPS > 50)                      │
└─────────────────────────────────────────────────────────────────┘
```

**Land:** Single Scrum Master adopts free tier for one team's retrospectives.  
**Activate:** First successful retro with action items tracked to completion.  
**Expand:** Team adds standups, planning poker, health checks. SM upgrades to Business tier.  
**Renew:** Engineering Manager sees cross-team analytics → enterprise deal for 20+ teams.

### 1.4 Strategic Moat Pillars

| Moat | Defensibility | Time to Replicate |
|------|---------------|-------------------|
| **Longitudinal Improvement Data** | High — requires 6+ months of team data to be useful | 18–24 months |
| **Action Accountability Engine** | High — workflow integration with Jira/Linear | 12–18 months |
| **Cross-Team Analytics** | Very High — network effects from aggregated data | 24–36 months |
| **Anonymity + Psychological Safety** | Medium-High — ML model trained on effective retro patterns | 12–18 months |
| **Local AI (Gemma 9B via Ollama)** | Medium — differentiator for privacy-conscious enterprises | 6–12 months |

---

## 2. Ideal Customer Profile (ICP)

### 2.1 ICP Tier 1 — Primary: The Frustrated Scrum Master

| Attribute | Detail |
|-----------|--------|
| **Role** | Scrum Master, Team Agile Coach |
| **Company Size** | 50–500 employees |
| **Team Size** | 2–8 Scrum teams under their facilitation |
| **Industry** | Software, FinTech, HealthTech, Digital Agencies |
| **Tech Stack** | Jira/Linear, Slack/Teams, Confluence, Miro (current) |
| **Budget Authority** | $500–$5,000/yr (team-level discretionary) |
| **Reporting To** | Engineering Manager, VP Engineering, CTO |

**Pain Signals:**
- "I spend 3 hours every sprint setting up Miro boards for retros"
- "My retro action items disappear into a Confluence page nobody reads"
- "I have no way to show my VP that retros are actually improving the team"
- "Planning poker takes 45 minutes because people can't find the tool"

**Buying Triggers:**
- New sprint cycle with a mandate to "do retros better"
- Team health check reveals low psychological safety scores
- Manager asks for "retro outcomes" and they have nothing to show
- Current tool (TeamRetro/EasyRetro) lacks analytics they need

**Persona Quote:** *"I don't need another board. I need to prove to my leadership that my teams are getting better."*

---

### 2.2 ICP Tier 2 — Secondary: The Scaling Engineering Manager

| Attribute | Detail |
|-----------|--------|
| **Role** | Engineering Manager, Director of Engineering, VP Eng |
| **Company Size** | 200–2,000 employees |
| **Team Span** | 10–40 Scrum teams (often 3–8 direct reports who are SMs) |
| **Industry** | SaaS, Marketplace, Enterprise Software |
| **Tech Stack** | Jira Advanced Roadmaps, GitHub, Datadog, Lattice |
| **Budget Authority** | $10,000–$100,000/yr (departmental budget) |
| **Reporting To** | CTO, COO |

**Pain Signals:**
- "I have no visibility into whether retros across teams are driving improvement"
- "My SMs are spending 30% of their time on ceremony logistics, not coaching"
- "We have 15 teams and no consistent ceremony format"
- "Our engagement surveys show teams feel ceremonies are a waste of time"

**Buying Triggers:**
- Agile transformation initiative with executive sponsorship
- Need for SOC 2 / compliance audit trail for team processes
- Post-merger team integration requiring standardized ceremonies
- Board asks for "engineering effectiveness" metrics

**Persona Quote:** *"I need a dashboard that shows me which teams are healthy and which are stuck — without reading 47 retro boards."*

---

### 2.3 ICP Tier 3 — Tertiary: The Enterprise Agile Coach / Transformation Lead

| Attribute | Detail |
|-----------|--------|
| **Role** | Agile Coach, SAFe Program Consultant, Head of Agile Transformation |
| **Company Size** | 2,000–50,000 employees |
| **Team Span** | 50–500+ Scrum teams (advisory/oversight role) |
| **Industry** | Banking, Insurance, Healthcare, Government, Automotive |
| **Tech Stack** | Jira Align, Azure DevOps, ServiceNow, SAP |
| **Budget Authority** | $100,000–$1,000,000/yr (transformation budget) |
| **Reporting To** | CIO, Chief Transformation Officer |

**Pain Signals:**
- "Our agile transformation is 18 months in and we can't measure behavioral change"
- "Every team uses a different retro format — we have no organizational learning"
- "We need SOC 2 + SAML + SCIM before we can even evaluate a new tool"
- "Our teams are distributed across 12 time zones — async ceremonies are a must"

**Buying Triggers:**
- Enterprise-wide tool consolidation initiative
- Regulatory/compliance requirement for audit trails
- Annual vendor review with mandate to reduce SaaS sprawl
- Need for self-hosted deployment (data sovereignty)

**Persona Quote:** *"I don't need a tool. I need a system that makes 200 teams better — and proves it to the board."*

---

## 3. Acquisition Channels

### 3.1 Dual-Track Acquisition Model

We run **parallel tracks** from Day 1:

| Track | Strategy | Target CAC | % of Pipeline (Y1) | % of Pipeline (Y3) |
|-------|----------|------------|--------------------|--------------------|
| **Bottoms-Up (PLG)** | Free tier → viral adoption → team upgrade | $50–$150 | 70% | 55% |
| **Top-Down (Enterprise)** | Targeted outbound → pilot → enterprise deal | $5,000–$15,000 | 30% | 45% |

### 3.2 Bottoms-Up Acquisition Channels

| Channel | Tactic | Est. Monthly Investment | Expected MQLs/Mo | CAC Estimate |
|---------|--------|------------------------|-------------------|--------------|
| **SEO — Ceremony Content Hub** | "How to run a [type] retro" pillar pages; comparison pages (vs TeamRetro, Miro) | $3,000 (content + tools) | 200–500 | $6–$15 |
| **Product Hunt Launch** | Coordinated launch with demo video, founder story | $500 (coordination) | 100–300 signups | $2–$5 |
| **Scrum Master Slack Communities** | Genuine participation in r/scrum, Agile Alliance Slack, SM Discord | $0 (founder time) | 50–100 | $0 |
| **YouTube — "Ceremony Masterclass" Series** | 10-part series: "Run a retro that actually changes behavior" | $2,000 (production) | 150–400 | $5–$12 |
| **Viral Loop — Shared Retro Summaries** | Public share links with "Powered by" branding | $0 (product feature) | 50–200 | $0 |
| **App Marketplace (Atlassian)** | Jira/Confluence marketplace listing | $1,000 (listing + integration) | 100–250 | $4–$10 |
| **GitHub — Open Source Tools** | Retro facilitation CLI, ceremony templates repo | $0 (existing repo) | 30–80 | $0 |

**Total Bottoms-Up Monthly Budget:** ~$6,500  
**Blended CAC Target:** $15–$30 per free user → 3–5% conversion to paid

### 3.3 Top-Down Acquisition Channels

| Channel | Tactic | Est. Monthly Investment | Expected SQLs/Mo | CAC Estimate |
|---------|--------|------------------------|-------------------|--------------|
| **LinkedIn Outbound (SDR team)** | Target: VP Eng, Agile Coaches, Head of Transformation at 200–5000 employee companies | $8,000 (2 SDRs) | 15–30 | $270–$530 |
| **Industry Conference Sponsorships** | Agile Alliance, Scrum Gathering, DevOps Enterprise Summit — booth + speaking | $5,000 (amortized) | 20–50 | $100–$250 |
| **Webinars (Product-Led)** | "State of Retrospectives Report" — quarterly benchmark report | $2,000 (production + promo) | 100–200 registrants | $10–$20 |
| **Case Study Content** | Customer success stories with quantified ROI | $3,000 (production) | 10–20 (high-intent) | $150–$300 |
| **Outbound Email Sequences** | Personalized outreach with team health assessment offer | $1,500 (tools + copy) | 20–40 | $40–$75 |
| **Partner Referrals** | Agile consultancies, Atlassian Solution Partners | $0 (commission-based) | 5–15 | $0 (rev share) |
| **Retargeting Ads** | LinkedIn + Google Ads targeting visitors who viewed pricing | $2,000 | 30–60 | $30–$65 |

**Total Top-Down Monthly Budget:** ~$21,500  
**Blended CAC Target:** $3,000–$8,000 per enterprise ACV deal

### 3.4 Channel Efficiency Targets

| Metric | Month 3 | Month 6 | Month 12 | Month 24 |
|--------|---------|---------|----------|----------|
| Free signups/month | 200 | 800 | 2,500 | 8,000 |
| Free-to-paid conversion | 2% | 3.5% | 5% | 6% |
| Enterprise SQLs/month | 5 | 15 | 30 | 50 |
| Enterprise close rate | 10% | 15% | 20% | 25% |
| Enterprise ACV | $5,000 | $8,000 | $12,000 | $18,000 |
| Blended CAC (paid) | $200 | $120 | $80 | $60 |
| LTV:CAC ratio | — | 8:1 | 15:1 | 22:1 |

---

## 4. Product-Led Growth (PLG) Motion

### 4.1 Free Tier Strategy

| Feature | Free (Forever) | Team ($29/mo) | Business ($69/mo) | Enterprise |
|---------|---------------|---------------|-------------------|------------|
| **Teams** | 1 | 1 | 5 | Unlimited |
| **Ceremony Types** | Retros only | Retros + Standups | All ceremonies | All + custom |
| **Participants** | Up to 8 | Up to 12 | Up to 25 | Unlimited |
| **Action Tracking** | Basic | Full + Jira sync | Full + cross-team | Full + API |
| **Analytics** | 30-day history | 90-day | 1 year | Unlimited |
| **AI Features** | — | Basic summaries | Full facilitation | Custom models |
| **Anonymity Engine** | — | ✓ | ✓ | ✓ |
| **Integrations** | — | Slack, Jira | + Linear, GitHub | + API, SCIM, SAML |
| **Support** | Community | Email | Priority | Dedicated CSM |

**Free Tier Philosophy:** The free tier is a **fully functional retrospective tool** — not a crippled demo. A single Scrum Master should be able to run excellent retros for one team forever without paying. The upgrade triggers are:
1. Need for a second ceremony type (standups, poker)
2. Need for more participants (>8)
3. Need for action tracking with Jira integration
4. Need for analytics beyond 30 days

### 4.2 Activation Metrics

**The "Aha Moment" Definition:** A team completes their first retrospective AND creates at least one action item that gets marked as "done" within the same sprint.

| Activation Milestone | Target | Time Window |
|---------------------|--------|-------------|
| Account created → First retro scheduled | 60% | Within 48 hours |
| First retro completed | 45% | Within 7 days |
| Action item created | 35% | Within 7 days |
| Action item marked "done" | 20% | Within 14 days |
| Second retro scheduled (retention signal) | 30% | Within 21 days |
| **Fully Activated (composite)** | **25%** | **Within 14 days** |

**Activation Rate Targets:**

| Phase | Activation Rate | Intervention Trigger |
|-------|----------------|---------------------|
| Alpha (M1–M3) | 15% | Manual onboarding calls |
| Beta (M4–M6) | 20% | In-app guided setup |
| GA (M7–M12) | 25% | Automated email sequences + templates |
| Scale (M13+) | 30% | AI-powered facilitation prompts |

### 4.3 Conversion Triggers (Free → Paid)

| Trigger | Mechanism | Expected Conversion |
|---------|-----------|-------------------|
| Team tries to add 2nd ceremony type | Soft paywall with preview | 15% |
| Team grows beyond 8 members | Participant limit prompt | 12% |
| User views analytics older than 30 days | Historical data paywall | 8% |
| User attempts to connect Jira/Linear | Integration paywall | 20% |
| Sprint retrospective summary email | "Upgrade for AI insights" CTA | 5% |
| NPS survey after 3rd retro | "Unlock more with Team plan" | 3% |

**Overall Free-to-Paid Conversion Target:** 5% by Month 12 (industry benchmark for PLG SaaS: 3–7%)

### 4.4 Viral Loops

```
┌─────────────────────────────────────────────────────────────────┐
│                     VIRAL LOOP ARCHITECTURE                      │
│                                                                   │
│  ┌─────────────┐                                                  │
│  │ SM runs     │                                                  │
│  │ retro       │                                                  │
│  └──────┬──────┘                                                  │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────────┐     ┌──────────────────┐                    │
│  │ Auto-generated  │────▶│ Share link sent  │                    │
│  │ summary with    │     │ to participants  │                    │
│  │ action items    │     │ (email/Slack)    │                    │
│  └─────────────────┘     └────────┬─────────┘                    │
│                                    │                              │
│                                    ▼                              │
│                          ┌──────────────────┐                    │
│                          │ Participant      │                    │
│                          │ clicks link,     │                    │
│                          │ sees "Run your   │                    │
│                          │ own retro" CTA   │                    │
│                          └────────┬─────────┘                    │
│                                    │                              │
│                                    ▼                              │
│                          ┌──────────────────┐                    │
│                          │ New SM signs up  │───▶ [LOOP REPEATS] │
│                          │ for free tier    │                    │
│                          └──────────────────┘                    │
│                                                                   │
│  VIRAL COEFFICIENT TARGET: k = 0.3 (each user brings 0.3 users) │
│  ACHIEVED THROUGH: Share links + Slack bot + marketplace         │
└─────────────────────────────────────────────────────────────────┘
```

**Viral Loop Amplifiers:**

| Amplifier | Mechanism | Expected k Contribution |
|-----------|-----------|------------------------|
| **Shared Retro Summary** | Branded link with "Run your own retro" CTA | 0.15 |
| **Slack/Teams Bot** | `/retro` command in channels where non-users see it | 0.08 |
| **Atlassian Marketplace** | Organic discovery by Jira admins searching for retro tools | 0.05 |
| **Template Gallery** | Public templates credited to creators (with signup prompt) | 0.02 |
| **Total Target k** | | **0.30** |

---

## 5. Enterprise Sales Motion

### 5.1 Target Account Profile

**Ideal Enterprise Accounts (Top 100 Target List):**

| Criteria | Specification |
|----------|---------------|
| **Company Size** | 500–10,000 employees |
| **Agile Maturity** | 20+ Scrum teams; existing agile transformation office |
| **Industry** | Financial Services, Healthcare, SaaS, E-commerce |
| **Signals** | Job postings for Agile Coaches; using Jira Align; SOC 2 required |
| **Geography** | North America, UK, DACH region |
| **Tech Stack** | Jira (Server/DC or Cloud), Confluence, Slack/Teams, Okta |

**Account Tiers:**

| Tier | # Accounts | Target ACV | Sales Cycle | Approach |
|------|-----------|------------|-------------|----------|
| **Tier 1 (Strategic)** | 10 | $50K–$150K | 3–6 months | Founder-led + AE + SE |
| **Tier 2 (Mid-Market)** | 40 | $15K–$50K | 1–3 months | AE-led + SE support |
| **Tier 3 (Acquisition)** | 50 | $5K–$15K | 2–6 weeks | SDR → AE (transactional) |

### 5.2 Enterprise Sales Stages

| Stage | Activities | Exit Criteria | Avg Duration |
|-------|-----------|---------------|--------------|
| **1. Qualification** | BANT + MEDDIC qualification; identify champion (SM or Agile Coach) | Champion confirmed + budget exists | 1–2 weeks |
| **2. Discovery** | Demo of retro + standup flow; map current ceremony pain points; identify decision process | Pain points documented; decision process mapped | 1–2 weeks |
| **3. Pilot Proposal** | 14-day pilot with 3–5 teams; success criteria agreed; security pre-qualification | Pilot signed; success metrics defined | 1 week |
| **4. Pilot Execution** | Weekly check-ins during pilot; track activation metrics; gather NPS | 80% of pilot teams activated | 2 weeks |
| **5. Business Case** | Present pilot results; ROI calculator; security docs; procurement packet | Economic buyer (VP/CTO) engaged | 1–2 weeks |
| **6. Negotiation** | Volume pricing; contract terms; SLA negotiation; MSAs | Verbal commitment | 2–4 weeks |
| **7. Close** | Legal review; security sign-off; PO issued | Signed contract | 1–3 weeks |

**Total Sales Cycle (Tier 2):** 6–12 weeks  
**Total Sales Cycle (Tier 1):** 12–24 weeks

### 5.3 Enterprise Demo Playbook

**The "Pain → Proof → Vision" Demo Framework (45 minutes):**

| Segment | Duration | Content | Goal |
|---------|----------|---------|------|
| **Opening** | 3 min | "How many of you run retros? How many can show me the action items from your last 3 retros?" | Surface pain |
| **Current State Mapping** | 5 min | Whiteboard exercise: "Walk me through your current ceremony workflow" | Understand status quo |
| **The Cost of Status Quo** | 5 min | Show data: avg SM spends 4.2 hrs/week on ceremony logistics; 67% of retro action items never completed | Quantify pain |
| **Live Demo — Retro** | 10 min | Run a real retro with the audience using the platform; show anonymity, timer, action creation | Show core value |
| **Live Demo — Analytics** | 5 min | Show the team health dashboard; trend lines; cross-team comparison | Show differentiation |
| **Live Demo — AI** | 5 min | "Here's what the AI facilitator noticed: 3 of 5 team members haven't spoken in the last 2 retros" | Show future vision |
| **Customer Story** | 5 min | Video testimonial or live customer reference from similar company | Social proof |
| **Pilot Proposal** | 5 min | "Let's do a 14-day pilot with your 3 most engaged teams. Here's what success looks like." | Call to action |
| **Q&A** | 2 min | Address objections; hand off to SDR for scheduling | Transition |

### 5.4 Procurement Navigation Playbook

| Procurement Hurdle | Our Response | Timeline to Prepare |
|--------------------|--------------|---------------------|
| **SOC 2 Type II** | Target: Complete by Month 8; Interim: SOC 2 Type I + pen test report | 6–8 months |
| **SAML/SSO (Okta)** | Built-in from Day 1 (Auth0 or Keycloak) | Ready at launch |
| **SCIM Provisioning** | Available on Business tier; custom for Enterprise | Month 4 |
| **Data Residency (EU)** | Self-hostable; EU cloud option via Hetzner | Month 6 |
| **Vendor Security Questionnaire** | Pre-filled SIG Lite + CAIQ; security page on website | Month 3 |
| **MSA/DPAs** | Standard templates reviewed by legal counsel | Month 2 |
| **Penetration Testing** | Annual third-party pen test; results shared under NDA | Month 6 |
| **Accessibility (WCAG 2.1 AA)** | Audit and remediation plan | Month 10 |

### 5.5 Security Questionnaire Pre-Positioning

We maintain a **Security & Compliance Center** (trust.scrumceremony.io) with:

- SOC 2 Type II report (once available)
- Architecture diagram (data flow)
- Sub-processor list
- Incident response policy
- Data retention and deletion policy
- Penetration test summary
- GDPR/CCPA compliance documentation
- Business continuity plan

**Goal:** Reduce security review from 4–6 weeks to 1–2 weeks for mid-market deals.

---

## 6. Pricing Strategy

### 6.1 Pricing Architecture

| Tier | Price | Target Segment | Key Value Driver |
|------|-------|---------------|-----------------|
| **Free** | $0/forever | Individual Scrum Masters, evaluation | Single team, retros only |
| **Team** | $29/mo ($290/yr) | Small teams, startups | Standups + retros + Jira sync |
| **Business** | $69/mo ($690/yr) | Growing companies, 5 teams | All ceremonies + AI + cross-team |
| **Enterprise** | Custom ($500–$2,000+/mo) | 500+ employee companies | SSO, SCIM, self-host, SLA, CSM |

### 6.2 Per-Team Pricing Rationale

**Why per-team, not per-user?**

| Factor | Per-Team (Ours) | Per-User (Parabol, Miro) |
|--------|-----------------|--------------------------|
| **Alignment with buyer** | SM manages 1–3 teams; pays per team | Developer counts create friction |
| **Viral adoption** | Adding a team = $29, not $6 × 8 users | Adding 8 devs = $48+ |
| **Predictable revenue** | Team count is stable | Churn risk from headcount changes |
| **Competitive differentiation** | Unique in market (most are per-user) | Commoditized |
| **Expansion motion** | Add teams linearly | Add users exponentially (but with pushback) |

**Per-team definition:** A "team" is a Scrum team of 2–12 members. Multiple teams under one organization are separate subscriptions.

### 6.3 Competitive Pricing Comparison

| Competitor | Their Price | Equivalent Team Cost | Our Advantage |
|------------|------------|---------------------|---------------|
| TeamRetro | $20.83/mo (1 team) | $250/yr | We include standups + poker at same price |
| Parabol | $6/user/mo | $468/yr (8 users) | 84% cheaper at same scale |
| Miro | $8/user/mo | $768/yr (8 users) | 96% cheaper; purpose-built vs template |
| Retrium | ~$12/user/mo | $1,152/yr (8 users) | 97% cheaper; transparent pricing |
| EasyRetro | $39/mo unlimited | $468/yr | We offer more ceremony types at lower price |
| Neatro | $29/mo | $348/yr | Comparable price; we offer more features |

**Our positioning:** 50–95% cheaper than per-user competitors at team scale, with broader ceremony coverage.

### 6.4 Expansion Revenue Mechanics

| Expansion Vector | Trigger | Revenue Impact | Target (per customer) |
|-----------------|---------|---------------|----------------------|
| **Team → Business upgrade** | Need for AI or >1 team | +$40/mo ($480/yr) | 30% of Team customers within 6 months |
| **Business → Enterprise** | Need for SSO/SCIM or >5 teams | +$300–$1,000/mo | 10% of Business customers within 12 months |
| **Add teams** | Org grows; SM adds teams | +$29/mo per team | 2–3 new teams/year per customer |
| **AI Premium** | Want advanced facilitation | +$20/mo add-on | 20% of paid customers |
| **Professional Services** | Onboarding, training, custom integrations | $2,000–$10,000 one-time | 15% of Enterprise deals |

**Net Revenue Retention (NRR) Target:** 120% by Month 24 (expansion revenue minus churn)

### 6.5 Annual Discount Strategy

| Commitment | Discount | Effective Monthly Price | Rationale |
|-----------|----------|------------------------|-----------|
| Monthly | 0% | $29 (Team) / $69 (Business) | Flexibility for new customers |
| Annual | 17% | $24.08 (Team) / $57.25 (Business) | Improve cash flow; reduce churn |
| 2-Year | 25% | $21.75 (Team) / $51.75 (Business) | Lock in enterprise accounts |

---

## 7. Launch Plan

### 7.1 Phase Overview

```
Month:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18
        ├───────────┤                                                              
        ALPHA       ├───────────────────┤                                          
                    BETA                  ├───────────────────────┤              
                                          PUBLIC GA               ├──────────────┤
                                                                  ENTERPRISE     
```

### 7.2 Phase 1: Alpha (Months 1–3)

| Parameter | Detail |
|-----------|--------|
| **Goal** | Product-market fit validation; 3–5 design partners |
| **Teams** | 3–5 Scrum teams from 2–3 companies |
| **Access** | Invite-only; founder-led onboarding |
| **Pricing** | Free (design partner agreement) |
| **Success Criteria** | 80% of teams run ≥3 retros; NPS ≥ 40; qualitative "would you pay?" validation |
| **Key Activities** | Weekly customer interviews; ship rapid iterations; build core retro + action tracking; establish analytics baseline |
| **Deliverables** | Validated value hypothesis; 3 case study candidates; product roadmap informed by feedback |

**Alpha Recruitment:**
- Personal network of Scrum Masters
- Scrum Master Slack community volunteers
- Local agile meetup connections
- Target: 1 design partner company (10–15 employees, 2–3 teams)

### 7.3 Phase 2: Beta (Months 4–6)

| Parameter | Detail |
|-----------|--------|
| **Goal** | Validate activation funnel; prove viral coefficient; refine pricing |
| **Teams** | 20–30 teams from 10–15 companies |
| **Access** | Waitlist → approved; self-serve with onboarding |
| **Pricing** | Free tier + Team plan ($29/mo) available |
| **Success Criteria** | 25% activation rate; 3% free-to-paid conversion; k ≥ 0.15; NPS ≥ 50 |
| **Key Activities** | Launch Product Hunt; open Slack community; begin SEO content; ship standup + planning poker ceremonies; integrate Jira/Slack |
| **Deliverables** | Working PLG funnel; first paying customers; initial content library (10 blog posts); Product Hunt launch |

**Beta Recruitment:**
- Product Hunt launch (target: #1 Product of the Day)
- Scrum Master community outreach (r/scrum, Agile Alliance)
- LinkedIn posts from founder
- Referral from alpha partners

### 7.4 Phase 3: Public GA (Months 7–12)

| Parameter | Detail |
|-----------|--------|
| **Goal** | Scale acquisition; hit 500 paying teams; prove unit economics |
| **Teams** | Target: 1,000 free teams → 500 paying teams by Month 12 |
| **Access** | Fully open; self-serve |
| **Pricing** | All tiers live (Free, Team $29, Business $69) |
| **Success Criteria** | 5% free-to-paid conversion; CAC < $150; MRR $15K→$35K; NPS ≥ 50; churn < 5% monthly |
| **Key Activities** | Scale SEO (20+ articles/month); launch Atlassian Marketplace; begin SDR outbound; ship AI features; attend 2 conferences |
| **Deliverables** | $35K MRR; 500 paying teams; Atlassian Marketplace listing; AI feature GA; 2 conference talks |

### 7.5 Phase 4: Enterprise (Months 13–18)

| Parameter | Detail |
|-----------|--------|
| **Goal** | Close first 5 enterprise deals; prove enterprise ACV |
| **Target** | 5 enterprise contracts at $20K–$50K ACV |
| **Access** | Enterprise sales-led + self-serve hybrid |
| **Pricing** | Enterprise tier with custom pricing |
| **Success Criteria** | 5 enterprise deals closed; ACV ≥ $25K; sales cycle < 90 days; security reviews passed |
| **Key Activities** | Hire 2 AEs + 1 SE; complete SOC 2 Type I; build security center; partner with 2 agile consultancies; attend 3 enterprise conferences |
| **Deliverables** | Enterprise playbook; SOC 2 Type I; 5 enterprise customers; partner program launch |

### 7.6 Phase 5: Scale (Months 19–36)

| Parameter | Detail |
|-----------|--------|
| **Goal** | Category leadership; $2M ARR; 150%+ NRR |
| **Target** | 4,000+ paying teams; 20+ enterprise accounts |
| **Key Activities** | International expansion (EU); self-hosted option; advanced AI; platform integrations marketplace |
| **Success Criteria** | $2M ARR; 150% NRR; 90%+ gross margin; category recognition (G2, Forrester) |

---

## 8. Content & Community Strategy

### 8.1 Content Pillars & Blog Topic Map

| Pillar | Topics (Examples) | SEO Value | Funnel Stage |
|--------|-----------------|-----------|--------------|
| **Ceremony How-To** | "How to Run a Sprint Retrospective That Actually Drives Change" | High (10K+ searches/mo) | Top of Funnel |
| **Team Health** | "5 Metrics Every Scrum Master Should Track" | Medium | Top of Funnel |
| **Agile Leadership** | "Why Your Retros Are Failing (And How to Fix Them)" | High | Top of Funnel |
| **Comparison/Alternative** | "TeamRetro vs. [Us]: Which Retro Tool Is Right for Your Team?" | High (commercial) | Middle of Funnel |
| **Case Studies** | "How [Company] Reduced Retro Action Item Leakage by 73%" | Low (high intent) | Bottom of Funnel |
| **Product Updates** | "Introducing AI-Powered Facilitation" | Low | Retention |
| **Industry Reports** | "State of Agile Ceremonies Report 2026" | Very High (backlinks) | All stages |

### 8.2 Content Production Cadence

| Content Type | Frequency | Owner | Distribution |
|-------------|-----------|-------|-------------|
| Blog posts (SEO) | 3–4/week | Content Manager | Blog, LinkedIn, Twitter |
| Long-form guides | 2/month | Founder + Content | Blog, email, gated |
| Video tutorials | 2/month | Product Marketing | YouTube, in-app |
| Customer stories | 1/month | Marketing | Blog, sales deck, web |
| Industry report | Quarterly | Marketing + Research | Gated download, PR |
| Newsletter | Weekly | Founder | Email list |
| Social (LinkedIn) | Daily | Founder + Marketing | LinkedIn, Twitter/X |

### 8.3 Scrum Master Community Engagement

| Community | Platform | Engagement Strategy | Time Investment |
|-----------|----------|--------------------|-----------------|
| r/scrum (45K members) | Reddit | Genuine answers to questions; occasional tool recommendation | 3 hrs/week |
| Agile Alliance | Slack + Forum | Member; contribute to discussions; submit talk proposals | 2 hrs/week |
| Scrum Master Discord (12K) | Discord | Active member; host monthly "Ask Me Anything" | 2 hrs/week |
| Local Agile Meetups | In-person | Monthly attendance; quarterly speaking slot | 4 hrs/month |
| Scrum.org Community | Forum | Answer PSPO/PSM questions; build credibility | 1 hr/week |
| LinkedIn Agile Groups | LinkedIn | Comment on posts; share insights | 2 hrs/week |

**Rule:** Provide 10x more value than self-promotion. Goal is to become a **recognized voice** in the Scrum Master community, not a vendor.

### 8.4 Open-Source Angle

| Initiative | Description | GTM Impact |
|-----------|-------------|------------|
| **Retro Template Library** | Open-source collection of 50+ retro formats (MIT license) | SEO + brand awareness; 200+ GitHub stars target |
| **Ceremony CLI** | Open-source CLI tool for running async retros from terminal | Developer love; GitHub visibility |
| **Agile Metrics Dashboard** | Open-source Grafana dashboards for DORA + team health metrics | Community building; leads to paid platform |
| **Contributor Program** | Community contributors get free Business tier | Lowers support cost; builds ecosystem |

### 8.5 Conference & Speaking Strategy

| Conference | Audience | Goal | Timeline |
|-----------|----------|------|----------|
| **Agile Alliance Global** | 2,000+ agile practitioners | Keynote or breakout; thought leadership | Annual (Q3) |
| **Scrum Gathering** | 1,500+ Scrum Masters | Workshop: "Data-Driven Retrospectives" | Annual (Q2) |
| **DevOps Enterprise Summit** | 2,000+ engineering leaders | Sponsor + talk: "Measuring Team Health" | Biannual |
| **Agile Testing Days** | 800+ QA/agile practitioners | Talk + booth | Annual (Q4) |
| **Regional Agile Meetups** | 50–200 local practitioners | Monthly speaking slot | Ongoing |
| **Company-Hosted Webinar** | Targeted accounts | Monthly "State of Ceremonies" webinar | Monthly |

**Speaking Proposal Topics (for submission):**
1. "The Longitudinal Retrospective: Why One-Off Retros Don't Work"
2. "From Feelings to Data: Measuring Psychological Safety Over Time"
3. "The Ceremony Operating System: Replacing Your Whiteboard Stack"
4. "AI as Scrum Master: Augmenting (Not Replacing) Facilitation"

---

## 9. Partnership Strategy

### 9.1 Partnership Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARTNERSHIP ECOSYSTEM                         │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │   TECHNOLOGY     │  │   CHANNEL        │  │   SERVICES     │ │
│  │   PARTNERS       │  │   PARTNERS       │  │   PARTNERS     │ │
│  │                  │  │                  │  │                │ │
│  │ • Atlassian      │  │ • Agile          │  │ • Agile        │ │
│  │   Marketplace    │  │   Consultancies  │  │   Training     │ │
│  │ • ERPNext        │  │ • DevOps tool    │  │   Companies    │ │
│  │   Ecosystem      │  │   vendors        │  │ • Scrum.org    │ │
│  │ • Slack/Teams    │  │ • Community      │  │   trainers     │ │
│  │   App Directory  │  │   platforms      │  │ • Independent  │ │
│  │ • Linear/GitHub  │  │                  │  │   coaches      │ │
│  │   Integrations   │  │                  │  │                │ │
│  └──────────────────┘  └──────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Atlassian Marketplace Partnership

| Element | Detail |
|---------|--------|
| **Marketplace Listing** | Jira + Confluence apps; free + paid tiers |
| **Integration Depth** | Deep Jira integration: create issues from retro actions; sync sprint data; embed retro boards in Jira |
| **Co-Marketing** | Joint webinars; featured in Atlassian Community; case study on Atlassian blog |
| **Revenue Model** | Atlassian takes 15–25% commission on marketplace sales |
| **Target** | 500 marketplace installs by Month 12; 20% of total revenue by Year 2 |
| **Investment** | $15K in dedicated Atlassian integration development |

### 9.3 ERPNext Ecosystem Partnership

| Element | Detail |
|---------|--------|
| **Integration** | CRM pipeline for sales; invoicing for self-hosted customers; project sync |
| **Co-Selling** | ERPNext community members who run agile teams are ideal customers |
| **Self-Hosted Bundle** | Offer Scrum Ceremony Platform as ERPNext-compatible self-hosted solution |
| **Target** | 50 self-hosted deployments by Year 2 |

### 9.4 Agile Consultancy Partnerships

| Partner Type | Value Proposition | Commission Structure | Target Partners |
|-------------|-------------------|---------------------|-----------------|
| **Large Agile Consultancies** (ThoughtWorks, Accenture Agile) | White-label or recommended tool for client transformations | 20% rev share or $500/referral | 3–5 |
| **Boutique Agile Shops** (1–20 consultants) | Tool they can recommend to clients; improves their delivery quality | 15% rev share | 15–25 |
| **Independent Agile Coaches** | Free Business tier for their own practice; referral income | 10% rev share or free license | 50–100 |
| **Scrum.org / Scrum Alliance Trainers** | Include platform in CSM/PSM training; students get free access | Co-branded training materials | 10–20 |

### 9.5 Training Company Partnerships

| Partner | Integration | Revenue Model |
|---------|------------|---------------|
| **Scrum.org** | Include platform as recommended tool in CSM/PSM courses | $50/student license (annual) |
| **Scrum Alliance** | CSM/CSPO course integration | Revenue share per cohort |
| **Corporate Training Providers** | License platform for in-house agile training | $500/course seat |
| **Udemy/Coursera** | Create "Scrum Master Toolkit" course featuring platform | Course revenue + funnel |

### 9.6 Partnership Activation Timeline

| Quarter | Partnership Milestone | Revenue Target |
|---------|----------------------|----------------|
| Q1 (M1–M3) | Atlassian Marketplace app submitted; 2 consultancies signed | $0 (investment phase) |
| Q2 (M4–M6) | Atlassian Marketplace live; 5 consultancies active; ERPNext integration | $2K MRR from partners |
| Q3 (M7–M9) | 10 consultancies active; first training company integration | $8K MRR from partners |
| Q4 (M10–M12) | 20 consultancies; 50 independent coaches; Scrum.org integration | $15K MRR from partners |
| Year 2 | Partner-sourced pipeline = 30% of total; 50 active partners | $50K MRR from partners |

---

## 10. Competitive Response Playbook

### 10.1 Competitive Threat Matrix

| Threat | Probability | Severity | Response Strategy |
|--------|------------|----------|-------------------|
| **Miro adds native retro features** | High (70%) | Medium | Out-depth them: multi-ceremony, longitudinal data, action tracking |
| **TeamRetro competes on price** | Medium (40%) | Low | Maintain 20% price advantage; compete on breadth, not price |
| **Microsoft bundles retro in M365** | Medium (50%) | High | Position as "purpose-built vs bundled"; target Microsoft-skeptical enterprises |
| **New AI-native entrant** | Medium (40%) | Medium | Accelerate AI features; leverage existing data moat |
| **Atlassian builds ceremony tool** | Low (15%) | High | Become Atlassian Marketplace partner; if acquired, exit opportunity |
| **Open-source alternative** | Low (10%) | Low | Open-source our own tools; compete on hosting + analytics |

### 10.2 Response Playbook: Miro Adds Retro Features

**Scenario:** Miro announces "Miro Retrospectives" with AI-powered facilitation.

**Immediate Response (Week 1):**
- Publish comparison page: "Miro vs. [Us]: Purpose-Built vs. Template"
- Email existing customers: reaffirm commitment to depth over breadth
- Sales enablement: update competitive battlecard

**Strategic Response (Month 1):**
- Accelerate multi-ceremony positioning: "We do ALL ceremonies, not just retros"
- Launch "Switch from Miro" migration tool (import Miro boards)
- Publish data: "Teams using purpose-built tools see 3x more action item completion"

**Messaging Framework:**

| Miro's Claim | Our Counter |
|-------------|-------------|
| "All-in-one platform" | "Jack of all trades, master of none. Your ceremonies deserve a specialist." |
| "AI-powered" | "Our AI runs locally (Gemma 9B) — your team's data never leaves your infrastructure." |
| "Free with Miro" | "Free isn't free. You're paying for it in ceremony quality." |
| "Familiar interface" | "Familiar = same problems, new skin. We solve the root cause." |

### 10.3 Response Playbook: TeamRetro Competes on Price

**Scenario:** TeamRetro drops to $15/mo per team.

**Response:**
- **Do not match price.** Our value is breadth (multi-ceremony) and depth (analytics, AI).
- Emphasize total cost of ownership: "TeamRetro does retros. We do your entire ceremony workflow."
- Offer 3-month price lock guarantee for annual plans
- If needed, introduce a "Retro-Only" tier at $19/mo to compete directly while protecting Team tier

### 10.4 Response Playbook: Microsoft Bundling

**Scenario:** Microsoft adds retro features to Whiteboard/Teams.

**Response:**
- Target the 60% of enterprises who actively dislike Microsoft bundling (lock-in concerns)
- Position as "best-of-breed vs. bundled" — same argument that worked against SharePoint
- Emphasize cross-platform: "Works with Teams AND Slack AND Zoom"
- For Microsoft shops: integrate deeply with Teams to become complementary, not competitive
- Enterprise angle: "SOC 2, data residency, self-hosted — things Microsoft won't offer for a bundled tool"

### 10.5 Competitive Intelligence Program

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Competitor website/feature monitoring | Weekly | Product Marketing |
| Competitor pricing monitoring | Monthly | GTM Lead |
| Win/loss analysis (all deals) | Per deal | Sales |
| Customer competitive feedback | Ongoing | CS + Sales |
| Analyst briefings (Gartner, Forrester) | Quarterly | CEO + Product |

---

## 11. Key Metrics & KPIs

### 11.1 AARRR Framework — Targets by Phase

#### Acquisition Metrics

| Metric | Alpha (M1–M3) | Beta (M4–M6) | GA (M7–M12) | Scale (M13–24) |
|--------|---------------|--------------|-------------|-----------------|
| Website visitors/month | 500 | 5,000 | 25,000 | 100,000 |
| Free signups/month | 50 | 300 | 1,000 | 3,000 |
| Signup conversion rate (visitor → signup) | 2% | 4% | 5% | 6% |
| Enterprise SQLs/month | — | 5 | 20 | 40 |
| Organic traffic % | 20% | 40% | 55% | 65% |
| CAC (blended) | N/A | $200 | $120 | $80 |

#### Activation Metrics

| Metric | Alpha | Beta | GA | Scale |
|--------|-------|------|-----|-------|
| Activation rate (complete first retro) | 40% | 30% | 35% | 40% |
| Time to first retro (median) | 3 days | 5 days | 3 days | 2 days |
| Action items created per retro | 2.0 | 2.5 | 3.0 | 3.5 |
| Action item completion rate | 40% | 50% | 60% | 70% |
| Teams using 2+ ceremony types | 10% | 20% | 35% | 50% |

#### Retention Metrics

| Metric | Alpha | Beta | GA | Scale |
|--------|-------|------|-----|-------|
| Day 1 retention | 60% | 55% | 60% | 65% |
| Day 7 retention | 40% | 35% | 40% | 45% |
| Day 30 retention | 25% | 20% | 28% | 35% |
| Monthly churn (paid) | <8% | <6% | <4% | <3% |
| NPS | 40 | 50 | 55 | 60 |
| CSAT | 4.2/5 | 4.4/5 | 4.5/5 | 4.6/5 |

#### Revenue Metrics

| Metric | Alpha | Beta | GA | Scale |
|--------|-------|------|-----|-------|
| MRR | $0 | $2K | $35K | $170K |
| ARR run-rate | — | $24K | $420K | $2.04M |
| Paying teams | 0 | 60 | 500 | 2,500 |
| Average revenue per paying team | — | $33 | $38 | $42 |
| Free-to-paid conversion | — | 2% | 5% | 6% |
| Expansion revenue % | — | — | 10% | 25% |
| Net Revenue Retention (NRR) | — | — | 105% | 120% |
| Gross margin | — | 75% | 80% | 85% |
| LTV:CAC | — | 5:1 | 12:1 | 20:1 |

#### Referral Metrics

| Metric | Alpha | Beta | GA | Scale |
|--------|-------|------|-----|-------|
| Viral coefficient (k) | 0.05 | 0.15 | 0.25 | 0.35 |
| % signups from referral | 5% | 12% | 20% | 30% |
| NPS promoters (%) | 30% | 40% | 45% | 50% |
| Customer-initiated referrals/month | 2 | 15 | 80 | 300 |
| "Powered by" link CTR | — | 2% | 3% | 4% |

### 11.2 North Star Metric

**Primary North Star:** **Weekly Active Teams Running ≥2 Ceremonies**

This metric captures:
- **Adoption** (team is active)
- **Depth** (using multiple ceremony types, not just one retro)
- **Habit** (weekly cadence = embedded in workflow)

**Supporting North Stars (by function):**

| Function | North Star | Target (Month 12) |
|----------|-----------|-------------------|
| Product | % teams with action item completion rate > 60% | 40% |
| Growth | Organic signup rate (monthly) | 500 |
| Revenue | Net Revenue Retention | 110% |
| Customer Success | Time-to-value (first retro with action) | <3 days |

### 11.3 Investor Dashboard — Monthly Executive Summary

| Metric | Current | Month 3 Target | Month 6 Target | Month 12 Target |
|--------|---------|----------------|----------------|-----------------|
| MRR | — | $500 | $5,000 | $35,000 |
| Paying teams | — | 15 | 100 | 500 |
| MoM growth | — | — | 30% | 25% |
| Activation rate | — | 20% | 25% | 35% |
| Monthly churn | — | <8% | <5% | <4% |
| NPS | — | 40 | 50 | 55 |
| CAC payback (months) | — | — | 6 | 4 |
| Cash burn (monthly) | $15K | $25K | $40K | $50K |
| Runway (months) | 18 | 12 | 10 | 8 |

---

## 12. Appendix — Resource Requirements & Budget

### 12.1 GTM Team Hiring Plan

| Role | Start Month | Fully Ramp | Annual Cost | Priority |
|------|------------|------------|-------------|----------|
| Founder (GTM leadership) | M1 | — | Opportunity cost | P0 |
| Content Marketer | M3 | M6 | $75K | P0 |
| SDR (Sales) | M6 | M9 | $60K + commission | P1 |
| AE (Account Executive) | M9 | M12 | $90K + commission | P1 |
| SE (Sales Engineer) | M10 | M13 | $120K | P2 |
| SDR #2 | M12 | M15 | $60K + commission | P2 |
| AE #2 | M15 | M18 | $90K + commission | P3 |
| Customer Success Manager | M12 | M15 | $80K | P2 |
| Demand Gen Manager | M12 | M15 | $100K | P3 |

### 12.2 GTM Budget — Year 1

| Category | Monthly (Avg) | Annual | Notes |
|----------|--------------|--------|-------|
| Content production | $4,000 | $48,000 | Blog, video, guides, reports |
| Paid acquisition (ads) | $3,000 | $36,000 | LinkedIn, Google, retargeting |
| Events & conferences | $2,500 | $30,000 | 4 conferences + local meetups |
| Tools & software | $1,500 | $18,000 | CRM, analytics, email, SEO |
| Community & open source | $500 | $6,000 | Sponsorships, swag |
| PR & communications | $1,000 | $12,000 | Press releases, analyst relations |
| Sales tools & enablement | $1,000 | $12,000 | Battlecards, demos, trials |
| **Total (excl. headcount)** | **$13,500** | **$162,000** | |

### 12.3 Key Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Slow PLG activation (<20%) | Medium | High | Invest in onboarding; add templates; AI-assisted setup |
| Enterprise sales cycle too long (>120 days) | Medium | High | Focus on mid-market first; build pilot-to-close playbook |
| Competitor (Miro/Microsoft) bundles | High | Medium | Differentiate on depth; multi-ceremony; data moat |
| Churn >5% monthly | Low | Very High | Proactive CS; usage alerts; executive sponsor mapping |
| Unable to hire AE/SE fast enough | Medium | Medium | Consider fractional/contract-to-hire; leverage founder-led sales longer |
| SOC 2 timeline slips | Medium | Medium | Start audit process at Month 4; use Type I as bridge |

### 12.4 Success Criteria — 18-Month Checkpoint

| Metric | Threshold | Stretch |
|--------|-----------|---------|
| ARR | $500K | $1.2M |
| Paying teams | 1,200 | 2,500 |
| Enterprise accounts | 3 | 10 |
| NRR | 110% | 130% |
| NPS | 50 | 65 |
| Monthly churn | <4% | <2.5% |
| CAC payback | <6 months | <4 months |
| Gross margin | 78% | 85% |
| Team size (GTM) | 5 | 8 |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | June 25, 2026 | GTM Team | Initial outline |
| 0.9 | June 26, 2026 | GTM Team | Full draft complete |
| 1.0 | June 27, 2026 | GTM Team | Final — investor grade |

---

*This document is confidential and intended for internal use, investors, and prospective strategic partners. Distribution requires approval from the CEO.*
