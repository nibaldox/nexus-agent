import sqlite3, json, sys

def inspect(session_id):
    db='agent.db'
    try:
        conn=sqlite3.connect(db)
        conn.row_factory=sqlite3.Row
        r=conn.execute('SELECT session_id, memory, created_at, updated_at FROM nexus_team_sessions WHERE session_id=?',(session_id,)).fetchone()
        if not r:
            print('Session not found')
            return
        print('Found session_id:', r['session_id'])
        mem=r['memory']
        if not mem:
            print('Memory empty')
        else:
            print('Memory length:', len(mem))
            try:
                js=json.loads(mem)
                print('Messages count:', len(js.get('messages',[])))
                msgs=js.get('messages',[])
                for i,m in enumerate(msgs[:10]):
                    print(i, m.get('role'), repr(m.get('content')[:200]))
            except Exception as e:
                print('JSON parse error:', e)
                print('Memory snippet:', mem[:1000])
        conn.close()
    except Exception as e:
        print('DB error:', e)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: inspect_session.py <session_id>')
        sys.exit(1)
    inspect(sys.argv[1])
