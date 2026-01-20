import sqlite3
import json
import sys

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
if not r or not r['runs']:
    print('No runs')
    sys.exit(0)

runs_str = r['runs']
# Iterate through parsed runs (they may be strings or dicts) and find indices where messages exist
runs_list = None
try:
    runs_list = json.loads(runs_str)
except Exception as e:
    print('Failed to parse runs as JSON:', e)
    sys.exit(1)

print('Total parsed runs:', len(runs_list))
found_indices = []
for i, run in enumerate(runs_list):
    if isinstance(run, str):
        try:
            run_obj = json.loads(run)
        except Exception:
            continue
    elif isinstance(run, dict):
        run_obj = run
    else:
        continue

    if not isinstance(run_obj, dict):
        continue

    if run_obj.get('messages'):
        found_indices.append(i)
        if len(found_indices) < 10:
            print('Index', i, 'sample messages count', len(run_obj.get('messages')))

print('Found messages in indices (first 20):', found_indices[:20])
conn.close()
