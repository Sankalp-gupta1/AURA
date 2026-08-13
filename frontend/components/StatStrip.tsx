import { Mail, ListChecks, CalendarClock, AlertTriangle } from "lucide-react";
import { DashboardStats } from "@/lib/api";

export default function StatStrip({ stats }: { stats: DashboardStats }) {
  const items = [
    { label: "Emails Synced", value: stats.emails, icon: Mail, color: "var(--color-text)" },
    { label: "Tasks Pending", value: stats.tasks_pending, icon: ListChecks, color: "var(--color-amber)" },
    { label: "Upcoming Events", value: stats.events_upcoming, icon: CalendarClock, color: "var(--color-teal)" },
    { label: "Needs Attention", value: stats.important_emails, icon: AlertTriangle, color: "var(--color-coral)" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {items.map(({ label, value, icon: Icon, color }) => (
        <div key={label} className="panel p-5">
          <div className="flex items-center justify-between mb-3">
            <span className="font-mono-ui text-[11px] tracking-wide text-[var(--color-muted)] uppercase">
              {label}
            </span>
            <Icon className="w-4 h-4" style={{ color }} />
          </div>
          <p className="font-display text-3xl font-bold" style={{ color }}>
            {value}
          </p>
        </div>
      ))}
    </div>
  );
}
