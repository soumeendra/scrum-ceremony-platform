# Personas & User Journeys

## Scrum Ceremony Platform

*Ceremony Operating System for Scrum Masters, Agile Coaches, and Engineering Teams*

---

Version 1.0 | June 2026

## Table of Contents

1. [Introduction & Design Philosophy](#introduction)
2. [Primary Personas](#primary-personas)
   - [1. Priya — Scrum Master](#priya)
   - [2. Alex — Agile Coach](#alex)
   - [3. Sarah — Engineering Manager](#sarah)
   - [4. David — Agile CoE / Transformation Office](#david)
   - [5. Jordan — Team Member / Participant](#jordan)
3. [Secondary Personas](#secondary-personas)
   - [6. PM — Product Manager](#pm)
   - [7. Program Manager / RTE](#program-manager)
   - [8. IT Admin](#it-admin)
4. [Key User Journeys](#key-user-journeys)
   - [Journey 1: Scrum Master Runs a Recurring Retrospective](#journey-1)
   - [Journey 2: Agile Coach Reviews Trends & Publishes Guidance](#journey-2)
   - [Journey 3: Team Member Participates in First Anonymous Retro](#journey-3)
5. [Persona Relationship Map](#relationship-map)
6. [Design Principles](#design-principles)

---

## 1. Introduction & Design Philosophy <a name="introduction"></a>

Every ceremony in Scrum exists to produce one of three things: **alignment**, **insight**, or **action**. When ceremonies fail, it's almost always because the tooling got in the way of one of these outcomes. forms were too long. anonymity was unclear. action items vanished into a next-sprint-shaped hole.

This platform exists to make ceremonies *work* — not just to host them, but to ensure they produce measurable outcomes sprint after sprint.

The personas below represent the people who interact with the platform, the mental models they carry, and the outcomes they need. The journeys map how those outcomes are (or aren't) achieved today, and where the platform creates leverage.

---

## 2. Primary Personas <a name="primary-personas"></a>

---

### 1. Priya — Scrum Master <a name="priya"></a>

**Tagline:** *"I don't need another tool. I need my tools to actually work together."*

---

#### Photo Description

Early 30s, dark hair pulled into a practical bun, wearing a company-branded polo. Standing at a whiteboard covered in sticky notes, marker in hand, mid-sentence with a confident half-smile. A laptop sits open behind her showing a zoom grid of 14 faces.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Priya Ramachandran |
| **Age** | 33 |
| **Location** | Austin, TX (hybrid — 2 days in office, 3 remote) |
| **Tenure at Org** | 4.5 years (hired as Developer → promoted to SM at 2.5 years) |
| **Teams Supported** | 5 teams (Platform, Growth, Onboarding, Internal Tools, Mobile) |
| **Sprint Cadence** | 2-week sprints, all starting Wednesdays |
| **Team Size** | 6–9 members each |
| **Tech Comfort** | High. Uses VS Code, GitHub, Jira, Miro, Confluence writes wiki docs for fun |
| **Education** | BS Computer Science, CSM-II, PSM-II, SAFe 6.0 |

---

#### Goals

- Run every retrospective in under 5 minutes of setup time
- Convert retro actions into tracked items that surface in the *next* retro automatically
- Identify recurring blockers across sprints without manually cross-referencing
- Keep team psychological safety high — anonymity must be unambiguous and irrevocable
- Spend less time on ceremony logistics and more on facilitation quality
- Have a single dashboard that tells her which teams need attention this week

---

#### Frustrations

| Pain Point | Impact |
|-----------|--------|
| Retro action items get filed and forgotten until the next retro manually "reminds" the team | Repeated failures, eroding trust in the retro process |
| Anonymity toggles are buried or unclear — team members worry IT can trace posts back | Honesty drops, especially in newer teams |
| Switching between Miro, Jira, and Confluence for a single retro flow | Context loss; team sees the fragmentation |
| No automatic detection that "API latency" was flagged as a blocker 3 sprints in a row | Systemic issues go unnamed until they become incidents |
| Board setup requires copy-pasting columns every sprint | 8+ minutes of dead time at retro start while team waits |
| Velocity and burndown exist in Jira but retro insights exist nowhere — no correlation view | Can't prove retro process improves delivery |

---

#### Skills & Competencies

- **Facilitation**: Expert at keeping energy high in remote-first retros, uses liberating structures
- **Technical fluency**: Can write basic JQL, understands CI/CD pipelines, reads Grafana dashboards
- **Coaching**: Trained in powerful questions; avoids being the "answer person"
- **Tool setup**: Configures and maintains team boards, knows Confluence templates
- **Data awareness**: Not a data scientist, but reads DORA metrics and sprint reports fluently

---

#### Day-in-the-Life Narrative

**Wednesday, 8:00 AM** — Priya opens Slack. Two team channels have @-mentions asking if the retro format changed this sprint. She confirms it hasn't (same template) but knows she needs to document that as feedback.

**Wednesday, 9:30 AM** — The Platform team retro starts in 30 minutes. She opens the platform, reviews the board, and sees a yellow warning: *"3 of 5 actions from Sprint 12 are overdue."* She mentally notes to surface that at the retro kickoff.

**Wednesday, 10:15 AM** — Retro is running. The team submitted 22 cards into "What's slowing us down." Two of them mention the CI pipeline. Priya groups them, tags them, and the platform auto-suggests: *"CI pipeline delays — surfaced in retros 11, 12, 13 (3 consecutive sprints)."* She clicks to promote it to a "Recurring Blocker" — at the next retro, it will appear in the pre-read.

**Wednesday, 11:47 AM** — Retro ends. Actions are auto-created in Jira, assigned to Priya and two team leads. The retro summary is posted to Slack. Priya exports the anonymized word cloud for the team wiki.

**Wednesday, 1:00 PM** — Priya has four more retros this week. She opens the platform's team health panel and notices the Onboarding team's "Energy" score has dropped for two consecutive sprints. She makes a 1:1 note to check in with their lead.

**Thursday, 2:00 PM** — Sprint planning prep. Priya glances at the platform's sprint insights — seeing correlations between retro actions taken and throughput improvements on the Growth team. She screenshots it for her monthly report to Sarah.

---

#### Key Scenarios

1. **"Last-minute retro change"** — It's 9:55 AM. Retro starts at 10:00. A team member asks, "Can we do a 4Ls format instead of Start/Stop/Continue?" Priya should be able to swap the board template in under 30 seconds without disrupting submitted cards.

2. **"Blocked again"** — During the retro, the team identifies the same blocker from last sprint. Priya needs to link them, flag recurrence, and create an escalation path — from team → engineering manager → platform team if unresolved in 2 sprints.

3. **"Empty cards"** — A team member hasn't submitted anything for three sprints in a row. Priya gets a gentle prompt and decides whether to reach out privately or adjust the board setup.

4. **"Cross-team pattern"** — Priya notices both her Platform team and the Growth team flagged "unclear acceptance criteria" as a bottleneck. She wants to tag both, surface it to Alex (Agile Coach), and create a shared action.

---

#### Buying Criteria

Priya won't champion the platform unless:

- Retro setup takes < 5 minutes and remembers her last configuration
- Actions are tracked across sprints and surface automatically
- Anonymity is the default and is *verifiable* (not just a UI toggle)
- Recurring blockers are detected without her doing cross-sprint analysis
- She can export retro data to CSV / Jira / Confluence at minimum
- The platform works reasonably in Zoom + browser (no install friction for participants)

---

#### Success Metric

> **Within 1 adoption sprint, Priya reports that her net facilitation time per retro dropped by 30% while action completion rate exceeds 80%.**

---

### 2. Alex — Agile Coach <a name="alex"></a>

**Tagline:** *"I don't want to inspect teams — I want to inspect the system they're working in."*

---

#### Photo Description

Mid-40s, gray-templed beard, glasses on a chain, favorite hoodie visible under a blazer. Leaning against a window with a coffee in a ceramic mug, phone open to a dashboard with line charts. A whiteboard behind him says "Organizational impediments → remove them."

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Alex Kowalski |
| **Age** | 46 |
| **Location** | Denver, CO (fully remote, travel to Seattle office quarterly) |
| **Tenure at Org** | 2 years as Agile Coach (previously 8 years as SM + Program Manager) |
| **Teams Coached** | 18 teams across 4 tribes (Engineering, Data, Design, Ops) |
| **Org Scale** | 420 engineers, 14 Scrum Masters, 3 other coaches |
| **Tech Comfort** | High. Writes SQL for DORA queries, uses Power BI, maintains Notion playbooks |
| **Education** | MS Organizational Leadership, ICP-ACC, SAFe Practice Consultant, PMI-ACP |

---

#### Goals

- Establish repeatable ceremony templates that teams can adopt and adapt
- Detect cross-team patterns: systemic blockers, morale dips, process breakdowns
- Measure whether ceremony quality improves over time — and correlate with team delivery
- Govern template usage without constraining team autonomy
- Coach Scrum Masters (not teams directly) — multiply impact through Priyas
- Provide quarterly insights to David (CoE) showing transformation progress

---

#### Frustrations

| Pain Point | Impact |
|-----------|--------|
| Each team uses a different retro format, making cross-team pattern detection impossible | Can't answer: "Is our retro practice working org-wide?" |
| No ceremony data before the platform — had to manually collect retro formats via Confluence pages | 4 hours of data wrangling for quarterly review |
| Scrum Masters interpret "adaptation" so broadly that nothing is shared or reusable | Reusable templates don't exist; every team reinvents |
| Team health metrics, when they exist, come from manual quarterly surveys — lagging and biased | Can't detect a team in trouble until it's too late to intervene |
| No way to A/B test ceremony formats across similar teams | Can't ground coaching in evidence, just intuition |
| SMs view coaching as observation/coaching as judgment | Platform needs to feel like a *tool for the SM*, not a surveillance tool from the coach |

---

#### Skills & Competencies

- **Systems thinking**: Sees organizational impediments, not just team-level problems
- **Data storytelling**: Builds compelling narratives from metrics to drive leadership buy-in
- **Coaching stance**: Non-directive; asks the powerful question rather than prescribing
- **Tool governance**: Understands template schema, RBAC, and org-wide defaults
- **Cross-functional influence**: Works with HR (engagement), Engineering (delivery), Product (alignment)

---

#### Day-in-the-Life Narrative

**Tuesday, 8:00 AM** — Alex opens the dashboard on his phone. A notification: "Q2 Retrospective Format Audit — 4 of 18 teams still using default Start/Stop/Continue with no customization." He bookmarks this for his next 1:1 with those SMs.

**Tuesday, 9:30 AM** — Cross-tribe sync. Alex presents a slide he built from platform data: teams using the "Sailboat Retro" format show 22% higher action completion. He proposes adding it to the template library. Priya (Platform team) offers to co-author it.

**Tuesday, 11:00 AM** — Alex reviews the org health panel. A cluster of red signals across the Data tribe: energy scores down, action completion at 41% (org avg: 73%), format drift away from established templates. He messages the Data tribe Sm: "Can we talk this week? I see signals, not judgments."

**Wednesday, 10:00 AM** — 1:1 with Priya (Growth team). She shares her retro board and asks about trying a new format for the next sprint. Alex suggests the "4Ls" and links her to the template. He notes that this A/B test will be valuable data.

**Thursday, 3:00 PM** — Monthly coaching circle with all SMs. Alex presents anonymized aggregate data: retro quality scores (a composite of submission rates, action completion, and format adherence), cross-team blocker recurrence. Conversation is data-informed, not opinion-driven.

**Friday, 2:00 PM** — Quarterly prep. Alex exports ceremony analytics to build his slide for David's Q2 transformation review. Key question: *"Is our investment in ceremony quality correlating with improved delivery metrics?"*

---

#### Key Scenarios

1. **"Template Drift"** — A team has modified the retro template significantly (added columns, removed anonymity). Alex needs to see this in a governance view, reach out to the SM, and offer guidance — without being punitive.

2. **"Cross-Tribe Pattern"** — Alex notices that teams under Tribe A consistently have lower "Trust" scores in retros than teams under Tribe B. He needs drill-down capability to explore root cause (management style? team maturity? workload?).

3. **"Format Adoption Campaign"** — Alex publishes a new "Lean Coffee" template with adoption support materials. He wants to track which teams try it, how long they stick with it, and why they revert.

4. **"Template Governance"** — David (CoE) asks Alex to ensure all teams use a standard set of retro columns that capture tags for categorization. Alex needs to set org-wide defaults while preserving team-level autonomy for non-required columns.

---

#### Buying Criteria

Alex will adopt the platform if:

- He can see ceremony data across all teams at once (aggregate views)
- Template lifecycle support exists (publish, adopt, deprecate, sunset)
- Health trend data exists with configurable indicators
- He can compare ceremony format effectiveness across comparable org segments
- The coaching workflow is separate from surveillance — SMs own their board, but aggregate data is visible at the tribe level
- Export/BI integration exists for his quarterly storytelling

---

#### Success Metric

> **Within 2 quarters, Alex can demonstrate correlation (r > 0.4) between ceremony quality score and DORA metrics (e.g., change failure rate, lead time) across the org.**

---

### 3. Sarah — Engineering Manager <a name="sarah"></a>

**Tagline:** *"I care about delivery. If ceremonies actually help delivery, show me."*

---

#### Photo Description

Early 40s, sharp navy blazer, minimal jewelry, MacBook open on a glass conference-room table. Photo background shows a timeline wall chart on a whiteboard. Calm, direct expression. The face of someone who has earned trust through delivery.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Sarah Chen |
| **Age** | 41 |
| **Location** | San Francisco, CA (in-office 4 days/week) |
| **Tenure at Org** | 6 years (SWE → Sr. Eng → Eng Manager at year 4) |
| **Org Scope** | Manager of 3 Scrum Masters managing 9 teams (total ~75 engineers) |
| **Reports to** | VP Engineering |
| **Tech Comfort** | Moderate-high. Reads dashboards fluently, can navigate Jira, doesn't write code daily |
| **Education** | BS Computer Science, MBA |

---

#### Goals

- Prove that retrospective quality correlates with delivery predictability (sprint goal success rate)
- Track action completion rate as a leading indicator of delivery health
- Get early warning signals when a team is trending toward dysfunction (low energy, low follow-through)
- Provide data-driven input to her SMs' quarterly performance conversations
- Demonstrate to VP Engineering that ceremony investment has ROI
- Reduce surprises — she should not learn about team dysfunction at the quarterly review

---

#### Frustrations

| Pain Point | Impact |
|-----------|--------|
| No connection between retro actions and Jira delivery data | Can't assess whether retros improve outcomes |
| SMs report "things are going well" but delivery metrics say otherwise | Trust deficit; gut feel vs. data mismatch |
| Quarterly engagement surveys arrive too late to act | By the time she sees a team's satisfaction drop, people are interviewing |
| No visibility into whether retro action items are actually completed in sprint | Actions are promises, not commitments |
| Different teams measure "retro impact" differently | Can't compare or standardize |
| Her SMs spend energy fighting for tooling rather than facilitating | Tooling friction competes with team time |

---

#### Skills & Competencies

- **Delivery management**: Sprint goals, OKR tracking, release planning
- **People leadership**: 1:1s, career development, psychological safety
- **Data-driven decision making**: Uses metrics to form hypotheses, not just report
- **Stakeholder communication**: Translates engineering reality into exec-friendly language
- **Tool evaluation**: Has evaluated 3+ agile tooling platforms, knows what questions to ask

---

#### Day-in-the-Life Narrative

**Monday, 8:00 AM** — Sarah opens the platform's management dashboard. She sees a health overview for all 9 teams: 6 green, 2 yellow, 1 red. The red team is Onboarding (Energy trend down for 3 sprints, action completion at 38%). She opens that team's retro history and notes the SM (Priya) has flagged it but escalation hasn't resolved. She schedules a coffee chat with Priya.

**Monday, 10:00 AM** — Sarah reviews the action completion rates for all 9 teams. Platform (82%), Growth (79%), Mobile (85%), Onboarding (38%), Data (71%). She notes that Onboarding's low rate is tightly coupled with a delivery dip — they've missed sprint goals 2 out of 3 sprints. She sends the data to Priya with the subject line: "Can we pair on Onboarding this week?"

**Tuesday, 1:00 PM** — Monthly business review with VP Engineering. Sarah presents a slide showing correlation between retro action completion and sprint goal success rate across her org. r=0.58, p<0.05. She uses this to argue for platform investment renewal.

**Wednesday, 3:00 PM** — 1:1 with Priya. Sarah asks about the "recurring blocker" pattern in the Mobile team. Priya pulls up the platform and shows that "Test environment instability" has appeared in 4 of the last 5 retros. Sarah asks: "What would it take to escalate this?" Priya: "I need a path from retro to incident backlog." Sarah adds it to her action list.

**Thursday, 11:00 AM** — Sprint review. The Growth team shows a demo that went smoothly. Sarah privately checks the platform data — that team had highest retro action completion (79%) and lowest recurring blocker count. The pattern is visible.

**Friday, 4:00 PM** — Weekly leadership sync. Sarah shares her team dashboard with other EM peers. Another EM (James, Platform Infrastructure) says "I want that dashboard too." Sarah smiles: "Ask your SMs to adopt the platform."

---

#### Key Scenarios

1. **"Prove ROI"** — VP Engineering asks Sarah to justify the platform spend. She needs to show: action completion rates over time, correlation with delivery metrics, and a before/after comparison for teams that adopted vs. didn't.

2. **"Intervention Threshold"** — Sarah wants an alert when a team's action completion falls below 60% OR energy trend drops for 2+ sprints. She shouldn't have to inspect manually.

3. **"Cross-Team Comparison"** — Sarah's organization has 3 tribes. She wants to compare ceremony health and delivery health across tribes to identify systemic issues vs. team-specific ones.

4. **"SM Performance"** — In a quarterly review with Priya, Sarah wants to use platform data as evidence: "Your action completion rate improved from 61% to 82% this quarter. What changed?" Data as coaching, not judgment.

---

#### Buying Criteria

Sarah will sponsor the platform if:

- She gets a management dashboard with team-level health and delivery correlation
- Action completion rate is tracked and trended over time
- Alerts exist for teams trending negative
- Data is exportable to her existing BI tools (or she can screenshot for exec reviews)
- The platform doesn't require her to attend retros to get data (passive collection)
- It integrates with Jira (her source of truth for delivery metrics)

---

#### Success Metric

> **Within 1 quarter, Sarah can produce a quarterly report showing ceremony health → delivery correlation, and has intervened on at least 2 at-risk teams using platform signals.**

---

### 4. David — Agile CoE / Transformation Office <a name="david"></a>

**Tagline:** *"I need to know our ceremonies are consistent, compliant, and actually transforming how we work."*

---

#### Photo Description

Late 40s, clean-shaven, wire-rimmed glasses, crisp white shirt with rolled sleeves. Standing in front of a large monitor showing a transformation roadmap. A coffee cup with a lid (always travel-ready). The look of someone who has presented to the board and survived.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | David Okafor |
| **Age** | 49 |
| **Location** | New York, NY (hybrid, 3 days in HQ) |
| **Tenure at Org** | 3 years as Head of Agile CoE (previously 12 years in consulting) |
| **Org Scope** | Enterprise-wide: 420 engineers, 14 SMs, 4 tribes, 3 product lines |
| **Reports to** | Chief Technology Officer |
| **Tech Comfort** | Moderate. Uses Excel, Power BI, Confluence. Doesn't write code. |
| **Education** | MBA, PMP, SAFe Program Consultant, ICP-ACC |

---

#### Goals

- Establish org-wide ceremony standards that ensure consistency without stifling team autonomy
- Detect systemic patterns: org-wide blockers, process breakdowns, transformation progress
- Provide governance and compliance reporting to CTO and board
- Ensure ceremony data is retained per data governance policies
- Benchmark ceremony maturity across teams and tribes
- Drive transformation KPIs: ceremony adoption rate, format standardization, action completion

---

#### Frustrations

| Pain Point | Impact |
|-----------|--------|
| No org-wide view of ceremony practices — each team is a black box | Can't report on transformation progress to CTO |
| Ceremony data is scattered across Miro, Google Docs, Confluence, sticky notes | No single source of truth for compliance or audit |
| No governance mechanism — teams can run any format with any rules | Inconsistent experience; no ability to enforce minimum standards |
| Transformation progress is measured by "adoption" not by "outcome quality" | Teams adopt the tool but don't change behavior |
| No historical data to show trend lines for board-level reporting | Transformation narrative is anecdotal, not data-backed |
| Compliance requirements (SOX, ISO) require audit trails for process decisions | Retro actions that affect compliance-relevant work need traceability |

---

#### Skills & Competencies

- **Transformation leadership**: Designs and drives org-wide change programs
- **Governance**: Understands policy, compliance, audit requirements
- **Executive communication**: Builds board-level narratives from data
- **Stakeholder management**: Balances team autonomy with org-wide standards
- **Data analysis**: Uses Power BI, builds dashboards, interprets trends
- **Agile frameworks**: Deep knowledge of Scrum, Kanban, SAFe, LeSS

---

#### Day-in-the-Life Narrative

**Monday, 7:30 AM** — David opens the CoE dashboard. He sees org-wide ceremony adoption: 87% of teams are using the platform for retros (up from 62% last quarter). Format standardization: 73% use one of the 5 approved templates. He notes that the Data tribe is lagging at 54% adoption — he flags it for his next sync with their leadership.

**Monday, 10:00 AM** — Monthly transformation review with CTO. David presents: ceremony adoption rate, action completion trends, top 5 org-wide recurring blockers, and a maturity scorecard by tribe. CTO asks: "Are we seeing delivery impact?" David shows the correlation analysis Alex prepared: r=0.51 between action completion and sprint goal success.

**Tuesday, 9:00 AM** — Governance committee. David presents the quarterly compliance report: all retro actions are traceable, data retention policy is enforced, anonymity is preserved per privacy policy. The audit committee is satisfied.

**Wednesday, 2:00 PM** — David works with Alex on the next quarter's transformation targets: (1) raise format standardization to 85%, (2) introduce "retro quality score" as a KPI, (3) pilot the platform for sprint planning ceremonies.

**Thursday, 11:00 AM** — David reviews a proposal from a team to use a custom retro format. He evaluates it against the governance framework: does it capture required fields? Is anonymity preserved? Does it produce action items? He approves it with a note: "Please add to the template library if it proves effective."

**Friday, 3:00 PM** — David exports the quarterly transformation report. Key metrics: adoption, standardization, action completion, recurring blocker resolution rate, correlation with delivery. He prepares the narrative for the board: "Our ceremony operating system is driving measurable improvement in delivery predictability."

---

#### Key Scenarios

1. **"Compliance Audit"** — An auditor asks for evidence that retro actions affecting SOX-relevant work are tracked and retained. David needs to produce an audit trail showing action creation, assignment, and completion timestamps.

2. **"Transformation Progress"** — The CTO asks: "Are we actually transforming, or just adopting a tool?" David needs to show leading indicators (ceremony quality, action completion) and lagging indicators (delivery metrics, engagement scores) with trend lines.

3. **"Template Governance"** — A team wants to use a non-standard format. David needs a governance workflow: request → review → approve/reject with rationale → add to library if approved.

4. **"Org-Wide Blocker"** — David notices that "CI pipeline instability" appears as a recurring blocker across 6 teams. He escalates to the Platform Engineering leadership with data: frequency, impact, duration.

---

#### Buying Criteria

David will mandate the platform if:

- Org-wide governance controls exist (RBAC, template policies, data retention)
- Audit trail capabilities exist for compliance-relevant actions
- Executive dashboards show transformation KPIs
- Data export and BI integration exist for custom reporting
- The platform supports his governance framework (standards + flexibility)
- Data residency and security meet enterprise requirements

---

#### Success Metric

> **Within 2 quarters, David can produce a board-ready transformation report with adoption, standardization, and delivery-impact metrics — and has identified + escalated at least 3 org-wide systemic blockers.**

---

### 5. Jordan — Team Member / Participant <a name="jordan"></a>

**Tagline:** *"I just want to be heard — safely — and know that saying something matters."*

---

#### Photo Description

Late 20s, casual hoodie, headphones around the neck, sitting at a desk with dual monitors. A half-empty coffee mug and a small succulent plant on the desk. The expression is focused but slightly guarded — the look of someone who has been burned by retros where their feedback was identifiable.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Jordan Martinez |
| **Age** | 28 |
| **Location** | Austin, TX (remote) |
| **Tenure at Org** | 1.5 years (joined as Mid-Level Frontend Engineer) |
| **Team** | Growth team (8 engineers, 1 SM = Priya) |
| **Tech Comfort** | High. Writes React, uses GitHub, comfortable with any web tool |
| **Personality** | Introverted, thoughtful, values psychological safety |
| **Education** | BS Computer Science |

---

#### Goals

- Share honest feedback without fear of attribution or judgment
- See that their input leads to actual change (not just disappears into a board)
- Participate in ceremonies with minimal friction (no account creation, no learning curve)
- Feel that the retro process is genuinely useful, not a mandatory hour
- Understand what happens to their anonymous submissions

---

#### Frustrations

| Pain Point | Impact |
|-----------|--------|
| In past jobs, "anonymous" retro tools logged user IDs in the database | Jordan doesn't trust anonymity claims |
| Retro boards feel like complaint boxes — feedback goes in, nothing comes out | Learned helplessness; stops submitting |
| Some retro tools require login, account setup, or install | Friction kills participation, especially for new joiners |
| Retro formats are confusing — unclear what goes in which column | Anxiety about "doing it right" instead of being honest |
| No follow-up: Jordan mentions a blocker, but never sees if it was addressed | Feels like talking into the void |
| In some retros, the SM reads cards aloud and people guess who wrote them | Pseudonymity is not anonymity; psychological safety collapses |

---

#### Skills & Competencies

- **Technical**: Frontend development, code review, testing
- **Communication**: Good writer, prefers async communication
- **Collaboration**: Values team health, contributes to team culture
- **Skepticism**: Healthy — has seen tools and processes fail before

---

#### Day-in-the-Life Narrative

**Wednesday, 9:00 AM** — Jordan gets a Slack notification: "Sprint 14 Retro starts in 15 minutes. Add your thoughts now." Jordan clicks the link. No login required — the board opens directly. Jordan appreciates this.

**Wednesday, 9:02 AM** — Jordan reads the retro prompt: "What's slowing us down? What's going well? What should we try?" Three columns, clear and simple. Jordan types into "Slowing us down": *"Design handoff docs are always late, causing last-minute rework."* Jordan hesitates — is this anonymous? A small lock icon and tooltip says: "Your identity is never stored with this card. Not even admins can trace it." Jordan submits.

**Wednesday, 9:15 AM** — Retro is live. Priya is facilitating. She groups similar cards, including Jordan's, into a cluster called "Design handoff delays." Jordan sees their words reflected in the cluster — not attributed, but acknowledged. The team votes on which clusters to discuss.

**Wednesday, 10:00 AM** — Retro ends. Priya creates an action: "Establish design handoff deadline — 2 days before dev starts." Assigned to the design lead. Jordan sees the action appear in the board's "Actions" tab.

**Next Sprint Retro, Wednesday, 9:00 AM** — Jordan opens the retro board and sees a section at the top: "Carry-over actions from last retro." The design handoff action is marked "In Progress." Jordan feels heard. They submit new feedback.

---

#### Key Scenarios

1. **"First Retro"** — Jordan's first retro at the company. The experience must be: zero friction to enter, crystal clear on anonymity, and produce a visible outcome within 1 sprint.

2. **"I Said Something — Did It Matter?"** — Jordan wants to trace what happened to their feedback. Not their identity, but the *idea*. The platform should show: "Your cluster 'Design handoff delays' generated 1 action, currently In Progress."

3. **"Unsafe Moment"** — Jordan wants to raise a sensitive concern (e.g., "I feel overloaded and can't say no"). They need absolute confidence that this cannot be traced to them. The platform must make this guarantee explicit and verifiable.

4. **"Retro Fatigue"** — Jordan has been in 10 retros. They're starting to feel repetitive. The platform should vary prompts, show progress over time, and make Jordan feel their participation is producing cumulative improvement.

---

#### Buying Criteria

Jordan doesn't buy the platform — but Jordan's *adoption* determines whether the platform succeeds. Jordan will participate if:

- No login or account creation is required to submit feedback
- Anonymity is the default and is explained clearly (not buried in a privacy policy)
- The retro board loads fast and works on a laptop or tablet
- They can see what happened to their feedback (action created, status tracked)
- The retro format is intuitive within 30 seconds
- They never feel pressured to identify themselves

---

#### Success Metric

> **Jordan's submission rate stays above 85% across 5+ consecutive retros, and they can point to at least 2 actions in the "Completed" state that originated from their feedback clusters.**

---

## 3. Secondary Personas <a name="secondary-personas"></a>

---

### 6. PM — Product Manager (Sprint Reviews) <a name="pm"></a>

**Tagline:** *"I need to see what we built, hear what's blocking the next sprint, and leave with confidence in the roadmap."*

---

#### Photo Description

Mid-30s, business-casual attire, tablet in hand showing a product roadmap. Standing near a demo station, engaged but slightly impatient — the look of someone whose next meeting starts in 12 minutes.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Maya Patel |
| **Age** | 35 |
| **Role** | Senior Product Manager, Growth Tribe |
| **Teams** | Partners with 2 Scrum teams (Growth, Onboarding) |
| **Tech Comfort** | Moderate. Uses Jira, Productboard, Google Suite |

---

#### Goals

- Participate in sprint reviews efficiently — see demos, understand progress, flag blockers
- Connect retro insights to product planning: if "unclear AC" is a recurring blocker, adjust definition-of-done with the team
- Understand team health signals that may affect roadmap delivery
- Provide feedback to the team in a structured, non-intrusive way

---

#### Frustrations

- Sprint reviews run over time because the retro bled into review time
- Retro insights are not accessible to PMs — they're in a separate tool
- No visibility into whether the team's recurring blockers affect the roadmap
- Action items from retros are engineering-only; PMs can't see or contribute

---

#### Key Scenario

Maya joins the sprint review. She opens the platform's read-only view and sees: sprint goal status, completed work, and a summary of retro actions from the last sprint. She notices "Design handoff delays" is a recurring blocker and decides to discuss timeline adjustments with the team.

---

#### Success Metric

> **Maya can access a sprint review summary in < 2 minutes and leaves each review with clear confidence level (High/Medium/Low) in the next sprint's plan.**

---

### 7. Program Manager / RTE (Cross-Team Planning) <a name="program-manager"></a>

**Tagline:** *"When 5 teams depend on each other, I need to see the dependencies — and the blockers — before they become delays."*

---

#### Photo Description

Early 40s, professional but slightly rumpled (it's PI Planning week). Laptop with 3 browser tabs open, a printed dependency map on the desk. The expression of someone who is always 5 minutes from solving the critical path problem.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Chris O'Brien |
| **Age** | 42 |
| **Role** | Release Train Engineer (RTE) / Program Manager |
| **Scope** | 5 teams, ~45 engineers, 1 product line |
| **Tech Comfort** | Moderate-high. Uses Jira Align, Confluence, Miro |

---

#### Goals

- Identify cross-team dependencies and blockers during PI planning
- Track whether retro actions that affect multiple teams are resolved before they cascade
- See ceremony health across the program — which teams are struggling
- Facilitate cross-team retros when systemic issues span teams

---

#### Frustrations

- Each team's retro is a black box — no cross-team visibility
- Cross-team blockers are raised in retro but never tracked across team boundaries
- No aggregated view of ceremony health for program-level planning
- PI planning retros (spanning 5 teams) require 5 separate tools

---

#### Key Scenario

Chris is preparing for PI planning. He opens the platform's program view and sees: cross-team blocker heatmap (red clusters around CI pipeline and shared API dependencies), ceremony health by team (2 teams in yellow), and a list of actions that span multiple teams. He uses this to structure the PI planning risk discussion.

---

#### Success Metric

> **Chris can identify all cross-team blockers within 15 minutes of sprint review and has a tracked action for each before PI planning starts.**

---

### 8. IT Admin (Security & Compliance Evaluation) <a name="it-admin"></a>

**Tagline:** *"If it doesn't pass security review, it doesn't matter how good the UX is."*

---

#### Photo Description

Mid-30s, calm and methodical expression, sitting at a desk with a security audit checklist visible on a second monitor. The look of someone who has evaluated 50+ SaaS tools and knows exactly which questions to ask.

---

#### Demographics

| Attribute | Detail |
|-----------|--------|
| **Name** | Raj Krishnamurthy |
| **Age** | 37 |
| **Role** | Senior IT Security Engineer |
| **Scope** | SaaS tool evaluation, compliance, data governance |
| **Tech Comfort** | Very high. Understands SOC 2, GDPR, SAML, encryption at rest |

---

#### Goals

- Ensure the platform meets enterprise security and compliance requirements
- Verify data residency, encryption, access control, and audit trail capabilities
- Confirm the platform integrates with the company's SSO (SAML/OIDC)
- Validate that anonymity claims are technically sound (not just UI-level)
- Ensure data retention policies align with company governance

---

#### Frustrations

- Vendors claim "anonymous" but store user IDs in database
- No SOC 2 Type II report available
- Data residency is "global" with no region selection
- No admin audit log for who accessed what
- RBAC is binary (admin/user) with no granular permissions

---

#### Key Scenario

Raj is evaluating the platform for enterprise deployment. He reviews: SOC 2 report, data flow diagrams, RBAC matrix, SAML integration docs, and the anonymity architecture. He asks: "Can you prove that a card submission cannot be traced to a user ID?" The platform team shows him the architecture: cards are submitted without session tokens, stored in a separate table with no user foreign key.

---

#### Success Metric

> **Raj approves the platform for enterprise deployment within 30 days of evaluation start, with no critical findings.**

---

## 4. Key User Journeys <a name="key-user-journeys"></a>

---

### Journey 1: Scrum Master Runs a Recurring Retrospective <a name="journey-1"></a>

**Persona:** Priya (Scrum Master)
**Goal:** Run a retrospective that surfaces recurring blockers and tracks action follow-through
**Total Time:** ~45 minutes (5 min setup + 40 min facilitation)

---

#### Step 1: Open Workspace

**Time:** Wednesday, 9:25 AM (5 min before retro)
**Action:** Priya opens the platform, navigates to her Growth team workspace.
**Emotion:** 😐 Neutral, focused. She's done this 40 times before.
**Touchpoint:** Platform dashboard → Team workspace
**Pain Point:** If she has to re-create the board or reconfigure columns, she loses 8 minutes and the team's patience.
**Opportunity:** The platform remembers her last configuration. The board is pre-populated with submitted cards from the past 24 hours. She sees: "14 cards submitted by 7 of 8 members."

---

#### Step 2: Review Pre-Read

**Time:** 9:26 AM
**Action:** Priya opens the pre-read panel. She sees: carry-over actions from last retro (2 In Progress, 1 Completed), recurring blockers (1 flagged: "CI pipeline delays — 3 consecutive sprints"), and a word cloud of submitted cards.
**Emotion:** 😊 Confident. She's prepared.
**Pain Point:** If the pre-read doesn't exist, she'd have to manually cross-reference last retro's actions.
**Opportunity:** The platform auto-generates the pre-read 1 hour before retro start. Recurring blockers are surfaced automatically.

---

#### Step 3: Start Retro

**Time:** 9:30 AM
**Action:** Priya clicks "Start Retro." The board is shared with the team via a single link. No login required for participants.
**Emotion:** 😌 Relief. The team joins in seconds.
**Pain Point:** If participants had to log in or create accounts, 2-3 minutes would be lost to "I forgot my password."
**Opportunity:** The platform uses magic-link or SSO — participants click and are in. Jordan (team member) appreciates the zero-friction entry.

---

#### Step 4: Facilitate Card Review

**Time:** 9:35 AM
**Action:** Priya reviews submitted cards with the team. She groups similar cards into clusters. The platform suggests clusters based on text similarity.
**Emotion:** 🤔 Focused. She's thinking about patterns.
**Pain Point:** Manual grouping is tedious — dragging 22 cards one by one.
**Opportunity:** The platform auto-suggests clusters. Priya confirms or adjusts. She groups "CI pipeline delays" and "Flaky tests in CI" into a single cluster.

---

#### Step 5: Surface Recurring Blocker

**Time:** 9:42 AM
**Action:** The platform highlights: "This cluster matches a recurring blocker from 3 previous retros." Priya clicks to view the history: Sprint 11, 12, 13 — all flagged CI pipeline issues.
**Emotion:** 😤 Frustrated (at the blocker, not the tool). This has been going on too long.
**Pain Point:** Without the platform, she'd have to manually remember or search for this pattern.
**Opportunity:** The platform auto-detects recurrence. Priya promotes it to "Escalation Path" — it will appear in Sarah's (EM) dashboard and auto-escalate if not resolved in 2 sprints.

---

#### Step 6: Team Discussion

**Time:** 9:45 AM
**Action:** The team discusses the top 3 clusters. Priya uses the timer feature to keep each discussion to 5 minutes.
**Emotion:** 😊 Engaged. The team is energized by the data.
**Pain Point:** Discussions can derail without timeboxing.
**Opportunity:** The platform provides per-topic timers and a "Parking Lot" for off-topic items.

---

#### Step 7: Vote on Actions

**Time:** 9:52 AM
**Action:** The team votes on which clusters should generate actions. Each member gets 3 votes. The platform tallies.
**Emotion:** 😌 Democratic. Everyone feels heard.
**Pain Point:** Voting can be biased if people vote for their own cards.
**Opportunity:** Voting is anonymous. The platform shows results as a ranked list.

---

#### Step 8: Create Actions

**Time:** 9:55 AM
**Action:** Priya creates 3 actions from the top-voted clusters. She assigns owners and due dates. The platform auto-links them to the recurring blocker.
**Emotion:** ✅ Accomplished. Actions are concrete, not vague.
**Pain Point:** If actions are vague ("improve CI"), they'll never get done.
**Opportunity:** The platform prompts for specificity: "What exactly? By whom? By when?" Actions are created in Jira automatically.

---

#### Step 9: Close Retro

**Time:** 10:00 AM
**Action:** Priya clicks "Close Retro." The platform generates a summary: cards submitted, clusters, actions created, recurring blockers updated. The summary is posted to the team's Slack channel.
**Emotion:** 😊 Satisfied. The retro felt productive.
**Pain Point:** If she had to write the summary manually, it would take 10 minutes.
**Opportunity:** Auto-generated summary. One-click Slack/email distribution.

---

#### Step 10: Next Sprint — Pre-Read Shows Recurring Blocker

**Time:** Next Sprint Retro, 9:25 AM
**Action:** Priya opens the pre-read. The recurring blocker "CI pipeline delays" is highlighted in red with a note: "4 consecutive sprints. Escalation: Notified Engineering Manager."
**Emotion:** 😟 Concerned but empowered. She has data to escalate.
**Pain Point:** If the platform didn't surface this, she'd have to remember to bring it up.
**Opportunity:** The platform ensures continuity between retros. Nothing falls through the cracks.

---

#### Step 11: Action Follow-Through Visible

**Time:** Next Sprint Retro, 9:30 AM
**Action:** Priya shows the team: "Last sprint's actions: 2 Completed, 1 In Progress (CI pipeline fix — assigned to Platform team)." The team sees their feedback led to action.
**Emotion:** 😊 Validated. The team trusts the process.
**Pain Point:** If actions were invisible, the team would lose faith in retros.
**Opportunity:** The platform closes the feedback loop. Jordan (team member) sees their feedback cluster generated a completed action. Trust increases.

---

### Journey 2: Agile Coach Reviews Trends & Publishes Updated Guidance <a name="journey-2"></a>

**Persona:** Alex (Agile Coach)
**Goal:** Identify cross-team patterns and publish improved ceremony guidance based on evidence
**Total Time:** ~90 minutes (spread across a week)

---

#### Step 1: Inspect Cross-Team Dashboard

**Time:** Tuesday, 9:00 AM
**Action:** Alex opens the platform's tribe-level dashboard. He sees: ceremony health scores for all 18 teams, action completion rates, format adoption, and recurring blocker heatmaps.
**Emotion:** 🤔 Analytical. He's looking for patterns.
**Pain Point:** If data were scattered across tools, he'd spend 2 hours just collecting it.
**Opportunity:** The platform aggregates ceremony data across teams. He spots: Data tribe has 41% action completion (org avg: 73%). He drills down.

---

#### Step 2: Identify Pattern

**Time:** 9:20 AM
**Action:** Alex filters by Data tribe. He sees: 3 of 5 teams use outdated retro formats, action completion is low, and "unclear requirements" is a recurring blocker across all 3 teams.
**Emotion:** 😤 Concerned. This is a systemic issue, not a team-level one.
**Pain Point:** Without cross-team data, he'd only see this if he attended each team's retro personally.
**Opportunity:** The platform surfaces cross-team patterns automatically. He tags the pattern: "Data Tribe — Format Drift + Low Completion."

---

#### Step 3: Design Improved Template

**Time:** Wednesday, 2:00 PM
**Action:** Alex creates a new retro template: "Data Team Retro v2" — includes a column for "Data Quality Blockers," a required action format (SMART), and auto-links to Jira.
**Emotion:** 😊 Creative. He's designing a solution.
**Pain Point:** If template creation required engineering effort, he'd be dependent on the platform team.
**Opportunity:** The platform has a visual template builder. Alex drags, drops, and publishes.

---

#### Step 4: Publish & Communicate

**Time:** Thursday, 10:00 AM
**Action:** Alex publishes the template to the Data tribe workspace. He adds a changelog note: "Added Data Quality column based on recurring blocker pattern. Required for all Data tribe teams starting Sprint 16." He notifies the Data tribe SMs.
**Emotion:** 📢 Proactive. He's driving improvement.
**Pain Point:** If publishing required admin approval, the cycle would be slow.
**Opportunity:** Alex has publish rights for his tribe. The platform sends notifications to affected SMs with adoption instructions.

---

#### Step 5: Monitor Adoption & Impact

**Time:** 2 weeks later, Monday
**Action:** Alex checks the adoption dashboard: 4 of 5 Data tribe teams have adopted the new template. Action completion is up to 67% (from 41%). The recurring blocker "unclear requirements" has decreased by 40%.
**Emotion:** 😊 Validated. The intervention worked.
**Pain Point:** If he had to wait a quarter for survey data, the feedback loop would be too slow.
**Opportunity:** Real-time adoption and impact metrics. Alex documents the case study for his quarterly report to David.

---

### Journey 3: Team Member Participates Safely in First Anonymous Retro <a name="journey-3"></a>

**Persona:** Jordan (Team Member / Participant)
**Goal:** Contribute honest feedback safely and see that it leads to action
**Total Time:** ~50 minutes (across the sprint)

---

#### Step 1: Receive Invitation

**Time:** Wednesday, 8:45 AM (day before retro)
**Action:** Jordan gets a Slack notification: "Sprint 14 Retro tomorrow at 9:30. Add your thoughts now — it's anonymous." Jordan clicks the link.
**Emotion:** 😐 Neutral. Another retro. But the "add your thoughts now" part is interesting — async submission.
**Pain Point:** If the link required login, Jordan might procrastinate.
**Opportunity:** The link opens directly to the board. No login. Jordan can submit now (async) or wait for the live retro.

---

#### Step 2: Submit Feedback Anonymously

**Time:** Wednesday, 8:50 AM
**Action:** Jordan types into the "Slowing us down" column: *"Design handoff docs are consistently 2 days late, causing rework."* A small lock icon confirms: "Anonymous — not even admins can trace this."
**Emotion:** 😟 Slightly anxious. Jordan has been burned before by "anonymous" tools that logged user IDs.
**Pain Point:** Trust is fragile. If Jordan suspects traceability, they'll self-censor.
**Opportunity:** The platform explains the anonymity architecture in plain language: "Cards are submitted without session data. There is no user ID field in the card table. This is verifiable in our privacy documentation." Jordan reads it and feels safer.

---

#### Step 3: Attend Live Retro

**Time:** Thursday, 9:30 AM
**Action:** Jordan joins the retro. Priya is facilitating. Jordan sees their card on the board — grouped with 3 others into a cluster called "Design handoff delays." No name attached.
**Emotion:** 😌 Relief. Their feedback is visible but not attributable.
**Pain Point:** In past retros, the SM read cards aloud and people guessed authors. Jordan dreaded this.
**Opportunity:** The platform displays cards without author info. Priya facilitates by cluster, not by individual card. Jordan feels safe.

---

#### Step 4: Watch the Discussion

**Time:** 9:40 AM
**Action:** The team discusses the "Design handoff delays" cluster. The design lead acknowledges the issue. Jordan watches — their concern is being addressed without them having to be the "complainer."
**Emotion:** 😊 Validated. The system works.
**Pain Point:** If the discussion became accusatory, Jordan would shut down.
**Opportunity:** The platform's format keeps discussion focused on patterns, not people. Priya's facilitation is supported by the data structure.

---

#### Step 5: See Action Created

**Time:** 9:55 AM
**Action:** Priya creates an action: "Design handoff deadline: 2 days before dev start. Owner: @design-lead. Due: Sprint 15." Jordan sees it appear in the Actions panel.
**Emotion:** 😊 Hopeful. Something concrete came out of this.
**Pain Point:** If actions were vague ("improve handoff"), Jordan would assume nothing will change.
**Opportunity:** The platform enforces SMART action format. Jordan can track the action's status.

---

#### Step 6: Track Action Status

**Time:** Next Sprint, mid-sprint
**Action:** Jordan opens the platform (he bookmarked it) and checks the Actions panel. The design handoff action is "In Progress." He sees a comment from the design lead: "New deadline policy drafted, team review next week."
**Emotion:** 😊 Engaged. Jordan feels like a stakeholder, not just a participant.
**Pain Point:** If actions disappeared after the retro, Jordan would lose faith.
**Opportunity:** The platform maintains action visibility across sprints. Jordan can see the trajectory.

---

#### Step 7: See Completion

**Time:** Sprint 15 Retro, 9:25 AM
**Action:** Jordan opens the pre-read. The design handoff action is marked "Completed." The recurring blocker "Design handoff delays" is marked "Resolved — 1 occurrence, addressed."
**Emotion:** 😊 Empowered. Jordan's feedback led to real change.
**Pain Point:** None — this is the ideal state.
**Opportunity:** The closed feedback loop builds trust. Jordan submits more feedback in this retro, and tells a teammate: "Actually, this retro thing works here."

---

## 5. Persona Relationship Map <a name="relationship-map"></a>

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORGANIZATION                                │
│                                                                 │
│  ┌──────────┐   reports to   ┌──────────────┐                  │
│  │  David   │◄──────────────│     CTO      │                  │
│  │  (CoE)   │               └──────────────┘                  │
│  └────┬─────┘                      ▲                            │
│       │ sponsors                   │ reports to                 │
│       │                            │                            │
│  ┌────▼─────┐   coaches    ┌──────┴───────┐                   │
│  │  Alex    │─────────────►│    Sarah     │                   │
│  │(Agile    │              │  (Eng Mgr)   │                   │
│  │ Coach)   │              └──────┬───────┘                   │
│  └────┬─────┘                     │ manages                    │
│       │ multiplies                │                            │
│       │ through                   │                            │
│  ┌────▼─────┐   facilitates ┌─────┴──────┐    ┌──────────┐   │
│  │  Priya   │─────────────►│   Jordan    │    │   Maya   │   │
│  │  (SM)    │              │(Team Member)│    │   (PM)   │   │
│  └──────────┘              └────────────┘    └──────────┘   │
│       │                            ▲                          │
│       │ participates                │ participates             │
│       └────────────────────────────┘                          │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐      │
│  │  Chris (RTE) │   │  Raj (IT)    │   │  James (EM)  │      │
│  │  (Program)   │   │  (Security)  │   │  (Peer EM)   │      │
│  └──────────────┘   └──────────────┘   └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

**Key Relationships:**
- **David → Alex:** Sponsors coaching program; receives transformation reports
- **Alex → Priya:** Coaches Scrum Masters; multiplies impact through them
- **Sarah → Priya:** Manages SMs; uses data for team health decisions
- **Priya → Jordan:** Facilitates ceremonies; ensures psychological safety
- **Maya → Priya:** Partners on sprint reviews; connects retro insights to roadmap
- **Chris → Priya:** Coordinates cross-team dependencies; uses retro data for PI planning
- **Raj → All:** Evaluates and approves the platform for enterprise use

---

## 6. Design Principles <a name="design-principles"></a>

Based on the personas and journeys above, the following principles should guide every product decision:

### 1. Anonymity Is Non-Negotiable
Jordan's trust depends on it. Anonymity must be the default, technically enforced (not just UI-level), and explained in plain language. If Jordan doesn't trust it, the platform gets polite noise instead of honest signal.

### 2. Actions Must Outlive the Ceremony
Priya's effectiveness depends on action follow-through. Actions created in a retro must persist across sprints, surface in the next retro's pre-read, and be traceable to completion. A retro without follow-through is a complaint session.

### 3. Setup Time = Trust Erosion
Every minute Priya spends configuring boards is a minute the team waits and trust erodes. The platform must remember, pre-populate, and automate. Setup should take < 5 minutes.

### 4. Data Must Flow Upward
Individual cards serve Jordan. Clusters serve Priya. Trends serve Alex. Org patterns serve David. The same data must serve all four levels without manual re-aggregation.

### 5. Governance ≠ Surveillance
Alex needs to see patterns. Priya needs to own her board. The platform must make aggregate data visible without making individual teams feel watched. The SM is the owner of their board; the coach sees the landscape.

### 6. Zero-Friction Participation
Jordan should never need to create an account, remember a password, or learn a new interface to submit feedback. The barrier to participation must be indistinguishable from zero.

### 7. Prove the Loop Closes
The most powerful feature is the one that shows Jordan: "You said something. Here's what happened." The feedback loop — from submission to action to completion — must be visible and satisfying.

---

*End of Document*
