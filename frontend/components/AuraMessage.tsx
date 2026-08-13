"use client";

/**
 * AURA's chat/briefing text often comes back from the AI with lightweight
 * markdown - **bold labels**, *italic asides*, and bullet points that are
 * sometimes separated by real newlines and sometimes inlined as " * ".
 * This renders that into readable JSX without pulling in a full markdown
 * dependency (react-markdown + remark plugins) just for this.
 */

function normalizeBullets(raw: string): string {
  return raw
    // "...: * **Label**" / ". * something" / start-of-line "* " -> bullet on its own line
    .replace(/(^|[.:\n])\s*\*\s+(?=\S)/g, (_match, prefix: string) => `${prefix}\n• `)
    .trim();
}

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];

  // Bold: **text**
  const boldParts = text.split(/(\*\*[^*]+\*\*)/g);
  boldParts.forEach((part, i) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      nodes.push(
        <strong key={`${keyPrefix}-b-${i}`} className="font-semibold text-[var(--color-text)]">
          {part.slice(2, -2)}
        </strong>
      );
      return;
    }

    // Italic: *text* (only single asterisks left after bold + bullets are stripped out)
    const italicParts = part.split(/(\*[^*]+\*)/g);
    italicParts.forEach((sub, j) => {
      if (sub.startsWith("*") && sub.endsWith("*") && sub.length > 2) {
        nodes.push(
          <em key={`${keyPrefix}-i-${i}-${j}`} className="not-italic text-[var(--color-muted)]">
            {sub.slice(1, -1)}
          </em>
        );
      } else if (sub) {
        nodes.push(<span key={`${keyPrefix}-t-${i}-${j}`}>{sub}</span>);
      }
    });
  });

  return nodes;
}

type Block = { type: "p" | "li"; content: string };

export default function AuraMessage({ text, className = "" }: { text: string; className?: string }) {
  if (!text) return null;

  const normalized = normalizeBullets(text);
  const lines = normalized
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  const blocks: Block[] = lines.map((line) =>
    line.startsWith("• ") ? { type: "li", content: line.slice(2) } : { type: "p", content: line }
  );

  const rendered: React.ReactNode[] = [];
  let currentList: string[] = [];
  let listKey = 0;

  const flushList = () => {
    if (currentList.length === 0) return;
    const key = listKey++;
    rendered.push(
      <ul key={`ul-${key}`} className="space-y-1.5 my-2">
        {currentList.map((item, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-[var(--color-amber)] mt-0.5 shrink-0">•</span>
            <span>{renderInline(item, `li-${key}-${i}`)}</span>
          </li>
        ))}
      </ul>
    );
    currentList = [];
  };

  blocks.forEach((block, idx) => {
    if (block.type === "li") {
      currentList.push(block.content);
    } else {
      flushList();
      rendered.push(
        <p key={`p-${idx}`} className="leading-relaxed">
          {renderInline(block.content, `p-${idx}`)}
        </p>
      );
    }
  });
  flushList();

  return <div className={`space-y-2 ${className}`}>{rendered}</div>;
}