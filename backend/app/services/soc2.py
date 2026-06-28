"""SOC 2 Type 2 readiness — controls mapping and evidence collection."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger()


# ── SOC 2 Trust Service Criteria ─────────────────────────────────────────────

SOC2_CONTROLS = {
    "CC6.1": {
        "name": "Logical Access Controls",
        "description": "Enforce least-privilege access to systems and data",
        "status": "implemented",
        "evidence": [
            "Clerk SSO/SAML authentication",
            "Row-level security in PostgreSQL",
            "Role-based access control (org_admin, workspace_admin, facilitator, member, viewer)",
            "JWT validation on all API endpoints",
        ],
    },
    "CC6.2": {
        "name": "Role Management",
        "description": "Manage user roles and permissions",
        "status": "implemented",
        "evidence": [
            "Role hierarchy with 5 levels",
            "Permission matrix enforced via middleware",
            "Role changes audited in audit_events table",
        ],
    },
    "CC6.3": {
        "name": "Least Privilege",
        "description": "Grant minimum necessary access",
        "status": "implemented",
        "evidence": [
            "Tenant isolation via RLS",
            "API endpoints scoped by role",
            "Anonymous contributions prevent identity exposure",
        ],
    },
    "CC7.1": {
        "name": "Incident Detection",
        "description": "Detect security incidents and anomalies",
        "status": "partial",
        "evidence": [
            "Sentry error tracking",
            "PostgreSQL audit logging",
            "CodeQL security scanning in CI",
        ],
        "gaps": [
            "No anomaly detection on user behavior",
            "No automated incident alerting",
        ],
    },
    "CC7.2": {
        "name": "Incident Response",
        "description": "Respond to and mitigate incidents",
        "status": "partial",
        "evidence": [
            "Runbooks for common failure scenarios",
            "Automated rollback on failed deploys",
        ],
        "gaps": [
            "No formal incident response plan documented",
            "No on-call rotation configured",
        ],
    },
    "CC8.1": {
        "name": "Change Management",
        "description": "Authorize and track system changes",
        "status": "implemented",
        "evidence": [
            "Git-based version control",
            "PR review required before merge",
            "CI pipeline with quality gates",
            "CodeQL security scan blocks merge on findings",
        ],
    },
    "CC9.1": {
        "name": "Risk Assessment",
        "description": "Identify and assess risks",
        "status": "partial",
        "evidence": [
            "Threat model documented in security-design.md",
            "STRIDE analysis completed",
        ],
        "gaps": [
            "No annual risk assessment process",
            "No third-party penetration test",
        ],
    },
}


class SOC2Service:
    """SOC 2 readiness tracking and evidence collection."""

    @staticmethod
    def get_readiness_summary() -> dict[str, Any]:
        """Get overall SOC 2 readiness status."""
        total = len(SOC2_CONTROLS)
        implemented = sum(
            1 for c in SOC2_CONTROLS.values() if c["status"] == "implemented"
        )
        partial = sum(
            1 for c in SOC2_CONTROLS.values() if c["status"] == "partial"
        )

        return {
            "total_controls": total,
            "implemented": implemented,
            "partial": partial,
            "not_started": total - implemented - partial,
            "readiness_percentage": round(implemented / total * 100, 1),
            "controls": SOC2_CONTROLS,
        }

    @staticmethod
    def get_control(control_id: str) -> dict[str, Any] | None:
        """Get details for a specific control."""
        return SOC2_CONTROLS.get(control_id)

    @staticmethod
    def collect_evidence(control_id: str) -> list[str]:
        """Collect evidence for a specific control."""
        control = SOC2_CONTROLS.get(control_id, {})
        return control.get("evidence", [])

    @staticmethod
    def get_gaps() -> list[dict[str, str]]:
        """Get all identified gaps across controls."""
        gaps = []
        for control_id, control in SOC2_CONTROLS.items():
            for gap in control.get("gaps", []):
                gaps.append({
                    "control_id": control_id,
                    "control_name": control["name"],
                    "gap": gap,
                })
        return gaps
