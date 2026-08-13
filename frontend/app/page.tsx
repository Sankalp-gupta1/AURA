import { Mail, CalendarClock, ListChecks, Radio } from "lucide-react";
import { API_BASE } from "@/lib/api";

export default async function LandingPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const params = await searchParams;

  return (
    <main className="min-h-screen flex flex-col">
      <div className="pulse-track" />

      <header className="flex items-center justify-between px-6 md:px-10 py-5">
        <div className="flex items-center gap-2">
          <Radio className="w-5 h-5 text-[var(--color-amber)]" strokeWidth={2.2} />
          <span className="font-display font-bold text-lg tracking-tight">AURA</span>
          <span className="badge text-[var(--color-muted)] ml-2">v2.0</span>
        </div>
        <span className="font-mono-ui text-xs text-[var(--color-muted)] hidden sm:block">
          PERSONAL AI OPERATING SYSTEM
        </span>
      </header>

      <section className="flex-1 flex flex-col items-center justify-center px-6 text-center max-w-3xl mx-auto">
        {params.error && (
          <div className="mb-6 badge border-[var(--color-coral)] text-[var(--color-coral)]">
            SIGN-IN FAILED — TRY AGAIN
          </div>
        )}

        <p className="font-mono-ui text-xs tracking-[0.2em] text-[var(--color-teal)] mb-4">
          SIGNAL &nbsp;•&nbsp; INBOX + CALENDAR + TASKS
        </p>
        <h1 className="font-display text-4xl md:text-6xl font-bold leading-[1.05] tracking-tight text-balance">
          One quiet layer <br className="hidden md:block" />
          above the noise.
        </h1>
        <p className="mt-6 text-[var(--color-muted)] text-base md:text-lg max-w-xl text-balance">
          AURA reads your inbox and calendar, extracts what actually needs your attention, and
          gives you a daily briefing you can act on — not another feed to scroll.
        </p>

        <a
          href={`${API_BASE}/api/auth/google/login`}
          className="focus-ring mt-10 inline-flex items-center gap-3 bg-[var(--color-amber)] text-[var(--color-ink)] font-semibold px-6 py-3.5 hover:brightness-110 transition"
        >
          <Mail className="w-5 h-5" />
          Connect Google Account
        </a>
        <p className="mt-3 font-mono-ui text-[11px] text-[var(--color-muted)]">
          READ-ONLY GMAIL ACCESS · CALENDAR EVENTS · REVOKE ANYTIME
        </p>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full">
          {[
            { icon: Mail, label: "Gmail Intelligence", desc: "Priority + category on every message" },
            { icon: ListChecks, label: "Task Extraction", desc: "Deadlines pulled straight from emails" },
            { icon: CalendarClock, label: "Daily Briefing", desc: "One summary, generated fresh each morning" },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="panel p-5 text-left">
              <Icon className="w-4 h-4 text-[var(--color-amber)] mb-3" />
              <p className="font-display font-semibold text-sm">{label}</p>
              <p className="text-xs text-[var(--color-muted)] mt-1">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="text-center py-6 font-mono-ui text-[11px] text-[var(--color-muted)]">
        AURA · built for people who are tired of managing their inbox
      </footer>
    </main>
  );
}
