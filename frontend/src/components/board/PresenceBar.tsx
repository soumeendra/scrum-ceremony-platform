"use client";

export function PresenceBar({ count }: { count: number }) {
  return (
    <div className="flex items-center gap-1">
      <div className="flex -space-x-2">
        {Array.from({ length: Math.min(count, 5) }).map((_, i) => (
          <div
            key={i}
            className="w-6 h-6 rounded-full bg-slate-300 border-2 border-white flex items-center justify-center text-xs text-slate-600"
          >
            {i + 1}
          </div>
        ))}
      </div>
      <span className="text-xs text-slate-500">{count} online</span>
    </div>
  );
}
