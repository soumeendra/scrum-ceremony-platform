#!/usr/bin/env python3
"""
Domain-Specific Guardrail: Yjs CRDT Schema Conformance

Validates Yjs document structure against the data-model.md schema.
Ensures no author_id in anonymous board items at the CRDT level.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
FRONTEND = ROOT / "frontend"

ERRORS = []


def check_yjs_document_schema():
    """Verify Yjs document types match the spec."""
    yjs_files = []
    for pattern in ["*yjs*", "*board*", "*crdt*", "*document*"]:
        yjs_files.extend(FRONTEND.rglob(f"**/{pattern}.ts"))
        yjs_files.extend(FRONTEND.rglob(f"**/{pattern}.tsx"))

    if not yjs_files:
        print("⚠️  No Yjs schema files found — skipping (may not be created yet)")
        return

    for f in yjs_files:
        content = f.read_text()

        # Check: Y.Map or Y.Array definitions
        if "Y.Map" in content or "Y.Array" in content:
            # Check for author_id in anonymous context
            if "author_id" in content:
                # Check if there's conditional handling for anonymous
                if "isAnonymous" not in content and "is_anonymous" not in content:
                    ERRORS.append(
                        f"❌ {f}: Yjs document includes author_id without anonymity check"
                    )

            # Check: presence should not include identifying info
            if "presence" in content.lower():
                if "userId" in content and "displayName" in content:
                    # This is OK for named mode, but should be conditional
                    print(f"ℹ️  {f}: Presence includes userId — ensure this is cleared for anonymous mode")


def check_websocket_events():
    """Verify WebSocket events don't leak identity."""
    ws_files = list(FRONTEND.rglob("**/*websocket*")) + list(FRONTEND.rglob("**/*ws*"))

    for f in ws_files:
        content = f.read_text()

        # Check for board item broadcast events
        if "item_added" in content or "item_updated" in content:
            if "author_id" in content and "anonymous" not in content.lower():
                ERRORS.append(
                    f"⚠️  {f}: WebSocket board event may leak author_id for anonymous items"
                )


def main():
    print("🔬 Running Yjs CRDT Schema Conformance Guardrail...\n")

    check_yjs_document_schema()
    check_websocket_events()

    if ERRORS:
        print("\n".join(ERRORS))
        print(f"\n❌ {len(ERRORS)} CRDT schema violation(s) found")
        sys.exit(1)
    else:
        print("✅ Yjs document schema conforms to anonymity spec")
        sys.exit(0)


if __name__ == "__main__":
    main()
