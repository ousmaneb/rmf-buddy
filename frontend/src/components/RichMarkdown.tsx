import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AttackChip, CciChip, CtrlChip } from "./CtrlChip";
import { EmassChip } from "./EmassChip";
import { GrcChip } from "./GrcChip";
import { PubChip } from "./PubChip";

/**
 * Renders markdown with `[[ctrl:ac-2]]`, `[[cci:CCI-000001]]`, `[[emass:slug]]`,
 * `[[pub:slug]]`, `[[atk:T1078]]`, and `[[grc:slug]]` tokens replaced by
 * interactive chips.
 *
 * Per-kind id validators below restrict what the model can send. If a token's
 * id doesn't match its expected shape we render it as plain text rather than
 * a chip — defends against the model emitting a crafted id that an interpolator
 * downstream could mishandle.
 */
const TOKEN_RE = /\[\[(ctrl|cci|emass|pub|atk|grc):([^\]]+)\]\]/g;

const ID_VALIDATORS: Record<string, RegExp> = {
  ctrl: /^[a-z]{2}-\d{1,3}(\.\d{1,3})?$/i,        // ac-2, ac-2.1
  cci: /^CCI-\d{6}$/i,                              // CCI-000001
  emass: /^[a-z0-9-]{1,60}$/i,                     // topic slug
  pub: /^[a-z0-9-]{1,60}$/i,                       // pub slug
  atk: /^T\d{4}(\.\d{3})?$/i,                       // T1078, T1078.001
  grc: /^[a-z0-9-]{1,60}$/i,                       // grc topic slug
};

function isSafeId(kind: string, id: string): boolean {
  const re = ID_VALIDATORS[kind];
  return !!re && re.test(id);
}

function rewrite(text: string): string {
  return text.replace(TOKEN_RE, (m, kind, id) => {
    if (!isSafeId(kind, id)) return m; // leave token verbatim, don't chipify
    return `[${kind}:${id}](rmf://${kind}/${id})`;
  });
}

function urlTransform(url: string): string {
  // Allow our custom protocol; everything else goes through the default
  // sanitizer (drop javascript:, vbscript:, etc.).
  if (url.startsWith("rmf://")) return url;
  // Allow http(s), mailto, anchors:
  if (/^(https?:|mailto:|#|\/)/i.test(url)) return url;
  return "";
}

export function RichMarkdown({ text }: { text: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      urlTransform={urlTransform}
      components={{
        a({ href, children }) {
          if (typeof href === "string" && href.startsWith("rmf://")) {
            const [, , kind, id] = href.split("/");
            // Defense in depth: re-validate the id at render time. The
            // rewrite() pre-filter already does this, but a future caller
            // might bypass it.
            if (!kind || !id || !isSafeId(kind, id)) return <>{children}</>;
            if (kind === "ctrl") return <CtrlChip id={id} />;
            if (kind === "cci") return <CciChip id={id} />;
            if (kind === "emass") return <EmassChip slug={id} />;
            if (kind === "pub") return <PubChip slug={id} />;
            if (kind === "atk") return <AttackChip id={id} />;
            if (kind === "grc") return <GrcChip slug={id} />;
          }
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-700 underline"
            >
              {children}
            </a>
          );
        },
        table({ children }) {
          return (
            <div className="overflow-x-auto my-3">
              <table className="min-w-full border-collapse text-sm">{children}</table>
            </div>
          );
        },
        thead({ children }) {
          return <thead className="bg-slate-100">{children}</thead>;
        },
        th({ children }) {
          return (
            <th className="border border-slate-300 px-3 py-1.5 text-left font-semibold text-slate-800">
              {children}
            </th>
          );
        },
        td({ children }) {
          return (
            <td className="border border-slate-200 px-3 py-1.5 align-top text-slate-700">
              {children}
            </td>
          );
        },
        ul({ children }) {
          return <ul className="list-disc ml-6 my-2 space-y-1 text-slate-700">{children}</ul>;
        },
        ol({ children }) {
          return <ol className="list-decimal ml-6 my-2 space-y-1 text-slate-700">{children}</ol>;
        },
      }}
    >
      {rewrite(text)}
    </ReactMarkdown>
  );
}
