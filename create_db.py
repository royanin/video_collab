import sqlite3

db_file = 'app/data/app_data.sqlite'

conn = sqlite3.connect(db_file)

# Create a cursor object:
c = conn.cursor()

# Create table room record
c.execute('''CREATE TABLE IF NOT EXISTS roomCreate
             (id INTEGER PRIMARY KEY ASC, timestamp, room_id)''')

# Create table current users
#c.execute('''CREATE TABLE IF NOT EXISTS currentUsers
#             (id INTEGER PRIMARY KEY ASC, room_id, sid, screenName)''')

conn.close()
