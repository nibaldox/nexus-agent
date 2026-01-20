#!/usr/bin/env python3
"""
Bulk session compaction script.
Processes all sessions in the database and creates compact message views.
Can be run periodically or on-demand to speed up /sessions/{id} lookups.
"""
import sqlite3
import json
import sys
import re
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('agent.db')
    conn.row_factory = sqlite3.Row
    return conn

def extract_from_run_string(s, max_items=20):
    """Extract messages from an opaque run string using regex."""
    items = []
    # Try to find a messages array
    m_arr = re.search(r'"messages"\s*:\s*\[(.*?)\]\s*(?:,|})', s, re.S)
    if m_arr:
        block = m_arr.group(1)
        for m in re.finditer(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', block, re.S):
            txt = m.group(1)
            try:
                txt = json.loads('"' + txt + '"')
            except Exception:
                pass
            items.append({'role': 'assistant', 'content': txt})
            if len(items) >= max_items:
                return items
    # Try input_content
    m_inp = re.search(r'"input_content"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.S)
    if m_inp:
        txt = m_inp.group(1)
        try:
            txt = json.loads('"' + txt + '"')
        except Exception:
            pass
        items.append({'role': 'user', 'content': txt})
    # Try standalone content
    m_cont = re.search(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.S)
    if m_cont:
        txt = m_cont.group(1)
        try:
            txt = json.loads('"' + txt + '"')
        except Exception:
            pass
        items.append({'role': 'assistant', 'content': txt})
    return items

def compact_session(session_id, limit=2000):
    """Extract messages from runs and store compact view."""
    conn = get_db_connection()
    try:
        # Check if compact_messages column exists
        cols = [r[1] for r in conn.execute("PRAGMA table_info('nexus_team_sessions')").fetchall()]
        if 'compact_messages' not in cols:
            conn.execute("ALTER TABLE nexus_team_sessions ADD COLUMN compact_messages TEXT")
            conn.commit()

        row = conn.execute("SELECT runs FROM nexus_team_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row or not row['runs']:
            return 0

        runs = json.loads(row['runs'])
        collected = []

        # Process runs from newest to oldest
        for raw_run in reversed(runs):
            if len(collected) >= limit:
                break
            run = None
            if isinstance(raw_run, str):
                try:
                    run = json.loads(raw_run)
                except Exception:
                    extracted = extract_from_run_string(raw_run, max_items=5)
                    for it in extracted:
                        collected.append(it)
                        if len(collected) >= limit:
                            break
                    continue
            elif isinstance(raw_run, dict):
                run = raw_run
            else:
                continue

            if not isinstance(run, dict):
                continue

            # Extract from structured messages
            if isinstance(run.get('messages'), list) and run.get('messages'):
                for m in reversed(run.get('messages')):
                    role = m.get('role', 'assistant') if isinstance(m, dict) else 'assistant'
                    content = m.get('content', '') if isinstance(m, dict) else str(m)
                    collected.append({'role': role, 'content': content})
                    if len(collected) >= limit:
                        break
                if len(collected) >= limit:
                    break
                continue

            # Reconstruct from input/content
            inp = run.get('input')
            content = run.get('content')
            if isinstance(inp, dict):
                input_content = inp.get('input_content') or inp.get('content')
            else:
                input_content = inp
            if input_content:
                collected.append({'role': 'user', 'content': input_content})
                if len(collected) >= limit:
                    break
            if content:
                collected.append({'role': 'assistant', 'content': content})
                if len(collected) >= limit:
                    break

        collected.reverse()
        compact_json = json.dumps(collected)

        conn.execute("UPDATE nexus_team_sessions SET compact_messages = ? WHERE session_id = ?",
                     (compact_json, session_id))
        conn.commit()
        return len(collected)

    finally:
        conn.close()

def main():
    print("=== Nexus Session Compaction Tool ===")
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    conn = get_db_connection()
    try:
        # Ensure compact_messages column exists
        cols = [r[1] for r in conn.execute("PRAGMA table_info('nexus_team_sessions')").fetchall()]
        if 'compact_messages' not in cols:
            print("Adding compact_messages column...")
            conn.execute("ALTER TABLE nexus_team_sessions ADD COLUMN compact_messages TEXT")
            conn.commit()

        # Get all sessions
        sessions = conn.execute("SELECT session_id, runs, compact_messages, updated_at FROM nexus_team_sessions").fetchall()
        total = len(sessions)
        print(f"Total sessions: {total}")

        # Count sessions needing compaction
        needs_compact = [s for s in sessions if s['runs'] and not s['compact_messages']]
        print(f"Sessions needing compaction: {len(needs_compact)}")

        if not needs_compact:
            print("All sessions already compacted!")
            return

        limit = 2000  # Default extraction limit
        compact_count = 0
        msg_count = 0
        errors = []

        print(f"\nProcessing sessions (limit={limit} messages per session)...")
        for i, s in enumerate(needs_compact, 1):
            try:
                extracted = compact_session(s['session_id'], limit=limit)
                if extracted > 0:
                    compact_count += 1
                    msg_count += extracted
                    print(f"  [{i}/{len(needs_compact)}] {s['session_id'][:8]}...: {extracted} messages")
                else:
                    print(f"  [{i}/{len(needs_compact)}] {s['session_id'][:8]}...: no messages extracted")
            except Exception as e:
                errors.append((s['session_id'], str(e)))
                print(f"  [{i}/{len(needs_compact)}] {s['session_id'][:8]}...: ERROR - {e}")

        print()
        print("=== Summary ===")
        print(f"Sessions compacted: {compact_count}/{len(needs_compact)}")
        print(f"Total messages extracted: {msg_count}")
        print(f"Errors: {len(errors)}")
        if errors:
            print("\nError details:")
            for sid, err in errors[:10]:
                print(f"  - {sid}: {err}")
            if len(errors) > 10:
                print(f"  ... and {len(errors)-10} more")

    finally:
        conn.close()

    print()
    print(f"Finished at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
