import sqlite3

db_file = 'data/chat_messages.sqlite'

conn = sqlite3.connect(db_file)

# Create a cursor object:
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE chat
             (timestamp, room_id, username, text)''')
conn.close()
