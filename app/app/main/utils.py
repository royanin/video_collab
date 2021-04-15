import sqlite3, json
from datetime import datetime,timezone
import random, string
from urllib.parse import urlparse, parse_qs
from flask import current_app
#from .models import db, Room, CurrentUser, RoomEvents
from .models import *

'''
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

'''

'''def parse_url(url_input):
    if url_input != None:
        return ("yt", "-Qr8QrMG3CQ")

    else:
        return (None, None)
'''
def get_guest_stat_msg(name, room_id):
    ulist_all = [u.screenName for u in CurrentUser.query.filter_by(room_id=room_id).all()]
    ulist = [ u_ for u_ in ulist_all if u_!= name]
    num_guests = len(ulist)
    if num_guests==0:
        guest_stat_msg = "You are the only one in the room"
    else:
        guest_string_ = (", ".join(ulist))
        if len(guest_string_)>30:
            guest_string = guest_string_[:30]+'...'
        else:
            guest_string = guest_string_
        guest_stat_msg ='{} guests: {}, {}'.format(num_guests+1, name, guest_string)

    return guest_stat_msg

def record_room_create(room_string, room_type='da', room_creator_uid = None,
                        room_state = 'a'):
    #room_type: 'd2' is demo for 2, 'da' -> demo for any
    #room_state: 'a' for active; could be inactive, read-only, secure etc. etc.
    ts = datetime.now(timezone.utc).timestamp()
    new_room = Room(timestamp=ts, room_string=room_string, room_type=room_type,
                        room_creator_uid = room_creator_uid, room_state = room_state)
    #print(new_room)
    db.session.add(new_room)
    db.session.commit()
    return new_room.id


def record_event(room_id, event_type, event_details=None):
    '''
    dictionary for event_type, event_details
    'rc': 'room created',
    'uj':'user joined', 'sid'
    'ul':'user left', 'sid'
    'tc':'text sent', 'sid'
    'vl':'video chat launched', 'sid'
    'vd':'video chat dismissed', 'sid'
    'es':'editor toggle', 'sid'
    'wl':'online video loaded',
    'wp':'watching paused', 'timstamp'
    'ws':'watching started/resumed', 'timstamp'
    'wf':'watching speed changed', 'new speed'
    'wh':'watching on hold', 'timestamp' #video play state other than 1 or 2
    'ep':'emoji panel toggled', 'sid'
    'et':'editor timestamp insert used', 'sid'
    'en':'editor username insert used', 'sid'
    'qs':'quick start clicked', 'sid'
    '''
    #This is a temporary implementation -- should be written with a buffer?
    ts = datetime.now(timezone.utc).timestamp()
    new_event = RoomEvents(timestamp=ts, room_id = room_id,
                        event_type = event_type, event_details = event_details)
    db.session.add(new_event)
    db.session.commit()
    return ()


def parse_url(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        #Youtube:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

        #Panopto:
        'xyz.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=abd...'
        'https://xyz.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=401da229-c9a6-49e4-aeab-ab91015553f6'

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """


    #if url.startswith(('youtu', 'www')):
    #    url = 'http://' + url
    if not url.startswith(("http://", "https://")):
        url = "http://"+url


    if url != "http://":
        query = urlparse(url)
    try:
        if 'youtube' in query.hostname:
            if query.path == '/watch':
                return ("yt", parse_qs(query.query)['v'][0])
            elif query.path.startswith(('/embed/', '/v/')):
                return ("yt", query.path.split('/')[2])
        elif 'youtu.be' in query.hostname:
            return ("yt", query.path[1:])
        elif 'hosted.panopto.com' in query.hostname:
            return ("pt", (query.netloc, parse_qs(query.query)['id'][0]))
        else:
            raise ValueError
    except Exception as e:
        return None, None

def get_room_id_from_submitted_url(room_url):
    if room_url[-1]=='/':
        room_url.rstrip('/')
    room_string = room_url.split("/")[-1]

    room = Room.query.filter_by(room_string=room_string).first()
    if room != None:
        return room.room_string, room.id
    else:
        return None, None

def validate_newname(name):
    '''
    if len(name)>=6 and len(name)<=20 and name.isalnum():
        msg_ = "Name change successful."

    else:
        msg_ = "Acceptable names are 6-20 characters long, and contain letters and numbers only."
        #name = ''.join(random.choices(string.ascii_lowercase, k=8))
        name = ""
    '''
    if name != "":
        msg_ = "Name change successful."
    else:
        msg_ = "Let's try again. Shall we?"
    return name, msg_

def validate_newroom(room_string):
    #time_window = 600 for certain room type?
    room = Room.query.filter_by(room_string=room_string).first()
    if room != None:
        return room.id
    else:
        return None

    '''
    if len(room)==32:
        return True
    else:
        return False
    '''
