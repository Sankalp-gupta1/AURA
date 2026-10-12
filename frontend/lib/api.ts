const rawApiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const API_BASE =
  rawApiBase.startsWith("http://") || rawApiBase.startsWith("https://")
    ? rawApiBase.replace(/\/$/, "")
    : `https://${rawApiBase.replace(/\/$/, "")}`;

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const authHeaders: Record<string, string> = {};
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem("aura_token");
    if (token) authHeaders.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore parse errors */
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  me: () => request<User>("/api/auth/me"),
  logout: () => request("/api/auth/logout", { method: "POST" }),

  stats: () => request<DashboardStats>("/api/dashboard/stats"),
  briefing: (force = false) => request<Briefing>(`/api/dashboard/briefing${force ? "?force=true" : ""}`),
  sync: () => request<SyncResult>("/api/dashboard/sync", { method: "POST" }),

  emails: (params: { category?: string; important_only?: boolean; search?: string } = {}) => {
    const qs = new URLSearchParams();
    if (params.category) qs.set("category", params.category);
    if (params.important_only) qs.set("important_only", "true");
    if (params.search) qs.set("search", params.search);
    const suffix = qs.toString() ? `?${qs.toString()}` : "";
    return request<Email[]>(`/api/emails${suffix}`);
  },

  tasks: (status?: string) => request<Task[]>(`/api/tasks${status ? `?status=${status}` : ""}`),
  createTask: (payload: Partial<Task>) =>
    request<Task>("/api/tasks", { method: "POST", body: JSON.stringify(payload) }),
  updateTask: (id: number, payload: Partial<Task>) =>
    request<Task>(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteTask: (id: number) => request(`/api/tasks/${id}`, { method: "DELETE" }),

  events: () => request<CalEvent[]>("/api/calendar"),
  createEvent: (payload: Partial<CalEvent>) =>
    request<CalEvent>("/api/calendar", { method: "POST", body: JSON.stringify(payload) }),

  notes: () => request<Note[]>("/api/notes"),
  createNote: (content: string) => request<Note>("/api/notes", { method: "POST", body: JSON.stringify({ content }) }),
  deleteNote: (id: number) => request(`/api/notes/${id}`, { method: "DELETE" }),

  memories: () => request<Memory[]>("/api/memory"),
  addMemory: (content: string) => request<Memory>("/api/memory", { method: "POST", body: JSON.stringify({ content }) }),
  forgetMemory: (id: number) => request(`/api/memory/${id}`, { method: "DELETE" }),

  planTask: (taskId: number) => request<AgentAction[]>(`/api/tasks/${taskId}/plan`, { method: "POST" }),
  approveAction: (id: number) => request<AgentAction>(`/api/actions/${id}/approve`, { method: "POST" }),
  rejectAction: (id: number) => request<AgentAction>(`/api/actions/${id}/reject`, { method: "POST" }),
};

export type User = {
  id: number;
  email: string;
  name: string;
  picture: string;
  last_synced_at: string;
};

export type DashboardStats = {
  emails: number;
  tasks_pending: number;
  events_upcoming: number;
  important_emails: number;
};

export type Briefing = {
  daily_briefing: string;
  top_focus: string[];
  risks: string[];
  suggested_actions: string[];
  motivational_note: string;
  generated_at: string;
};

export type SyncResult = {
  new_emails: number;
  new_events: number;
  new_tasks: number;
  synced_at: string;
};

export type Email = {
  id: number;
  sender: string;
  subject: string;
  snippet: string;
  email_date: string;
  category: string;
  priority: string;
  is_important: boolean;
  ai_summary: string;
};

export type Task = {
  id: number;
  title: string;
  description: string;
  priority: string;
  status: string;
  deadline: string;
  source: string;
};

export type CalEvent = {
  id: number;
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
  meet_link: string;
};

export type Note = {
  id: number;
  content: string;
};

export type Memory = {
  id: number;
  content: string;
  category: string;
  importance: number;
  source: string;
};

export type AgentAction = {
  id: number;
  task_id: number | null;
  action_type: string;
  title: string;
  description: string;
  payload: Record<string, string>;
  status: string;
  result_note: string;
};
