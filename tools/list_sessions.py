import sqlite3

def show_schema():
    conn=sqlite3.connect('agent.db')
    c=conn.cursor()
    print('TABLE INFO:')
    for row in c.execute("PRAGMA table_info('nexus_team_sessions')"):
        print(row)
    print('\nSAMPLE ROWS:')
    for row in c.execute("SELECT rowid, * FROM nexus_team_sessions LIMIT 20"):
        print(row[:6])
    conn.close()

if __name__ == '__main__':
    show_schema()
