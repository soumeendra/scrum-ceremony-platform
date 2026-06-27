#!/usr/bin/env python3
"""
Agent Skill: Peek Database

Returns schema and sample rows for any table.
Usage: python scripts/agent_tools/peek_db.py [table_name]
"""

import asyncio
import os
import sys

import asyncpg


async def peek_table(table_name: str):
    """Show schema and 5 sample rows."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://scp_user:scp_dev_password@localhost:5432/scp_platform"
    )

    conn = await asyncpg.connect(database_url)
    try:
        # Get columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        """, table_name)

        if not columns:
            print(f"Table '{table_name}' not found")
            return

        print(f"\n📊 Table: {table_name}")
        print(f"{'='*60}")
        print(f"{'Column':<25} {'Type':<20} {'Nullable':<10} {'Default'}")
        print(f"{'-'*60}")
        for col in columns:
            print(f"{col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']:<10} {col['column_default'] or ''}")

        # Get sample rows
        rows = await conn.fetch(f"SELECT * FROM {table_name} LIMIT 5")
        print(f"\n📋 Sample rows ({len(rows)}):")
        if rows:
            for i, row in enumerate(rows, 1):
                print(f"  Row {i}: {dict(row)}")
        else:
            print("  (empty table)")

        # Get row count
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
        print(f"\n📊 Total rows: {count}")

    finally:
        await conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/agent_tools/peek_db.py [table_name]")
        print("Example: python scripts/agent_tools/peek_db.py board_items")
        sys.exit(1)

    asyncio.run(peek_table(sys.argv[1]))
