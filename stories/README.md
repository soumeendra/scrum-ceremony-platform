# Epic + Story Structure for Huly

**Document ID:** SCP-DOC-STRY-001  
**Version:** 1.0  
**Date:** 2026-06-26  

---

## Story Format Convention

Each story in Huly follows this format:

```
As a [persona], I want [action], so that [outcome].

Acceptance Criteria:
- [ ] Given... When... Then...
- [ ] Given... When... Then...

Zone: GREEN | RED
Phase: Phase 1 (MVP) | Phase 2 | Phase 3 | Phase 4
Priority: P0 | P1 | P2 | P3
Story Points: 1 | 2 | 3 | 5 | 8 | 13
Dependencies: [list of story IDs]
```

---

## Epic List

| Epic ID | Epic Name | Phase | Priority | # Features | # Stories (est.) |
|---------|-----------|-------|----------|------------|-------------------|
| EPIC-01 | Retrospective Board | Phase 1 | P0 | 6 | 18 |
| EPIC-02 | Facilitation & Safety | Phase 1 | P0 | 4 | 14 |
| EPIC-03 | Action Tracking | Phase 1 | P0 | 4 | 12 |
| EPIC-04 | AI Intelligence | Phase 1-2 | P0-P1 | 4 | 12 |
| EPIC-05 | Analytics Dashboard | Phase 1-2 | P1 | 3 | 9 |
| EPIC-06 | Multi-Ceremony Suite | Phase 3 | P2 | 4 | 14 |
| EPIC-07 | Integrations | Phase 1-3 | P0-P2 | 5 | 16 |
| EPIC-08 | Enterprise Governance | Phase 4 | P3 | 4 | 12 |
| EPIC-09 | Billing & Subscription | Phase 2 | P1 | 3 | 10 |
| EPIC-10 | Platform Infrastructure | Phase 0 | P0 | 4 | 12 |
| | **TOTAL** | | | **41 features** | **~129 stories** |

---

## EPIC-01: Retrospective Board

**Description:** The core retrospective board — template-driven, real-time collaborative, with structured phase flow. This is the wedge that gets Scrum Masters using the product.

**Value Hypothesis:** If Scrum Masters can start a retro in under 2 minutes from a template and run it with guided facilitation, they will prefer this over setting up a Miro board manually.

### Feature F01: Template Library
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Create retro from template | Scrum Master, I want to select a retro template and create a board in one click, so that I can start facilitating immediately | 3 | GREEN | P1 |
| S02 | Default template set (5 templates) | Scrum Master, I want 5+ built-in templates (Start/Stop/Continue, Mad/Sad/Glad, 4Ls, Sailboat, WLB), so that I have common formats ready | 2 | GREEN | P1 |
| S03 | Custom template builder | Scrum Master, I want to create custom templates with my own columns and phase settings, so that I can match my team's ceremony norms | 5 | GREEN | P1 |
| S04 | Template sharing across teams | Agile Coach, I want to publish templates at org level, so that all teams use consistent ceremony formats | 3 | GREEN | P2 |

### Feature F02: Live Board
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S05 | Add/edit/delete sticky notes | Team Member, I want to add sticky notes with text in real-time, so that my ideas are captured during collection | 3 | GREEN | P1 |
| S06 | Real-time sync (CRDT) | Team Member, I want to see other people's notes appear instantly, so that the board feels collaborative not sequential | 8 | RED | P1 |
| S07 | Drag-and-drop grouping | Scrum Master, I want to drag notes into groups during clustering, so that related themes are visually organized | 5 | GREEN | P1 |
| S08 | Color coding and reactions | Team Member, I want to color-code notes and add emoji reactions, so that emotional tone and emphasis are visible | 2 | GREEN | P1 |
| S09 | Board persistence and reconnect | Team Member, I want the board to survive disconnects and refreshes, so that no contributions are lost | 5 | RED | P1 |

### Feature F03: Voting System
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S10 | Dot voting on items | Team Member, I want to allocate dot-votes to the most important items, so that the team prioritizes together | 3 | GREEN | P1 |
| S11 | Vote quota management | Scrum Master, I want to set vote counts per participant, so that voting is balanced | 2 | GREEN | P1 |
| S12 | Vote results display | Scrum Master, I want to see ranked results after voting closes, so that top priorities are clear | 2 | GREEN | P1 |

### Feature F04: Timer & Facilitator Controls
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S13 | Phase timer | Scrum Master, I want a visible timer for each phase, so that ceremonies stay time-boxed | 2 | GREEN | P1 |
| S14 | Facilitator phase controls | Scrum Master, I want to advance/lock phases, so that the ceremony flows in the right order | 3 | RED | P1 |
| S15 | Focus/stealth mode | Scrum Master, I want to hide vote counts until I reveal them, so that voting isn't influenced by early results | 2 | GREEN | P1 |

### Feature F05: Ceremony Lifecycle
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S16 | Schedule recurring retros | Scrum Master, I want to schedule retros on sprint cadence, so that they happen automatically | 3 | GREEN | P1 |
| S17 | Retro history list | Scrum Master, I want to see past retro summaries, so that I can reference previous discussions | 2 | GREEN | P1 |

### Feature F06: Async Mode
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S18 | Async participation mode | Team Member, I want to contribute to retros asynchronously before the live session, so that distributed teams participate across timezones | 5 | GREEN | P2 |

---

## EPIC-02: Facilitation & Safety

**Description:** Psychological safety features that make retrospectives honest. Anonymity, quiet mode, participation equity — the features that differentiate us from a blank whiteboard.

### Feature F07: Phase-Aware Anonymity
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Anonymous note submission | Team Member, I want to submit notes without my name attached, so that I can be honest about blockers | 5 | RED | P1 |
| S02 | Anonymity by phase config | Scrum Master, I want anonymous collection + named discussion + anonymous voting, so that each phase has the right safety level | 5 | RED | P1 |
| S03 | Anonymous voting | Team Member, I want to vote without others seeing my choices, so that I'm not influenced by senior voices | 3 | RED | P1 |
| S04 | Named action ownership | Scrum Master, I want action items to always have a named owner, so that accountability exists even after anonymous discussion | 2 | GREEN | P1 |

### Feature F08: Quiet Mode
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S05 | Silent brainstorm (quiet mode) | Scrum Master, I want to hide notes from other participants during collection, so that ideas aren't influenced by early submissions | 5 | RED | P1 |
| S06 | Delayed reveal | Scrum Master, I want to reveal all notes simultaneously after collection ends, so that anchoring bias is eliminated | 3 | GREEN | P2 |

### Feature F09: Participation Equity
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S07 | Participation counter | Scrum Master, I want to see how many people have contributed vs. total participants, so that I know if voices are missing | 2 | GREEN | P1 |
| S08 | Silent participant detection | Scrum Master, I want a nudge when someone hasn't contributed, so that I can invite them in without calling them out | 3 | GREEN | P2 |
| S09 | Participation balance analytics | Agile Coach, I want to see contribution distribution across team members over multiple retros, so that I can identify chronic non-participants | 5 | GREEN | P2 |

### Feature F10: Moderator Tools
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S10 | Merge duplicate notes | Scrum Master, I want to merge notes that say the same thing, so that the board stays clean | 2 | GREEN | P1 |
| S11 | Edit/delete inappropriate notes | Scrum Master, I want to moderate notes that are toxic, so that psychological safety is maintained | 2 | GREEN | P1 |
| S12 | Speaker queue | Scrum Master, I want a raise-hand / speaker queue during discussion, so that everyone gets a turn | 3 | GREEN | P2 |
| S13 | Anonymity break-glass (admin) | Org Admin, I want to identify the author of an anonymous note in extreme cases (policy violation), so that I can address harmful behavior | 3 | RED | P4 |
| S14 | Anonymity break audit log | Org Admin, I want every identity reveal logged with reason and actor, so that break-glass access is accountable | 2 | RED | P4 |

---

## EPIC-03: Action Tracking

**Description:** The action accountability layer — the single most important differentiator. Most tools capture discussion; this tool ensures follow-through.

### Feature F11: Action CRUD
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Create action from note | Scrum Master, I want to convert a note into an action item in one click, so that insights become commitments | 3 | GREEN | P1 |
| S02 | Assign owner and due date | Scrum Master, I want to assign an owner and due date to each action, so that accountability is clear | 2 | GREEN | P1 |
| S03 | Action status workflow | Team Member, I want to track action status (open → in-progress → done), so that I can manage my commitments | 3 | GREEN | P1 |

### Feature F12: Cross-Retro Action Register
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S04 | Persistent action register | Scrum Master, I want to see all open actions across all past retros, so that nothing falls through the cracks | 3 | GREEN | P1 |
| S05 | Carry-forward into next retro | Scrum Master, I want unresolved actions auto-surfaced in the next retro, so that accountability persists across sprints | 3 | GREEN | P1 |
| S06 | Retro debt dashboard | Scrum Master, I want a "retro debt" view showing repeatedly deferred actions, so that I can confront avoidance | 5 | GREEN | P2 |

### Feature F13: Action Quality
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S07 | Action quality nudge | Scrum Master, I want the system to flag vague actions (no owner, no deadline, no measurable outcome), so that commitments are concrete | 3 | GREEN | P2 |
| S08 | Completion rate tracking | Engineering Manager, I want to see what % of actions get completed within 2 sprints, so that I know if retros drive real change | 3 | GREEN | P2 |

### Feature F14: External Sync
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S09 | Push action to Jira | Scrum Master, I want to create a Jira ticket from an action, so that it enters the team's delivery workflow | 5 | RED | P1 |
| S10 | Sync Jira status back | Team Member, I want to see Jira ticket status inside the action register, so that I don't have to switch tools | 5 | RED | P1 |
| S11 | Jira OAuth connection | Org Admin, I want to connect Jira via OAuth, so that integration is secure | 3 | RED | P1 |
| S12 | Sync error handling | Scrum Master, I want to see sync errors with retry option, so that integration failures don't lose data | 3 | RED | P1 |

---

## EPIC-04: AI Intelligence

**Description:** AI features powered by local Gemma 3 9B + mxbai-embed-large. All outputs are suggestions requiring facilitator approval.

### Feature F15: AI Clustering
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Generate note embeddings | System, I want to embed all notes into vector space after collection, so that semantic similarity is computable | 3 | GREEN | P1 |
| S02 | Suggest clusters by similarity | Scrum Master, I want AI to suggest note groupings based on semantic similarity, so that clustering is faster than manual | 5 | GREEN | P1 |
| S03 | AI cluster labels | Scrum Master, I want AI to suggest a label for each cluster, so that themes are immediately named | 2 | GREEN | P2 |

### Feature F16: AI Summaries
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S04 | Generate retro summary | Scrum Master, I want AI to draft a summary (top themes, top votes, proposed actions, carry-forward), so that I have a starting point for the meeting record | 5 | RED | P1 |
| S05 | AI output approval gate | Scrum Master, I want to review/edit/reject AI summaries before they become official, so that AI errors don't enter the record | 3 | RED | P1 |
| S06 | Extract action items from notes | Scrum Master, I want AI to suggest action items from discussion notes, so that no insight is missed | 3 | GREEN | P2 |

### Feature F17: Recurring Detection
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S07 | Detect recurring themes | Scrum Master, I want the system to flag themes that appeared in the last 3+ retros, so that chronic issues get attention | 5 | GREEN | P2 |
| S08 | Blocker category classification | Agile Coach, I want recurring issues auto-classified (tech debt, process, people, tooling), so that systemic patterns emerge | 5 | GREEN | P2 |

### Feature F18: Sentiment Analysis
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S09 | Note sentiment scoring | Scrum Master, I want sentiment labels on notes (positive/negative/neutral), so that emotional tone is visible | 3 | GREEN | P2 |
| S10 | Team mood trend | Agile Coach, I want to see team sentiment trending over sprints, so that I can intervene when morale drops | 3 | GREEN | P2 |
| S11 | Ollama deployment guide | DevOps, I want a Docker Compose config for Ollama + Gemma 3 9B + mxbai-embed-large, so that AI infra is reproducible | 2 | GREEN | P1 |
| S12 | AI fallback to cloud LLM | Scrum Master, I want AI features to fall back to a cloud LLM if Ollama is down, so that the product works even when local GPU fails | 3 | GREEN | P2 |

---

## EPIC-05: Analytics Dashboard

### Feature F19: Team Analytics
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Retro cadence dashboard | Scrum Master, I want to see retro frequency, participation, and action rates over time, so that I know if our retros are effective | 5 | GREEN | P1 |
| S02 | Action completion metrics | Engineering Manager, I want to see action creation, completion, and overdue rates, so that I measure follow-through | 3 | GREEN | P1 |
| S03 | Top themes report | Scrum Master, I want a report of most-voted themes across retros, so that I know what matters most | 3 | GREEN | P2 |

### Feature F20: Team Health
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S04 | Team health radar | Scrum Master, I want to run a multi-dimensional health check (communication, process, quality, etc.) after each retro, so that wellness is tracked | 5 | GREEN | P2 |
| S05 | Health trend over sprints | Agile Coach, I want to see team health scores trending over time, so that I can measure improvement or decline | 3 | GREEN | P2 |

### Feature F21: Org-Level Analytics
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S06 | Cross-team heatmap | Agile CoE, I want to see recurring issues across all teams in a heatmap, so that systemic problems are visible | 8 | RED | P4 |
| S07 | Executive dashboard | VP Engineering, I want a summary dashboard showing org-wide retro health, action completion, and team maturity, so that I can make data-driven decisions | 8 | GREEN | P4 |
| S08 | Analytics export | Scrum Master, I want to export analytics to CSV/PDF, so that I can share with stakeholders | 2 | GREEN | P2 |
| S09 | Delivery maturity score | Agile Coach, I want a composite "agile maturity" score per team based on ceremony discipline, action completion, and health trends, so that I can measure transformation progress | 5 | GREEN | P3 |

---

## EPIC-06: Multi-Ceremony Suite

### Feature F22: Planning Poker
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Poker session setup | Scrum Master, I want to start a planning poker session with a list of stories, so that the team estimates together | 5 | GREEN | P3 |
| S02 | Hidden estimation | Team Member, I want to submit estimates without seeing others' votes, so that I'm not influenced | 3 | GREEN | P3 |
| S03 | Estimate reveal and consensus | Scrum Master, I want to reveal all estimates and facilitate consensus, so that the team agrees on story points | 5 | GREEN | P3 |

### Feature F23: Async Standup
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S04 | Standup prompt and submission | Team Member, I want to submit my standup update (done, doing, blockers) asynchronously, so that standups work across timezones | 3 | GREEN | P3 |
| S05 | Blocker auto-flagging | Scrum Master, I want blockers from standups auto-flagged and added to the action register, so that nothing waits until retro | 5 | GREEN | P3 |
| S06 | Standup digest | Team Member, I want a digest of my team's standup updates, so that I stay informed | 2 | GREEN | P3 |

### Feature F24: Sprint Review Feedback
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S07 | Stakeholder feedback capture | Product Manager, I want to capture stakeholder reactions to sprint demos, so that feedback shapes the backlog | 3 | GREEN | P3 |
| S08 | Feedback-to-backlog link | Product Manager, I want feedback items linkable to Jira stories, so that stakeholder input enters the product process | 3 | GREEN | P3 |

### Feature F25: Shared Action Register
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S09 | Actions across all ceremonies | Scrum Master, I want one action register spanning retros, standups, poker, and reviews, so that no commitment is siloed | 5 | GREEN | P3 |
| S10 | Ceremony-type filter | Scrum Master, I want to filter actions by source ceremony type, so that I can see which ceremonies generate the most improvement | 2 | GREEN | P3 |
| S11 | Decision log | Scrum Master, I want to log decisions made during ceremonies (not just actions), so that we remember WHY we chose X | 3 | GREEN | P3 |
| S12 | Experiment tracking (hypothesis → outcome) | Agile Coach, I want to track improvement experiments: hypothesis, action, expected impact, actual outcome, so that we learn what works | 5 | GREEN | P3 |

---

## EPIC-07: Integrations

### Feature F26: Jira Integration
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Jira OAuth connection setup | already in EPIC-03 | — | — | — |
| S02 | Map action fields to Jira | Scrum Master, I want to configure field mapping (project, issue type, assignee, sprint), so that Jira tickets have the right data | 3 | RED | P1 |
| S03 | Pull Jira status updates | System, I want to poll Jira for status changes on linked tickets, so that the action register stays current | 5 | RED | P1 |
| S04 | Atlassian marketplace listing | Product Owner, I want to publish on Atlassian Marketplace, so that Jira users discover the integration | 8 | GREEN | P4 |

### Feature F27: ERPNext Integration
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S05 | ERPNext REST API connection | DevOps, I want to connect to ERPNext via REST API with token auth, so that CRM and finance data flows | 3 | GREEN | P1 |
| S06 | Trial signup → ERPNext lead | System, I want trial signups to auto-create leads in ERPNext CRM, so that sales pipeline is populated | 3 | GREEN | P2 |
| S07 | Paid conversion → ERPNext customer | System, I want plan upgrades to create customers and sales orders in ERPNext, so that finance has revenue records | 3 | GREEN | P2 |
| S08 | Usage metrics → ERPNext custom doctype | System, I want team usage metrics pushed to ERPNext, so that account managers see engagement data | 3 | GREEN | P2 |

### Feature F28: Stripe Billing
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S09 | Stripe product/price setup | Product Owner, I want Stripe products and prices configured for each plan tier, so that billing works | 2 | GREEN | P2 |
| S10 | Trial → paid conversion | Scrum Master, I want to upgrade from free trial to paid plan via Stripe Checkout, so that payment is seamless | 3 | GREEN | P2 |
| S11 | Webhook signature verification | System, I want Stripe webhook signatures verified before processing, so that webhook fraud is prevented | 2 | RED | P2 |
| S12 | Subscription lifecycle management | System, I want to handle plan changes, cancellations, and past-due subscriptions, so that billing accounts stay accurate | 5 | GREEN | P2 |

### Feature F29: Slack Integration
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S13 | Retro notification to Slack | Team Member, I want retro reminders and summaries posted to Slack, so that the team channel stays informed | 3 | GREEN | P3 |
| S14 | Slack slash command | Scrum Master, I want /retro slash command to start retros from Slack, so that context switching is reduced | 5 | GREEN | P3 |

### Feature F30: Microsoft Teams Integration
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S15 | Teams notification adapter card | Team Member, I want retro summaries posted as adaptive cards in Teams, so that MSFT-ecosystem orgs get notifications | 3 | GREEN | P3 |
| S16 | Azure DevOps sync | Engineering Manager, I want action sync to Azure DevOps work items, so that MSFT-heavy orgs have parity with Jira integration | 5 | GREEN | P3 |

---

## EPIC-08: Enterprise Governance

### Feature F31: SSO & Provisioning
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | SAML 2.0 SSO via Clerk | IT Admin, I want SAML SSO so employees login with corporate IdP, so that access is governed centrally | 3 | GREEN | P4 |
| S02 | SCIM user provisioning | IT Admin, I want SCIM so user create/suspend/delete flows from IdP, so that offboarding is automatic | 5 | RED | P4 |
| S03 | RBAC permission matrix | Org Admin, I want configurable roles (org_admin, workspace_admin, facilitator, member, viewer), so that access is least-privilege | 5 | RED | P4 |

### Feature F32: Audit & Compliance
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S04 | Immutable audit log | IT Admin, I want an INSERT-ONLY audit log of all security-relevant actions, so that compliance evidence exists | 3 | RED | P2 |
| S05 | SOC 2 readiness | IT Admin, I want documented SOC 2 controls with evidence collection, so that enterprise procurement is unblocked | 13 | RED | P4 |

### Feature F33: Template Governance
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S06 | Org-level template publishing | Agile CoE, I want to publish mandatory templates that teams can use but not modify, so that ceremony standards are enforced | 3 | GREEN | P4 |
| S07 | Template override per team | Scrum Master, I want to customize a locked template's non-structural settings, so that teams have autonomy within guardrails | 3 | GREEN | P4 |

### Feature F34: Platform Admin
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S08 | Admin console | Org Admin, I want a console to manage workspaces, teams, integrations, and audit logs, so that I can administer the platform | 5 | GREEN | P4 |
| S09 | API and webhooks | IT Admin, I want REST API + webhooks for SIEM/SOAR integration, so that the platform fits our security infrastructure | 5 | GREEN | P4 |
| S10 | Data residency controls | IT Admin, I want to choose data storage region, so that regulatory requirements are met | 5 | RED | P4 |
| S11 | Data retention policies | IT Admin, I want configurable retention periods per data type, so that data lifecycle matches policy | 3 | GREEN | P4 |
| S12 | IP allowlisting | IT Admin, I want to restrict access to specific IP ranges, so that network security policy is enforced | 2 | GREEN | P4 |

---

## EPIC-09: Billing & Subscription

### Feature F35: Plan Tiers
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Free tier (1 team, limited history) | Product Owner, I want a free tier for 1 team with 5 retro history, so that adoption is frictionless | 3 | GREEN | P2 |
| S02 | Team plan (unlimited retros + analytics) | Scrum Master, I want a per-team paid plan with unlimited retros and basic analytics, so that active teams upgrade | 2 | GREEN | P2 |
| S03 | Business plan (multi-team insights) | Engineering Manager, I want a business plan with cross-team analytics and integrations, so that org-level value justifies higher pricing | 3 | GREEN | P2 |

### Feature F36: Trial & Conversion
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S04 | 14-day trial flow | Scrum Master, I want a 14-day trial with full features, so that I can evaluate before buying | 3 | GREEN | P2 |
| S05 | In-app upgrade prompt | Scrum Master, I want usage-gated upgrade prompts when hitting free tier limits, so that conversion is natural | 3 | GREEN | P2 |
| S06 | Plan feature gating | System, I want features gated by plan tier with graceful fallback messages, so that free users understand upgrade value | 3 | GREEN | P2 |

### Feature F37: Customer Portal
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S07 | Self-serve billing management | Scrum Master, I want to view invoices, change plans, and cancel in a self-serve portal, so that I don't need support for billing changes | 5 | GREEN | P2 |
| S08 | Team member seat management | Org Admin, I want to add/remove teams and see per-team usage, so that I can optimize my subscription | 3 | GREEN | P2 |
| S09 | Usage metering | System, I want to track per-team ceremony counts and action counts, so that usage-based pricing is possible | 5 | GREEN | P2 |
| S10 | Dunning and past-due handling | System, I want automated dunning emails and feature lock on past-due, so that revenue is protected | 3 | GREEN | P2 |

---

## EPIC-10: Platform Infrastructure

### Feature F38: Project Scaffold
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S01 | Monorepo setup (frontend + backend + AI + integration) | DevOps, I want a monorepo with Next.js, FastAPI, AI service, and integration service, so that development is cohesive | 3 | GREEN | P0 |
| S02 | Docker Compose dev environment | DevOps, I want one-command dev startup with all services, so that onboarding takes minutes not days | 5 | GREEN | P0 |
| S03 | CI/CD pipeline | DevOps, I want GitHub Actions with lint, test, build, and guardrail checks, so that quality is enforced automatically | 3 | GREEN | P0 |
| S04 | ERPNext Docker setup | DevOps, I want ERPNext running in Docker with custom doctypes pre-configured, so that the back-office is ready | 3 | GREEN | P0 |

### Feature F39: Auth & Identity
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S05 | Clerk integration (email + social login) | Scrum Master, I want to sign up/in with email or Google, so that onboarding is fast | 3 | GREEN | P0 |
| S06 | Team/workspace data model | System, I want org → workspace → team hierarchy with role-based access, so that multi-tenancy is correct from day 1 | 5 | RED | P0 |
| S07 | Multi-tenant RLS | System, I want row-level security on all tenant-scoped tables, so that cross-tenant data leaks are impossible | 5 | RED | P0 |

### Feature F40: Database & Migration
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S08 | PostgreSQL schema + Alembic migrations | DevOps, I want versioned schema migrations, so that DB changes are trackable and reversible | 3 | GREEN | P0 |
| S09 | pgvector extension setup | DevOps, I want pgvector enabled for embedding storage and similarity search, so that AI features can query vectors | 2 | GREEN | P0 |
| S10 | Redis setup for sessions/presence | DevOps, I want Redis for WebSocket session state, voter tokens, and presence, so that real-time features perform | 2 | GREEN | P0 |

### Feature F41: Guardrails & Quality
| ID | Story | As a... | Points | Zone | Phase |
|----|-------|---------|--------|------|-------|
| S11 | .hermes.md guardrails file | Product Owner, I want architecture constraints in .hermes.md so that vibe coding respects RED zones | 1 | GREEN | P0 |
| S12 | CI guardrail checks (tenant isolation, anonymity, FSM, no raw SQL) | DevOps, I want CI checks that enforce architecture invariants, so that violations are caught before merge | 5 | GREEN | P0 |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Epics** | 10 |
| **Total Features** | 41 |
| **Total Stories** | 129 |
| **Total Story Points** | ~520 |
| **RED Zone Stories** | 26 (20%) |
| **GREEN Zone Stories** | 103 (80%) |
| **Phase 0 (Infrastructure)** | 12 stories, ~43 points |
| **Phase 1 (MVP)** | 42 stories, ~185 points |
| **Phase 2 (Differentiation)** | 25 stories, ~95 points |
| **Phase 3 (Multi-Ceremony)** | 14 stories, ~55 points |
| **Phase 4 (Enterprise)** | 12 stories, ~58 points |
| **Cross-phase (Integrations/Billing)** | 24 stories, ~84 points |
