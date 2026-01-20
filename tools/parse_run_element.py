import sqlite3, json

sess='22786604-5f31-4eef-95c1-b2a21cc5de71'
conn=sqlite3.connect('agent.db')
conn.row_factory=sqlite3.Row
r=conn.execute('SELECT runs FROM nexus_team_sessions WHERE session_id=?',(sess,)).fetchone()
runs = json.loads(r['runs'])

print('runs is a list of strings')
print('Count:', len(runs))
print('First element type:', type(runs[0]))

# Parse first element
first = json.loads(runs[0])
print('\nFirst run parsed:')
print('Type:', type(first))
print('Keys:', list(first.keys()))

# Look for content and messages
if 'content' in first:
    print('\nHas content field')
    print('Content length:', len(str(first['content'])))
    print('Content preview:', str(first['content'])[:300])

if 'input' in first:
    print('\nHas input field')
    print('Input:', first['input'])

# Check if there's a nested runs array
if 'runs' in first:
    print('\nHas nested runs array')
    nested = first['runs']
    print('Nested type:', type(nested))
    if isinstance(nested, list) and len(nested) > 0:
        print('Nested length:', len(nested))
        nested_first = nested[0]
        print('Nested first type:', type(nested_first))
        if isinstance(nested_first, dict):
            print('Nested first keys:', list(nested_first.keys())[:10])
            if 'content' in nested_first:
                print('Nested content preview:', str(nested_first['content'])[:200])

conn.close()
