import sqlite3, json, sys
sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs_str = r['runs']
needle = 'You are the leader of a team'
idx = runs_str.find(needle)
print('index:', idx)
if idx!=-1:
    start = max(0, idx-400)
    print(runs_str[start:idx+400])
conn.close()