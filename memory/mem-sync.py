#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mem-sync — local, free, zero-token session-memory capture for Claude Code.

Reads ~/.claude/projects/**/*.jsonl (Claude Code's transcript of "everything
that happened") and deterministically (no LLM, 0 tokens) extracts per session:
user prompts, files read/edited/created, bash commands, and the final outcome.

For each project it writes ONE aggregated file into your Obsidian vault:
  projects/<Project>/Session Log.md   — full auto-log of every session (for Claude)

Your hand-written page (projects/<Project>.md or projects/<Project>/*.md) is
NEVER touched — mem-sync only writes "Session Log.md".

Optionally (if the third-party `claude-mem` plugin is installed) it also writes
to ~/.claude-mem/claude-mem.db so claude-mem's viewer and MCP search light up.
This is best-effort: if the DB isn't there, mem-sync just skips it silently.

Incremental: state.json stores each transcript's mtime; a project is only
regenerated when at least one of its transcripts changed.

Configuration (all optional, resolved in this order):
  • Vault path:  env MEMSYNC_VAULT  →  ~/.claude-obsidian-wiki/config.json {"vault": "..."}
  • Project map: ~/.claude-obsidian-wiki/project-map.json
        {"substring-in-cwd (lowercase)": "Project Name", ...}
        Any cwd not matched falls back to the last path component (basename).
"""
import argparse
import json
import os
import re
import sqlite3
import time
from datetime import datetime

HOME = os.path.expanduser("~")
PROJECTS_DIR = os.path.join(HOME, ".claude", "projects")
DB_PATH = os.path.join(HOME, ".claude-mem", "claude-mem.db")
CONFIG_DIR = os.path.join(HOME, ".claude-obsidian-wiki")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
PROJECT_MAP_PATH = os.path.join(CONFIG_DIR, "project-map.json")
STATE_PATH = os.path.join(CONFIG_DIR, "state.json")
LOG_FILENAME = "Session Log.md"
MISC_BUCKET = "Misc"

MAX_PROMPT = 400
MAX_OUTCOME = 800
MAX_LIST = 40           # max items per list per session


# ----------------------- configuration -----------------------
def _read_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def resolve_vault():
    v = os.environ.get("MEMSYNC_VAULT")
    if v:
        return os.path.expanduser(v)
    cfg = _read_json(CONFIG_PATH, {})
    v = cfg.get("vault")
    if v:
        return os.path.expanduser(v)
    raise SystemExit(
        "mem-sync: vault path not configured.\n"
        f"Set env MEMSYNC_VAULT or create {CONFIG_PATH} with "
        '{"vault": "/path/to/your/vault/Claude"}'
    )


PROJECT_MAP = _read_json(PROJECT_MAP_PATH, {})


# ----------------------- cwd → canonical project -----------------------
def canonical_project(cwd: str):
    """Map a session's working directory to a wiki project folder name."""
    if not cwd:
        return MISC_BUCKET
    low = cwd.lower().rstrip("/")
    for substr, name in PROJECT_MAP.items():
        if substr and substr.lower() in low:
            return name
    base = os.path.basename(low)
    return base or MISC_BUCKET


# ----------------------- transcript parsing -----------------------
CAVEAT_RE = re.compile(
    r"^\s*<(local-command|command-name|command-message|command-args|command-stdout|command-contents)")
SYSREMIND_RE = re.compile(r"^\s*<system-reminder")


def _text_from_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(it.get("text", "") for it in content
                         if isinstance(it, dict) and it.get("type") == "text")
    return ""


def _is_tool_result(content):
    return isinstance(content, list) and any(
        isinstance(it, dict) and it.get("type") == "tool_result" for it in content)


def parse_transcript(path: str) -> dict:
    sid = cwd = git_branch = ai_title = None
    first_prompt = None
    prompts, files_read, files_edited, files_created, commands, assistant_texts = [], [], [], [], [], []
    ts_first = ts_last = None

    def add(lst, v):
        if v and v not in lst:
            lst.append(v)

    with open(path, "r", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            t = o.get("type")
            sid = sid or o.get("sessionId")
            cwd = cwd or o.get("cwd")
            git_branch = git_branch or o.get("gitBranch")
            if o.get("aiTitle"):
                ai_title = o.get("aiTitle")
            ts = o.get("timestamp")
            if ts:
                ts_first = ts_first or ts
                ts_last = ts
            if o.get("isMeta"):
                continue
            msg = o.get("message") if isinstance(o.get("message"), dict) else {}
            role, content = msg.get("role"), msg.get("content")

            if t == "user" and role == "user":
                if _is_tool_result(content):
                    continue
                txt = _text_from_content(content).strip()
                if not txt or CAVEAT_RE.match(txt) or SYSREMIND_RE.match(txt):
                    continue
                txt = re.split(r"\n?<system-reminder>", txt)[0].strip()
                if not txt:
                    continue
                if first_prompt is None:
                    first_prompt = txt
                prompts.append(txt[:MAX_PROMPT])
            elif t == "assistant" and isinstance(content, list):
                for it in content:
                    if not isinstance(it, dict):
                        continue
                    if it.get("type") == "text":
                        tx = it.get("text", "").strip()
                        if tx:
                            assistant_texts.append(tx)
                    elif it.get("type") == "tool_use":
                        name = it.get("name", "")
                        inp = it.get("input", {}) or {}
                        if name == "Bash":
                            c = (inp.get("command") or "").strip()
                            if c:
                                commands.append(c[:240])
                        elif name in ("Edit", "MultiEdit", "NotebookEdit"):
                            add(files_edited, inp.get("file_path") or inp.get("notebook_path"))
                        elif name == "Write":
                            add(files_created, inp.get("file_path"))
                        elif name == "Read":
                            add(files_read, inp.get("file_path"))

    return {
        "session_id": sid or os.path.splitext(os.path.basename(path))[0],
        "cwd": cwd, "git_branch": git_branch, "ai_title": ai_title,
        "first_prompt": first_prompt or "", "prompts": prompts,
        "files_read": files_read, "files_edited": files_edited, "files_created": files_created,
        "commands": commands, "outcome": (assistant_texts[-1].strip() if assistant_texts else "")[:MAX_OUTCOME],
        "ts_first": ts_first, "ts_last": ts_last, "path": path,
    }


# ----------------------- helpers -----------------------
def dedup(seq):
    return list(dict.fromkeys(x for x in seq if x))


def iso_to_date(ts):
    if not ts:
        return "0000-00-00"
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d")
    except Exception:
        return ts[:10]


def short_id(sid):
    return sid.split("-")[0] if sid else "????????"


def epoch_of(ts):
    if not ts:
        return int(time.time() * 1000)
    try:
        return int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000)
    except Exception:
        return int(time.time() * 1000)


def rel(p):
    return os.path.relpath(p, HOME) if p and p.startswith(HOME) else p


def md_inline_list(items, n=MAX_LIST):
    items = dedup(items)
    if not items:
        return "_(none)_"
    out = items[:n]
    extra = len(items) - len(out)
    s = ", ".join(out)
    return s + (f" … +{extra}" if extra > 0 else "")


# ----------------------- write aggregated project log -----------------------
def write_project_log(vault_projects: str, project: str, sessions: list):
    folder = os.path.join(vault_projects, project)
    os.makedirs(folder, exist_ok=True)
    sessions = sorted(sessions, key=lambda d: d["ts_first"] or "", reverse=True)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    out = []
    out.append("---")
    out.append(f"project: {project}")
    out.append("type: session-log")
    out.append("source: mem-sync (local transcript parser, no LLM)")
    out.append(f"updated: {now}")
    out.append("---\n")
    out.append(f"# Session Log — {project}\n")
    out.append("Full auto-generated journal of every Claude Code session for this project "
               "(for Claude to read). Built locally, no LLM. Your hand-written page lives "
               "next to this file.\n")
    out.append(f"_Sessions: {len(sessions)} · updated {now}_\n")
    for d in sessions:
        date = iso_to_date(d["ts_first"])
        title = (d["ai_title"] or d["first_prompt"][:70] or "Session").replace("\n", " ").strip()
        out.append("\n---\n")
        out.append(f"## {date} — {title}")
        sub = f"`{short_id(d['session_id'])}` · prompts: {len(d['prompts'])}"
        if d["git_branch"]:
            sub += f" · branch `{d['git_branch']}`"
        out.append(sub + "\n")
        if d["prompts"]:
            out.append("**Requests:**")
            for i, p in enumerate(d["prompts"][:MAX_LIST], 1):
                out.append(f"{i}. {p.replace(chr(10), ' ').strip()}")
            if len(d["prompts"]) > MAX_LIST:
                out.append(f"… +{len(d['prompts']) - MAX_LIST} more")
        edited = dedup([rel(x) for x in d["files_edited"] + d["files_created"]])
        readf = dedup([rel(x) for x in d["files_read"]])
        if edited:
            out.append(f"\n**Files ✏️:** {md_inline_list(edited)}")
        if readf:
            out.append(f"\n**Files 👁:** {md_inline_list(readf)}")
        if d["commands"]:
            out.append("\n**Commands:**")
            for c in d["commands"][:MAX_LIST]:
                out.append(f"- `{c}`")
            if len(d["commands"]) > MAX_LIST:
                out.append(f"- … +{len(d['commands']) - MAX_LIST} more")
        if d["outcome"]:
            out.append(f"\n**Outcome:** {d['outcome']}")
    with open(os.path.join(folder, LOG_FILENAME), "w") as f:
        f.write("\n".join(out) + "\n")
    return os.path.join(folder, LOG_FILENAME)


# ----------------------- write to claude-mem DB (optional) -----------------------
def write_db(d, project, conn):
    sid = d["session_id"]
    started = d["ts_first"] or ""
    ended = d["ts_last"] or started
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sdk_sessions
           (content_session_id, memory_session_id, project, platform_source, user_prompt,
            started_at, started_at_epoch, completed_at, completed_at_epoch, status, custom_title)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(content_session_id) DO UPDATE SET
             project=excluded.project, completed_at=excluded.completed_at,
             completed_at_epoch=excluded.completed_at_epoch, status='completed',
             custom_title=excluded.custom_title""",
        (sid, sid, project, "claude", d["first_prompt"][:500], started, epoch_of(started),
         ended, epoch_of(ended), "completed", (d["ai_title"] or "")[:200]))
    cur.execute("DELETE FROM session_summaries WHERE memory_session_id=?", (sid,))
    cur.execute(
        """INSERT INTO session_summaries
           (memory_session_id, project, request, investigated, learned, completed, next_steps,
            files_read, files_edited, notes, prompt_number, created_at, created_at_epoch)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (sid, project, d["first_prompt"][:1000], "",
         "\n".join(f"• {p}" for p in d["prompts"][:20]), d["outcome"], "",
         json.dumps(dedup(d["files_read"])[:80], ensure_ascii=False),
         json.dumps(dedup(d["files_edited"] + d["files_created"])[:80], ensure_ascii=False),
         "mem-sync: local deterministic import (no LLM)",
         len(d["prompts"]), ended, epoch_of(ended)))
    conn.commit()


# ----------------------- traversal -----------------------
def find_transcripts():
    out = []
    for root, _d, files in os.walk(PROJECTS_DIR):
        if "/subagents" in root:
            continue
        out += [os.path.join(root, fn) for fn in files if fn.endswith(".jsonl")]
    return out


def load_state():
    return _read_json(STATE_PATH, {})


def save_state(st):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(st, f, indent=2)


def main():
    ap = argparse.ArgumentParser(description="Local session-memory sync for Claude Code.")
    ap.add_argument("--all", action="store_true", help="reprocess every transcript, ignore state")
    ap.add_argument("--recent", type=int, default=0, help="only transcripts modified in the last N days")
    ap.add_argument("--only", type=str, default="", help="only transcripts whose path contains this substring")
    ap.add_argument("--no-db", action="store_true", help="skip the claude-mem DB, write only the vault")
    ap.add_argument("--dry-run", action="store_true", help="show what would be written, change nothing")
    ap.add_argument("--max-bytes", type=int, default=250_000_000, help="skip transcripts larger than this")
    args = ap.parse_args()

    vault = resolve_vault()
    vault_projects = os.path.join(vault, "projects")

    state = {} if args.all else load_state()
    files = find_transcripts()
    if args.only:
        files = [f for f in files if args.only in f]
    now = time.time()
    if args.recent:
        files = [f for f in files if now - os.path.getmtime(f) <= args.recent * 86400]

    by_project = {}      # project -> list of parsed dicts
    mtimes = {}          # path -> mtime
    dirty = set()
    parsed = skipped = 0
    for path in files:
        mt = os.path.getmtime(path)
        mtimes[path] = mt
        if os.path.getsize(path) > args.max_bytes:
            print(f"  ⚠ skipping large file {os.path.getsize(path)//1_000_000}MB: {os.path.basename(path)}")
            continue
        d = parse_transcript(path)
        proj = canonical_project(d["cwd"])
        if proj is None:
            continue
        if not d["prompts"] and not d["commands"] and not d["files_edited"]:
            continue
        by_project.setdefault(proj, []).append(d)
        if args.all or state.get(path) != mt:
            dirty.add(proj)
        parsed += 1

    conn = None
    if not args.no_db and not args.dry_run and os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH, timeout=15)
        conn.execute("PRAGMA busy_timeout=15000")

    written = 0
    for proj, sessions in sorted(by_project.items()):
        if not args.all and proj not in dirty:
            skipped += 1
            continue
        if args.dry_run:
            print(f"  [dry] {proj:42} sessions={len(sessions)}")
            continue
        note = write_project_log(vault_projects, proj, sessions)
        if conn is not None:
            for d in sessions:
                try:
                    write_db(d, proj, conn)
                except Exception as e:
                    print(f"  ⚠ DB {short_id(d['session_id'])}: {e}")
        print(f"  ✓ {proj:42} sessions={len(sessions)} → {os.path.relpath(note, vault)}")
        written += 1

    if conn is not None:
        conn.close()
    if not args.dry_run:
        for p, mt in mtimes.items():
            state[p] = mt
        save_state(state)
    print(f"\nDone: projects written={written} skipped(unchanged)={skipped} "
          f"sessions parsed={parsed}")


if __name__ == "__main__":
    main()
