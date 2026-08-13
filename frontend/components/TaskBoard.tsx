"use client";

import { useState } from "react";
import { Plus, Check, Trash2, Bot, Wand2, CalendarPlus, Mail, ListPlus, BellRing, Loader2, X } from "lucide-react";
import { api, Task, AgentAction } from "@/lib/api";

const priorityColor: Record<string, string> = {
  High: "var(--color-coral)",
  Medium: "var(--color-amber)",
  Low: "var(--color-teal)",
};

const actionIcon: Record<string, React.ElementType> = {
  create_event: CalendarPlus,
  draft_reply: Mail,
  add_subtask: ListPlus,
  set_reminder: BellRing,
};

function TaskPlan({ taskId, onActionResolved }: { taskId: number; onActionResolved: () => void }) {
  const [actions, setActions] = useState<AgentAction[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  const generatePlan = async () => {
    setLoading(true);
    setError("");
    try {
      setActions(await api.planTask(taskId));
    } catch {
      setError("AURA couldn't generate a plan right now. Try again shortly.");
    } finally {
      setLoading(false);
    }
  };

  const respond = async (action: AgentAction, approve: boolean) => {
    setBusyId(action.id);
    try {
      const updated = approve ? await api.approveAction(action.id) : await api.rejectAction(action.id);
      setActions((prev) => (prev ? prev.map((a) => (a.id === action.id ? updated : a)) : prev));
      if (approve) onActionResolved();
    } finally {
      setBusyId(null);
    }
  };

  if (actions === null) {
    return (
      <button
        onClick={generatePlan}
        disabled={loading}
        className="focus-ring flex items-center gap-1.5 text-[11px] font-mono-ui text-[var(--color-violet)] hover:brightness-125 transition disabled:opacity-50"
      >
        {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
        {loading ? "PLANNING…" : "GENERATE PLAN"}
      </button>
    );
  }

  return (
    <div className="mt-2 space-y-2 border-t border-[var(--color-line)] pt-2">
      {error && <p className="text-xs text-[var(--color-coral)]">{error}</p>}
      {actions.length === 0 && !error && (
        <p className="text-xs text-[var(--color-muted)]">AURA has no additional actions to propose here.</p>
      )}
      {actions.map((action) => {
        const Icon = actionIcon[action.action_type] || Wand2;
        return (
          <div key={action.id} className="bg-[var(--color-ink)] border border-[var(--color-line)] p-2.5">
            <div className="flex items-start gap-2">
              <Icon className="w-3.5 h-3.5 mt-0.5 text-[var(--color-violet)] shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium">{action.title}</p>
                <p className="text-[11px] text-[var(--color-muted)] mt-0.5">{action.description}</p>
                {action.status !== "proposed" && (
                  <p
                    className="text-[11px] mt-1 font-mono-ui"
                    style={{
                      color:
                        action.status === "executed"
                          ? "var(--color-teal)"
                          : action.status === "failed"
                          ? "var(--color-coral)"
                          : "var(--color-muted)",
                    }}
                  >
                    {action.status.toUpperCase()} {action.result_note && `· ${action.result_note}`}
                  </p>
                )}
              </div>
              {action.status === "proposed" && (
                <div className="flex gap-1 shrink-0">
                  <button
                    onClick={() => respond(action, true)}
                    disabled={busyId === action.id}
                    className="focus-ring w-6 h-6 flex items-center justify-center border border-[var(--color-teal)] text-[var(--color-teal)] hover:bg-[var(--color-teal)]/10 transition disabled:opacity-50"
                    aria-label="Approve"
                  >
                    <Check className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => respond(action, false)}
                    disabled={busyId === action.id}
                    className="focus-ring w-6 h-6 flex items-center justify-center border border-[var(--color-line)] text-[var(--color-muted)] hover:border-[var(--color-coral)] hover:text-[var(--color-coral)] transition disabled:opacity-50"
                    aria-label="Reject"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function TaskBoard({
  tasks,
  onCreate,
  onToggleDone,
  onDelete,
  onActionResolved,
}: {
  tasks: Task[];
  onCreate: (title: string) => void;
  onToggleDone: (task: Task) => void;
  onDelete: (id: number) => void;
  onActionResolved: () => void;
}) {
  const [title, setTitle] = useState("");
  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null);

  const pending = tasks.filter((t) => t.status !== "done");
  const done = tasks.filter((t) => t.status === "done").slice(0, 5);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    onCreate(title.trim());
    setTitle("");
  };

  return (
    <div className="panel p-6">
      <h2 className="font-display font-semibold text-sm tracking-wide uppercase mb-4">Today Focus</h2>

      <form onSubmit={submit} className="flex gap-2 mb-4">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a task..."
          className="focus-ring flex-1 bg-[var(--color-panel-2)] border border-[var(--color-line)] px-3 py-2 text-sm rounded-none placeholder:text-[var(--color-muted)]"
        />
        <button
          type="submit"
          className="focus-ring bg-[var(--color-amber)] text-[var(--color-ink)] px-3 flex items-center justify-center hover:brightness-110 transition"
        >
          <Plus className="w-4 h-4" />
        </button>
      </form>

      {pending.length === 0 && (
        <p className="text-sm text-[var(--color-muted)]">No pending tasks. Nice.</p>
      )}

      <ul className="space-y-2">
        {pending.map((task) => (
          <li
            key={task.id}
            className="flex flex-col gap-2 group bg-[var(--color-panel-2)] border border-[var(--color-line)] p-3"
          >
            <div className="flex items-start gap-3">
              <button
                onClick={() => onToggleDone(task)}
                className="focus-ring mt-0.5 w-4 h-4 border border-[var(--color-line)] flex items-center justify-center shrink-0 hover:border-[var(--color-teal)] transition"
                aria-label="Mark done"
              >
                <Check className="w-3 h-3 opacity-0 group-hover:opacity-60" />
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm">{task.title}</p>
                  {task.source === "ai_email" && <Bot className="w-3 h-3 text-[var(--color-violet)]" />}
                </div>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <span
                    className="badge"
                    style={{ color: priorityColor[task.priority], borderColor: priorityColor[task.priority] }}
                  >
                    {task.priority}
                  </span>
                  {task.deadline && (
                    <span className="font-mono-ui text-[11px] text-[var(--color-muted)]">due {task.deadline}</span>
                  )}
                  <button
                    onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}
                    className="focus-ring text-[11px] font-mono-ui text-[var(--color-violet)] hover:brightness-125 transition ml-1"
                  >
                    {expandedTaskId === task.id ? "HIDE PLAN" : "PLAN WITH AURA"}
                  </button>
                </div>
              </div>
              <button
                onClick={() => onDelete(task.id)}
                className="focus-ring text-[var(--color-muted)] hover:text-[var(--color-coral)] transition opacity-0 group-hover:opacity-100"
                aria-label="Delete task"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>

            {expandedTaskId === task.id && (
              <div className="pl-7">
                <TaskPlan taskId={task.id} onActionResolved={onActionResolved} />
              </div>
            )}
          </li>
        ))}
      </ul>

      {done.length > 0 && (
        <div className="mt-4 pt-4 border-t border-[var(--color-line)]">
          <p className="font-mono-ui text-[11px] text-[var(--color-muted)] uppercase mb-2">Recently done</p>
          <ul className="space-y-1">
            {done.map((task) => (
              <li key={task.id} className="text-xs text-[var(--color-muted)] line-through">
                {task.title}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
