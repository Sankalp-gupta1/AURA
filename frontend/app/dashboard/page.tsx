"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  api,
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
        await loadBriefing();
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/");
          return;
        }
        setError("Could not reach the AURA backend. Is it running?");
      } finally {
        setLoading(false);
      }
    })();
  }, [loadCore, loadBriefing, router]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.sync();
      await loadCore();
      await loadBriefing(true);
      const me = await api.me();
      setUser(me);
    } catch {
      setError("Sync failed. Check that your Google + Gemini keys are configured.");
    } finally {
      setSyncing(false);
    }
  };

  const handleLogout = async () => {
    await api.logout();
    router.replace("/");
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

  const handleCreateEvent = async (payload: { title: string; start_time: string; end_time: string }) => {
    try {
      const ev = await api.createEvent(payload);
      setEvents((e) => [...e, ev].sort((a, b) => a.start_time.localeCompare(b.start_time)));
    } catch {
      setError("Could not create the calendar event. Check Calendar permission was granted.");
    }
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

  // When an autonomous action executes (e.g. creates a calendar event or a
  // new sub-task), refresh the lists that could have changed as a result.
  const handleActionResolved = () => {
    loadCore();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="font-mono-ui text-sm text-[var(--color-muted)] animate-pulse">BOOTING AURA…</p>
      </div>
    );
  }

  if (!user) return null;

  return (
    <main className="min-h-screen pb-24">
      <TopBar user={user} onSync={handleSync} syncing={syncing} onLogout={handleLogout} />

      <div className="px-6 md:px-10 py-8 max-w-7xl mx-auto space-y-6">
        {error && (
          <div className="panel p-4 border-[var(--color-coral)] text-sm text-[var(--color-coral)]">{error}</div>
        )}

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
