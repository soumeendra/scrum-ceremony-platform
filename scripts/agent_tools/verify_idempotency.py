#!/usr/bin/env python3
"""
Domain-Specific Guardrail: Idempotency Key Verification

Ensures all integration sync operations include idempotency keys.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
INTEGRATION_SERVICE = ROOT / "integration-service"

ERRORS = []


def check_integration_idempotency():
    """Verify all external API calls have idempotency keys."""
    if not INTEGRATION_SERVICE.exists():
        print("⚠️  Integration service not found — skipping")
        return

    for py_file in INTEGRATION_SERVICE.rglob("*.py"):
        content = py_file.read_text()

        # Check for HTTP calls to external services
        external_calls = re.findall(r'(requests\.|httpx\.|aiohttp\.)(get|post|put|patch|delete)', content)

        if external_calls:
            # Check for idempotency key in headers
            if "idempotency" not in content.lower() and "idempotency_key" not in content:
                ERRORS.append(
                    f"❌ {py_file}: External API calls without idempotency keys"
                )

            # Check for retry logic
            if "retry" not in content.lower() and "backoff" not in content.lower():
                ERRORS.append(
                    f"⚠️  {py_file}: External API calls without retry/backoff logic"
                )


def check_stripe_webhook_verification():
    """Verify Stripe webhook signature verification."""
    stripe_files = list(INTEGRATION_SERVICE.rglob("*stripe*"))

    for f in stripe_files:
        content = f.read_text()
        if "webhook" in content.lower() and "signature" in content.lower():
            if "verify" not in content.lower() and "hmac" not in content.lower():
                ERRORS.append(
                    f"❌ {f}: Stripe webhook without signature verification"
                )


def main():
    print("🔬 Running Idempotency Key Guardrail...\n")

    check_integration_idempotency()
    check_stripe_webhook_verification()

    if ERRORS:
        print("\n".join(ERRORS))
        print(f"\n❌ {len(ERRORS)} idempotency concern(s) found")
        sys.exit(1)
    else:
        print("✅ All integration operations have proper idempotency")
        sys.exit(0)


if __name__ == "__main__":
    main()
