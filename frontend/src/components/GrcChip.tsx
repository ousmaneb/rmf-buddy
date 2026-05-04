import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getGrcTopic, type GrcTopic } from "../api";

const CACHE = new Map<string, Promise<GrcTopic>>();
function load(slug: string): Promise<GrcTopic> {
  if (!CACHE.has(slug)) CACHE.set(slug, getGrcTopic(slug));
  return CACHE.get(slug)!;
}

export function GrcChip({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [topic, setTopic] = useState<GrcTopic | null>(null);
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
        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-emerald-800 text-xs font-semibold"
      >
        GRC · {topic?.title?.split(" - ")[0] || slug}
        <span className="text-[10px]">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div className="block my-2 bg-white border border-emerald-200 rounded-lg p-3 shadow-sm text-sm">
          {loading && <div className="text-slate-400 italic">Loading…</div>}
          {topic && (
            <>
              <div className="text-xs text-emerald-700 uppercase font-semibold">{topic.category}</div>
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
