import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getNistPublication, type NistPub } from "../api";

const CACHE = new Map<string, Promise<NistPub>>();
function load(slug: string): Promise<NistPub> {
  if (!CACHE.has(slug)) CACHE.set(slug, getNistPublication(slug));
  return CACHE.get(slug)!;
}

export function PubChip({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [pub, setPub] = useState<NistPub | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && !pub && !loading) {
      setLoading(true);
      load(slug)
        .then(setPub)
        .finally(() => setLoading(false));
    }
  }, [open, pub, loading, slug]);

  return (
    <span className="inline-block align-baseline">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm bg-teal-50 hover:bg-teal-100 border border-teal-200 text-teal-800 text-xs font-semibold"
      >
        NIST · {pub?.title?.split(" - ")[0] || slug}
        <span className="text-[10px]">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div className="block my-2 bg-white border border-teal-200 rounded-lg p-3 shadow-xs text-sm">
          {loading && <div className="text-slate-400 italic">Loading…</div>}
          {pub && (
            <>
              <div className="text-xs text-teal-700 uppercase font-semibold">{pub.category}</div>
              <div className="font-bold text-slate-900">{pub.title}</div>
              <a
                href={pub.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-teal-700 underline"
              >
                csrc.nist.gov
              </a>
              <div className="prose-rmf text-[13px] mt-2">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{pub.body}</ReactMarkdown>
              </div>
            </>
          )}
        </div>
      )}
    </span>
  );
}
