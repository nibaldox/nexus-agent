import sqlite3, json, re

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs = json.loads(r['runs'])
print('Total runs:', len(runs))

pattern_messages = re.compile(r'"messages"\s*:\s*\[(.*?)\]\s*(?:,|})', re.S)
pattern_content = re.compile(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', re.S)
pattern_input = re.compile(r'"input_content"\s*:\s*"((?:\\.|[^"\\])*)"', re.S)

found = 0
for i, raw in enumerate(runs[-1000:]):
    if isinstance(raw, str):
        s = raw
    else:
        s = json.dumps(raw)

    m = pattern_messages.search(s)
    if m:
        block = m.group(1)
        cont = pattern_content.search(block)
        if cont:
            txt = cont.group(1)
            try:
                txt = json.loads('"' + txt + '"')
            except Exception:
                pass
            print('Found messages in run index', i - 1000, 'snippet:', txt[:200])
            found += 1
    else:
        # check single content or input_content
        c = pattern_content.search(s)
        if c:
            txt = c.group(1)
            try:
                txt = json.loads('"' + txt + '"')
            except Exception:
                pass
            print('Found content in run index', i - 1000, 'snippet:', txt[:200])
            found += 1

    if found >= 10:
        break

print('Done. found:', found)
conn.close()