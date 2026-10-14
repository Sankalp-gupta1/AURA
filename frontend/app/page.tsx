import { Mail, CalendarClock, ListChecks, Radio } from "lucide-react";
import { API_BASE } from "@/lib/api";

export default async function LandingPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const params = await searchParams;
  const errors: Record<string, string> = {
    oauth_cancelled: "Google sign-in was cancelled. You can try again whenever you are ready.",
    oauth_state: "That sign-in link expired. Start again using the button below.",
    oauth_failed: "We could not complete Google sign-in. Please try again.",
  };

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
          <div role="alert" className="mb-6 panel p-4 text-sm border-[var(--color-coral)] text-[var(--color-coral)]">
            {errors[params.error] || errors.oauth_failed}
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
          Bring your Gmail, calendar and tasks into one clear workspace.
          See what needs your attention, plan your day and ask questions about your own information.
        </p>

        <a
          href={`${API_BASE}/api/auth/google/login`}
          className="focus-ring mt-10 inline-flex items-center gap-3 bg-[var(--color-amber)] text-[var(--color-ink)] font-semibold px-6 py-3.5 hover:brightness-110 transition"
        >
          <Mail className="w-5 h-5" />
          Get started with Google
        </a>
        <p className="mt-3 font-mono-ui text-[11px] text-[var(--color-muted)]">
          Gmail is read-only. You decide which calendar actions to approve.
        </p>
        <p className="mt-2 text-xs text-[var(--color-muted)] max-w-md leading-relaxed">
          AURA is an independent app, not a Google product. Sign-in happens on Google&apos;s website.
          AURA never asks you to enter your Google password here.
        </p>
        <p className="mt-4 text-xs text-[var(--color-muted)] max-w-md leading-relaxed">
          Early access: Google sign-in is currently available to approved test users.
          Your first connection may take about a minute while the service wakes up.
        </p>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full">
          {[
            { icon: Mail, label: "1. Connect and sync", desc: "Choose your Google account and bring in recent emails and upcoming events." },
            { icon: ListChecks, label: "2. Review your priorities", desc: "Check suggested tasks and deadlines. AI suggestions always need your judgment." },
            { icon: CalendarClock, label: "3. Plan your day", desc: "Read your briefing, add a task or event, and ask AURA for help." },
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
        <span>AURA · built for people who are tired of managing their inbox</span>
        <span className="mx-2">·</span>
        <a className="underline hover:text-[var(--color-text)]" href="/privacy">Privacy</a>
      </footer>
    </main>
  );
}
