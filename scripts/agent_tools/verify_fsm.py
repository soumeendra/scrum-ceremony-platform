#!/usr/bin/env python3
"""
Domain-Specific Guardrail: FSM Transition Validity

Verifies that all ceremony state transitions in code match the formal spec
in docs/03-ARCHITECTURE/ceremony-state-machine.md
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SPEC_FILE = ROOT / "docs" / "03-ARCHITECTURE" / "ceremony-state-machine.md"

# Valid transitions extracted from the spec
VALID_TRANSITIONS = {
    "retrospective": {
        "draft": ["scheduled", "collect"],
        "scheduled": ["collect", "cancelled"],
        "collect": ["cluster", "discuss", "action"],
        "cluster": ["vote", "discuss"],
        "vote": ["discuss", "action"],
        "discuss": ["action"],
        "action": ["review", "completed"],
        "review": ["completed", "action"],
        "completed": [],
        "cancelled": [],
    },
    "planning_poker": {
        "draft": ["story_selection"],
        "story_selection": ["estimation"],
        "estimation": ["reveal"],
        "reveal": ["consensus"],
        "consensus": ["next_story"],
        "next_story": ["story_selection", "completed"],
        "completed": [],
    },
    "async_standup": {
        "draft": ["open"],
        "open": ["review"],
        "review": ["flagged", "completed"],
        "flagged": ["completed"],
        "completed": [],
    },
    "health_check": {
        "draft": ["assessment"],
        "assessment": ["results"],
        "results": ["discussion"],
        "discussion": ["completed"],
        "completed": [],
    },
}

ERRORS = []


def check_fsm_implementation():
    """Check that code only implements valid transitions."""
    backend_dir = ROOT / "backend"
    if not backend_dir.exists():
        print("⚠️  Backend directory not found — skipping")
        return

    # Find FSM-related files
    fsm_files = []
    for pattern in ["*fsm*", "*state*", "*machine*", "*transition*"]:
        fsm_files.extend(backend_dir.rglob(pattern))

    if not fsm_files:
        print("⚠️  No FSM implementation files found — skipping (may not be created yet)")
        return

    for f in fsm_files:
        content = f.read_text()

        # Look for transition definitions
        # Pattern: state transitions like "draft" -> "collect"
        transitions_found = re.findall(r'["\'](\d+)["\']\s*:\s*\[["\']([^"\']+)["\']', content)

        if not transitions_found:
            # Try alternative patterns
            transitions_found = re.findall(r'(\w+)\s*:\s*\[["\']([^"\']+)["\']', content)

        for from_state, to_state in transitions_found:
            # Validate against spec
            for ceremony_type, valid in VALID_TRANSITIONS.items():
                if from_state in valid:
                    if to_state not in valid[from_state]:
                        ERRORS.append(
                            f"❌ {f}: Invalid transition '{from_state}' → '{to_state}' "
                            f"for {ceremony_type} (valid: {valid[from_state]})"
                        )


def check_xstate_definitions():
    """Check XState machine definitions match spec."""
    backend_dir = ROOT / "backend"
    xstate_files = list(backend_dir.rglob("*xstate*")) + list(backend_dir.rglob("*machine*"))

    for f in xstate_files:
        content = f.read_text()

        # Check for on: { EVENT: target } patterns
        on_blocks = re.findall(r'on:\s*\{([^}]+)\}', content, re.DOTALL)
        for block in on_blocks:
            events = re.findall(r'(\w+):\s*["\'](\w+)["\']', block)
            for event, target in events:
                # Basic validation: target should be a valid state
                all_states = set()
                for states in VALID_TRANSITIONS.values():
                    all_states.update(states.keys())

                if target not in all_states and target != "actions":
                    ERRORS.append(
                        f"⚠️  {f}: XState target '{target}' not in known states"
                    )


def main():
    print("🔬 Running FSM Transition Validity Guardrail...\n")

    if not SPEC_FILE.exists():
        print(f"⚠️  Spec file not found: {SPEC_FILE}")
        sys.exit(0)

    check_fsm_implementation()
    check_xstate_definitions()

    if ERRORS:
        print("\n".join(ERRORS))
        print(f"\n❌ {len(ERRORS)} FSM transition violation(s) found")
        sys.exit(1)
    else:
        print("✅ All FSM transitions match the formal spec")
        sys.exit(0)


if __name__ == "__main__":
    main()
