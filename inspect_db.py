import sqlite3

try:
    conn = sqlite3.connect('agent.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(nexus_team_sessions)")
    columns = cursor.fetchall()
    print("Columns:", columns)
    
    # Check if there's any data
    cursor.execute("SELECT * FROM nexus_team_sessions LIMIT 1")
    rows = cursor.fetchall()
    print("Sample Row:", rows)
    conn.close()
except Exception as e:
    print(e)
