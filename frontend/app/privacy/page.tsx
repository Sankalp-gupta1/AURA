import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="min-h-screen px-6 py-12 md:py-16">
      <article className="max-w-3xl mx-auto panel p-6 md:p-10">
        <Link href="/" className="font-mono-ui text-xs text-[var(--color-teal)] hover:underline">
          ← BACK TO AURA
        </Link>

        <h1 className="font-display text-3xl md:text-4xl font-bold mt-6">Privacy Policy</h1>
        <p className="text-sm text-[var(--color-muted)] mt-2">Last updated: October 12, 2026</p>

        <div className="mt-8 space-y-7 text-sm md:text-base leading-7 text-[var(--color-text)]">
          <section>
            <h2 className="font-display text-xl font-semibold">What AURA accesses</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              When you connect a Google Account, AURA may access your basic Google profile,
              read-only Gmail data, and Google Calendar data needed to view and create calendar
              events for features you choose to use.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold">How your data is used</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              AURA uses connected data to synchronize your inbox and calendar, identify useful
              tasks and priorities, generate briefings, answer your questions, and perform
              user-approved productivity actions. AURA does not sell your Google user data.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold">AI processing</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              Selected email, calendar, task, note, and memory context may be sent to the
              configured Google Gemini API when an AI-powered feature needs that context.
              AURA is designed to send only the context needed for the requested feature.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold">Storage and security</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              AURA stores synchronized application data in its database. Google OAuth access
              and refresh tokens are encrypted before they are stored. Access to a user&apos;s
              AURA data is tied to that user&apos;s authenticated account.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold">Google API data</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              AURA&apos;s use and transfer of information received from Google APIs follows the
              Google API Services User Data Policy, including its Limited Use requirements.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold">Your control</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              You can disconnect AURA by revoking its Google Account access from your Google
              Account&apos;s third-party connections page. Revoking access prevents AURA from
              obtaining new Google data with that authorization.
            </p>
          </section>

          <section>
            <h2 className="font-display text-xl font-semibold">Project status</h2>
            <p className="mt-2 text-[var(--color-muted)]">
              AURA is an independently built software project. Features and data practices may
              evolve as the project is improved; material changes will be reflected on this page.
            </p>
          </section>
        </div>
      </article>
    </main>
  );
}
