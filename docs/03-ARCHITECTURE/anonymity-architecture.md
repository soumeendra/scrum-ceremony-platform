# Anonymity Architecture ⚠️ RED ZONE

**Document ID:** SCP-DOC-007  
**Version:** 1.0  
**Status:** Draft  
**Date:** 2026-06-26  
**Classification:** RED ZONE — Privacy engineering document. Every implementation decision must be reviewed by someone with security/privacy expertise before merge.

---

## 1. Design Principles

| # | Principle | Implication |
|---|-----------|-------------|
| 1 | **Identity never travels with content in anonymous mode** | Board item payloads, WebSocket events, and API responses NEVER contain author_id when anonymity is active |
| 2 | **Anonymity is per-phase, not per-ceremony** | A retro can have anonymous collection + named voting + named action ownership in one session |
| 3 | **Double-vote prevention without identity** | Use per-ceremony random voter tokens, not user IDs, in vote records |
| 4 | **Break-glass is audited** | Any access to the identity map is logged with actor, reason, and timestamp |
| 5 | **Retention honors deletion** | If a user requests data deletion, all their anonymous contributions are deleted even though the identity was separated |
| 6 | **No inference attacks** | Participation counts, typing patterns, and timing must not allow de-anonymization |

---

## 2. Anonymity Modes

### Per-Phase Configuration

| Phase | Default Mode | Rationale | Configurable? |
|-------|-------------|-----------|---------------|
| `collect` | **anonymous** | Maximize candor during idea submission | Yes → named for team-norm orgs |
| `cluster` | **system** | AI/facilitator operates on content only | No |
| `vote` | **anonymous** | Prevent bandwagon voting | Yes → named for transparent cultures |
| `discuss` | **named** | Accountability during discussion | Yes → anonymous for sensitive topics |
| `action` | **named** | Action owners MUST be identifiable | No (always named) |

### Anonymity Configuration Schema

```typescript
interface AnonymityConfig {
  collect: 'anonymous' | 'named';
  vote: 'anonymous' | 'named';
  discuss: 'anonymous' | 'named';
  action: 'named'; // ALWAYS named — non-negotiable
  quietMode: boolean; // "Silent brainstorm" — notes hidden until reveal
  delayedReveal: boolean; // Notes appear only after collection phase ends
}
```

### Default Configuration (for most teams)

```typescript
const defaultAnonymity: AnonymityConfig = {
  collect: 'anonymous',
  vote: 'anonymous',
  discuss: 'named',
  action: 'named',
  quietMode: false,
  delayedReveal: false,
};
```

---

## 3. Dual-Path Data Architecture

### Path A: Display Content (Board Items)

This is what ALL users see — accessible via standard API.

```sql
SELECT id, text, column_id, group_id, color, reactions,
       is_anonymous, author_display, created_at
FROM board_items
WHERE ceremony_id = ?;
```

**Result when anonymous:** `author_display = "Anonymous"`, `author_id = NULL`

### Path B: Identity Map (Access-Controlled)

This is what ONLY org admins can access — under break-glass.

```sql
-- This table has ROW LEVEL SECURITY:
-- Only accessible when current_user_role = 'org_admin'
SELECT board_item_id, actual_author_id
FROM anonymous_author_map
WHERE ceremony_id = ?;
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    WRITE PATH                           │
│                                                         │
│  Participant submits note (anonymous: true)             │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────┐                            │
│  │   Ceremony Service      │                            │
│  │                         │                            │
│  │   IF anonymous:        │                            │
│  │     author_id = NULL   │──────────► board_items     │
│  │     author_display =   │           (display path)    │
│  │       "Anonymous"      │                            │
│  │                         │                            │
│  │     actual_author_id   │──────────► anonymous_      │
│  │       = current_user   │           author_map       │
│  │                         │           (identity path)  │
│  │   ELSE:                │                            │
│  │     author_id =        │──────────► board_items     │
│  │       current_user     │           (display path)    │
│  │     author_display =   │                            │
│  │       user.name        │                            │
│  └─────────────────────────┘                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    READ PATH                            │
│                                                         │
│  Standard API (facilitator, member):                    │
│    → Reads from board_items ONLY                       │
│    → NEVER sees anonymous_author_map                   │
│    → author_display = "Anonymous" for anon items       │
│                                                         │
│  Admin API (org_admin, break-glass):                    │
│    → Reads from both tables                            │
│    → Every read LOGGED to audit_events                 │
│    → Requires reason parameter in API call             │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Anti-Double-Vote: Voter Token System

### Problem
Anonymous voting must prevent the same person from voting twice, without storing their identity in the vote record.

### Solution: Per-Ceremony Voter Tokens

```
┌──────────────────────────────────────────────────────────┐
│  When a participant joins a ceremony:                    │
│                                                          │
│    voter_token = UUID4()  (random, per ceremony)        │
│    STORE in Redis:                                       │
│      ceremony:{id}:voter_tokens:{user_id} = voter_token │
│    SEND to client:                                       │
│      voter_token (stored in browser session)             │
│                                                          │
│  When a participant votes:                               │
│    POST /ceremony/{id}/vote                              │
│      { item_id: "...", voter_token: "..." }             │
│                                                          │
│  Vote table stores:                                      │
│    item_id, voter_token, weight                         │
│    (NOT user_id)                                         │
│                                                          │
│  UNIQUE constraint on (item_id, voter_token)             │
│    → prevents double-voting                              │
│                                                          │
│  Participation verification:                             │
│    Redis lookup: voter_token → user_id                  │
│    (Used only for participation counting, never exposed) │
└──────────────────────────────────────────────────────────┘
```

### Voter Token Lifecycle

| Event | Action |
|-------|--------|
| Participant joins ceremony | Generate token, store in Redis + send to client |
| Participant votes | Verify token exists in Redis, accept vote |
| Ceremony completes | Delete all tokens from Redis for this ceremony |
| Participant disconnects + reconnects | Re-issue same token (lookup by user_id) |
| Ceremony archived | Tokens already deleted, no PII retained |

---

## 5. Quiet Mode (Silent Brainstorm)

Inspired by Mentimeter's staged interaction pattern.

### How It Works

1. Facilitator enables `quietMode: true` before starting collection
2. Participants submit notes — each note visible ONLY to its author
3. No participant can see other participants' notes during collection
4. When facilitator advances to cluster phase → ALL notes are revealed simultaneously
5. This prevents anchoring bias and social conformity effects

### Implementation

```typescript
// During collection phase, WebSocket broadcast is filtered
function onNoteAdded(note: BoardItem, socket: WebSocket) {
  if (ceremony.anonymityConfig.quietMode && ceremony.currentPhase === 'collect') {
    // Send ONLY to the author
    if (socket.userId === note.authorId || socket.userId === ceremony.facilitatorId) {
      socket.send({ type: 'item_added', item: note });
    } else {
      // Don't send — note is private until reveal
    }
    
    // Send count update to all (so they know others are contributing)
    broadcast({ type: 'collection_count', count: totalNotes });
  }
}
```

**Facilitator can always see all notes** — even during quiet mode, for moderation purposes.

---

## 6. Delayed Reveal

Similar to quiet mode but less strict.

| Setting | During Collection | After Collection |
|---------|------------------|-----------------|
| Neither | All notes visible immediately | — |
| `quietMode` only | Each person sees ONLY their own notes | All revealed at once |
| `delayedReveal` only | Notes appear but without names | Names still hidden |
| Both | Each person sees ONLY their own notes | All revealed, names still hidden |

---

## 7. Inference Attack Defenses

### Risks and Mitigations

| Attack | Risk Level | Mitigation |
|--------|-----------|------------|
| **Timing correlation** — matching note submission time to user activity | Medium | Batch note submissions with random 0-2 second delay before broadcast |
| **Participation count** — if one person's activity pattern reveals identity | Low | Show only aggregate counts, never per-user activity during anonymous phase |
| **Typing style** — distinctive writing reveals author | Low-Medium | Beyond scope for v1; document as known limitation; AI rephrasing could be future feature |
| **Small group** — with 3 people, elimination reveals author | Medium | Minimum team size of 5 for anonymous mode; warn facilitator if team < 5 |
| **Vote clustering** — senior person's votes predict their notes | Low | Anonymous voting means votes are not attributable to individuals |
| **Cursor/presence** — watching someone type in real-time | High | Quiet mode disables cursor visibility; presence shows only count, not who |

---

## 8. GDPR / Right to Deletion

### Problem: Deleting anonymous contributions

When a user requests account deletion (GDPR Art. 17), we must delete ALL their data — including anonymous contributions. But how do we find "all board items by user X" when `board_items.author_id = NULL`?

### Solution: Identity map is the deletion index

```
DELETE FLOW:

1. User requests account deletion
2. Query anonymous_author_map WHERE actual_author_id = ${user_id}
3. For each board_item_id found:
     DELETE FROM board_items WHERE id = board_item_id
     DELETE FROM anonymous_author_map WHERE board_item_id = board_item_id
4. Delete all named contributions:
     DELETE FROM board_items WHERE author_id = ${user_id}
5. Delete votes:
     DELETE FROM votes WHERE voter_id = ${user_id}
6. Delete user account
7. Log audit event: "user.account_deleted"
```

**Critical:** The identity map MUST be retained until deletion is complete. It cannot be purged on ceremony completion — it must persist for the data retention period (typically 90 days for audit, configurable per org).

---

## 9. Data Retention

| Data | Default Retention | Configurable? | Reason |
|------|------------------|---------------|--------|
| `board_items` (display) | 2 years | Yes | Historical retro data for analytics |
| `anonymous_author_map` | 90 days | Yes (min 30) | Audit trail; PII minimization |
| `votes` (voter_token only) | Deleted on ceremony complete | No | No reason to retain |
| Redis voter tokens | Deleted on ceremony complete | No | Ephemeral by design |
| `audit_events` (anonymity break) | 7 years | No | Compliance requirement |

### Automated Purge Job

```python
# Celery/ARQ task: runs daily
async def purge_expired_anonymity_mappings():
    """Delete anonymous_author_map rows older than retention period."""
    retention_days = await get_org_setting('anonymity_retention_days', default=90)
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    
    deleted = await db.execute(
        delete(AnonymousAuthorMap)
        .where(AnonymousAuthorMap.created_at < cutoff)
    )
    
    logger.info(f"Purged {deleted} expired anonymity mappings")
```

---

## 10. Penetration Test Checklist

Before launch, the anonymity system MUST pass these security tests:

- [ ] **API test:** Anonymous note API response contains NO author_id, email, or identifiable fields
- [ ] **WebSocket test:** Real-time events for anonymous notes contain NO author identity
- [ ] **Database test:** Direct SQL query on board_items returns NULL author_id for anonymous items
- [ ] **RLS test:** Non-admin user querying anonymous_author_map gets 0 rows
- [ ] **Audit test:** Every break-glass access is logged with actor, timestamp, and reason
- [ ] **Double-vote test:** Same voter_token voting twice on same item returns 409
- [ ] **Token uniqueness test:** Different users get different voter tokens in same ceremony
- [ ] **Deletion test:** Account deletion removes all anonymous contributions
- [ ] **Retention test:** Purge job deletes mappings older than retention period
- [ ] **Quiet mode test:** Non-author non-facilitator cannot see notes during quiet mode collection
- [ ] **Inference test:** Participation metrics do not leak per-user activity during anonymous phases

---

*This document is the authoritative specification for anonymity implementation. All code that touches the anonymity system is RED ZONE and requires security review before merge.*
