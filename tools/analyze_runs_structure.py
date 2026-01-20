import sqlite3, json, re

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs_str = r['runs']

# Try to parse the full JSON
try:
    runs = json.loads(runs_str)
    print('Parsed as JSON successfully')
    print('Type:', type(runs))
    if isinstance(runs, list):
        print('Length:', len(runs))
        # Show structure of first few items
        for i, item in enumerate(runs[:3]):
            print(f'\n--- Item {i} ---')
            print('Type:', type(item))
            if isinstance(item, dict):
                print('Keys:', list(item.keys())[:10])
                # Check for messages inside
                if 'messages' in item:
                    print('Has messages array')
                    print('Messages count:', len(item['messages']))
                # Check for content
                if 'content' in item:
                    print('Has content:', len(str(item['content'])))
                # Check for input
                if 'input' in item:
                    print('Has input:', item['input'])
            elif isinstance(item, str):
                print('String length:', len(item))
                # Try to parse
                try:
                    inner = json.loads(item)
                    print('Parsed inner to:', type(inner), list(inner.keys())[:5] if isinstance(inner, dict) else len(inner))
                except Exception as e:
                    print('Failed to parse inner:', e)
    elif isinstance(runs, dict):
        print('Dict keys:', list(runs.keys())[:10])
except json.JSONDecodeError as e:
    print('JSON parse error:', e)
    # Try to find where it fails
    idx = runs_str.find('[{')
    if idx != -1:
        print('First array start at:', idx)
        print('Snippet:', runs_str[idx:idx+200])

conn.close()
