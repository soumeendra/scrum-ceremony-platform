"use client";

import { useEffect, useState } from "react";

export function PhaseTimer({
  seconds,
  isRunning,
  onComplete,
}: {
  seconds: number | null;
  isRunning: boolean;
  onComplete?: () => void;
}) {
  const [remaining, setRemaining] = useState(seconds || 0);

  useEffect(() => {
    setRemaining(seconds || 0);
  }, [seconds]);

  useEffect(() => {
    if (!isRunning || remaining <= 0) return;

    const interval = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onComplete?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, remaining, onComplete]);

  const minutes = Math.floor(remaining / 60);
  const secs = remaining % 60;

  const isLow = remaining <= 30 && remaining > 0;
  const isCritical = remaining <= 10 && remaining > 0;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md font-mono text-sm ${
        isCritical
          ? "bg-red-100 text-red-700"
          : isLow
            ? "bg-amber-100 text-amber-700"
            : "bg-slate-100 text-slate-700"
      }`}
    >
      <span>⏱</span>
      <span>
        {String(minutes).padStart(2, "0")}:{String(secs).padStart(2, "0")}
      </span>
    </div>
  );
}
