"use client";

import { useEffect, useState } from "react";

const API = "http://localhost:8000";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [briefing, setBriefing] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [askLoading, setAskLoading] = useState(false);

  async function loadDashboard() {
    const res = await fetch(`${API}/api/dashboard/`);
    const json = await res.json();
    setData(json);
    setLoading(false);
  }

  async function loadAI() {
    setAiLoading(true);
    const res = await fetch(`${API}/api/dashboard/ai`);
    const json = await res.json();

    try {
      setBriefing(JSON.parse(json.briefing));
    } catch {
      setBriefing({ daily_briefing: json.briefing });
    }

    setAiLoading(false);
  }

  async function syncGmail() {
    setSyncing(true);
    await fetch(`${API}/api/emails/sync`);
    await loadDashboard();
    setSyncing(false);
  }

  async function askAura() {
    if (!question.trim()) return;

    setAskLoading(true);
    setAnswer("");

    const res = await fetch(`${API}/api/ask/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    const json = await res.json();
    setAnswer(json.answer);
    setAskLoading(false);
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-black text-white flex items-center justify-center">
        <h1 className="text-3xl font-bold animate-pulse">
          Loading Life OS AI...
        </h1>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#050505] text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-5xl font-black tracking-tight">
              Life OS <span className="text-cyan-400">AI</span>
            </h1>
            <p className="text-gray-400 mt-2">
              Autonomous Personal Chief of Staff Dashboard
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={syncGmail}
              className="bg-zinc-800 hover:bg-zinc-700 text-white font-bold px-6 py-3 rounded-xl border border-zinc-700"
            >
              {syncing ? "Syncing..." : "Sync Gmail"}
            </button>

            <button
              onClick={loadAI}
              className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-6 py-3 rounded-xl shadow-lg"
            >
              {aiLoading ? "Thinking..." : "Generate AI Briefing"}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card title="Emails" value={data.stats.total_emails} />
          <Card title="Tasks" value={data.stats.total_tasks} />
          <Card title="Events" value={data.stats.total_events} />
          <Card title="Pending" value={data.stats.pending_tasks} />
        </div>

        {briefing && (
          <section className="bg-gradient-to-r from-cyan-950 to-purple-950 border border-cyan-700 rounded-2xl p-6">
            <h2 className="text-2xl font-bold mb-3">
              🤖 AI Chief of Staff Briefing
            </h2>

            <p className="text-gray-200 leading-relaxed">
              {briefing.daily_briefing}
            </p>

            {briefing.top_focus && (
              <div className="mt-4">
                <h3 className="font-bold text-cyan-300">Top Focus</h3>
                <p>{briefing.top_focus}</p>
              </div>
            )}
          </section>
        )}

        <section>
          <h2 className="text-2xl font-bold mb-3">🎯 Today Focus</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {data.today_focus.map((item: any, i: number) => (
              <div
                key={i}
                className="bg-zinc-900 border border-zinc-800 rounded-xl p-5"
              >
                <p className="text-sm text-cyan-400 uppercase">{item.type}</p>
                <h3 className="text-xl font-bold mt-1">{item.title}</h3>
                <p className="text-gray-400 mt-2">{item.reason}</p>
              </div>
            ))}
          </div>
        </section>

        <div className="grid lg:grid-cols-2 gap-6">
          <Section title="✅ Pending Tasks">
            {data.pending_tasks.length === 0 ? (
              <Empty text="No pending tasks" />
            ) : (
              data.pending_tasks.map((t: any) => (
                <Item
                  key={t.id}
                  title={t.title}
                  desc={t.description}
                  tag={t.priority}
                />
              ))
            )}
          </Section>

          <Section title="📅 Upcoming Events">
            {data.upcoming_events.length === 0 ? (
              <Empty text="No important upcoming events" />
            ) : (
              data.upcoming_events.map((e: any) => (
                <Item
                  key={e.id}
                  title={e.title}
                  desc={`${e.start} → ${e.end}`}
                  tag="Calendar"
                />
              ))
            )}
          </Section>
        </div>

        <Section title="📧 Latest Emails">
          {data.latest_emails.map((e: any) => (
            <Item
              key={e.id}
              title={e.subject}
              desc={e.snippet}
              tag={e.from}
            />
          ))}
        </Section>
      </div>

      {/* Aura Floating Chat */}
      <div className="fixed right-6 bottom-24 z-50">
        {chatOpen && (
          <div className="w-96 bg-zinc-950 border border-cyan-700 rounded-2xl shadow-2xl p-4 mb-4">
            <h2 className="text-xl font-bold text-cyan-400 mb-3">
              Ask Aura 💬
            </h2>

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask: IBM assessment ke baare me batao..."
              className="w-full h-24 bg-zinc-900 border border-zinc-700 rounded-xl p-3 text-white outline-none"
            />

            <button
              onClick={askAura}
              className="w-full mt-3 bg-cyan-500 text-black font-bold py-2 rounded-xl hover:bg-cyan-400"
            >
              {askLoading ? "Aura thinking..." : "Ask Aura"}
            </button>

            {answer && (
              <div className="mt-4 bg-zinc-900 border border-zinc-800 rounded-xl p-3 text-sm text-gray-200 max-h-64 overflow-y-auto whitespace-pre-line">
                {answer}
              </div>
            )}
          </div>
        )}

        <button
          onClick={() => setChatOpen(!chatOpen)}
          className="bg-cyan-500 hover:bg-cyan-400 text-black font-black px-5 py-4 rounded-full shadow-xl"
        >
          {chatOpen ? "Close Aura" : "Ask Aura"}
        </button>
      </div>
    </main>
  );
}

function Card({ title, value }: any) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
      <p className="text-gray-400">{title}</p>
      <h2 className="text-4xl font-black mt-2 text-cyan-400">{value}</h2>
    </div>
  );
}

function Section({ title, children }: any) {
  return (
    <section className="bg-zinc-950 border border-zinc-800 rounded-2xl p-5">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <div className="space-y-3">{children}</div>
    </section>
  );
}

function Item({ title, desc, tag }: any) {
  return (
    <div className="bg-zinc-900 rounded-xl p-4 border border-zinc-800">
      <div className="flex justify-between gap-4">
        <h3 className="font-bold text-lg">{title}</h3>
        <span className="text-xs bg-cyan-500 text-black px-2 py-1 rounded-lg h-fit">
          {tag}
        </span>
      </div>
      <p className="text-gray-400 mt-2 text-sm line-clamp-2">{desc}</p>
    </div>
  );
}

function Empty({ text }: any) {
  return (
    <p className="text-gray-500 text-sm border border-zinc-800 rounded-xl p-4">
      {text}
    </p>
  );
}
