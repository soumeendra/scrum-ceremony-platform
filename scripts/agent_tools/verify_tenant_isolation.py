#!/usr/bin/env python3
"""
Domain-Specific Guardrail: Tenant Isolation Verification

Ensures all database queries include tenant_id filtering.
Scans API routes and service layer for potential cross-tenant data leaks.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
BACKEND = ROOT / "backend"

ERRORS = []


def check_api_routes():
    """Verify all API routes enforce tenant isolation."""
    api_dir = BACKEND / "app" / "api"
    if not api_dir.exists():
        print("⚠️  API directory not found — skipping")
        return

    for py_file in api_dir.rglob("*.py"):
        content = py_file.read_text()
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for database queries without tenant_id
            if any(kw in line.lower() for kw in ["db.query", "session.execute", "select("]):
                # Check surrounding context for tenant_id
                context = "\n".join(lines[max(0, i-5):min(len(lines), i+5)])
                if "tenant_id" not in context:
                    ERRORS.append(
                        f"❌ {py_file}:{i}: Database query without tenant_id in context\n"
                        f"   Line: {line.strip()}"
                    )


def check_service_layer():
    """Verify service layer always sets tenant context."""
    services_dir = BACKEND / "app" / "services"
    if not services_dir.exists():
        print("⚠️  Services directory not found — skipping")
        return

    for py_file in services_dir.rglob("*.py"):
        content = py_file.read_text()

        # Check for get_db or session usage without set_tenant_context
        if "get_db" in content or "async with" in content:
            if "set_tenant_context" not in content and "tenant_id" not in content:
                ERRORS.append(
                    f"❌ {py_file}: Database session used without setting tenant context"
                )


def check_rls_policies():
    """Verify RLS policies exist for tenant-scoped tables."""
    migrations_dir = BACKEND / "migrations" / "versions"
    if not migrations_dir.exists():
        print("⚠️  Migrations directory not found — skipping")
        return

    # Check for RLS policy creation in migrations
    migration_files = list(migrations_dir.glob("*.py"))
    rls_found = False

    for f in migration_files:
        content = f.read_text()
        if "ROW LEVEL SECURITY" in content or "rls" in content.lower():
            rls_found = True
            break

    if not rls_found and migration_files:
        ERRORS.append(
            "⚠️  No RLS policy migrations found — tenant isolation not enforced at DB level"
        )


def main():
    print("🔬 Running Tenant Isolation Guardrail...\n")

    check_api_routes()
    check_service_layer()
    check_rls_policies()

    if ERRORS:
        print("\n".join(ERRORS))
        print(f"\n❌ {len(ERRORS)} tenant isolation concern(s) found")
        sys.exit(1)
    else:
        print("✅ All queries properly scoped by tenant_id")
        sys.exit(0)


if __name__ == "__main__":
    main()
