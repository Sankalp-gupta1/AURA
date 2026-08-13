"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Radio, Sparkles } from "lucide-react";
import { API_BASE } from "@/lib/api";
import AuraMessage from "./AuraMessage";

type Message = { role: "user" | "assistant"; content: string };

const SUGGESTIONS = [
  "What should I focus on today?",
  "Summarize my most urgent emails",
  "Any risks I should know about this week?",
];

export default function AskAura() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open, streaming]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || streaming) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }, { role: "assistant", content: "" }]);
    setStreaming(true);

    try {
      const res = await fetch(`${API_BASE}/api/ask`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      if (!res.body) throw new Error("No response stream");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = JSON.parse(line.slice(6));
          if (payload.delta) {
            setMessages((prev) => {
              const copy = [...prev];
              copy[copy.length - 1] = {
                role: "assistant",
                content: copy[copy.length - 1].content + payload.delta,
              };
              return copy;
            });
          }
        }
      }
    } catch {
      setMessages((prev) => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: "assistant", content: "Connection to AURA was interrupted. Try again." };
        return copy;
      });
    } finally {
      setStreaming(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="focus-ring fixed bottom-6 right-6 bg-[var(--color-amber)] text-[var(--color-ink)] w-14 h-14 rounded-full flex items-center justify-center shadow-2xl hover:brightness-110 hover:scale-105 transition z-50"
        aria-label="Ask Aura"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  const isThinking = streaming && messages.length > 0 && messages[messages.length - 1].content === "";

  return (
    <div className="fixed inset-0 sm:inset-auto sm:bottom-6 sm:right-6 w-full sm:w-[420px] h-full sm:h-[640px] sm:max-h-[80vh] panel flex flex-col z-50 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--color-line)] bg-[var(--color-panel-2)]">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-[var(--color-amber)]/15 border border-[var(--color-amber)]/40 flex items-center justify-center">
              <Radio className="w-4 h-4 text-[var(--color-amber)]" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[var(--color-teal)] border-2 border-[var(--color-panel-2)]" />
          </div>
          <div>
            <p className="font-display font-semibold text-sm leading-tight">Ask Aura</p>
            <p className="font-mono-ui text-[10px] text-[var(--color-muted)] leading-tight">
              {isThinking ? "THINKING…" : "ONLINE · GROUNDED IN YOUR DATA"}
            </p>
          </div>
        </div>
        <button
          onClick={() => setOpen(false)}
          className="focus-ring text-[var(--color-muted)] hover:text-[var(--color-text)] transition"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col justify-end gap-4">
            <div className="flex items-start gap-2.5">
              <div className="w-7 h-7 rounded-full bg-[var(--color-amber)]/15 border border-[var(--color-amber)]/40 flex items-center justify-center shrink-0">
                <Sparkles className="w-3.5 h-3.5 text-[var(--color-amber)]" />
              </div>
              <div className="text-sm bg-[var(--color-panel-2)] border border-[var(--color-line)] px-3.5 py-2.5 max-w-[85%]">
                Hi, I&apos;m Aura. Ask me anything about your inbox, tasks, or calendar — I only
                answer from what&apos;s actually synced.
              </div>
            </div>
            <div className="flex flex-col gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => ask(s)}
                  className="focus-ring text-left text-xs badge normal-case tracking-normal font-body py-2 px-3 hover:border-[var(--color-amber)] hover:text-[var(--color-amber)] transition"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => {
          const isUser = m.role === "user";
          const isLastAssistantEmpty = !isUser && i === messages.length - 1 && m.content === "" && streaming;
          return (
            <div key={i} className={`flex items-start gap-2.5 ${isUser ? "flex-row-reverse" : ""}`}>
              {!isUser && (
                <div className="w-7 h-7 rounded-full bg-[var(--color-amber)]/15 border border-[var(--color-amber)]/40 flex items-center justify-center shrink-0 mt-0.5">
                  <Sparkles className="w-3.5 h-3.5 text-[var(--color-amber)]" />
                </div>
              )}
              <div
                className={`text-sm px-3.5 py-2.5 max-w-[85%] ${
                  isUser
                    ? "bg-[var(--color-amber)] text-[var(--color-ink)] font-medium"
                    : "bg-[var(--color-panel-2)] border border-[var(--color-line)]"
                }`}
              >
                {isLastAssistantEmpty ? (
                  <span className="flex gap-1 py-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted)] animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted)] animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted)] animate-bounce" />
                  </span>
                ) : isUser ? (
                  m.content
                ) : (
                  <AuraMessage text={m.content} />
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        className="flex gap-2 p-3 border-t border-[var(--color-line)] bg-[var(--color-panel-2)]"
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Aura anything..."
          className="focus-ring flex-1 bg-[var(--color-ink)] border border-[var(--color-line)] px-3.5 py-2.5 text-sm placeholder:text-[var(--color-muted)]"
        />
        <button
          type="submit"
          disabled={streaming || !input.trim()}
          className="focus-ring bg-[var(--color-amber)] text-[var(--color-ink)] px-4 flex items-center justify-center hover:brightness-110 transition disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label="Send"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}