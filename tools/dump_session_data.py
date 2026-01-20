import sqlite3, json, sys

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT session_id, session_data, runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
if not r:
    print('Session not found')
else:
    print('session_id:', r['session_id'])
    print('\nsession_data preview:')
    sd = r['session_data']
    if sd:
        print(sd[:2000])
        try:
            sdj = json.loads(sd)
            print('\nkeys in session_data:', list(sdj.keys()))
        except Exception as e:
            print('session_data JSON parse error', e)
    else:
        print('None')
    print('\nruns preview:')
    runs = r['runs']
    if runs:
        print(runs[:2000])
        try:
            runsj = json.loads(runs)
            print('\n# runs:', len(runsj))
        except Exception as e:
            print('runs JSON parse error', e)
    else:
        print('None')
conn.close()
