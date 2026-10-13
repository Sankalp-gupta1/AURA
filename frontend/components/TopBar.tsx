"use client";

import { Radio, RefreshCw, LogOut } from "lucide-react";
import { User } from "@/lib/api";

export default function TopBar({
  user,
  onSync,
  syncing,
  onLogout,
}: {
  user: User;
  onSync: () => void;
  syncing: boolean;
  onLogout: () => void;
}) {
  const lastSynced = user.last_synced_at
    ? new Date(user.last_synced_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "never";

  return (
    <>
      <div className="pulse-track" />
      <header className="flex items-center justify-between px-6 md:px-10 py-4 border-b border-[var(--color-line)]">
        <div className="flex items-center gap-2">
          <Radio className="w-5 h-5 text-[var(--color-amber)]" strokeWidth={2.2} />
          <span className="font-display font-bold text-lg tracking-tight">AURA</span>
        </div>

        <div className="flex items-center gap-3">
          <span className="font-mono-ui text-[11px] text-[var(--color-muted)] hidden sm:block">
            LAST SYNC {lastSynced.toUpperCase()}
          </span>
          <button
            onClick={onSync}
            disabled={syncing}
            className="focus-ring flex items-center gap-2 badge text-[var(--color-text)] hover:border-[var(--color-amber)] transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin" : ""}`} />
            {syncing ? "SYNCING" : "SYNC NOW"}
          </button>

          <div className="flex items-center gap-2 pl-3 border-l border-[var(--color-line)]">
            {user.picture ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={user.picture} alt={user.name} className="w-7 h-7 rounded-full" />
            ) : (
              <div className="w-7 h-7 rounded-full bg-[var(--color-panel-2)]" />
            )}
            <span className="text-sm hidden md:block">{user.name || user.email}</span>
            <button onClick={onLogout} aria-label="Sign out" title="Sign out" className="focus-ring text-[var(--color-muted)] hover:text-[var(--color-coral)] transition ml-1">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>
    </>
  );
}
