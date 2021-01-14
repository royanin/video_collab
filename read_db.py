import sqlite3

db_file = 'data/chat_messages.sqlite'

conn = sqlite3.connect(db_file)

# Create a cursor object:
c = conn.cursor()

# Read from a table
#c.execute('''SELECT * FROM chat WHERE room_id={} ORDER BY timestamp  LIMIT {}'''.format("123", 10))
#c.execute('''SELECT * FROM chat WHERE room_id="123" ORDER BY timestamp DESC LIMIT 10''')
c.execute('''SELECT * FROM chat ORDER BY timestamp DESC''')
ret_list = c.fetchall()

conn.close()

count = 0
for _ in ret_list:
    count += 1
    print(count, _)
