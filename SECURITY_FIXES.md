# Security Audit & Fixes

Comprehensive security audit performed across the RMF Buddy codebase. This
document records the threat model, the issues that were found and fixed, and
the residual risks that were intentionally not addressed (with rationale).

## Threat Model

This application is a **single-user local development tool**. The backend
binds `127.0.0.1:8911` only and the frontend runs on `localhost:5173`. There
is intentionally no end-user authentication, no multi-tenancy, no payments,
no persistent user accounts.

The audit prioritised:

1. Vulnerabilities that are exploitable in this deployment (SSRF, prompt
   injection, XSS through model output, dependency CVEs, info leaks).
2. Hardening that protects the user if the server is *ever* exposed beyond
   localhost (CORS, security headers, input limits, error sanitization).
3. Defense in depth on every external-data boundary: web fetch, LLM tool
   outputs, browser storage.

The audit deliberately did NOT add user authentication, RBAC, JWT, OAuth,
session management, or rate-limiting middleware: those are the wrong
abstraction for a local single-user tool. If you decide to deploy this
publicly, those become required and a follow-up review is needed.

---

## Findings & Fixes

### 1. Dependency Vulnerabilities

**Frontend (npm audit):**

| Package | Severity | Vuln | Fix |
| --- | --- | --- | --- |
| esbuild ≤0.24.2 | moderate | dev server can be requested cross-origin | upgraded |
| vite ≤6.4.1 | moderate | path traversal in `.map` handling | upgraded to vite@^7 |

**Result:** `npm audit` now reports **0 vulnerabilities**. Build verified on
Vite 7.

**Backend (pip-audit):** 11 known CVEs in 7 packages. The fix versions for
most require **Python ≥ 3.10**. The local venv is on Python 3.9 (default
macOS Xcode python). I upgraded what's installable on 3.9 (`setuptools`),
and assessed each remaining CVE against the actual deployment context:

| Package | Vuln | Exploitable here? | Mitigation |
| --- | --- | --- | --- |
| pillow 11.3.0 | image processing CVEs | **No** — we never decode user-supplied images | Documented; upgrade with venv recreation |
| transformers 4.57.6 | unsafe pickle in untrusted models | **No** — only the fixed `all-MiniLM-L6-v2` model from HF is loaded | Documented |
| requests 2.32.5 | various HTTP CVEs | **Low** — we use `httpx` for our own network calls; `requests` is only a transitive dep used by HF tooling not exposed to user input | Documented |
| python-dotenv 1.2.1 | low-impact CLI info leak | **No** — we only use the library API, not the CLI | Documented |
| filelock 3.19.1 | concurrent-access race | **No** — single-user, single-process | Documented |
| pip / setuptools | install-time issues | **N/A at runtime** | Documented; setuptools upgraded to 78.1.1 |

**Recommended follow-up:** recreate the venv with Python 3.11+ to clear the
remaining advisories cleanly. Files modified: `backend/requirements.txt`.

---

### 2. SQL Injection

**Audit:** grep across all `.py` files for f-string SQL, string-concat SQL,
or unsafe `%` interpolation. Single dynamic SQL site found in
`backend/app/main.py` `/api/baselines/diff`:

```py
f"SELECT ... WHERE id IN ({marks})"
```

**Verdict:** safe. `marks` is built only from `?` placeholders; all values
remain bound parameters. Verified.

All other SQL sites use parameterised queries throughout (`?` placeholders).
No fixes required.

---

### 3. Server-Side Request Forgery (SSRF)

The `web_fetch` and `web_search` agent tools call Firecrawl with URLs the
LLM chooses. Hardening in `backend/app/web.py`:

**Before:** allow-list checked hostname suffixes only. Allowed `http://` and
`https://`.

**After:**
- **HTTPS only** — `http://` rejected.
- **Reject userinfo** — `https://attacker@nist.gov/` rejected (some parsers
  resolve this differently from the host check).
- **Reject IP literals** — IPv4 dotted-quad and IPv6 brackets rejected.
- **Length cap** — URL strings over 2,000 chars rejected.
- **Lowercase + strip trailing dot** before allow-list match (so legitimate
  variants pass and equivalent attack variants don't bypass).

Verified test cases (all pass):

| URL | Verdict |
| --- | --- |
| `https://csrc.nist.gov/pubs/sp/800/53/r5/` | allowed |
| `http://csrc.nist.gov/x` | rejected (http) |
| `https://attacker.com/` | rejected (off-list) |
| `https://nist.gov.attacker.com/` | rejected (suffix spoof) |
| `https://attacker@csrc.nist.gov/` | rejected (userinfo) |
| `https://10.0.0.1/` | rejected (IPv4 literal) |
| `https://[::1]/` | rejected (IPv6 literal) |
| `file:///etc/passwd` | rejected (scheme) |

**Files modified:** `backend/app/web.py`.

---

### 4. Prompt Injection

The agent has a `web_fetch` tool that returns content from third-party
pages. Even with an allow-list, malicious or compromised content could
contain prompt-injection payloads.

**Mitigations (defense in depth):**

1. **System prompt update** (`backend/app/main.py`): explicit instruction
   that tool results are *data*, not instructions; never reveal system
   prompt or env vars.
2. **Sanitize untrusted text before LLM** (`backend/app/security.py`
   `sanitize_untrusted_text`): strips ASCII control chars, C1 controls,
   bidi override marks, zero-width spaces, deprecated formatting, the
   Unicode Tags block (U+E0000–U+E007F — used for invisible
   prompt-injection smuggling), and length-caps to 30k chars.
3. **Apply sanitizer to all `web_fetch` and `web_search` outputs** before
   they re-enter the LLM as tool results.

**Files modified:** `backend/app/security.py`, `backend/app/main.py`.

---

### 5. Tool Argument Injection

The chat agent emits arbitrary JSON arguments for each tool call. Without
validation, a hallucinated or adversarial arg could trigger unexpected
behavior in tools (oversized URLs, malformed control IDs, etc.).

**Fix:** added `validate_tool_args()` in `backend/app/security.py`.
Per-field allow-list with type + length + pattern enforcement:

| Field | Pattern | Max length |
| --- | --- | --- |
| `control_id`, `control_a`, `control_b`, `cci_id` | `^[A-Za-z0-9._\-+()]+$` | 40 |
| `slug` | `^[A-Za-z0-9._\-+()]+$` | 60 |
| `family` | `^[a-zA-Z]{1,4}$` | 4 |
| `baseline` | `^(LOW|MODERATE|HIGH)$` | 8 |
| `technique_id` | `^T\d+(\.\d+)?$` | 12 |
| `query` | free text | 500 |
| `url` | free text | 2,000 |
| `limit`, `k` | integer | 1–50 / 1–25 |

Unknown keys are silently dropped. Validation happens in the tool dispatch
loop in `_agentic_stream` *before* calling `dispatch()`. Failures return a
graceful `{"error": "invalid arguments: ..."}` to the model so it can recover.

**Files modified:** `backend/app/security.py`, `backend/app/main.py`.

---

### 6. CORS Misconfiguration

**Before:** `allow_origins=["*"]` — any origin could call the API from a
browser if the backend was ever exposed.

**After:** allow-list of localhost origins only:
- `http://localhost:5173`, `http://127.0.0.1:5173` (vite dev)
- `http://localhost:4173`, `http://127.0.0.1:4173` (vite preview)

Methods restricted to `GET`, `POST`, `OPTIONS`. Headers restricted to
`Content-Type`, `Accept`. `allow_credentials=False`.

**Files modified:** `backend/app/main.py`, `backend/app/security.py`.

---

### 7. Missing Security Headers

Added a `SecurityHeadersMiddleware` that sets on every response:

| Header | Value |
| --- | --- |
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `no-referrer` |
| `Permissions-Policy` | restricts camera/mic/geolocation/payment/USB/etc. |

**`Strict-Transport-Security` is not set** because the server speaks HTTP
on localhost. If you put TLS in front of it, add HSTS.

The `Server: uvicorn` and `Date` headers (info disclosure) are suppressed
via uvicorn `--no-server-header --no-date-header` flags in
`.claude/start-rmf.sh`.

**Files modified:** `backend/app/security.py`, `backend/app/main.py`,
`.claude/start-rmf.sh`.

---

### 8. Information Disclosure / Verbose Errors

**Before:** unhandled exceptions could let FastAPI surface a stack trace
to the client.

**After:** registered a generic exception handler
(`sanitized_exception_handler`) that logs the trace internally (stderr) and
returns `{"detail": "internal server error"}` to the client.

Also gated FastAPI's interactive docs behind an env flag — `/docs`,
`/redoc`, and `/openapi.json` return 404 unless `RMF_BUDDY_DOCS=1` is set.

**Files modified:** `backend/app/security.py`, `backend/app/main.py`.

---

### 9. Denial of Service / Cost Protection

The chat endpoint streams to a paid LLM (OpenRouter / GPT-4o). Without
limits, an oversized payload would burn money and resources.

**Fix:** added `_validate_chat_request()` in `backend/app/main.py`:

| Limit | Value | Status code if exceeded |
| --- | --- | --- |
| Per-message length | 8,000 chars | 413 |
| Total conversation length | 80,000 chars | 413 |
| Number of turns per request | 40 | 413 |
| Template `context` value length | 1,000 chars | 413 |
| Empty messages array | rejected | 400 |
| Unknown mode | rejected | 400 |
| Invalid role | rejected | 400 |

Verified 413 / 400 returned for each violation.

**Files modified:** `backend/app/main.py`, `backend/app/security.py`.

---

### 10. Cross-Site Scripting (XSS)

**Audit:** grep for `dangerouslySetInnerHTML`, `innerHTML`, `outerHTML`,
`document.write`, `eval`, `new Function(`, direct `window.location.href =
…` assignments. **All clean** — every render path goes through
ReactMarkdown which escapes HTML.

Two real risks identified in chip rendering and fixed:

**a) `[[atk:T1078]]` chip URL injection.** `AttackChip` interpolated `id`
into an external URL. Crafted text from the LLM could smuggle to a
different host. Fix in `frontend/src/components/CtrlChip.tsx`: strict regex
validation `^T\d{4}(?:\.\d{3})?$` with case normalisation. If the id
doesn't match, render as plain "ATT&CK ?" instead of a clickable link.
Also URL-encoded the path component.

**b) Per-kind id validation in `RichMarkdown`.** Previously any text
matching `[[kind:anything]]` (where kind was one of 6 known) was rendered
as a chip and the `id` was passed to API client functions for fetching.
Crafted ids could land at unexpected API paths. Fix in
`frontend/src/components/RichMarkdown.tsx`:

- Per-kind regex validators (e.g. `^[a-z]{2}-\d{1,3}(\.\d{1,3})?$` for
  `ctrl`, `^CCI-\d{6}$` for `cci`).
- Tokens with malformed ids are left as plain text in the markdown — never
  rendered as chips.
- The link interceptor re-validates at render time as defense in depth.

**c) URL-encode IDs in API client paths** (`frontend/src/api.ts`). Even
though the backend now validates control/topic/pub IDs strictly, the
client now wraps `getControl/getEmassTopic/getNistPublication/getGrcTopic`
calls with `encodeURIComponent()` so a stray `../` from any source can't
escape the intended path.

**Files modified:** `frontend/src/api.ts`,
`frontend/src/components/RichMarkdown.tsx`,
`frontend/src/components/CtrlChip.tsx`.

---

### 11. Reverse Tabnabbing

Five `target="_blank"` external links existed. All had `rel="noreferrer"`
but not `noopener`. Updated all five to `rel="noopener noreferrer"`.

**Files modified:** `frontend/src/App.tsx`,
`frontend/src/components/PubChip.tsx`,
`frontend/src/components/RichMarkdown.tsx`,
`frontend/src/components/CtrlChip.tsx`.

---

### 12. Secrets Handling

- `backend/.env` permissions tightened: `644 → 600` (`chmod 600`).
- Verified `.env` is in `.gitignore`.
- Verified no API key, secret, or credential is hardcoded in any source
  file (grep across all `.py` and `.ts*` files).
- Verified no API key is ever returned to the frontend (the `api.ts`
  client only ever consumes JSON; the OpenRouter / Firecrawl keys live
  exclusively in the backend env).
- Stack traces and exception details are scrubbed from client responses
  (see §8); secrets in env vars are not surfaced via error paths.

**Files modified:** `backend/.env` (permissions only).

---

### 13. Localhost Binding

The server binds `127.0.0.1` (loopback) explicitly via the hook script
(`uvicorn ... --host 127.0.0.1 ...`). Verified no listener exposed on `0.0.0.0`.

**No change needed.**

---

### 14. Local Storage Use

Conversation history is stored in `localStorage` under
`rmf-buddy:conversations`. Risk assessment:

- This is a single-user local tool; localStorage is not shared with other
  origins (same-origin policy).
- Capped at 50 conversations in `saveConversations()`.
- No auth tokens, API keys, or PII expected (the user's questions about
  RMF are not sensitive in any normal use).

**No change required** for this deployment context. Documented for any
future deployment scenario where the threat model changes.

---

## Categories Reviewed With No Findings

For completeness — these categories from the audit checklist were
reviewed and produced no findings:

- **No SQL injection** anywhere (grep + manual review of every `execute(`
  call site)
- **No `eval`, `exec`, `pickle.loads`, `yaml.load`, `os.system`,
  `subprocess`, `shell=True`** in any file
- **No hardcoded secrets** (grep for `sk-`, `api_key.*=`, `password=`)
- **No XML / XXE / SAML / SOAP** processing
- **No file upload endpoint** — no zip-slip / path traversal / image
  processing risk
- **No webhooks** — no Stripe / GitHub signature verification needed
- **No JWT / session tokens / cookies** — auth is out of scope
- **No payments / financial code**
- **No OAuth / OIDC / SAML**
- **No GraphQL** (REST only)
- **No CSRF risk** — no state-changing endpoints with cookie-based session
  auth (and CORS is restricted)
- **No Open Redirect** — no redirect endpoints exist
- **No prototype pollution** — no `Object.assign` / spread of unvalidated
  user data into base prototypes
- **No ReDoS** — every regex is anchored, bounded, and free of nested
  quantifiers (verified)
- **No insecure deserialization** — only `json.loads` of bounded inputs
- **No weak cryptography** — no crypto code
- **No hardcoded IVs / nonces** — N/A
- **No insecure random for security purposes** — `random.sample` used only
  for non-security flashcard selection
- **No directory listing** enabled
- **No dev / debug routes** exposed (docs gated)
- **No source map exposure** in production (Vite default behaviour)

---

## Files Modified (Summary)

```
backend/.env                              chmod 600
backend/requirements.txt                  add security pins
backend/app/main.py                       wire security middleware,
                                           CORS lockdown, gate docs,
                                           validate chat input,
                                           validate + sanitize tool args
backend/app/security.py                   NEW — middleware, validators,
                                           sanitizer
backend/app/web.py                        SSRF allow-list hardening
.claude/start-rmf.sh                      --no-server-header --no-date-header
frontend/package.json                     vite ^7 (security upgrade)
frontend/src/api.ts                       URL-encode path IDs
frontend/src/components/CtrlChip.tsx      AttackChip strict id validation,
                                           noopener
frontend/src/components/RichMarkdown.tsx  per-kind id validators,
                                           noopener
frontend/src/components/PubChip.tsx       noopener
frontend/src/App.tsx                      noopener
SECURITY_FIXES.md                         this report
```

---

## Recommended Follow-ups (out of scope, not done)

1. **Recreate the Python venv with Python 3.11+** to clear the remaining
   pip-audit advisories cleanly.
2. **If ever deployed beyond localhost**: add user authentication, HSTS,
   per-user rate limiting, request logging, and a fresh threat-model review.
3. **Consider running with `--workers 1` only** (current default) to keep
   the SQLite single-writer assumption explicit.
