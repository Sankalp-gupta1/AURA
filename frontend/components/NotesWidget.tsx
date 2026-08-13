"use client";

import { useState } from "react";
import { StickyNote, Plus, X } from "lucide-react";
import { Note } from "@/lib/api";

export default function NotesWidget({
  notes,
  onCreate,
  onDelete,
}: {
  notes: Note[];
  onCreate: (content: string) => void;
  onDelete: (id: number) => void;
}) {
  const [content, setContent] = useState("");

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    onCreate(content.trim());
    setContent("");
  };

  return (
    <div className="panel p-6">
      <div className="flex items-center gap-2 mb-4">
        <StickyNote className="w-4 h-4 text-[var(--color-violet)]" />
        <h2 className="font-display font-semibold text-sm tracking-wide uppercase">Quick Notes</h2>
      </div>

      <form onSubmit={submit} className="flex gap-2 mb-3">
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Jot something down for Aura to remember..."
          className="focus-ring flex-1 bg-[var(--color-panel-2)] border border-[var(--color-line)] px-3 py-2 text-sm placeholder:text-[var(--color-muted)]"
        />
        <button
          type="submit"
          className="focus-ring bg-[var(--color-violet)] text-[var(--color-ink)] px-3 flex items-center justify-center hover:brightness-110 transition"
        >
          <Plus className="w-4 h-4" />
        </button>
      </form>

      <ul className="space-y-1.5 max-h-40 overflow-y-auto">
        {notes.map((note) => (
          <li
            key={note.id}
            className="flex items-center justify-between gap-2 text-xs bg-[var(--color-panel-2)] border border-[var(--color-line)] px-3 py-2 group"
          >
            <span className="truncate">{note.content}</span>
            <button
              onClick={() => onDelete(note.id)}
              className="focus-ring text-[var(--color-muted)] hover:text-[var(--color-coral)] opacity-0 group-hover:opacity-100 transition shrink-0"
            >
              <X className="w-3 h-3" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
