"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

const COLORS = ["#e2e8f0", "#fca5a5", "#fdba74", "#fde047", "#86efac", "#93c5fd", "#c4b5fd"];

export function AddNoteForm({ onAdd }: { onAdd: (text: string, color: string, isAnonymous: boolean) => void }) {
  const [text, setText] = useState("");
  const [color, setColor] = useState(COLORS[0]);
  const [isAnonymous, setIsAnonymous] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onAdd(text.trim(), color, isAnonymous);
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 items-end">
      <div className="flex-1">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a note..."
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm resize-none"
          rows={2}
        />
      </div>
      <div className="flex gap-1">
        {COLORS.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setColor(c)}
            className={`w-6 h-6 rounded-full border-2 ${color === c ? "border-slate-900" : "border-transparent"}`}
            style={{ backgroundColor: c }}
          />
        ))}
      </div>
      <label className="flex items-center gap-1 text-xs text-slate-600">
        <input type="checkbox" checked={isAnonymous} onChange={(e) => setIsAnonymous(e.target.checked)} />
        Anonymous
      </label>
      <Button type="submit" size="sm">Add</Button>
    </form>
  );
}
