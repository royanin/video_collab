from flask import session, current_app
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from datetime import datetime,timezone
import sqlite3
from .utils import record_room_create, read_room_create, parse_url
import time


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    #time.sleep(0.5) #this ensures that the new client has time to render html
    join_room(room)

    emit('status', {'msg': session.get('name') + ' joined the room!'},
                        room=room,  broadcast=True, include_self=False)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    username = session.get('name')
    ts = datetime.now(timezone.utc).timestamp()
    #db_file = current_app.config['db_file']
    #conn = sqlite3.connect(db_file)
    text_ = message['msg']
    print(ts, room, username, text_)

    #write_chat(conn, ts, room, username, text_)
    #emit('message', {'msg': username + ':' + message['msg']}, room=room)
    emit('message', {'who': username,'when':ts,
                    'msg':text_}, room=room)

'''
@socketio.on('value changed', namespace='/chat')
def value_changed(message):
    room = session.get('room')
    print(message)
    #print(session)
    values[message['who']] = message['data']
    emit('update value', message, room=room)
'''

@socketio.on('state update', namespace='/chat')
def playpause(message):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    message['who'] = username
    message['what'] = 'playpause'
    message['when'] = ts
    print(message)
    emit('update state', message, room=room, broadcast=True, include_self=False)

@socketio.on('state update speed', namespace='/chat')
def speedchange(message):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    message['who'] = username
    message['what'] = 'speed'
    message['when'] = ts
    print(message)
    emit('update state', message, room=room, broadcast=True, include_self=False)

#'video update'
@socketio.on('video update', namespace='/chat')
def updateVideo(response):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')

    response['who'] = username
    response['what'] = 'updated video'
    response['when'] = ts
    print(response)
    emit('video updated', response, room=room, broadcast=True, include_self=False)

#'video sync'
@socketio.on('video sync', namespace='/chat')
def syncing_video(stateNow):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    url_type, url_key = parse_url(stateNow['vidURL'])
    stateNow['vtype'] = url_type
    stateNow['vkey'] = url_key
    #time.sleep(0.1) #this ensures that the new client has time to render html
    print('stateNow',stateNow)
    emit('video synced', stateNow, room=room, broadcast=True, include_self=False)



@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('update message', {'msg': session.get('name') + ' has left the room.'}, room=room)

@socketio.on('launched_service', namespace='/chat')
def service_launch(service_name):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    emit('update message', {'msg': username + ' has launched the '+service_name}, room=room)

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    print('client disconnected')
    emit('update message', {'msg': session.get('name') + ' has left the room.'}, room=session.get('room'))
