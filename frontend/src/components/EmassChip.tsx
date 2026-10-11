import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getEmassTopic, type EmassTopic } from "../api";

const CACHE = new Map<string, Promise<EmassTopic>>();
function load(slug: string): Promise<EmassTopic> {
  if (!CACHE.has(slug)) CACHE.set(slug, getEmassTopic(slug));
  return CACHE.get(slug)!;
}

export function EmassChip({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [topic, setTopic] = useState<EmassTopic | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && !topic && !loading) {
      setLoading(true);
      load(slug)
        .then(setTopic)
        .finally(() => setLoading(false));
    }
  }, [open, topic, loading, slug]);

  return (
    <span className="inline-block align-baseline">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm bg-violet-50 hover:bg-violet-100 border border-violet-200 text-violet-800 text-xs font-semibold"
      >
        eMASS · {topic?.title?.split(" - ")[0] || slug}
        <span className="text-[10px]">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div className="block my-2 bg-white border border-violet-200 rounded-lg p-3 shadow-xs text-sm">
          {loading && <div className="text-slate-400 italic">Loading…</div>}
          {topic && (
            <>
              <div className="text-xs text-violet-700 uppercase font-semibold">{topic.category}</div>
              <div className="font-bold text-slate-900 mb-2">{topic.title}</div>
              <div className="prose-rmf text-[13px]">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{topic.body}</ReactMarkdown>
              </div>
            </>
          )}
        </div>
      )}
    </span>
  );
}
