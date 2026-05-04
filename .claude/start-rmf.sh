#!/usr/bin/env bash
# Hook script: when user types exactly "go", boot RMF Buddy backend + frontend
# and emit a systemMessage with the local URL. Otherwise no-op.

set -u

# Read hook stdin (UserPromptSubmit JSON: { "prompt": "...", ... })
prompt=$(jq -r '.prompt // ""' | tr -d '[:space:]')
[[ "$prompt" == "go" ]] || exit 0

ROOT="/Users/alphabah/Library/CloudStorage/OneDrive-Personal/Dell Windows/ClaudeCode/RMF Tool"
LOG_DIR="$ROOT/.claude/logs"
mkdir -p "$LOG_DIR"

backend_up() { lsof -nP -iTCP:8911 -sTCP:LISTEN >/dev/null 2>&1; }
frontend_up() { lsof -nP -iTCP:5173 -sTCP:LISTEN >/dev/null 2>&1; }

backend_status="already running"
if ! backend_up; then
  (
    cd "$ROOT/backend" || exit 1
    # shellcheck disable=SC1091
    source .venv/bin/activate
    nohup uvicorn app.main:app --host 127.0.0.1 --port 8911 \
      --no-server-header --no-date-header \
      >"$LOG_DIR/backend.log" 2>&1 &
    disown
  )
  backend_status="starting (logs: .claude/logs/backend.log)"
fi

frontend_status="already running"
if ! frontend_up; then
  (
    cd "$ROOT/frontend" || exit 1
    nohup npx vite --host 127.0.0.1 --port 5173 --strictPort \
      >"$LOG_DIR/frontend.log" 2>&1 &
    disown
  )
  frontend_status="starting (logs: .claude/logs/frontend.log)"
fi

# Emit systemMessage so the URL appears in the Claude Code UI.
jq -nc --arg msg "RMF Buddy: backend $backend_status; frontend $frontend_status. Open http://localhost:5173 (give it ~10s on first start)." \
  '{systemMessage: $msg, decision: "block", reason: $msg}'
