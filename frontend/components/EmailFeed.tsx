"use client";

import { useState } from "react";
import { Search, ShieldAlert, Briefcase, Clock, Mail } from "lucide-react";
import { Email } from "@/lib/api";

const categoryIcon: Record<string, React.ElementType> = {
  security: ShieldAlert,
  job_opportunity: Briefcase,
  deadline: Clock,
};

const priorityColor: Record<string, string> = {
  High: "var(--color-coral)",
  Medium: "var(--color-amber)",
  Low: "var(--color-teal)",
};

export default function EmailFeed({
  emails,
  onSearch,
}: {
  emails: Email[];
  onSearch: (q: string) => void;
}) {
  const [query, setQuery] = useState("");

  return (
    <div className="panel p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display font-semibold text-sm tracking-wide uppercase">Gmail Intelligence</h2>
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" />
          <input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              onSearch(e.target.value);
            }}
            placeholder="Search inbox"
            className="focus-ring bg-[var(--color-panel-2)] border border-[var(--color-line)] pl-8 pr-3 py-1.5 text-xs w-40 sm:w-56 placeholder:text-[var(--color-muted)]"
          />
        </div>
      </div>

      {emails.length === 0 && (
        <div className="text-center py-10">
          <Mail className="w-6 h-6 text-[var(--color-muted)] mx-auto mb-2" />
          <p className="text-sm text-[var(--color-muted)]">No emails synced yet.</p>
        </div>
      )}

      <ul className="divide-y divide-[var(--color-line)] max-h-[520px] overflow-y-auto">
        {emails.map((email) => {
          const Icon = categoryIcon[email.category] || Mail;
          return (
            <li key={email.id} className="py-3 first:pt-0">
              <div className="flex items-start gap-3">
                <Icon className="w-4 h-4 mt-0.5 text-[var(--color-muted)] shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium truncate">{email.subject}</p>
                    <span
                      className="badge shrink-0"
                      style={{ color: priorityColor[email.priority], borderColor: priorityColor[email.priority] }}
                    >
                      {email.priority}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--color-muted)] truncate mt-0.5">{email.sender}</p>
                  <p className="text-xs text-[var(--color-text)] mt-1.5 line-clamp-2">
                    {email.ai_summary || email.snippet}
                  </p>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
