import sqlite3, json, sys

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
if not r or not r['runs']:
    print('No runs')
    sys.exit(0)

runs = json.loads(r['runs'])
print('Total runs:', len(runs))
count = 0
for i, raw in enumerate(runs[:300]):
    # parse if string
    run = raw
    if isinstance(raw, str):
        try:
            run = json.loads(raw)
        except Exception:
            run = None
    if not isinstance(run, dict):
        continue
    if 'messages' in run:
        print('Found at index', i)
        m = run['messages']
        print('messages type:', type(m), 'count:', len(m) if isinstance(m, list) else 'n/a')
        if isinstance(m, list):
            for j,mm in enumerate(m[:3]):
                print(' -', j, type(mm), list(mm.keys())[:5] if isinstance(mm, dict) else repr(mm)[:80])
        else:
            print('messages sample (string):', str(m)[:400])
        count += 1
        if count > 5:
            break

print('Done')
conn.close()