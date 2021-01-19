import sqlite3, json
from datetime import datetime,timezone
import random, string
from urllib.parse import urlparse, parse_qs

def write_chat(conn, ts, room_id, username, text):
    c = conn.cursor()
    sql_ = """INSERT INTO chat (timestamp, room_id, username, text)
     VALUES (?,?,?,?)"""
    c.execute(sql_, (ts, room_id, username, text))
    conn.commit()
    c.close()

    return ()

def read_chat(conn, room_id, limit_=25, timestamp_=datetime.now(timezone.utc).timestamp()):
    c = conn.cursor()
    #get chats for a room
    sql_ = """SELECT * FROM chat WHERE room_id='{}' AND timestamp < {}
    ORDER BY timestamp DESC LIMIT {}""".format(room_id, timestamp_, limit_)
    print(sql_)
    c.execute(sql_)
    ret_list = []
    ret_list = c.fetchall()
    if len(ret_list)>0:
        ret_list_json = [{'who': item[2],'when':item[0],
                        'msg':item[3]} for item in ret_list ]
    else:
        ret_list_json = []
    c.close()

    return (ret_list_json)

'''def parse_url(url_input):
    if url_input != None:
        return ("ytid", "-Qr8QrMG3CQ")

    else:
        return (None, None)
'''

def parse_url(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """


    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return ("ytid", parse_qs(query.query)['v'][0])
        elif query.path.startswith(('/embed/', '/v/')):
            return ("ytid", query.path.split('/')[2])
    elif 'youtu.be' in query.hostname:
        return ("ytid", query.path[1:])
    else:
        raise ValueError


def validate_newname(name):
    if len(name)>=6 and len(name)<=20 and name.isalnum():
        msg_ = "Name change successful."

    else:
        msg_ = "We chose a random name for you; acceptable names are 6-20 characters long, and contain letters and numbers only."
        name = ''.join(random.choices(string.ascii_lowercase, k=8))

    return name, msg_

def validate_newroom(room):
    return True
    '''
    if len(room)==32:
        return True
    else:
        return False
    '''
