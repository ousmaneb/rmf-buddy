import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  type BaselineDiff,
  type ChatMode,
  type ChatTurn,
  type Control,
  type ControlSummary,
  type EmassTerm,
  type EmassTopic,
  type EmassTopicSummary,
  type Family,
  type Flashcard,
  type Grade,
  type GrcTerm,
  type GrcTopic,
  type GrcTopicSummary,
  type NistPub,
  type NistPubSummary,
  type Scenario,
  getBaselineDiff,
  getControl,
  getEmassTopic,
  getFlashcards,
  getGrcTopic,
  getNistPublication,
  getScenario,
  gradeAnswer,
  listControls,
  listEmassGlossary,
  listEmassTopics,
  listFamilies,
  listGrcGlossary,
  listGrcTopics,
  listNistPublications,
  streamChat,
} from "./api";
import { RichMarkdown } from "./components/RichMarkdown";

type Tab = "chat" | "browse" | "emass" | "grc" | "library" | "study";

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  // Incrementing counter so ChatView can detect a tab-click and return to its
  // welcome screen even when it's already mounted.
  const [chatHomeNonce, setChatHomeNonce] = useState(0);

  function selectTab(t: Tab) {
    if (t === "chat") setChatHomeNonce((n) => n + 1);
    setTab(t);
  }

  return (
    <div className="h-full flex flex-col bg-slate-50">
      <Header tab={tab} setTab={selectTab} />
      <div className="flex-1 min-h-0 overflow-hidden">
        {tab === "chat" && <ChatView homeNonce={chatHomeNonce} />}
        {tab === "browse" && <BrowseView />}
        {tab === "emass" && <EmassView />}
        {tab === "grc" && <GrcView />}
        {tab === "library" && <LibraryView />}
        {tab === "study" && <StudyView />}
      </div>
    </div>
  );
}

const TAB_INFO: Record<Tab, { label: string; sub: string }> = {
  chat: { label: "Chat", sub: "Ask anything" },
  browse: { label: "Controls", sub: "Look up a security control" },
  emass: { label: "eMASS Guide", sub: "How DoD's RMF tool works" },
  grc: { label: "GRC Guide", sub: "Frameworks, risk, audit" },
  library: { label: "NIST Docs", sub: "Reference publications" },
  study: { label: "Practice", sub: "Flashcards & quizzes" },
};

function Header({ tab, setTab }: { tab: Tab; setTab: (t: Tab) => void }) {
  return (
    <header className="shrink-0 bg-white border-b border-slate-200 px-3 sm:px-6 py-3 flex items-center gap-3 sm:gap-6">
      <button
        onClick={() => setTab("chat")}
        title="Go to home"
        className="shrink-0 text-left hover:opacity-75 transition cursor-pointer"
      >
        <div className="font-bold text-base sm:text-lg text-slate-900 leading-tight sm:leading-7">RMF Buddy</div>
        <div className="text-[11px] text-slate-500 leading-tight hidden sm:block">
          Your friendly RMF tutor
        </div>
      </button>
      <nav className="ml-auto flex gap-1 overflow-x-auto -mx-1 px-1">
        {(Object.keys(TAB_INFO) as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            title={TAB_INFO[t].sub}
            className={`shrink-0 px-2 sm:px-3 py-2 rounded text-sm font-medium leading-tight text-left whitespace-nowrap ${
              tab === t ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            <div>{TAB_INFO[t].label}</div>
            <div
              className={`text-[10px] font-normal hidden md:block ${
                tab === t ? "text-slate-300" : "text-slate-400"
              }`}
            >
              {TAB_INFO[t].sub}
            </div>
          </button>
        ))}
      </nav>
    </header>
  );
}

// ============================================================
// CHAT
// ============================================================

type ToolEvent = { id: string; name: string; status: "running" | "done"; summary?: string };

type Message = {
  role: "user" | "assistant";
  content: string;
  tools?: ToolEvent[];
  done?: boolean;
};

type Conversation = {
  id: string;
  title: string;
  updatedAt: number;
  messages: Message[];
};

const CONV_STORAGE_KEY = "rmf-buddy:conversations";

function loadConversations(): Conversation[] {
  try {
    const raw = localStorage.getItem(CONV_STORAGE_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as Conversation[];
    return arr.sort((a, b) => b.updatedAt - a.updatedAt);
  } catch {
    return [];
  }
}

function saveConversations(list: Conversation[]) {
  try {
    localStorage.setItem(CONV_STORAGE_KEY, JSON.stringify(list.slice(0, 50)));
  } catch {
    /* quota exceeded - best effort */
  }
}

function newConversation(): Conversation {
  return { id: crypto.randomUUID(), title: "New conversation", updatedAt: Date.now(), messages: [] };
}

type ModeColor = { bg: string; border: string; text: string; hover: string };

const MODE_INFO: Record<ChatMode, { label: string; help: string; needs?: string[]; hint?: string; color?: ModeColor }> = {
  ask: {
    label: "Just ask",
    help: "Type any question about RMF, controls, CCIs, or eMASS.",
  },
  compare: {
    label: "Compare two controls",
    help: "See the differences side-by-side.",
    needs: ["control_a", "control_b"],
    hint: "Pick two controls (e.g. AC-2 and AC-3) and see exactly how they differ.",
    color: { bg: "bg-emerald-50", border: "border-emerald-300", text: "text-emerald-900", hover: "hover:bg-emerald-100" },
  },
  implement: {
    label: "Write implementation statement",
    help: "Get an eMASS-ready paragraph you can paste into your package.",
    needs: ["control", "system_context"],
    hint: "Tell me which control + a sentence about your system, and I'll draft the implementation statement.",
    color: { bg: "bg-blue-50", border: "border-blue-300", text: "text-blue-900", hover: "hover:bg-blue-100" },
  },
  assess: {
    label: "Plan an assessment",
    help: "Build a test plan from NIST 800-53A objectives.",
    needs: ["control"],
    hint: "Pick the control you're testing, get a checklist of what to examine / interview / test.",
    color: { bg: "bg-amber-50", border: "border-amber-300", text: "text-amber-900", hover: "hover:bg-amber-100" },
  },
  poam: {
    label: "Draft a POA&M item",
    help: "Turn a finding into a complete eMASS POA&M entry.",
    needs: ["control", "weakness"],
    hint: "Describe the weakness - get a POA&M draft with severity, milestones, and risk-acceptance notes.",
    color: { bg: "bg-rose-50", border: "border-rose-300", text: "text-rose-900", hover: "hover:bg-rose-100" },
  },
  testresult: {
    label: "Draft a test result",
    help: "Per-CCI test result entry for the SCA to use.",
    needs: ["control", "finding"],
    hint: "Give me the control + your finding, get back a draft test result with assessment methods and tester comments.",
    color: { bg: "bg-violet-50", border: "border-violet-300", text: "text-violet-900", hover: "hover:bg-violet-100" },
  },
};

function ChatView({ homeNonce = 0 }: { homeNonce?: number }) {
  const [conversations, setConversations] = useState<Conversation[]>(() => loadConversations());
  // Default to no active conversation -> show the welcome screen on first load.
  const [activeId, setActiveId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<ChatMode>("ask");
  const [ctx, setCtx] = useState<Record<string, string>>({});
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const active = conversations.find((c) => c.id === activeId) ?? null;
  const messages = active?.messages ?? [];

  // When the user clicks the Chat tab in the top nav, return to the welcome
  // screen by deselecting the active conversation. Skip on initial mount.
  const firstNonce = useRef(homeNonce);
  useEffect(() => {
    if (homeNonce === firstNonce.current) return;
    abortRef.current?.abort();
    setActiveId(null);
    setInput("");
    setMode("ask");
    setCtx({});
  }, [homeNonce]);

  const persist = useCallback((list: Conversation[]) => {
    setConversations(list);
    saveConversations(list);
  }, []);

  useEffect(() => {
    // No messages = welcome screen: pin to top so "Hi, I'm RMF Buddy" is visible.
    // Has messages = active chat: scroll to bottom for new content.
    if (!scrollRef.current) return;
    if (messages.length === 0) {
      scrollRef.current.scrollTo({ top: 0 });
    } else {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  function ensureActive(): Conversation {
    if (active) return active;
    const fresh = newConversation();
    persist([fresh, ...conversations]);
    setActiveId(fresh.id);
    return fresh;
  }

  // Functional update keyed by an explicit id. Doesn't depend on `activeId`
  // closure (which can be stale during streaming, causing updates to drop).
  function updateById(id: string, updater: (c: Conversation) => Conversation) {
    setConversations((list) => {
      const next = list.map((c) => (c.id === id ? updater(c) : c));
      saveConversations(next);
      return next;
    });
  }

  function startNew() {
    abortRef.current?.abort();
    const fresh = newConversation();
    persist([fresh, ...conversations]);
    setActiveId(fresh.id);
    setInput("");
  }

  function deleteConversation(id: string) {
    const remaining = conversations.filter((c) => c.id !== id);
    persist(remaining);
    if (activeId === id) setActiveId(remaining[0]?.id ?? null);
  }

  async function send(override?: string) {
    const text = (override ?? input).trim();
    if (!text || streaming) return;
    if (override === undefined) setInput("");

    let conv = ensureActive();
    if (conv.messages.length === 0) {
      conv = { ...conv, title: text.slice(0, 60) };
    }
    const targetId = conv.id;
    const newMsgs: Message[] = [
      ...conv.messages,
      { role: "user", content: text, done: true },
      { role: "assistant", content: "", tools: [], done: false },
    ];
    const updatedConv: Conversation = { ...conv, messages: newMsgs, updatedAt: Date.now() };
    persist(
      [updatedConv, ...conversations.filter((c) => c.id !== targetId)].sort(
        (a, b) => b.updatedAt - a.updatedAt
      )
    );
    setActiveId(targetId);

    const cleanTurns: ChatTurn[] = newMsgs
      .filter((m) => !(m.role === "assistant" && !m.content))
      .map((m) => ({ role: m.role, content: m.content }));

    setStreaming(true);
    abortRef.current = new AbortController();

    try {
      await streamChat(
        cleanTurns,
        mode,
        ctx,
        (e) => {
          updateById(targetId, (c) => {
            const list = [...c.messages];
            const last = list[list.length - 1];
            if (!last || last.role !== "assistant") return c;
            const upd = { ...last };
            if (e.type === "text") {
              upd.content += e.text;
            } else if (e.type === "tool_use_start") {
              upd.tools = [...(upd.tools || []), { id: e.id, name: e.name, status: "running" }];
            } else if (e.type === "tool_call") {
              upd.tools = (upd.tools || []).map((t) =>
                t.id === e.id ? { ...t, summary: paramsHint(e.name, e.input) } : t
              );
            } else if (e.type === "tool_result") {
              upd.tools = (upd.tools || []).map((t) =>
                t.id === e.id ? { ...t, status: "done", summary: e.summary } : t
              );
            } else if (e.type === "done") {
              upd.done = true;
            } else if (e.type === "error") {
              upd.content += `\n\n**Error:** ${e.message}`;
              upd.done = true;
            }
            list[list.length - 1] = upd;
            return { ...c, messages: list, updatedAt: Date.now() };
          });
        },
        abortRef.current.signal
      );
    } catch (err: any) {
      updateById(targetId, (c) => {
        const list = [...c.messages];
        const last = list[list.length - 1];
        if (last?.role === "assistant") {
          list[list.length - 1] = {
            ...last,
            content: last.content + `\n\n**Network error:** ${err.message || err}`,
            done: true,
          };
        }
        return { ...c, messages: list };
      });
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  return (
    <div className="h-full flex min-h-0">
      <aside className="hidden md:flex w-[220px] lg:w-[260px] shrink-0 border-r border-slate-200 bg-slate-50 flex-col min-h-0">
        <div className="p-3 border-b border-slate-200">
          <button
            onClick={startNew}
            className="w-full bg-slate-900 text-white text-sm font-semibold py-2 rounded-sm hover:bg-slate-800"
          >
            + New chat
          </button>
        </div>
        <ul className="flex-1 min-h-0 overflow-y-auto">
          {conversations.length === 0 && (
            <li className="text-sm text-slate-500 italic px-3 py-2">No history yet.</li>
          )}
          {conversations.map((c) => (
            <li key={c.id} className="group">
              <div
                className={`flex items-center gap-1 px-3 py-2 cursor-pointer text-sm ${
                  c.id === activeId ? "bg-white border-l-4 border-slate-900" : "hover:bg-white/60"
                }`}
                onClick={() => setActiveId(c.id)}
              >
                <span className="flex-1 truncate text-slate-700">{c.title || "(untitled)"}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm("Delete this conversation?")) deleteConversation(c.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 text-xs"
                  title="Delete"
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
        <div className="px-3 py-2 text-[10px] text-slate-400 border-t border-slate-200">
          History stored locally in your browser.
        </div>
      </aside>
      <section
        className="flex-1 bg-white min-w-0 min-h-0 grid"
        style={{ gridTemplateRows: "auto minmax(0,1fr) auto" }}
      >
        <ModeBar
          mode={mode}
          setMode={setMode}
          ctx={ctx}
          setCtx={setCtx}
          streaming={streaming}
          onRunTemplate={(p) => send(p)}
        />
        <div ref={scrollRef} className="overflow-y-auto px-6 py-4 space-y-6">
          {messages.length === 0 && <Suggestions onPick={(s) => setInput(s)} />}
          {messages.map((m, i) => (
            <MessageView key={i} m={m} />
          ))}
        </div>
        <form
          className="border-t border-slate-200 px-3 pt-3 bg-white flex gap-2"
          style={{ paddingBottom: "100px" }}
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              mode === "ask"
                ? "Type your question here and press Enter…"
                : `Type your request - ${MODE_INFO[mode].help}`
            }
            className="flex-1 border border-slate-300 rounded-lg px-4 py-3 text-base focus:outline-hidden focus:ring-2 focus:ring-slate-900 focus:border-slate-900"
            disabled={streaming}
            autoFocus
          />
          {streaming ? (
            <button
              type="button"
              onClick={() => abortRef.current?.abort()}
              className="bg-red-600 text-white px-5 py-3 rounded-lg font-semibold hover:bg-red-700"
            >
              Stop
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="bg-slate-900 text-white px-6 py-3 rounded-lg font-semibold disabled:opacity-40 hover:bg-slate-800"
            >
              Send →
            </button>
          )}
        </form>
      </section>
    </div>
  );
}

function templatePrompt(mode: ChatMode, ctx: Record<string, string>): string {
  switch (mode) {
    case "compare":
      return `Compare ${ctx.control_a || "?"} and ${ctx.control_b || "?"}.`;
    case "implement":
      return `Write an implementation statement for ${ctx.control || "?"} for this system: ${ctx.system_context || "(no context provided)"}.`;
    case "assess":
      return `Build an assessment plan for ${ctx.control || "?"}.`;
    case "poam":
      return `Draft a POA&M item for ${ctx.control || "?"}. Weakness: ${ctx.weakness || "(unspecified)"}.`;
    case "testresult":
      return `Draft a test result for ${ctx.control || "?"}. Finding: ${ctx.finding || "(none - produce a Compliant template)"}.`;
    default:
      return "";
  }
}

function ModeBar({
  mode,
  setMode,
  ctx,
  setCtx,
  onRunTemplate,
  streaming,
}: {
  mode: ChatMode;
  setMode: (m: ChatMode) => void;
  ctx: Record<string, string>;
  setCtx: (c: Record<string, string>) => void;
  onRunTemplate: (prompt: string) => void;
  streaming: boolean;
}) {
  const needs = MODE_INFO[mode].needs || [];
  const advanced = mode !== "ask";
  const ready = needs.every((f) => (ctx[f] || "").trim().length > 0);

  function close() {
    setMode("ask");
    setCtx({});
  }
  const activeColor = advanced ? MODE_INFO[mode].color! : null;

  return (
    <div className="shrink-0 border-b border-slate-200">
      {/* Always-visible templates row */}
      <div className="bg-slate-50 px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="shrink-0 text-xs font-bold uppercase tracking-wider text-slate-500">
            Templates:
          </span>
          <div className="flex-1 flex items-center gap-2 overflow-x-auto pb-1">
            {(Object.keys(MODE_INFO) as ChatMode[])
              .filter((m) => m !== "ask")
              .map((m) => {
                const c = MODE_INFO[m].color!;
                const selected = m === mode;
                return (
                  <button
                    key={m}
                    onClick={() => (selected ? close() : setMode(m))}
                    title={MODE_INFO[m].hint || MODE_INFO[m].help}
                    className={
                      "shrink-0 text-sm font-semibold px-3 py-1.5 rounded-lg border transition whitespace-nowrap " +
                      (selected
                        ? `${c.bg} ${c.text} border-2 border-slate-900 shadow-xs`
                        : `${c.bg} ${c.border} ${c.text} ${c.hover}`)
                    }
                  >
                    {selected ? "✓ " : ""}
                    {MODE_INFO[m].label}
                  </button>
                );
              })}
          </div>
          {advanced && (
            <button
              onClick={close}
              title="Cancel template and return to plain chat"
              className="shrink-0 w-7 h-7 rounded-full bg-white border border-slate-300 text-slate-600 hover:bg-slate-100 hover:text-slate-900 flex items-center justify-center text-sm font-bold leading-none"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Active template fill-in panel */}
      {advanced && activeColor && (
        <div className={`px-4 py-3 ${activeColor.bg} border-t border-slate-200`}>
          <div className="text-xs text-slate-700 mb-2">
            {MODE_INFO[mode].hint || MODE_INFO[mode].help}
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            {needs.map((field) => (
              <input
                key={field}
                value={ctx[field] || ""}
                onChange={(e) => setCtx({ ...ctx, [field]: e.target.value })}
                placeholder={fieldPlaceholder(field)}
                className="text-sm border border-slate-300 rounded-sm px-3 py-1.5 w-64 bg-white"
              />
            ))}
            <button
              onClick={() => ready && !streaming && onRunTemplate(templatePrompt(mode, ctx))}
              disabled={!ready || streaming}
              className="bg-slate-900 text-white px-4 py-1.5 rounded-sm font-semibold disabled:opacity-40 hover:bg-slate-800 text-sm"
            >
              Generate →
            </button>
            <button
              onClick={close}
              className="text-sm text-slate-600 hover:text-slate-900 underline ml-1"
            >
              Cancel
            </button>
            {!ready && (
              <span className="text-xs text-slate-500">Fill in all fields to enable</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function fieldPlaceholder(f: string): string {
  switch (f) {
    case "control":
      return "control id (e.g. ac-2)";
    case "control_a":
      return "control A (e.g. au-2)";
    case "control_b":
      return "control B (e.g. au-12)";
    case "system_context":
      return "system context (e.g. Linux web app, Moderate)";
    case "weakness":
      return "weakness (e.g. password complexity not enforced)";
    case "finding":
      return "finding (or blank for Compliant template)";
    default:
      return f;
  }
}

function paramsHint(name: string, input: Record<string, unknown>): string {
  const k = Object.keys(input);
  if (k.length === 0) return "";
  return k.map((x) => `${x}=${String(input[x]).slice(0, 40)}`).join(", ");
}

function Suggestions({ onPick }: { onPick: (s: string) => void }) {
  const items = [
    {
      cat: "Beginner",
      q: "I'm new to RMF - what is it and where do I start?",
    },
    {
      cat: "Beginner",
      q: "What does ATO mean and how do I get one?",
    },
    {
      cat: "Look up a control",
      q: "What control covers account lockout after failed logins?",
    },
    {
      cat: "Look up a control",
      q: "List the AU family controls in the Moderate baseline.",
    },
    {
      cat: "eMASS",
      q: "Walk me through the RMF lifecycle in eMASS step by step.",
    },
    {
      cat: "eMASS",
      q: "How do I document AC-2 in eMASS? What artifacts do I need?",
    },
    {
      cat: "Threats",
      q: "Which controls defend against credential dumping (T1003)?",
    },
  ];
  return (
    <div className="max-w-2xl mx-auto mt-2 mb-4">
      <h2 className="text-2xl font-bold text-slate-900 mb-2">Hi, I'm RMF Buddy.</h2>
      <p className="text-slate-700 mb-1">
        Ask me anything about the Risk Management Framework, NIST controls, CCIs, eMASS, or how to handle a real RMF task.
      </p>
      <p className="text-sm text-slate-500 mb-5">
        I have live access to all 1,196 NIST 800-53 controls, 5,137 CCIs, MITRE ATT&CK mappings, an eMASS knowledge base,
        and the public web for NIST/DISA pages. Just type your question below - or pick one to get started.
      </p>

      <div className="space-y-3">
        {Array.from(new Set(items.map((i) => i.cat))).map((cat) => (
          <div key={cat}>
            <div className="text-[11px] uppercase tracking-wider font-bold text-slate-500 mb-1">{cat}</div>
            <div className="grid gap-1.5">
              {items
                .filter((i) => i.cat === cat)
                .map((i) => (
                  <button
                    key={i.q}
                    onClick={() => onPick(i.q)}
                    className="text-left text-sm bg-white hover:bg-slate-50 border border-slate-200 rounded-md px-3 py-2 text-slate-700 hover:border-slate-400 transition"
                  >
                    {i.q}
                  </button>
                ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 text-xs text-slate-500 italic">
        Tip: The "Templates" button above the input has shortcuts for common eMASS tasks like drafting an implementation
        statement or a POA&amp;M item.
      </div>
    </div>
  );
}

const TOOL_LABEL: Record<string, string> = {
  search_controls: "Searching the catalog",
  get_control: "Looking up a control",
  get_cci: "Looking up a CCI",
  list_controls_in_family: "Listing controls in a family",
  find_related_controls: "Finding related controls",
  get_assessment_procedures: "Fetching assessment procedures",
  compare_controls: "Comparing controls",
  search_emass: "Searching the eMASS guide",
  get_emass_topic: "Reading an eMASS topic",
  lookup_emass_term: "Looking up an acronym",
  list_emass_topics: "Listing eMASS topics",
  list_nist_publications: "Listing NIST documents",
  get_nist_publication: "Reading a NIST document",
  get_attack_techniques_for_control: "Looking up ATT&CK coverage",
  get_controls_for_technique: "Finding controls for an ATT&CK technique",
  search_attack_techniques: "Searching ATT&CK techniques",
  web_fetch: "Fetching a NIST/DISA web page",
  web_search: "Searching the web (NIST/DISA only)",
};

function MessageView({ m }: { m: Message }) {
  if (m.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-slate-900 text-white rounded-lg px-4 py-2 max-w-3xl whitespace-pre-wrap">
          {m.content}
        </div>
      </div>
    );
  }
  return (
    <div className="max-w-4xl">
      {m.tools && m.tools.length > 0 && (
        <div className="mb-3 space-y-1">
          {m.tools.map((t) => {
            const label = TOOL_LABEL[t.name] || t.name;
            const isRunning = t.status === "running";
            return (
              <div
                key={t.id}
                className={`text-xs flex items-center gap-2 ${
                  isRunning ? "text-blue-700" : "text-slate-500"
                }`}
                title={t.summary}
              >
                <span className={isRunning ? "animate-pulse" : ""}>
                  {isRunning ? "•" : "✓"}
                </span>
                <span>
                  {label}
                  {!isRunning && t.summary && t.summary !== "ok" ? (
                    <span className="text-slate-400"> - {t.summary}</span>
                  ) : null}
                </span>
              </div>
            );
          })}
        </div>
      )}
      <div className="prose-rmf">
        {m.content ? <RichMarkdown text={m.content} /> : !m.done && <span className="text-slate-400 italic">Thinking…</span>}
      </div>
    </div>
  );
}

// ============================================================
// BROWSE
// ============================================================

function BrowseView() {
  const [families, setFamilies] = useState<Family[]>([]);
  const [family, setFamily] = useState("");
  const [baseline, setBaseline] = useState("");
  const [q, setQ] = useState("");
  const [items, setItems] = useState<ControlSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [showDiff, setShowDiff] = useState(false);
  const detailRef = useRef<HTMLElement>(null);

  // If the search query looks like a CCI ID, deep-link to it within the
  // selected control's detail panel.
  const targetCci = useMemo(() => {
    const s = q.trim();
    if (!s) return null;
    const m = s.match(/CCI-(\d{1,6})/i);
    if (m) return `CCI-${m[1].padStart(6, "0").toUpperCase()}`;
    if (/^\d{1,6}$/.test(s)) return `CCI-${s.padStart(6, "0")}`;
    return null;
  }, [q]);

  useEffect(() => {
    listFamilies().then(setFamilies);
  }, []);
  useEffect(() => {
    listControls({ family, baseline, q }).then(setItems);
  }, [family, baseline, q]);
  useEffect(() => {
    // Only scroll to top when there's no target CCI; ControlDetail handles
    // the scroll-to-CCI itself when targetCci is set.
    if (selected && !targetCci) detailRef.current?.scrollTo({ top: 0 });
  }, [selected, targetCci]);

  if (showDiff) {
    return <BaselineDiffView onClose={() => setShowDiff(false)} />;
  }

  return (
    <div className="h-full flex min-h-0">
      <section
        className={`w-full lg:w-[420px] shrink-0 border-r border-slate-200 bg-white flex-col min-h-0 ${
          selected ? "hidden lg:flex" : "flex"
        }`}
      >
        <div className="p-4 border-b border-slate-200 space-y-2">
          <div className="text-xs text-slate-500 mb-3">
            Browse all 1,196 NIST 800-53 controls. Click one to see its full text, CCIs, and ATT&amp;CK coverage.
          </div>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search by control (AC-2), CCI (CCI-000213), title, or any keyword..."
            className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
          />
          <div className="flex gap-2">
            <select
              value={family}
              onChange={(e) => setFamily(e.target.value)}
              className="flex-1 border border-slate-300 rounded-md px-2 py-1.5 text-sm"
            >
              <option value="">All families</option>
              {families.map((f) => (
                <option key={f.family} value={f.family}>
                  {f.family.toUpperCase()} - {f.family_name} ({f.n})
                </option>
              ))}
            </select>
            <select
              value={baseline}
              onChange={(e) => setBaseline(e.target.value)}
              className="border border-slate-300 rounded-md px-2 py-1.5 text-sm"
            >
              <option value="">All baselines</option>
              <option value="LOW">Low</option>
              <option value="MODERATE">Moderate</option>
              <option value="HIGH">High</option>
            </select>
          </div>
          <div className="flex items-center justify-between gap-2">
            <div className="text-xs text-slate-500">{items.length} controls</div>
            <button
              onClick={() => setShowDiff(true)}
              className="text-xs font-semibold px-3 py-1.5 rounded-sm bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 text-emerald-900"
              title="See which controls are added or removed between Low / Moderate / High baselines"
            >
              Compare Baselines
            </button>
          </div>
        </div>
        <ul className="flex-1 min-h-0 overflow-y-auto divide-y divide-slate-100">
          {items.map((c) => (
            <li key={c.id}>
              <button
                onClick={() => setSelected(c.id)}
                className={`w-full text-left px-4 py-2 hover:bg-slate-50 ${
                  selected === c.id ? "bg-blue-50" : ""
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-slate-800">{c.label}</span>
                  {c.is_enhancement === 1 && (
                    <span className="text-[10px] bg-slate-200 text-slate-700 px-1 rounded-sm">ENH</span>
                  )}
                </div>
                <div className="text-sm text-slate-700">{c.title}</div>
              </button>
            </li>
          ))}
        </ul>
      </section>
      <section
        ref={detailRef}
        className={`flex-1 min-w-0 overflow-y-auto bg-slate-50 ${
          selected ? "block" : "hidden lg:block"
        }`}
      >
        {selected ? (
          <>
            <button
              onClick={() => setSelected(null)}
              className="lg:hidden m-3 inline-flex items-center gap-1 text-sm text-slate-700 hover:text-slate-900 bg-white border border-slate-300 rounded-md px-3 py-1.5"
            >
              {"<-"} Back to list
            </button>
            <ControlDetail id={selected} highlightCci={targetCci} />
          </>
        ) : (
          <div className="p-8 text-slate-500">
            Select a control to view its statement, discussion, baselines, CCIs, and assessment objectives.
          </div>
        )}
      </section>
    </div>
  );
}

function ControlDetail({ id, highlightCci }: { id: string; highlightCci?: string | null }) {
  const [ctrl, setCtrl] = useState<Control | null>(null);
  useEffect(() => {
    setCtrl(null);
    getControl(id).then(setCtrl);
  }, [id]);

  // After ctrl loads, if we have a highlightCci, scroll it into view + flash.
  useEffect(() => {
    if (!ctrl || !highlightCci) return;
    const el = document.getElementById(`cci-${highlightCci}`);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.classList.add("cci-flash");
    const t = setTimeout(() => el.classList.remove("cci-flash"), 2400);
    return () => clearTimeout(t);
  }, [ctrl, highlightCci]);

  if (!ctrl) return <div className="p-6 text-slate-400 italic">Loading…</div>;
  return (
    <div className="p-6 max-w-3xl">
      <div className="text-xs text-slate-500 uppercase tracking-wider">{ctrl.family_name}</div>
      <h2 className="text-2xl font-bold text-slate-900">
        {ctrl.label} - {ctrl.title}
      </h2>
      <div className="mt-1 flex gap-1">
        {ctrl.baselines.map((b) => (
          <span
            key={b}
            className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-sm font-semibold"
          >
            {b}
          </span>
        ))}
      </div>
      <Section title="Control Statement">
        <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700">{ctrl.statement}</pre>
      </Section>
      {ctrl.guidance && (
        <Section title="Discussion">
          <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700">{ctrl.guidance}</pre>
        </Section>
      )}
      {ctrl.assessment && (
        <Section title="Assessment Objectives (NIST 800-53A)">
          <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700">{ctrl.assessment}</pre>
        </Section>
      )}
      {ctrl.enhancements.length > 0 && (
        <Section title={`Enhancements (${ctrl.enhancements.length})`}>
          <ul className="space-y-1">
            {ctrl.enhancements.map((e) => (
              <li key={e.id} className="text-sm">
                <span className="font-mono font-semibold text-slate-800">{e.label}</span> - {e.title}
              </li>
            ))}
          </ul>
        </Section>
      )}
      <Section title={`Linked CCIs (${ctrl.ccis.length})`}>
        {ctrl.ccis.length === 0 ? (
          <div className="text-sm text-slate-500">No CCIs mapped.</div>
        ) : (
          <ul className="space-y-2">
            {ctrl.ccis.map((c) => {
              const isTarget = highlightCci && c.id.toUpperCase() === highlightCci.toUpperCase();
              return (
                <li
                  key={c.id}
                  id={`cci-${c.id}`}
                  className={
                    "bg-white border rounded-sm p-3 text-sm transition-colors duration-300 " +
                    (isTarget ? "border-amber-500 ring-2 ring-amber-300" : "border-slate-200")
                  }
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono font-semibold text-amber-800">{c.id}</span>
                    {c.control_index && (
                      <span className="text-xs text-slate-500">{"->"} {c.control_index}</span>
                    )}
                    {isTarget && (
                      <span className="text-[10px] bg-amber-200 text-amber-900 px-1.5 py-0.5 rounded-sm font-semibold">
                        SEARCHED
                      </span>
                    )}
                  </div>
                  <div className="text-slate-700">{c.definition}</div>
                </li>
              );
            })}
          </ul>
        )}
      </Section>
      {ctrl.attack && ctrl.attack.length > 0 && (
        <Section title={`Mitigates ${ctrl.attack.length} MITRE ATT&CK Technique${ctrl.attack.length === 1 ? "" : "s"}`}>
          <div className="text-xs text-slate-500 mb-2">
            From the MITRE Center for Threat-Informed Defense NIST 800-53 ↔ ATT&CK mapping.
          </div>
          <ul className="space-y-2">
            {ctrl.attack.map((t) => (
              <li key={t.id} className="bg-white border border-rose-200 rounded-sm p-3 text-sm">
                <div className="flex items-center gap-2 mb-1">
                  <a
                    href={`https://attack.mitre.org/techniques/${t.id.replace(".", "/")}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-mono font-semibold text-rose-800 hover:underline"
                  >
                    {t.id}
                  </a>
                  <span className="text-slate-700 font-medium">{t.name}</span>
                </div>
                {t.rationale && <div className="text-xs text-slate-600">{t.rationale}</div>}
              </li>
            ))}
          </ul>
        </Section>
      )}
      <div className="text-xs text-slate-500 mt-6">
        Source: NIST SP 800-53 Rev. 5, {ctrl.label} ({ctrl.family_name}).
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-5">
      <h3 className="font-semibold text-slate-800 mb-1 mt-4">{title}</h3>
      <div>{children}</div>
    </div>
  );
}

function BaselineDiffView({ onClose }: { onClose: () => void }) {
  const [low, setLow] = useState("LOW");
  const [high, setHigh] = useState("MODERATE");
  const [diff, setDiff] = useState<BaselineDiff | null>(null);

  useEffect(() => {
    setDiff(null);
    getBaselineDiff(low, high).then(setDiff);
  }, [low, high]);

  const sameBaseline = low === high;

  return (
    <div className="h-full overflow-y-auto bg-slate-50">
      <div className="max-w-6xl mx-auto p-6">
        <button
          onClick={onClose}
          className="mb-3 inline-flex items-center gap-1 text-sm text-slate-700 hover:text-slate-900 bg-white border border-slate-300 hover:border-slate-500 rounded-md px-3 py-1.5"
        >
          {"<-"} Back to controls list
        </button>
        <h2 className="text-2xl font-bold text-slate-900 mb-1">Compare Baselines</h2>
        <p className="text-sm text-slate-600 mb-4">
          See which NIST 800-53 Rev. 5 controls are added (or removed) between any two impact baselines.
          Helpful when planning a categorization change or scoping additional control work.
        </p>

        <div className="flex gap-3 items-center flex-wrap mb-4 bg-white border border-slate-200 rounded-lg p-4">
          <label className="text-sm font-semibold text-slate-700">From</label>
          <select
            value={low}
            onChange={(e) => setLow(e.target.value)}
            className="border border-slate-300 rounded-sm px-3 py-1.5 text-sm bg-white"
          >
            <option>LOW</option>
            <option>MODERATE</option>
            <option>HIGH</option>
          </select>
          <span className="text-slate-400">{"->"}</span>
          <label className="text-sm font-semibold text-slate-700">To</label>
          <select
            value={high}
            onChange={(e) => setHigh(e.target.value)}
            className="border border-slate-300 rounded-sm px-3 py-1.5 text-sm bg-white"
          >
            <option>LOW</option>
            <option>MODERATE</option>
            <option>HIGH</option>
          </select>
          {diff && !sameBaseline && (
            <div className="ml-2 flex gap-3 text-xs">
              <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded-sm font-semibold">
                {diff.shared_count} shared
              </span>
              <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded-sm font-semibold">
                +{diff.added.length} added
              </span>
              <span className="bg-rose-100 text-rose-800 px-2 py-1 rounded-sm font-semibold">
                -{diff.removed.length} removed
              </span>
            </div>
          )}
        </div>

        {sameBaseline ? (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-900">
            Pick two different baselines to see a comparison.
          </div>
        ) : !diff ? (
          <div className="text-slate-400 italic p-4">Loading...</div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            <DiffColumn
              title={`Added going ${diff.from} -> ${diff.to}`}
              color="emerald"
              controls={diff.added}
            />
            <DiffColumn
              title={`Removed going ${diff.from} -> ${diff.to}`}
              color="rose"
              controls={diff.removed}
            />
          </div>
        )}
      </div>
    </div>
  );
}

function DiffColumn({
  title,
  color,
  controls,
}: {
  title: string;
  color: "emerald" | "rose";
  controls: ControlSummary[];
}) {
  const head =
    color === "emerald"
      ? "bg-emerald-50 border-emerald-200 text-emerald-900"
      : "bg-rose-50 border-rose-200 text-rose-900";
  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
      <div className={`${head} border-b px-3 py-2 text-sm font-semibold`}>{title} ({controls.length})</div>
      <ul className="divide-y divide-slate-100 max-h-[60vh] overflow-y-auto">
        {controls.length === 0 && (
          <li className="text-slate-500 text-sm p-3 italic">none</li>
        )}
        {controls.map((c) => (
          <li key={c.id} className="px-3 py-1.5 text-sm">
            <span className="font-mono font-semibold text-slate-800">{c.label}</span>
            {c.is_enhancement === 1 && (
              <span className="ml-1 text-[10px] bg-slate-200 text-slate-700 px-1 rounded-sm">ENH</span>
            )}
            <span className="text-slate-700"> - {c.title}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ============================================================
// GRC GUIDE
// ============================================================

function GrcView() {
  const [sub, setSub] = useState<"topics" | "glossary">("topics");
  return (
    <div className="h-full flex flex-col">
      <div className="bg-slate-50 border-b border-slate-200 px-4 py-2 flex gap-2">
        {(["topics", "glossary"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setSub(s)}
            className={`px-3 py-1 rounded text-sm font-semibold ${
              sub === s ? "bg-slate-900 text-white" : "bg-white border border-slate-200 text-slate-700"
            }`}
          >
            {s === "topics" ? "Knowledge Base" : "Glossary"}
          </button>
        ))}
        <span className="ml-2 text-xs text-slate-500 self-center hidden md:inline">
          Frameworks (ISO 27001, SOC 2, PCI, HIPAA, GDPR, SOX, FedRAMP, CMMC…), risk theory, audit, governance.
        </span>
      </div>
      <div className="flex-1 min-h-0 overflow-hidden">
        {sub === "topics" ? <GrcTopicsView /> : <GrcGlossaryView />}
      </div>
    </div>
  );
}

function GrcTopicsView() {
  const [topics, setTopics] = useState<GrcTopicSummary[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [topic, setTopic] = useState<GrcTopic | null>(null);
  const [filter, setFilter] = useState("");
  const bodyRef = useRef<HTMLElement>(null);

  useEffect(() => {
    listGrcTopics().then((t) => {
      setTopics(t);
      if (!active && t.length) setActive(t[0].slug);
    });
  }, []);

  useEffect(() => {
    if (active) {
      setTopic(null);
      bodyRef.current?.scrollTo({ top: 0 });
      getGrcTopic(active).then((t) => {
        setTopic(t);
        bodyRef.current?.scrollTo({ top: 0 });
      });
    }
  }, [active]);

  const grouped = useMemo(() => {
    const f = filter.toLowerCase();
    const visible = topics.filter(
      (t) => !f || t.title.toLowerCase().includes(f) || t.category.toLowerCase().includes(f)
    );
    const out: Record<string, GrcTopicSummary[]> = {};
    for (const t of visible) (out[t.category] ||= []).push(t);
    return out;
  }, [topics, filter]);

  const [mobileOpened, setMobileOpened] = useState(false);

  return (
    <div className="h-full flex min-h-0">
      <aside
        className={`w-full lg:w-[320px] shrink-0 border-r border-slate-200 bg-white flex-col min-h-0 ${
          mobileOpened ? "hidden lg:flex" : "flex"
        }`}
      >
        <div className="p-3 border-b border-slate-200">
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter topics..."
            className="w-full border border-slate-300 rounded-md px-3 py-1.5 text-sm"
          />
        </div>
        <nav className="flex-1 min-h-0 overflow-y-auto py-2">
          {Object.entries(grouped).map(([cat, items]) => (
            <div key={cat} className="mb-3">
              <div className="px-4 text-[10px] uppercase tracking-wider font-bold text-slate-500 mb-1">
                {cat}
              </div>
              {items.map((t) => (
                <button
                  key={t.slug}
                  onClick={() => {
                    setActive(t.slug);
                    setMobileOpened(true);
                  }}
                  className={`w-full text-left px-4 py-1.5 text-sm hover:bg-slate-50 ${
                    active === t.slug ? "bg-emerald-50 text-emerald-900 font-semibold" : "text-slate-700"
                  }`}
                >
                  {t.title}
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>
      <section
        ref={bodyRef}
        className={`flex-1 min-w-0 overflow-y-auto bg-slate-50 ${
          mobileOpened ? "block" : "hidden lg:block"
        }`}
      >
        <button
          onClick={() => setMobileOpened(false)}
          className="lg:hidden m-3 inline-flex items-center gap-1 text-sm text-slate-700 hover:text-slate-900 bg-white border border-slate-300 rounded-md px-3 py-1.5"
        >
          {"<-"} Back to topics
        </button>
        {!topic ? (
          <div className="p-8 text-slate-400 italic">Loading…</div>
        ) : (
          <div className="max-w-3xl mx-auto p-4 lg:p-8">
            <div className="text-xs text-emerald-700 uppercase tracking-wider font-semibold">
              {topic.category}
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mb-4">{topic.title}</h1>
            <article className="prose-rmf">
              <RichMarkdown text={topic.body} />
            </article>
          </div>
        )}
      </section>
    </div>
  );
}

function GrcGlossaryView() {
  const [terms, setTerms] = useState<GrcTerm[]>([]);
  const [filter, setFilter] = useState("");
  useEffect(() => { listGrcGlossary().then(setTerms); }, []);

  const visible = useMemo(() => {
    const f = filter.toLowerCase().trim();
    if (!f) return terms;
    return terms.filter(
      (t) => t.term.toLowerCase().includes(f) || t.definition.toLowerCase().includes(f)
    );
  }, [terms, filter]);

  return (
    <div className="h-full overflow-y-auto bg-slate-50">
      <div className="max-w-3xl mx-auto p-6">
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Search terms or definitions..."
          className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white mb-4"
        />
        <div className="text-xs text-slate-500 mb-3">
          {visible.length} of {terms.length} terms
        </div>
        <dl className="space-y-3">
          {visible.map((t) => (
            <div key={t.term} className="bg-white border border-slate-200 rounded-md p-3">
              <dt className="font-mono font-bold text-emerald-800 text-sm">{t.term}</dt>
              <dd className="text-sm text-slate-700 mt-1">{t.definition}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}

// ============================================================
// NIST PUBLICATION LIBRARY
// ============================================================

function LibraryView() {
  const [pubs, setPubs] = useState<NistPubSummary[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [pub, setPub] = useState<NistPub | null>(null);
  const [filter, setFilter] = useState("");
  const bodyRef = useRef<HTMLElement>(null);

  useEffect(() => {
    listNistPublications().then((p) => {
      setPubs(p);
      if (!active && p.length) setActive(p[0].slug);
    });
  }, []);

  useEffect(() => {
    if (active) {
      setPub(null);
      bodyRef.current?.scrollTo({ top: 0 });
      getNistPublication(active).then((p) => {
        setPub(p);
        bodyRef.current?.scrollTo({ top: 0 });
      });
    }
  }, [active]);

  const grouped = useMemo(() => {
    const f = filter.toLowerCase().trim();
    const visible = !f
      ? pubs
      : pubs.filter(
          (p) =>
            p.title.toLowerCase().includes(f) ||
            p.summary.toLowerCase().includes(f) ||
            p.category.toLowerCase().includes(f) ||
            p.slug.toLowerCase().includes(f)
        );
    const out: Record<string, NistPubSummary[]> = {};
    for (const p of visible) (out[p.category] ||= []).push(p);
    return out;
  }, [pubs, filter]);

  const matchCount = useMemo(
    () => Object.values(grouped).reduce((n, items) => n + items.length, 0),
    [grouped]
  );

  const [mobileOpened, setMobileOpened] = useState(false);

  return (
    <div className="h-full flex min-h-0">
      <aside
        className={`w-full lg:w-[320px] shrink-0 border-r border-slate-200 bg-white flex-col min-h-0 ${
          mobileOpened ? "hidden lg:flex" : "flex"
        }`}
      >
        <div className="p-3 border-b border-slate-200">
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Search by title, summary, or number (e.g. 800-53, FIPS, Zero Trust)"
            className="w-full border border-slate-300 rounded-md px-3 py-1.5 text-sm"
          />
          <div className="text-[11px] text-slate-500 mt-1">
            {matchCount} of {pubs.length} publications
          </div>
        </div>
        <nav className="flex-1 min-h-0 overflow-y-auto py-2">
          {Object.entries(grouped).map(([cat, items]) => (
            <div key={cat} className="mb-3">
              <div className="px-4 text-[10px] uppercase tracking-wider font-bold text-slate-500 mb-1">
                {cat}
              </div>
              {items.map((p) => (
                <button
                  key={p.slug}
                  onClick={() => {
                    setActive(p.slug);
                    setMobileOpened(true);
                  }}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 ${
                    active === p.slug ? "bg-teal-50 text-teal-900 font-semibold" : "text-slate-700"
                  }`}
                >
                  {p.title}
                </button>
              ))}
            </div>
          ))}
          {matchCount === 0 && (
            <div className="px-4 py-6 text-sm text-slate-500 italic">
              No publications match {`"${filter}"`}.
            </div>
          )}
        </nav>
      </aside>
      <section
        ref={bodyRef}
        className={`flex-1 min-w-0 overflow-y-auto bg-slate-50 ${
          mobileOpened ? "block" : "hidden lg:block"
        }`}
      >
        <button
          onClick={() => setMobileOpened(false)}
          className="lg:hidden m-3 inline-flex items-center gap-1 text-sm text-slate-700 hover:text-slate-900 bg-white border border-slate-300 rounded-md px-3 py-1.5"
        >
          {"<-"} Back to publications
        </button>
        {!pub ? (
          <div className="p-8 text-slate-400 italic">Loading…</div>
        ) : (
          <div className="max-w-3xl mx-auto p-4 lg:p-8">
            <div className="text-xs text-teal-700 uppercase tracking-wider font-semibold">
              {pub.category}
            </div>
            <h1 className="text-2xl font-bold text-slate-900">{pub.title}</h1>
            <a
              href={pub.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-teal-700 underline"
            >
              Open at csrc.nist.gov ↗
            </a>
            <div className="bg-white border border-slate-200 rounded-sm p-3 my-4 text-sm text-slate-700">
              {pub.summary}
            </div>
            <article className="prose-rmf">
              <RichMarkdown text={pub.body} />
            </article>
          </div>
        )}
      </section>
    </div>
  );
}

// ============================================================
// eMASS
// ============================================================

function EmassView() {
  const [sub, setSub] = useState<"topics" | "glossary">("topics");
  return (
    <div className="h-full flex flex-col">
      <div className="bg-slate-50 border-b border-slate-200 px-4 py-2 flex gap-2">
        {(["topics", "glossary"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setSub(s)}
            className={`px-3 py-1 rounded text-sm font-semibold ${
              sub === s ? "bg-slate-900 text-white" : "bg-white border border-slate-200 text-slate-700"
            }`}
          >
            {s === "topics" ? "Knowledge Base" : "Glossary"}
          </button>
        ))}
        <span className="ml-2 text-xs text-slate-500 self-center hidden md:inline">
          Practitioner reference based on public DoD/NIST sources. Not authoritative DoD policy.
        </span>
      </div>
      <div className="flex-1 min-h-0 overflow-hidden">
        {sub === "topics" ? <EmassTopicsView /> : <EmassGlossaryView />}
      </div>
    </div>
  );
}

function EmassTopicsView() {
  const [topics, setTopics] = useState<EmassTopicSummary[]>([]);
  const [active, setActive] = useState<string | null>(null);
  const [topic, setTopic] = useState<EmassTopic | null>(null);
  const [filter, setFilter] = useState("");
  const bodyRef = useRef<HTMLElement>(null);

  useEffect(() => {
    listEmassTopics().then((t) => {
      setTopics(t);
      if (!active && t.length) setActive(t[0].slug);
    });
  }, []);

  useEffect(() => {
    if (active) {
      setTopic(null);
      bodyRef.current?.scrollTo({ top: 0 });
      getEmassTopic(active).then((t) => {
        setTopic(t);
        bodyRef.current?.scrollTo({ top: 0 });
      });
    }
  }, [active]);

  const grouped = useMemo(() => {
    const f = filter.toLowerCase();
    const visible = topics.filter(
      (t) => !f || t.title.toLowerCase().includes(f) || t.category.toLowerCase().includes(f)
    );
    const out: Record<string, EmassTopicSummary[]> = {};
    for (const t of visible) (out[t.category] ||= []).push(t);
    return out;
  }, [topics, filter]);

  // Track whether the user has explicitly opened a topic on mobile (vs the
  // initial auto-select). On mobile, only show the body when explicitly opened.
  const [mobileOpened, setMobileOpened] = useState(false);

  return (
    <div className="h-full flex min-h-0">
      <aside
        className={`w-full lg:w-[320px] shrink-0 border-r border-slate-200 bg-white flex-col min-h-0 ${
          mobileOpened ? "hidden lg:flex" : "flex"
        }`}
      >
        <div className="p-3 border-b border-slate-200">
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter topics..."
            className="w-full border border-slate-300 rounded-md px-3 py-1.5 text-sm"
          />
        </div>
        <nav className="flex-1 min-h-0 overflow-y-auto py-2">
          {Object.entries(grouped).map(([cat, items]) => (
            <div key={cat} className="mb-3">
              <div className="px-4 text-[10px] uppercase tracking-wider font-bold text-slate-500 mb-1">
                {cat}
              </div>
              {items.map((t) => (
                <button
                  key={t.slug}
                  onClick={() => {
                    setActive(t.slug);
                    setMobileOpened(true);
                  }}
                  className={`w-full text-left px-4 py-1.5 text-sm hover:bg-slate-50 ${
                    active === t.slug ? "bg-violet-50 text-violet-900 font-semibold" : "text-slate-700"
                  }`}
                >
                  {t.title}
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>
      <section
        ref={bodyRef}
        className={`flex-1 min-w-0 overflow-y-auto bg-slate-50 ${
          mobileOpened ? "block" : "hidden lg:block"
        }`}
      >
        <button
          onClick={() => setMobileOpened(false)}
          className="lg:hidden m-3 inline-flex items-center gap-1 text-sm text-slate-700 hover:text-slate-900 bg-white border border-slate-300 rounded-md px-3 py-1.5"
        >
          {"<-"} Back to topics
        </button>
        {!topic ? (
          <div className="p-8 text-slate-400 italic">Loading…</div>
        ) : (
          <div className="max-w-3xl mx-auto p-4 lg:p-8">
            <div className="text-xs text-violet-700 uppercase tracking-wider font-semibold">
              {topic.category}
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mb-4">{topic.title}</h1>
            <article className="prose-rmf">
              <RichMarkdown text={topic.body} />
            </article>
          </div>
        )}
      </section>
    </div>
  );
}

function EmassGlossaryView() {
  const [terms, setTerms] = useState<EmassTerm[]>([]);
  const [filter, setFilter] = useState("");
  useEffect(() => { listEmassGlossary().then(setTerms); }, []);

  const visible = useMemo(() => {
    const f = filter.toLowerCase().trim();
    if (!f) return terms;
    return terms.filter(
      (t) => t.term.toLowerCase().includes(f) || t.definition.toLowerCase().includes(f)
    );
  }, [terms, filter]);

  return (
    <div className="h-full overflow-y-auto bg-slate-50">
      <div className="max-w-3xl mx-auto p-6">
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Search terms or definitions..."
          className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white mb-4"
        />
        <div className="text-xs text-slate-500 mb-3">
          {visible.length} of {terms.length} terms
        </div>
        <dl className="space-y-3">
          {visible.map((t) => (
            <div key={t.term} className="bg-white border border-slate-200 rounded-md p-3">
              <dt className="font-mono font-bold text-violet-800 text-sm">{t.term}</dt>
              <dd className="text-sm text-slate-700 mt-1">{t.definition}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}

// ============================================================
// STUDY
// ============================================================

function StudyView() {
  const [sub, setSub] = useState<"flashcards" | "scenarios">("flashcards");
  const SUBS = {
    flashcards: { label: "Flashcards", desc: "Quiz yourself on what each control covers." },
    scenarios: { label: "Scenarios", desc: "Read a real-world situation and identify the right controls." },
  } as const;
  return (
    <div className="h-full flex flex-col">
      <div className="shrink-0 bg-slate-50 border-b border-slate-200 px-4 py-3">
        <div className="flex gap-2 flex-wrap">
          {(Object.keys(SUBS) as (keyof typeof SUBS)[]).map((s) => {
            const selected = sub === s;
            return (
              <button
                key={s}
                onClick={() => setSub(s)}
                className={`text-left px-3 py-2 rounded-lg border min-w-[200px] ${
                  selected
                    ? "bg-slate-900 text-white border-slate-900"
                    : "bg-white border-slate-200 text-slate-700 hover:border-slate-400"
                }`}
              >
                <div className="text-sm font-semibold">{SUBS[s].label}</div>
                <div className={`text-[11px] mt-0.5 ${selected ? "text-slate-300" : "text-slate-500"}`}>
                  {SUBS[s].desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>
      <div className="flex-1 min-h-0 overflow-auto bg-slate-50">
        {sub === "flashcards" ? <FlashcardsView /> : <ScenariosView />}
      </div>
    </div>
  );
}

function FlashcardsView() {
  const [families, setFamilies] = useState<Family[]>([]);
  const [family, setFamily] = useState("");
  const [count, setCount] = useState(10);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [i, setI] = useState(0);
  const [reveal, setReveal] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => { listFamilies().then(setFamilies); }, []);

  async function load() {
    setLoading(true);
    setReveal(false);
    setI(0);
    try {
      setCards(await getFlashcards(family || undefined, count));
    } finally {
      setLoading(false);
    }
  }

  const card = cards[i];

  // Keyboard navigation: ←/→ to move, Space/Enter to reveal
  useEffect(() => {
    if (cards.length === 0) return;
    function onKey(e: KeyboardEvent) {
      if (e.target && (e.target as HTMLElement).tagName.match(/INPUT|TEXTAREA|SELECT/)) return;
      if (e.key === "ArrowRight" || e.key === "n") {
        setReveal(false);
        setI((x) => Math.min(cards.length - 1, x + 1));
      } else if (e.key === "ArrowLeft" || e.key === "p") {
        setReveal(false);
        setI((x) => Math.max(0, x - 1));
      } else if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        setReveal((r) => !r);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cards.length]);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white border border-slate-200 rounded-lg p-4 mb-4">
        <h3 className="font-bold text-slate-900 mb-1">How it works</h3>
        <p className="text-sm text-slate-600 mb-3">
          Pick a control family (or leave on "All"), choose how many cards, and click Start.
          Each card asks a question; click the card to reveal the control. Use arrow keys to navigate.
        </p>
        <div className="flex gap-2 flex-wrap items-center">
          <label className="text-xs font-semibold text-slate-700">Family:</label>
          <select
            value={family}
            onChange={(e) => setFamily(e.target.value)}
            className="flex-1 min-w-[180px] border border-slate-300 rounded-sm px-2 py-1.5 text-sm bg-white"
          >
            <option value="">All families</option>
            {families.map((f) => (
              <option key={f.family} value={f.family}>
                {f.family.toUpperCase()} - {f.family_name}
              </option>
            ))}
          </select>
          <label className="text-xs font-semibold text-slate-700">Cards:</label>
          <select
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="border border-slate-300 rounded-sm px-2 py-1.5 text-sm bg-white"
          >
            {[5, 10, 15, 20, 30].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
          <button
            onClick={load}
            disabled={loading}
            className="bg-slate-900 text-white px-4 py-1.5 rounded-sm font-semibold text-sm disabled:opacity-50 hover:bg-slate-800"
          >
            {loading ? "Loading..." : cards.length > 0 ? "New deck" : "Start ->"}
          </button>
        </div>
      </div>

      {!card && !loading && (
        <div className="bg-white border-2 border-dashed border-slate-200 rounded-lg p-10 text-center text-slate-500">
          Click <span className="font-semibold text-slate-700">Start -&gt;</span> to draw a deck of cards.
        </div>
      )}

      {card && (
        <>
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-semibold text-slate-600">
              Card {i + 1} of {cards.length}
            </div>
            <div className="text-[11px] text-slate-400">
              ← prev · → next · space/enter to flip
            </div>
          </div>
          <div className="h-1 bg-slate-200 rounded-full overflow-hidden mb-3">
            <div
              className="h-full bg-slate-900 transition-all"
              style={{ width: `${((i + 1) / cards.length) * 100}%` }}
            />
          </div>

          <div
            onClick={() => setReveal((r) => !r)}
            className={`bg-white border-2 rounded-lg p-6 cursor-pointer min-h-[220px] transition ${
              reveal ? "border-emerald-300" : "border-slate-200 hover:border-slate-400"
            }`}
          >
            {!reveal ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="text-xs uppercase font-bold text-slate-500 mb-2">Question</div>
                <div className="text-lg text-slate-800">{card.front}</div>
                <div className="mt-6 text-sm text-slate-400">click anywhere to reveal answer</div>
              </div>
            ) : (
              <>
                <div className="text-xs uppercase font-bold text-emerald-700 mb-2">Answer</div>
                <div className="font-bold text-slate-900 text-lg">
                  {card.back.label} - {card.back.title}
                </div>
                <div className="text-xs text-slate-500 mb-3">{card.back.family}</div>
                <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700">
                  {card.back.summary}
                </pre>
                <div className="mt-3 text-sm text-slate-400">click to hide</div>
              </>
            )}
          </div>

          <div className="flex items-center justify-between mt-4">
            <button
              onClick={() => {
                setReveal(false);
                setI((x) => Math.max(0, x - 1));
              }}
              disabled={i === 0}
              className="px-3 py-1.5 text-sm bg-white border border-slate-300 rounded-sm hover:border-slate-500 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              {"<-"} Previous
            </button>
            <button
              onClick={() => setReveal((r) => !r)}
              className="px-4 py-1.5 text-sm font-semibold bg-slate-900 text-white rounded-sm hover:bg-slate-800"
            >
              {reveal ? "Hide answer" : "Reveal answer"}
            </button>
            <button
              onClick={() => {
                setReveal(false);
                setI((x) => Math.min(cards.length - 1, x + 1));
              }}
              disabled={i >= cards.length - 1}
              className="px-3 py-1.5 text-sm bg-white border border-slate-300 rounded-sm hover:border-slate-500 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Next {"->"}
            </button>
          </div>

          {i === cards.length - 1 && (
            <div className="mt-4 text-center text-sm text-slate-500">
              Last card. <button onClick={load} className="text-slate-900 underline font-semibold">Draw a new deck</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ScenariosView() {
  const [families, setFamilies] = useState<Family[]>([]);
  const [family, setFamily] = useState("");
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [answer, setAnswer] = useState("");
  const [grade, setGrade] = useState<Grade | null>(null);
  const [loading, setLoading] = useState(false);
  const [grading, setGrading] = useState(false);

  useEffect(() => {
    listFamilies().then(setFamilies);
  }, []);

  async function fresh() {
    setLoading(true);
    setGrade(null);
    setAnswer("");
    setScenario(null);
    try {
      setScenario(await getScenario(family || undefined));
    } finally {
      setLoading(false);
    }
  }

  async function submit() {
    if (!scenario || !answer.trim()) return;
    setGrading(true);
    try {
      setGrade(await gradeAnswer({
        scenario: scenario.scenario,
        expected_controls: scenario.expected_controls,
        user_answer: answer,
      }));
    } finally {
      setGrading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white border border-slate-200 rounded-lg p-4 mb-4">
        <h3 className="font-bold text-slate-900 mb-1">How it works</h3>
        <p className="text-sm text-slate-600 mb-3">
          You'll get a short real-world scenario. Read it, then write which 800-53 controls apply
          and why. You'll get a score and feedback to help you learn.
        </p>
        <div className="flex gap-2 flex-wrap items-center">
          <label className="text-xs font-semibold text-slate-700">Focus on family:</label>
          <select
            value={family}
            onChange={(e) => setFamily(e.target.value)}
            className="flex-1 min-w-[180px] border border-slate-300 rounded-sm px-2 py-1.5 text-sm bg-white"
          >
            <option value="">Any family</option>
            {families.map((f) => (
              <option key={f.family} value={f.family}>
                {f.family.toUpperCase()} - {f.family_name}
              </option>
            ))}
          </select>
          <button
            onClick={fresh}
            disabled={loading}
            className="bg-slate-900 text-white px-4 py-1.5 rounded-sm font-semibold text-sm disabled:opacity-50 hover:bg-slate-800"
          >
            {loading ? "Generating..." : scenario ? "New scenario" : "Start ->"}
          </button>
        </div>
      </div>

      {!scenario && !loading && (
        <div className="bg-white border-2 border-dashed border-slate-200 rounded-lg p-10 text-center text-slate-500">
          Click <span className="font-semibold text-slate-700">Start -&gt;</span> to generate your first scenario.
        </div>
      )}

      {scenario && (
        <>
          <div className="bg-white border border-slate-200 rounded-lg p-4 mb-3">
            <div className="text-xs uppercase font-bold text-slate-500 mb-1">Scenario</div>
            <div className="text-slate-800 leading-relaxed">{scenario.scenario}</div>
          </div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Your answer</label>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="List the 800-53 controls you think apply (e.g. AC-2, AU-6) and a short reason for each..."
            rows={5}
            className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-hidden focus:ring-2 focus:ring-slate-900"
          />
          <div className="flex items-center gap-2 mt-2">
            <button
              onClick={submit}
              disabled={!answer.trim() || grading}
              className="bg-slate-900 text-white px-5 py-1.5 rounded-sm font-semibold text-sm disabled:opacity-40 hover:bg-slate-800"
            >
              {grading ? "Grading..." : "Submit answer"}
            </button>
            {!answer.trim() && (
              <span className="text-xs text-slate-500">Type an answer to enable submit</span>
            )}
          </div>
          {grade && (
            <div
              className={`mt-3 rounded-lg p-4 border ${
                grade.verdict === "correct"
                  ? "bg-emerald-50 border-emerald-200"
                  : grade.verdict === "partial"
                    ? "bg-amber-50 border-amber-200"
                    : "bg-rose-50 border-rose-200"
              }`}
            >
              <div className="flex items-baseline justify-between mb-2">
                <div className="font-bold text-slate-900 capitalize">{grade.verdict}</div>
                <div className="text-2xl font-bold">{grade.score}/100</div>
              </div>
              <div className="text-sm text-slate-700">{grade.feedback}</div>
              <div className="mt-2 text-xs text-slate-500">
                Expected: {scenario.expected_controls.join(", ")}
              </div>
              {scenario.rationale && (
                <details className="mt-2 text-sm">
                  <summary className="cursor-pointer text-slate-600">Rationale</summary>
                  <div className="mt-1 text-slate-700">{scenario.rationale}</div>
                </details>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
