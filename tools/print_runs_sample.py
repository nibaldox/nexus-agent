import sqlite3, json
sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs = json.loads(r['runs'])
print('Total runs:', len(runs))
for i in range(20):
    raw = runs[i]
    print('INDEX', i, 'type', type(raw))
    run = raw
    if isinstance(raw, str):
        try:
            run = json.loads(raw)
            print('  parsed to dict keys:', list(run.keys())[:10])
        except Exception as e:
            print('  string but failed to parse', e)
    elif isinstance(raw, dict):
        print('  dict keys:', list(run.keys())[:10])
    else:
        print('  other type', raw)
conn.close()