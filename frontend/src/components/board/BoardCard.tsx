"use client";

import { cn } from "@/lib/utils";

interface BoardItem {
  id: string;
  text: string;
  color: string;
  reactions: Record<string, number>;
  isAnonymous: boolean;
  authorDisplay: string;
  votes: number;
}

export function BoardCard({
  item,
  phase,
  isDragging,
}: {
  item: BoardItem;
  phase?: string;
  isDragging?: boolean;
}) {
  return (
    <div
      className={cn(
        "bg-white rounded-lg shadow-sm border border-slate-200 p-3 cursor-grab active:cursor-grabbing",
        isDragging && "shadow-lg ring-2 ring-blue-500"
      )}
      style={{ borderLeftColor: item.color, borderLeftWidth: 4 }}
    >
      <p className="text-sm text-slate-800 mb-2">{item.text}</p>

      {/* Reactions */}
      {Object.keys(item.reactions).length > 0 && (
        <div className="flex gap-1 mb-2">
          {Object.entries(item.reactions).map(([emoji, count]) => (
            <span key={emoji} className="text-xs bg-slate-100 rounded px-1">
              {emoji} {count}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500">
          {item.isAnonymous ? "Anonymous" : item.authorDisplay}
        </span>
        {item.votes > 0 && (
          <span className="text-xs text-slate-500">● {item.votes}</span>
        )}
      </div>
    </div>
  );
}
