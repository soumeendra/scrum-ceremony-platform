"use client";

import { useEffect, useState, useCallback } from "react";
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { useAuthToken } from "@/lib/auth";
import { useCeremonyStore } from "@/stores/ceremony-store";
import { BoardColumn } from "./BoardColumn";
import { BoardCard } from "./BoardCard";
import { AddNoteForm } from "./AddNoteForm";
import { PresenceBar } from "./PresenceBar";
import { VoteDisplay } from "./VoteDisplay";

interface Column {
  id: string;
  name: string;
  items: BoardItem[];
}

interface BoardItem {
  id: string;
  text: string;
  color: string;
  reactions: Record<string, number>;
  isAnonymous: boolean;
  authorDisplay: string;
  votes: number;
}

export function Board({ ceremonyId, templateId }: { ceremonyId: string; templateId: string | null }) {
  const { getToken } = useAuthToken();
  const { currentPhase, isFacilitator, participantCount } = useCeremonyStore();
  const [columns, setColumns] = useState<Column[]>([]);
  const [activeItem, setActiveItem] = useState<BoardItem | null>(null);
  const [connected, setConnected] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  // Load board items
  useEffect(() => {
    async function loadItems() {
      const token = await getToken();
      const res = await fetch(`/api/v1/ceremonies/${ceremonyId}/items`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        // Group items by column
        const cols: Record<string, Column> = {};
        for (const item of data.items) {
          if (!cols[item.column_name]) {
            cols[item.column_name] = { id: item.column_name, name: item.column_name, items: [] };
          }
          cols[item.column_name].items.push({
            id: item.id,
            text: item.content,
            color: "#e2e8f0",
            reactions: {},
            isAnonymous: !item.authorDisplay || item.authorDisplay === "Anonymous",
            authorDisplay: item.authorDisplay || "Anonymous",
            votes: 0,
          });
        }
        setColumns(Object.values(cols));
      }
    }
    loadItems();
  }, [ceremonyId, getToken]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const { active } = event;
    for (const col of columns) {
      const item = col.items.find((i) => i.id === active.id);
      if (item) setActiveItem(item);
    }
  }, [columns]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    setActiveItem(null);
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Find source column
    let sourceCol: Column | null = null;
    let item: BoardItem | null = null;
    for (const col of columns) {
      const found = col.items.find((i) => i.id === activeId);
      if (found) {
        sourceCol = col;
        item = found;
      }
    }
    if (!sourceCol || !item) return;

    // Update local state
    setColumns((prev) => {
      const updated = prev.map((col) => ({ ...col, items: [...col.items] }));
      // Remove from source
      const src = updated.find((c) => c.id === sourceCol!.id);
      if (src) src.items = src.items.filter((i) => i.id !== activeId);
      // Add to target
      const target = updated.find((c) => c.id === overId);
      if (target) target.items.push(item!);
      return updated;
    });
  }, [columns]);

  const handleAddNote = useCallback(async (text: string, color: string, isAnonymous: boolean) => {
    const token = await getToken();
    const res = await fetch(`/api/v1/ceremonies/${ceremonyId}/items`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ content: text, column_name: "default", is_anonymous: isAnonymous }),
    });
    if (res.ok) {
      const data = await res.json();
      setColumns((prev) => {
        const updated = prev.map((c) => ({ ...c, items: [...c.items] }));
        const col = updated[0]; // Add to first column
        if (col) {
          col.items.push({
            id: data.id,
            text: data.content,
            color,
            reactions: {},
            isAnonymous,
            authorDisplay: "You",
            votes: 0,
          });
        }
        return updated;
      });
    }
  }, [ceremonyId, getToken]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-slate-600">
            Phase: <span className="text-slate-900 capitalize">{currentPhase}</span>
          </span>
          <PresenceBar count={participantCount} />
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-xs text-slate-500">{connected ? "Connected" : "Disconnected"}</span>
        </div>
      </div>

      {/* Board */}
      <div className="flex-1 overflow-x-auto p-4">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-4 h-full min-w-max">
            {columns.map((column) => (
              <SortableContext key={column.id} items={column.items.map((i) => i.id)} strategy={verticalListSortingStrategy}>
                <BoardColumn key={column.id} column={column} phase={currentPhase} />
              </SortableContext>
            ))}
          </div>
          <DragOverlay>
            {activeItem ? <BoardCard item={activeItem} isDragging /> : null}
          </DragOverlay>
        </DndContext>
      </div>

      {/* Add Note Form (only in collect phase) */}
      {currentPhase === "collect" && (
        <div className="p-4 border-t border-slate-200">
          <AddNoteForm onAdd={handleAddNote} />
        </div>
      )}
    </div>
  );
}
