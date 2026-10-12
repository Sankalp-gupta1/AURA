"use client";

import { useState } from "react";
import { BrainCircuit, Trash2, Plus } from "lucide-react";
import { Memory } from "@/lib/api";

const categoryColor: Record<string, string> = {
  goal: "var(--color-amber)",
  preference: "var(--color-teal)",
  ongoing_situation: "var(--color-violet)",
  fact: "var(--color-muted)",
};

export default function MemoryPanel({
  memories,
  onAdd,
  onDelete,
}: {
  memories: Memory[];
  onAdd: (content: string) => void;
  onDelete: (id: number) => void;
}) {
  const [content, setContent] = useState("");
  const [open, setOpen] = useState(false);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    onAdd(content.trim());
    setContent("");
    setOpen(false);
  };

  return (
    <div className="panel p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-[var(--color-violet)]" />
          <h2 className="font-display font-semibold text-sm tracking-wide uppercase">What Aura Remembers</h2>
        </div>
        <button
          onClick={() => setOpen((v) => !v)}
          className="focus-ring flex items-center gap-1.5 badge hover:border-[var(--color-violet)] transition"
        >
          <Plus className="w-3 h-3" />
          TEACH AURA
        </button>
      </div>

      {open && (
        <form onSubmit={submit} className="mb-4 flex gap-2">
          <input
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="e.g. I prefer short, direct answers"
            className="focus-ring flex-1 bg-[var(--color-panel-2)] border border-[var(--color-line)] px-3 py-2 text-sm placeholder:text-[var(--color-muted)]"
          />
          <button
            type="submit"
            className="focus-ring bg-[var(--color-violet)] text-white px-3 text-sm font-medium hover:brightness-110 transition"
          >
            Save
          </button>
        </form>
      )}

      {memories.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">
          Nothing remembered yet - Aura learns your goals and preferences as you chat.
        </p>
      ) : (
        <ul className="space-y-2 max-h-[280px] overflow-y-auto">
          {memories.map((m) => (
            <li key={m.id} className="flex items-start gap-2 group">
              <span
                className="badge shrink-0 mt-0.5"
                style={{ color: categoryColor[m.category], borderColor: categoryColor[m.category] }}
              >
                {m.category.replace("_", " ")}
              </span>
              <p className="text-xs flex-1 leading-relaxed">{m.content}</p>
              <button
                onClick={() => onDelete(m.id)}
                className="focus-ring text-[var(--color-muted)] hover:text-[var(--color-coral)] transition opacity-0 group-hover:opacity-100 shrink-0"
                aria-label="Forget this"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
