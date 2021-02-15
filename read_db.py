import sqlite3

#db_file = 'data/chat_messages.sqlite'
db_file = 'data/rooms_created.sqlite'

conn = sqlite3.connect(db_file)

# Create a cursor object:
c = conn.cursor()

# Read from a table
#c.execute('''SELECT * FROM chat WHERE room_id={} ORDER BY timestamp  LIMIT {}'''.format("123", 10))
#c.execute('''SELECT * FROM chat WHERE room_id="123" ORDER BY timestamp DESC LIMIT 10''')
#c.execute('''SELECT * FROM chat ORDER BY timestamp DESC''')i
#c.execute('''SELECT * FROM roomCreate''')

room_id = "244b228be0574a4e874dff27659026db"
#c.execute("""IF EXISTS (SELECT 1 FROM roomCreate WHERE room_id = '{}') PRINT 'Column Exists' ELSE PRINT 'Column not found'""".format(room_id)
#)
#sql_ = """SELECT * FROM roomCreate WHERE room_id = '{}' LIMIT 1""".format(room_id)
sql_ = """SELECT * FROM roomCreate"""
print(sql_)
c.execute(sql_)
#c.execute("""SELECT * FROM roomCreate  WHERE room_id = '244b228be0574a4e874dff27659026db'""")
ret_list = c.fetchall()

conn.close()

print(ret_list)
