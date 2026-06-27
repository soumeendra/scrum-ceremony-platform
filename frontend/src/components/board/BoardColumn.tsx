"use client";

import { useDroppable } from "@dnd-kit/core";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { BoardCard } from "./BoardCard";
import type { BoardItem } from "./Board";

interface Column {
  id: string;
  name: string;
  items: BoardItem[];
}

export function BoardColumn({ column, phase }: { column: Column; phase: string }) {
  const { setNodeRef } = useDroppable({ id: column.id });

  return (
    <div className="flex flex-col w-72 bg-slate-100 rounded-lg">
      <div className="p-3 border-b border-slate-200">
        <h3 className="font-medium text-slate-900">{column.name}</h3>
        <span className="text-xs text-slate-500">{column.items.length} items</span>
      </div>
      <div ref={setNodeRef} className="flex-1 p-2 space-y-2 overflow-y-auto">
        {column.items.map((item) => (
          <SortableCard key={item.id} item={item} phase={phase} />
        ))}
      </div>
    </div>
  );
}

function SortableCard({ item, phase }: { item: BoardItem; phase: string }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <BoardCard item={item} phase={phase} />
    </div>
  );
}
