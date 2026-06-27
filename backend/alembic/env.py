"""Alembic migration environment.

Supports both offline (SQL generation) and online (direct DB connection) modes.
Uses async engine for compatibility with the application's asyncpg driver.
"""

from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig
from typing import Any

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Ensure the project root is on sys.path so `app` package resolves
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Alembic Config object
config = context.config

# ── Import all models so autogenerate can detect them ─────────────────────────
from app.models import *  # noqa: F401,F403 — imports every ORM model
from app.models.base import Base  # noqa: E402

target_metadata = Base.metadata

# ── Logging ────────────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Database URL from environment ─────────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://localhost:5432/scrum_ceremony",
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def get_url() -> str:
    """Return the database URL, converting to sync psycopg2 if needed for alembic."""
    url = config.get_main_option("sqlalchemy.url")
    # Alembic works with sync drivers; convert asyncpg URL to psycopg2 for online mode
    if url and url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    return url


# ── Object inclusion policy for RLS ───────────────────────────────────────────
# Prevent autogenerate from dropping RLS policies and triggers that exist in the
# database but are not reflected in the ORM models.
def include_object(
    object: Any,
    name: str,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Filter objects during autogenerate — preserve RLS policies and triggers."""
    if type_ == "policy" or type_ == "trigger":
        # Don't drop RLS policies/triggers managed by migration 002_rls_policies
        return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL script."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_migrations(connection: Connection) -> None:
    """Callback to run migrations with a live connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    # Use sync psycopg2 URL for alembic's online mode
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
