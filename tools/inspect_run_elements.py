import sqlite3, json

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs = json.loads(r['runs'])

print('runs is list, length:', len(runs))
print('\nFirst 3 elements raw:')
for i in range(min(3, len(runs))):
    elem = runs[i]
    print(f'\nElement {i}:')
    print('  Type:', type(elem))
    print('  Length:', len(elem))
    print('  First 200 chars:', repr(elem[:200]))
    # Try to see if it's a number
    try:
        num = int(elem)
        print('  Is a number:', num)
    except Exception:
        pass
    # Try to see if it's a simple string
    if len(elem) < 100:
        print('  Full repr:', repr(elem))
conn.close()
