"use client";

import { useState } from "react";
import { CalendarClock, Plus, MapPin, Video, X } from "lucide-react";
import { CalEvent } from "@/lib/api";

export default function EventList({
  events,
  onCreate,
}: {
  events: CalEvent[];
  onCreate: (payload: { title: string; start_time: string; end_time: string; location: string }) => Promise<void>;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [location, setLocation] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !start || !end) return;
    setError("");
    if (new Date(end) <= new Date(start)) {
      setError("The end time must be after the start time.");
      return;
    }
    setSaving(true);
    try {
      // datetime-local has no offset. Convert the user's local time to UTC for Google.
      await onCreate({ title: title.trim(), start_time: new Date(start).toISOString(), end_time: new Date(end).toISOString(), location });
      setTitle("");
      setStart("");
      setEnd("");
      setLocation("");
      setOpen(false);
    } catch {
      setError("The event was not saved. Please try again or reconnect Google Calendar.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="panel p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display font-semibold text-sm tracking-wide uppercase">Calendar Awareness</h2>
        <button
          onClick={() => setOpen((v) => !v)}
          className="focus-ring flex items-center gap-1.5 badge hover:border-[var(--color-amber)] transition"
        >
          {open ? <X className="w-3 h-3" /> : <Plus className="w-3 h-3" />}
          {open ? "CANCEL" : "NEW EVENT"}
        </button>
      </div>

      {open && (
        <form onSubmit={submit} className="grid grid-cols-2 gap-2 mb-4 bg-[var(--color-panel-2)] border border-[var(--color-line)] p-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Event title"
            aria-label="Event title"
            required
            className="focus-ring col-span-2 bg-transparent border border-[var(--color-line)] px-2 py-1.5 text-xs placeholder:text-[var(--color-muted)]"
          />
          <input
            type="datetime-local"
            aria-label="Start time"
            required
            value={start}
            onChange={(e) => setStart(e.target.value)}
            className="focus-ring bg-transparent border border-[var(--color-line)] px-2 py-1.5 text-xs"
          />
          <input
            type="datetime-local"
            aria-label="End time"
            required
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            className="focus-ring bg-transparent border border-[var(--color-line)] px-2 py-1.5 text-xs"
          />
          <input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Location (optional)"
            aria-label="Location (optional)"
            className="focus-ring col-span-2 bg-transparent border border-[var(--color-line)] px-2 py-1.5 text-xs placeholder:text-[var(--color-muted)]"
          />
          <button
            type="submit"
            disabled={saving}
            className="focus-ring col-span-2 bg-[var(--color-amber)] text-[var(--color-ink)] py-1.5 text-xs font-semibold hover:brightness-110 transition"
          >
            {saving ? "SAVING…" : "ADD TO GOOGLE CALENDAR"}
          </button>
          <p className="col-span-2 text-xs text-[var(--color-muted)]">Times use your device&apos;s timezone.</p>
          {error && <p role="alert" className="col-span-2 text-xs text-[var(--color-coral)]">{error}</p>}
        </form>
      )}

      {events.length === 0 && (
        <div className="text-center py-8">
          <CalendarClock className="w-6 h-6 text-[var(--color-muted)] mx-auto mb-2" />
          <p className="text-sm text-[var(--color-muted)]">No upcoming events synced.</p>
        </div>
      )}

      <ul className="space-y-2 max-h-72 overflow-y-auto">
        {events.map((ev) => (
          <li key={ev.id} className="bg-[var(--color-panel-2)] border border-[var(--color-line)] p-3">
            <p className="text-sm font-medium">{ev.title}</p>
            <p className="font-mono-ui text-[11px] text-[var(--color-teal)] mt-1">
              {new Date(ev.start_time).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })}
            </p>
            {ev.location && (
              <p className="text-xs text-[var(--color-muted)] flex items-center gap-1 mt-1">
                <MapPin className="w-3 h-3" /> {ev.location}
              </p>
            )}
            {ev.meet_link && (
              <a
                href={ev.meet_link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-[var(--color-amber)] flex items-center gap-1 mt-1 hover:underline"
              >
                <Video className="w-3 h-3" /> Join meet
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
