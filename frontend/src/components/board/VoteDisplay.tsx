"use client";

export function VoteDisplay({ votes, onVote, remaining }: { votes: number; onVote: () => void; remaining: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-1">
        {Array.from({ length: votes }).map((_, i) => (
          <span key={i} className="w-2 h-2 rounded-full bg-blue-500" />
        ))}
      </div>
      {remaining > 0 && (
        <button onClick={onVote} className="text-xs text-blue-600 hover:underline">
          Vote ({remaining} left)
        </button>
      )}
    </div>
  );
}
