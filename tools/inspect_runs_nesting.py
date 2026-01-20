import sqlite3, json

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs = json.loads(r['runs'])
print('Type:', type(runs))
print('Length:', len(runs))
# Inspect first item
first = runs[0]
print('\nFirst item type:', type(first))
if isinstance(first, dict):
    print('Keys:', list(first.keys()))
    # Look for nested structure
    for k, v in first.items():
        print(f'  {k}: {type(v)}')
        if isinstance(v, list) and len(v) > 0:
            print(f'    List of {type(v[0])}, length {len(v)}')
            print(f'    First item keys: {list(v[0].keys())[:5] if isinstance(v[0], dict) else v[0]}')
        elif isinstance(v, dict):
            print(f'    Dict keys: {list(v.keys())[:5]}')
elif isinstance(first, list):
    print('First is a list!')
    print('Length:', len(first))
    print('First element type:', type(first[0]))
    if isinstance(first[0], dict):
        print('First element keys:', list(first[0].keys())[:5])
conn.close()
