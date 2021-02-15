import sqlite3

db_file = 'data/rooms_created.sqlite'

conn = sqlite3.connect(db_file)

# Create a cursor object:
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE roomCreate
             (timestamp, room_id)''')
conn.close()
