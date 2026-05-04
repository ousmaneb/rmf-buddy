export type Citation = {
  kind: "control" | "cci";
  id: string;
  label?: string;
  title?: string;
  snippet?: string;
};

export type ChatTurn = { role: "user" | "assistant"; content: string };
export type ChatMode = "ask" | "compare" | "implement" | "assess" | "poam" | "testresult";

export type EmassTopicSummary = { slug: string; title: string; category: string };
export type EmassTopic = EmassTopicSummary & { body: string };
export type EmassTerm = { term: string; definition: string };

export type AttackTechnique = { id: string; name: string; rationale?: string };

export type NistPubSummary = {
  slug: string;
  title: string;
  category: string;
  summary: string;
  url: string;
};
export type NistPub = NistPubSummary & { body: string };

export type BaselineDiff = {
  from: string;
  to: string;
  added: ControlSummary[];
  removed: ControlSummary[];
  shared_count: number;
};

export type ControlSummary = {
  id: string;
  label: string;
  family: string;
  family_name: string;
  title: string;
  is_enhancement: number;
  parent_id: string | null;
};

export type CCI = {
  id: string;
  definition: string;
  type?: string;
  control_index?: string;
  control_id?: string;
};

export type Control = ControlSummary & {
  statement: string;
  guidance: string;
  assessment: string;
  full_text: string;
  baselines: string[];
  ccis: CCI[];
  enhancements: { id: string; label: string; title: string }[];
  attack: AttackTechnique[];
};

export type Family = { family: string; family_name: string; n: number };

export type Flashcard = {
  kind: "control";
  front: string;
  back: { label: string; title: string; family: string; summary: string };
  ref_id: string;
};

export type Scenario = {
  scenario: string;
  expected_controls: string[];
  rationale: string;
};

export type Grade = { score: number; verdict: string; feedback: string };

export type StreamEvent =
  | { type: "text"; text: string }
  | { type: "tool_use_start"; id: string; name: string }
  | { type: "tool_call"; id: string; name: string; input: Record<string, unknown> }
  | { type: "tool_result"; id: string; name: string; summary: string }
  | { type: "done"; stop_reason: string }
  | { type: "error"; message: string };

export async function listFamilies(): Promise<Family[]> {
  return (await fetch("/api/families")).json();
}

export async function listControls(params: {
  family?: string;
  baseline?: string;
  q?: string;
}): Promise<ControlSummary[]> {
  const url = new URL("/api/controls", window.location.origin);
  Object.entries(params).forEach(([k, v]) => v && url.searchParams.set(k, v));
  return (await fetch(url.pathname + url.search)).json();
}

export async function getControl(id: string): Promise<Control> {
  return (await fetch(`/api/controls/${encodeURIComponent(id)}`)).json();
}

export async function listEmassTopics(): Promise<EmassTopicSummary[]> {
  return (await fetch("/api/emass/topics")).json();
}

export async function getEmassTopic(slug: string): Promise<EmassTopic> {
  return (await fetch(`/api/emass/topics/${encodeURIComponent(slug)}`)).json();
}

export async function listEmassGlossary(): Promise<EmassTerm[]> {
  return (await fetch("/api/emass/glossary")).json();
}

export type GrcTopicSummary = EmassTopicSummary;
export type GrcTopic = EmassTopic;
export type GrcTerm = EmassTerm;

export async function listGrcTopics(): Promise<GrcTopicSummary[]> {
  return (await fetch("/api/grc/topics")).json();
}

export async function getGrcTopic(slug: string): Promise<GrcTopic> {
  return (await fetch(`/api/grc/topics/${encodeURIComponent(slug)}`)).json();
}

export async function listGrcGlossary(): Promise<GrcTerm[]> {
  return (await fetch("/api/grc/glossary")).json();
}

export async function listNistPublications(): Promise<NistPubSummary[]> {
  return (await fetch("/api/nist/publications")).json();
}

export async function getNistPublication(slug: string): Promise<NistPub> {
  return (await fetch(`/api/nist/publications/${encodeURIComponent(slug)}`)).json();
}

export async function getBaselineDiff(low: string, high: string): Promise<BaselineDiff> {
  const u = new URL("/api/baselines/diff", window.location.origin);
  u.searchParams.set("low", low);
  u.searchParams.set("high", high);
  return (await fetch(u.pathname + u.search)).json();
}

export async function getFlashcards(family?: string, count = 10): Promise<Flashcard[]> {
  const url = new URL("/api/study/flashcards", window.location.origin);
  if (family) url.searchParams.set("family", family);
  url.searchParams.set("count", String(count));
  return (await fetch(url.pathname + url.search)).json();
}

export async function getScenario(family?: string): Promise<Scenario> {
  const url = new URL("/api/study/scenario", window.location.origin);
  if (family) url.searchParams.set("family", family);
  return (await fetch(url.pathname + url.search)).json();
}

export async function gradeAnswer(body: {
  scenario: string;
  expected_controls: string[];
  user_answer: string;
}): Promise<Grade> {
  return (
    await fetch("/api/study/grade", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
  ).json();
}

/**
 * Stream a chat response. Calls onEvent for every SSE event.
 * Returns a promise that resolves when the stream ends.
 */
export async function streamChat(
  messages: ChatTurn[],
  mode: ChatMode,
  context: Record<string, unknown> | undefined,
  onEvent: (e: StreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const r = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, mode, context }),
    signal,
  });
  if (!r.ok || !r.body) {
    onEvent({ type: "error", message: `HTTP ${r.status}: ${await r.text()}` });
    return;
  }
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let nl;
    while ((nl = buf.indexOf("\n\n")) !== -1) {
      const chunk = buf.slice(0, nl);
      buf = buf.slice(nl + 2);
      const ev = parseSSE(chunk);
      if (ev) onEvent(ev);
    }
  }
}

function parseSSE(chunk: string): StreamEvent | null {
  let event = "message";
  let data = "";
  for (const line of chunk.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return null;
  try {
    const parsed = JSON.parse(data);
    return { type: event, ...parsed } as StreamEvent;
  } catch {
    return null;
  }
}
