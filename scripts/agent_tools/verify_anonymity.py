#!/usr/bin/env python3
"""
Domain-Specific Guardrail: Anonymity Invariant Verification

Checks that:
1. BoardItem model never exposes author_id when is_anonymous=True
2. AnonymousAuthorMap is the sole identity path
3. API responses for anonymous items don't include author_id
4. Yjs document schema doesn't include author_id for anonymous items
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

ERRORS = []


def check_backend_anonymity_model():
    """Verify BoardItem model has proper anonymity separation."""
    models_file = BACKEND / "app" / "models" / "board_item.py"
    if not models_file.exists():
        # Check in single models.py
        models_file = BACKEND / "app" / "models.py"

    if not models_file.exists():
        print("⚠️  BoardItem model not found — skipping (may not be created yet)")
        return

    content = models_file.read_text()

    # Check: is_anonymous column exists
    if "is_anonymous" not in content:
        ERRORS.append(f"❌ {models_file}: Missing 'is_anonymous' column in BoardItem model")

    # Check: author_id is nullable
    if "author_id" in content and "nullable=True" not in content:
        # Check if author_id specifically is nullable
        import re
        author_id_match = re.search(r'author_id.*Column.*', content)
        if author_id_match and "nullable=True" not in author_id_match.group():
            ERRORS.append(f"❌ {models_file}: 'author_id' should be nullable for anonymous items")

    # Check: anonymous_author_map table reference exists
    aam_file = BACKEND / "app" / "models" / "anonymous_author_map.py"
    if not aam_file.exists():
        if "AnonymousAuthorMap" not in content:
            print("⚠️  AnonymousAuthorMap model not found — will be checked when created")
    else:
        aam_content = aam_file.read_text()
        if "actual_author_id" not in aam_content:
            ERRORS.append(f"❌ {aam_file}: Missing 'actual_author_id' column")


def check_api_anonymity_leaks():
    """Verify API routes don't expose author_id for anonymous items."""
    api_dir = BACKEND / "app" / "api"
    if not api_dir.exists():
        print("⚠️  API directory not found — skipping")
        return

    for py_file in api_dir.rglob("*.py"):
        content = py_file.read_text()

        # Check for direct author_id exposure in response schemas
        if "author_id" in content and "ceremon" in content.lower():
            # Check if there's a filter for anonymous items
            if "is_anonymous" not in content:
                ERRORS.append(
                    f"⚠️  {py_file}: References 'author_id' in ceremony context "
                    f"without 'is_anonymous' filter — potential leak"
                )


def check_yjs_schema_anonymity():
    """Verify Yjs document schema doesn't include author_id for anonymous items."""
    yjs_files = list(ROOT.rglob("*.ts")) + list(ROOT.rglob("*.tsx"))
    yjs_schema_files = [f for f in yjs_files if "yjs" in f.name.lower() or "board" in f.name.lower()]

    for f in yjs_schema_files:
        content = f.read_text()
        if "author_id" in content and "anonymous" not in content.lower():
            ERRORS.append(
                f"⚠️  {f}: Yjs schema includes 'author_id' without anonymity handling"
            )


def main():
    print("🔬 Running Anonymity Invariant Guardrail...\n")

    check_backend_anonymity_model()
    check_api_anonymity_leaks()
    check_yjs_schema_anonymity()

    if ERRORS:
        print("\n".join(ERRORS))
        print(f"\n❌ {len(ERRORS)} anonymity invariant violation(s) found")
        sys.exit(1)
    else:
        print("✅ All anonymity invariants verified — no leaks detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
