"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  api,
  API_BASE,
  ApiError,
  User,
  DashboardStats,
  Briefing,
  Task,
  Email,
  CalEvent,
  Note,
  Memory,
} from "@/lib/api";
import TopBar from "@/components/TopBar";
import StatStrip from "@/components/StatStrip";
import BriefingPanel from "@/components/BriefingPanel";
import TaskBoard from "@/components/TaskBoard";
import EmailFeed from "@/components/EmailFeed";
import EventList from "@/components/EventList";
import NotesWidget from "@/components/NotesWidget";
import MemoryPanel from "@/components/MemoryPanel";
import AskAura from "@/components/AskAura";

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [briefingLoading, setBriefingLoading] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [events, setEvents] = useState<CalEvent[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadCore = useCallback(async () => {
    const [statsData, tasksData, emailsData, eventsData, notesData, memoriesData] = await Promise.all([
      api.stats(),
      api.tasks(),
      api.emails(),
      api.events(),
      api.notes(),
      api.memories(),
    ]);
    setStats(statsData);
    setTasks(tasksData);
    setEmails(emailsData);
    setEvents(eventsData);
    setNotes(notesData);
    setMemories(memoriesData);
  }, []);

  const loadBriefing = useCallback(async (force = false) => {
    setBriefingLoading(true);
    try {
      setBriefing(await api.briefing(force));
    } catch {
      // surfaced via empty state in BriefingPanel
    } finally {
      setBriefingLoading(false);
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const me = await api.me();
        setUser(me);
        await loadCore();
        void loadBriefing();
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/");
          return;
        }
        setError("AURA could not load your workspace. The service may be waking up. Please try again in a moment.");
      } finally {
        setLoading(false);
      }
    })();
  }, [loadCore, loadBriefing, router]);

  const handleSync = async () => {
    setSyncing(true);
    setError("");
    setNotice("");
    try {
      const result = await api.sync();
      if (result.warnings?.length) setError(result.warnings.join(" "));
      else setNotice(`Up to date. Added ${result.new_emails} emails, ${result.new_events} events and ${result.new_tasks} tasks.`);
      await loadCore();
      await loadBriefing(true);
      const me = await api.me();
      setUser(me);
    } catch {
      setError("We could not finish syncing. Try again, or reconnect Google if your access has expired.");
    } finally {
      setSyncing(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/");
      else setError("Sign-out could not finish. Please try again so your session can be closed.");
    }
  };

  const handleCreateTask = async (title: string) => {
    const task = await api.createTask({ title, priority: "Medium" });
    setTasks((t) => [task, ...t]);
    setStats((s) => (s ? { ...s, tasks_pending: s.tasks_pending + 1 } : s));
  };

  const handleToggleDone = async (task: Task) => {
    const updated = await api.updateTask(task.id, { status: "done" });
    setTasks((t) => t.map((x) => (x.id === task.id ? updated : x)));
    setStats((s) => (s ? { ...s, tasks_pending: Math.max(0, s.tasks_pending - 1) } : s));
  };

  const handleDeleteTask = async (id: number) => {
    await api.deleteTask(id);
    setTasks((t) => t.filter((x) => x.id !== id));
  };

  const handleSearch = async (q: string) => {
    setEmails(await api.emails(q ? { search: q } : {}));
  };

  const handleCreateEvent = async (payload: { title: string; start_time: string; end_time: string; location: string }) => {
    const ev = await api.createEvent(payload);
    setEvents((e) => [...e, ev].sort((a, b) => a.start_time.localeCompare(b.start_time)));
  };

  const handleCreateNote = async (content: string) => {
    const note = await api.createNote(content);
    setNotes((n) => [note, ...n]);
  };

  const handleDeleteNote = async (id: number) => {
    await api.deleteNote(id);
    setNotes((n) => n.filter((x) => x.id !== id));
  };

  const handleAddMemory = async (content: string) => {
    const memory = await api.addMemory(content);
    setMemories((m) => [memory, ...m]);
  };

  const handleForgetMemory = async (id: number) => {
    await api.forgetMemory(id);
    setMemories((m) => m.filter((x) => x.id !== id));
  };

  const handleActionResolved = () => {
    void loadCore().catch(() => setError("Your action was saved, but the workspace could not refresh. Please reload."));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center p-6 space-y-3">
          <p className="font-display text-xl animate-pulse">Opening your workspace…</p>
          <p className="text-sm text-[var(--color-muted)]">The first visit can take about a minute while AURA wakes up.</p>
        </div>
      </div>
    );
  }

  if (!user) return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="panel p-8 max-w-md space-y-5">
        <h1 className="font-display text-xl">Let&apos;s try that again</h1>
        <p className="text-sm text-[var(--color-muted)]" role="alert">{error || "Please sign in to open your workspace."}</p>
        <button className="focus-ring badge" onClick={() => window.location.reload()}>Try again</button>
        <Link href="/" className="ml-5 text-sm underline">Back to sign in</Link>
      </div>
    </main>
  );

  return (
    <main className="min-h-screen pb-24">
      <TopBar user={user} onSync={handleSync} syncing={syncing} onLogout={handleLogout} />

      <div className="px-6 md:px-10 py-8 max-w-7xl mx-auto space-y-6">
        {error && (
          <div role="alert" className="panel p-4 border-[var(--color-coral)] text-sm text-[var(--color-coral)]">
            {error} <a className="underline ml-2" href={`${API_BASE}/api/auth/google/login`}>Reconnect Google</a>
          </div>
        )}
        {notice && <p role="status" className="panel p-4 text-sm text-[var(--color-teal)]">{notice}</p>}

        <section className="panel p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <p className="font-mono-ui text-xs text-[var(--color-teal)] mb-2">YOUR PERSONAL WORKSPACE</p>
            <h1 className="font-display text-2xl font-semibold">Welcome{user.name ? `, ${user.name.split(" ")[0]}` : ""}.</h1>
            <p className="text-sm text-[var(--color-muted)] mt-2">
              {user.last_synced_at ? "Review your priorities, plan your day, or ask AURA a question." : "Start by syncing your Gmail and Calendar. Then review your briefing and suggested tasks."}
            </p>
          </div>
          {!user.last_synced_at && <button onClick={handleSync} disabled={syncing} className="focus-ring bg-[var(--color-amber)] text-[var(--color-ink)] px-5 py-3 font-semibold disabled:opacity-50">{syncing ? "Syncing your account…" : "Sync my account"}</button>}
        </section>

        {stats && <StatStrip stats={stats} />}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <BriefingPanel briefing={briefing} loading={briefingLoading} onRegenerate={() => loadBriefing(true)} />
            <TaskBoard
              tasks={tasks}
              onCreate={handleCreateTask}
              onToggleDone={handleToggleDone}
              onDelete={handleDeleteTask}
              onActionResolved={handleActionResolved}
            />
          </div>
          <div className="space-y-6">
            <EmailFeed emails={emails} onSearch={handleSearch} />
            <EventList events={events} onCreate={handleCreateEvent} />
            <MemoryPanel memories={memories} onAdd={handleAddMemory} onDelete={handleForgetMemory} />
            <NotesWidget notes={notes} onCreate={handleCreateNote} onDelete={handleDeleteNote} />
          </div>
        </div>
      </div>

      <AskAura />
    </main>
  );
}
