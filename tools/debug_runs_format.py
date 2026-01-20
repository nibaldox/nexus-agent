import sqlite3, json

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs_str = r['runs']
print('runs type:', type(runs_str))
print('runs length:', len(runs_str))
print('first 500 chars:')
print(runs_str[:500])
print('\n---')
print('last 500 chars:')
print(runs_str[-500:])
conn.close()
