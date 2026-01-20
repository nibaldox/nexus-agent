import sqlite3, json

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
if not r or not r['runs']:
    print('No runs found')
else:
    runs = json.loads(r['runs'])
    print('Total runs:', len(runs))
    count_messages = 0
    examples = []
    for i,run in enumerate(runs[-200:]):
        if isinstance(run, str):
            try:
                run = json.loads(run)
            except Exception:
                continue

        if not isinstance(run, dict):
            continue

        if run.get('messages'):
            count_messages += len(run['messages'])
            if len(examples) < 5:
                examples.append(run['messages'][:2])
        else:
            # check for input/content
            inp = run.get('input')
            content = run.get('content')
            if inp or content:
                count_messages += (1 if inp else 0) + (1 if content else 0)
                if len(examples) < 5:
                    examples.append({'input': inp, 'content': content})
    print('Found messages in first 200 runs:', count_messages)
    print('Examples:', examples)
conn.close()
