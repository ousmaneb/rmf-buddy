import { useEffect, useState } from "react";
import { getControl, type Control } from "../api";

const CACHE = new Map<string, Promise<Control>>();
function loadControl(id: string): Promise<Control> {
  if (!CACHE.has(id)) CACHE.set(id, getControl(id));
  return CACHE.get(id)!;
}

export function CtrlChip({ id }: { id: string }) {
  const [open, setOpen] = useState(false);
  const [ctrl, setCtrl] = useState<Control | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && !ctrl && !loading) {
      setLoading(true);
      loadControl(id)
        .then(setCtrl)
        .finally(() => setLoading(false));
    }
  }, [open, ctrl, loading, id]);

  return (
    <span className="inline-block align-baseline">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-800 text-xs font-mono font-semibold transition"
      >
        {ctrl?.label || id.toUpperCase()}
        <span className="text-[10px]">{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div className="block my-2 bg-white border border-blue-200 rounded-lg p-3 shadow-xs text-sm">
          {loading && <div className="text-slate-400 italic">Loading…</div>}
          {ctrl && (
            <>
              <div className="flex items-baseline justify-between mb-2">
                <div>
                  <div className="font-semibold text-slate-900">
                    {ctrl.label} - {ctrl.title}
                  </div>
                  <div className="text-xs text-slate-500">{ctrl.family_name}</div>
                </div>
                <div className="flex gap-1">
                  {ctrl.baselines.map((b) => (
                    <span
                      key={b}
                      className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-sm font-semibold"
                    >
                      {b}
                    </span>
                  ))}
                </div>
              </div>
              <div className="text-xs text-slate-500 uppercase font-semibold mt-2">Statement</div>
              <pre className="whitespace-pre-wrap font-sans text-slate-700 text-[13px]">{ctrl.statement}</pre>
              {ctrl.guidance && (
                <details className="mt-2">
                  <summary className="text-xs text-slate-500 uppercase font-semibold cursor-pointer">
                    Discussion
                  </summary>
                  <pre className="whitespace-pre-wrap font-sans text-slate-700 text-[13px] mt-1">{ctrl.guidance}</pre>
                </details>
              )}
              {ctrl.assessment && (
                <details className="mt-2">
                  <summary className="text-xs text-slate-500 uppercase font-semibold cursor-pointer">
                    Assessment objectives ({ctrl.assessment.split("\n").filter(Boolean).length} items)
                  </summary>
                  <pre className="whitespace-pre-wrap font-sans text-slate-700 text-[13px] mt-1">{ctrl.assessment}</pre>
                </details>
              )}
              {ctrl.ccis.length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-slate-500 uppercase font-semibold cursor-pointer">
                    {ctrl.ccis.length} linked CCIs
                  </summary>
                  <ul className="mt-1 space-y-1">
                    {ctrl.ccis.map((c) => (
                      <li key={c.id} className="text-[12px]">
                        <span className="font-mono font-semibold text-amber-800">{c.id}</span>
                        <span className="text-slate-700"> - {c.definition}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </>
          )}
        </div>
      )}
    </span>
  );
}

export function CciChip({ id }: { id: string }) {
  return (
    <span className="inline-flex items-center px-1.5 py-0.5 rounded-sm bg-amber-50 border border-amber-200 text-amber-800 text-xs font-mono font-semibold">
      {id}
    </span>
  );
}

// Strict ATT&CK technique id pattern. Must be Txxxx or Txxxx.NNN.
// Defense-in-depth against the model emitting a crafted id that could be
// interpolated into a URL pointing somewhere unexpected.
const _ATTACK_ID_RE = /^T\d{4}(?:\.\d{3})?$/;

export function AttackChip({ id }: { id: string }) {
  const safeId = _ATTACK_ID_RE.test(id) ? id.toUpperCase() : null;
  if (!safeId) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded-sm bg-rose-50 border border-rose-200 text-rose-800 text-xs font-mono font-semibold">
        ATT&amp;CK ?
      </span>
    );
  }
  // T1078 -> /techniques/T1078; T1078.001 -> /techniques/T1078/001
  const path = safeId.includes(".") ? safeId.replace(".", "/") : safeId;
  return (
    <a
      href={`https://attack.mitre.org/techniques/${encodeURIComponent(path).replace(/%2F/gi, "/")}`}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center px-1.5 py-0.5 rounded-sm bg-rose-50 border border-rose-200 text-rose-800 text-xs font-mono font-semibold hover:bg-rose-100"
      title="Open in MITRE ATT&CK"
    >
      ATT&amp;CK {safeId}
    </a>
  );
}
