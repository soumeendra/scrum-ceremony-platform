#!/usr/bin/env python3
"""
Agent Skill: Check Anonymity

Verifies anonymity invariants for a specific ceremony or globally.
Usage: python scripts/agent_tools/check_anonymity.py [ceremony_id]
"""

import asyncio
import os
import sys
from uuid import UUID

import asyncpg


async def check_ceremony_anonymity(ceremony_id: str):
    """Check anonymity integrity for a specific ceremony."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://scp_user:***@localhost:5432/scp_platform"
    )

    conn = await asyncpg.connect(database_url)
    try:
        # Check: no anonymous board items have author_id set
        leaks = await conn.fetch("""
            SELECT id, text, is_anonymous, author_id
            FROM board_items
            WHERE ceremony_id = $1
              AND is_anonymous = TRUE
              AND author_id IS NOT NULL
        """, UUID(ceremony_id))

        if leaks:
            print(f"❌ ANONYMITY BREACH: {len(leaks)} anonymous items have author_id set!")
            for leak in leaks:
                print(f"   Item {leak['id']}: author_id={leak['author_id']}")
            return False

        # Check: all anonymous items have entry in anonymous_author_map
        missing_map = await conn.fetch("""
            SELECT bi.id
            FROM board_items bi
            LEFT JOIN anonymous_author_map aam ON aam.board_item_id = bi.id
            WHERE bi.ceremony_id = $1
              AND bi.is_anonymous = TRUE
              AND aam.id IS NULL
        """, UUID(ceremony_id))

        if missing_map:
            print(f"⚠️  {len(missing_map)} anonymous items missing from author map")
            return False

        # Stats
        total = await conn.fetchval(
            "SELECT COUNT(*) FROM board_items WHERE ceremony_id = $1", UUID(ceremony_id)
        )
        anon = await conn.fetchval(
            "SELECT COUNT(*) FROM board_items WHERE ceremony_id = $1 AND is_anonymous = TRUE",
            UUID(ceremony_id)
        )

        print(f"✅ Ceremony {ceremony_id}: Anonymity intact")
        print(f"   Total items: {total}, Anonymous: {anon}, Named: {total - anon}")
        return True

    finally:
        await conn.close()


async def check_global_anonymity():
    """Check anonymity integrity across all ceremonies."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://scp_user:***@localhost:5432/scp_platform"
    )

    conn = await asyncpg.connect(database_url)
    try:
        # Global check: any anonymous items with author_id
        leaks = await conn.fetch("""
            SELECT COUNT(*) as leak_count
            FROM board_items
            WHERE is_anonymous = TRUE AND author_id IS NOT NULL
        """)

        leak_count = leaks[0]['leak_count'] if leaks else 0

        if leak_count > 0:
            print(f"❌ GLOBAL ANONYMITY BREACH: {leak_count} items leaking author_id")
            return False

        # Stats
        total = await conn.fetchval("SELECT COUNT(*) FROM board_items")
        anon = await conn.fetchval("SELECT COUNT(*) FROM board_items WHERE is_anonymous = TRUE")

        print(f"✅ Global anonymity check passed")
        print(f"   Total items: {total}, Anonymous: {anon}, Named: {total - anon}")
        return True

    finally:
        await conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = asyncio.run(check_ceremony_anonymity(sys.argv[1]))
    else:
        result = asyncio.run(check_global_anonymity())

    sys.exit(0 if result else 1)
