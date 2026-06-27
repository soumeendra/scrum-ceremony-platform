"""Seed script for default retrospective templates.

Creates 5 built-in retro templates that are available to all organizations.
Idempotent — safe to run multiple times. Skips templates that already exist.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

# Add parent package to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.template import Template


# ── Default Templates ──────────────────────────────────────────────────────────

DEFAULT_TEMPLATES: list[dict] = [
    {
        "name": "Start / Stop / Continue",
        "description": "Classic retro format: what to start doing, stop doing, and continue doing.",
        "ceremony_type": "retrospective",
        "phases": ["collect", "cluster", "vote", "action"],
        "columns": ["Start", "Stop", "Continue"],
        "scope": "org",
        "is_locked": True,
        "is_default": True,
    },
    {
        "name": "Mad / Sad / Glad",
        "description": "Emotion-based retro: what made you mad, sad, or glad.",
        "ceremony_type": "retrospective",
        "phases": ["collect", "cluster", "vote", "action"],
        "columns": ["Mad", "Sad", "Glad"],
        "scope": "org",
        "is_locked": True,
        "is_default": True,
    },
    {
        "name": "4Ls",
        "description": "Liked, Learned, Lacked, Longed For — a comprehensive team reflection.",
        "ceremony_type": "retrospective",
        "phases": ["collect", "cluster", "vote", "action"],
        "columns": ["Liked", "Learned", "Lacked", "Longed For"],
        "scope": "org",
        "is_locked": True,
        "is_default": True,
    },
    {
        "name": "Sailboat",
        "description": "Visual retro: wind pushes you forward, anchors hold back, rocks are risks, island is the goal.",
        "ceremony_type": "retrospective",
        "phases": ["collect", "cluster", "vote", "action"],
        "columns": ["Wind (helping)", "Anchors (holding back)", "Rocks (risks)", "Island (goal)"],
        "scope": "org",
        "is_locked": True,
        "is_default": True,
    },
    {
        "name": "What Went Well / What Didn't / Ideas",
        "description": "Simple retro: celebrate wins, identify issues, brainstorm improvements.",
        "ceremony_type": "retrospective",
        "phases": ["collect", "cluster", "vote", "action"],
        "columns": ["What Went Well", "What Didn't Go Well", "Ideas / Actions"],
        "scope": "org",
        "is_locked": True,
        "is_default": True,
    },
]


async def seed_templates() -> None:
    """Insert default templates if they don't already exist."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        for tmpl_data in DEFAULT_TEMPLATES:
            # Check if template with this name already exists
            stmt = select(Template).where(
                Template.name == tmpl_data["name"],
                Template.is_default == True,
            )
            result = (await session.execute(stmt)).scalars().first()

            if result is not None:
                print(f"  SKIP: '{tmpl_data['name']}' already exists (id={result.id})")
                continue

            template = Template(
                name=tmpl_data["name"],
                description=tmpl_data["description"],
                ceremony_type=tmpl_data["ceremony_type"],
                structure=json.dumps({
                    "phases": tmpl_data["phases"],
                    "columns": tmpl_data["columns"],
                    "scope": tmpl_data["scope"],
                    "is_locked": tmpl_data["is_locked"],
                }),
                is_default=tmpl_data["is_default"],
            )
            session.add(template)
            print(f"  CREATE: '{tmpl_data['name']}'")

        await session.commit()
        print("\nSeed complete.")

    await engine.dispose()


if __name__ == "__main__":
    print("Seeding default retrospective templates...")
    asyncio.run(seed_templates())
