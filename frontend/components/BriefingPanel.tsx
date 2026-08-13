"use client";

import { Sparkles, RefreshCw, TriangleAlert, ArrowRight } from "lucide-react";
import { Briefing } from "@/lib/api";
import AuraMessage from "./AuraMessage";

export default function BriefingPanel({
  briefing,
  loading,
  onRegenerate,
}: {
  briefing: Briefing | null;
  loading: boolean;
  onRegenerate: () => void;
}) {
  return (
    <div className="panel p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[var(--color-amber)]" />
          <h2 className="font-display font-semibold text-sm tracking-wide uppercase">
            Chief-of-Staff Briefing
          </h2>
        </div>
        <button
          onClick={onRegenerate}
          disabled={loading}
          className="focus-ring flex items-center gap-1.5 badge hover:border-[var(--color-amber)] transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
          REGENERATE
        </button>
      </div>

      {loading && !briefing && (
        <div className="space-y-2 animate-pulse">
          <div className="h-3 bg-[var(--color-panel-2)] rounded w-full" />
          <div className="h-3 bg-[var(--color-panel-2)] rounded w-5/6" />
          <div className="h-3 bg-[var(--color-panel-2)] rounded w-2/3" />
        </div>
      )}

      {briefing && (
        <div className="space-y-5">
          <div className="text-sm text-[var(--color-text)]">
            <AuraMessage text={briefing.daily_briefing} />
          </div>

          {briefing.top_focus.length > 0 && (
            <div>
              <p className="font-mono-ui text-[11px] text-[var(--color-muted)] uppercase mb-2">Top Focus</p>
              <ul className="space-y-1.5">
                {briefing.top_focus.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <ArrowRight className="w-3.5 h-3.5 mt-0.5 text-[var(--color-amber)] shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {briefing.risks.length > 0 && (
            <div>
              <p className="font-mono-ui text-[11px] text-[var(--color-coral)] uppercase mb-2">Risks</p>
              <ul className="space-y-1.5">
                {briefing.risks.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-[var(--color-muted)]">
                    <TriangleAlert className="w-3.5 h-3.5 mt-0.5 text-[var(--color-coral)] shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {briefing.suggested_actions.length > 0 && (
            <div>
              <p className="font-mono-ui text-[11px] text-[var(--color-teal)] uppercase mb-2">Suggested Actions</p>
              <div className="flex flex-wrap gap-2">
                {briefing.suggested_actions.map((item, i) => (
                  <span key={i} className="badge border-[var(--color-teal)] text-[var(--color-teal)]">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {briefing.motivational_note && (
            <p className="text-xs italic text-[var(--color-muted)] border-t border-[var(--color-line)] pt-3">
              {briefing.motivational_note}
            </p>
          )}
        </div>
      )}

      {!loading && !briefing && (
        <p className="text-sm text-[var(--color-muted)]">
          Sync your account to generate your first briefing.
        </p>
      )}
    </div>
  );
}