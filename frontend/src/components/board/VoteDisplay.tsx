"use client";

import { useEffect, useState } from "react";

export function VoteDisplay({
  votes,
  itemId,
  onVote,
  remaining,
}: {
  votes: number;
  itemId: string;
  onVote: (itemId: string) => void;
  remaining: number;
}) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-0.5">
        {Array.from({ length: Math.min(votes, 5) }).map((_, i) => (
          <span key={i} className="w-2 h-2 rounded-full bg-blue-500" />
        ))}
      </div>
      {votes > 0 && <span className="text-xs text-slate-500">{votes}</span>}
      {remaining > 0 && (
        <button
          onClick={() => onVote(itemId)}
          className="text-xs text-blue-600 hover:underline disabled:opacity-50"
          disabled={remaining === 0}
        >
          +Vote ({remaining})
        </button>
      )}
    </div>
  );
}
