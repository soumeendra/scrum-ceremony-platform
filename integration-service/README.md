# Integration Service — Scrum Ceremony Platform

## Overview
Handles all external system integrations through a connector pattern with:
- Idempotency guarantees
- Circuit breaker for fault tolerance
- Dead-letter queue for failed syncs
- Exponential backoff retry

## Connectors

### Jira Cloud Connector
- OAuth 2.0 with PKCE authentication
- Push: Create Jira issues from actions (field mapping: project, issue type, assignee, sprint, labels)
- Pull: Sync Jira issue status back to action status
- Rate limiting: Token bucket adaptive strategy
- Webhook support for real-time updates

### ERPNext Connector
- REST API with API key + secret authentication
- Custom doctypes: SCP Team, SCP Subscription, SCP Plan, SCP Usage Metric
- Sync flows: trial→lead, paid→customer, plan change→order, payment→invoice, usage metrics
- Frappe framework considerations: CSRF handling, rate limits

### Stripe Webhook Handler
- HMAC-SHA256 signature verification
- Events: checkout.session.completed, customer.subscription.updated, invoice.payment_failed, customer.subscription.deleted
- Feature gating enforcement on plan changes
- ERPNext invoice sync bridge

## Architecture
```
Event Source → Connector → Idempotency Check → External API → Success/Failure
                                        ↓ Failure
                                        Circuit Breaker → Dead Letter Queue → Retry Worker
```

## Configuration
- JIRA_BASE_URL, JIRA_CLIENT_ID, JIRA_CLIENT_SECRET
- ERPNEXT_URL, ERPNEXT_API_KEY, ERPNEXT_API_SECRET
- STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
- CIRCUIT_BREAKER_THRESHOLD — Failures before opening (default: 5)
- CIRCUIT_BREAKER_TIMEOUT — Seconds before half-open (default: 60)
- RETRY_MAX_ATTEMPTS — Max retry attempts (default: 3)
- RETRY_BACKOFF_BASE — Exponential backoff base in seconds (default: 2)
