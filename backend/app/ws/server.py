"""WebSocket server for real-time Yjs CRDT sync."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import asyncpg
import structlog
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
import y_py as Y

from app.core.config import settings
from app.core.security import verify_token

logger = structlog.get_logger()

router = APIRouter()

# ── Room Management ────────────────────────────────────────────────────────────

@dataclass
class Participant:
    user_id: str
    display_name: str
    websocket: WebSocket
    cursor: dict | None = None
    connected_at: float = field(default_factory=time.time)


@dataclass
class CeremonyRoom:
    ceremony_id: str
    participants: dict[str, Participant] = field(default_factory=dict)
    doc: Y.YDoc = field(default_factory=Y.YDoc)
    last_saved: float = 0
    save_task: asyncio.Task | None = None

    async def broadcast_binary(self, data: bytes, exclude: str | None = None):
        """Broadcast binary Yjs sync data to all participants."""
        for uid, participant in self.participants.items():
            if uid == exclude:
                continue
            try:
                await participant.websocket.send_bytes(data)
            except Exception:
                pass

    async def broadcast_presence(self):
        """Broadcast presence update to all participants."""
        presence = {
            "type": "presence",
            "participants": [
                {
                    "user_id": p.user_id,
                    "display_name": p.display_name,
                    "cursor": p.cursor,
                }
                for p in self.participants.values()
            ],
        }
        data = json.dumps(presence).encode()
        for participant in self.participants.values():
            try:
                await participant.websocket.send_bytes(b"\x02" + data)
            except Exception:
                pass


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, CeremonyRoom] = {}

    def get_or_create(self, ceremony_id: str) -> CeremonyRoom:
        if ceremony_id not in self._rooms:
            self._rooms[ceremony_id] = CeremonyRoom(ceremony_id=ceremony_id)
        return self._rooms[ceremony_id]

    def get(self, ceremony_id: str) -> CeremonyRoom | None:
        return self._rooms.get(ceremony_id)

    def remove_participant(self, ceremony_id: str, user_id: str):
        room = self._rooms.get(ceremony_id)
        if not room:
            return
        room.participants.pop(user_id, None)
        if not room.participants:
            if room.save_task:
                room.save_task.cancel()
            del self._rooms[ceremony_id]


room_manager = RoomManager()


# ── Document Persistence ──────────────────────────────────────────────────────

async def load_document(ceremony_id: str, doc: Y.YDoc):
    """Load Yjs document state from PostgreSQL."""
    pool = await asyncpg.create_pool(settings.DATABASE_URL.replace("+asyncpg", ""))
    try:
        row = await pool.fetchrow(
            "SELECT doc_state FROM yjs_documents WHERE ceremony_id = $1",
            ceremony_id,
        )
        if row and row["doc_state"]:
            Y.apply_update(doc, bytes(row["doc_state"]))
            logger.info("yjs.loaded", ceremony_id=ceremony_id)
    finally:
        await pool.close()


async def save_document(ceremony_id: str, doc: Y.YDoc):
    """Save Yjs document state to PostgreSQL."""
    update = Y.encode_state_as_update(doc)
    pool = await asyncpg.create_pool(settings.DATABASE_URL.replace("+asyncpg", ""))
    try:
        await pool.execute(
            """
            INSERT INTO yjs_documents (ceremony_id, doc_state, updated_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (ceremony_id)
            DO UPDATE SET doc_state = $2, updated_at = NOW()
            """,
            ceremony_id,
            update,
        )
        logger.info("yjs.saved", ceremony_id=ceremony_id)
    finally:
        await pool.close()


# ── WebSocket Endpoint ────────────────────────────────────────────────────────

@router.websocket("/ceremony/{ceremony_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ceremony_id: str,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time ceremony board sync."""
    # Authenticate
    try:
        user = await verify_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept(subprotocol="yjs")

    # Get or create room
    room = room_manager.get_or_create(ceremony_id)

    # Load document if first participant
    if len(room.participants) == 0:
        await load_document(ceremony_id, room.doc)

    # Register participant
    participant = Participant(
        user_id=user.id,
        display_name=user.email.split("@")[0],
        websocket=websocket,
    )
    room.participants[user.id] = participant

    # Broadcast user joined
    await room.broadcast_presence()

    # Send initial sync state
    state_vector = Y.encode_state_vector(room.doc)
    await websocket.send_bytes(b"\x01" + state_vector)

    try:
        while True:
            data = await websocket.receive_bytes()
            if not data:
                continue

            # Yjs sync message
            if data[0:1] == b"\x01":
                update = data[1:]
                Y.apply_update(room.doc, update)
                await room.broadcast_binary(data, exclude=user.id)

                # Debounced save
                now = time.time()
                if now - room.last_saved > 2.0:
                    room.last_saved = now
                    if room.save_task:
                        room.save_task.cancel()
                    room.save_task = asyncio.create_task(
                        _debounced_save(ceremony_id, room.doc)
                    )

            # Presence update
            elif data[0:1] == b"\x02":
                msg = json.loads(data[1:])
                if "cursor" in msg:
                    participant.cursor = msg["cursor"]
                await room.broadcast_presence()

    except WebSocketDisconnect:
        pass
    finally:
        room_manager.remove_participant(ceremony_id, user.id)
        await room.broadcast_presence()


async def _debounced_save(ceremony_id: str, doc: Y.YDoc):
    """Save document after debounce period."""
    await asyncio.sleep(2.0)
    await save_document(ceremony_id, doc)
