from flask import session, current_app, request
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from datetime import datetime,timezone
import sqlite3
from .utils import record_room_create, record_event, parse_url
import time
#from .models import db, Room, CurrentUser
from .models import *



@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    #time.sleep(0.5) #this ensures that the new client has time to render html
    join_room(room)

    #emit('status', {'msg': session.get('name') + ' joined the room'},
    #                    room=room,  broadcast=True, include_self=False)
    emit('status', {'msg': ''},
                        room=room,  broadcast=True, include_self=False)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room, room_id = session.get('room'), session.get('room_id')
    username = session.get('name')
    ts = datetime.now(timezone.utc).timestamp()
    text_ = message['msg']
    #print(ts, room, username, text_)

    #write_chat(conn, ts, room, username, text_)
    #emit('message', {'msg': username + ':' + message['msg']}, room=room)
    record_event(room_id, 'tc', event_details=session.get('sid')[:4])
    emit('message', {'who': username,'when':ts,
                    'msg':text_}, room=room)

'''
@socketio.on('value changed', namespace='/chat')
def value_changed(message):
    room = session.get('room')
    #print(message)
    #print(session)
    values[message['who']] = message['data']
    emit('update value', message, room=room)
'''

@socketio.on('state update', namespace='/chat')
def playpause(message):
    ts = datetime.now(timezone.utc).timestamp()
    room, room_id = session.get('room'), session.get('room_id')
    username = session.get('name')
    message['who'] = username
    message['what'] = 'playpause'
    message['when'] = message['ptime']
    #print(message)
    if message['pstate'] == 1:
        event_type = 'ws'
    elif message['pstate'] == 2:
        event_type = 'wp'
    record_event(room_id, event_type, event_details=message['ptime'])
    emit('update state', message, room=room, broadcast=True, include_self=False)

@socketio.on('state update speed', namespace='/chat')
def speedchange(message):
    ts = datetime.now(timezone.utc).timestamp()
    room, room_id = session.get('room'), session.get('room_id')
    username = session.get('name')
    message['who'] = username
    message['what'] = 'speed'
    message['when'] = message['ptime']
    #print(message)
    record_event(room_id, 'wf', event_details=message['pspeed'])
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
    #print(response)
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
    #print('stateNow',stateNow)
    emit('video synced', stateNow, room=room, broadcast=True, include_self=False)



@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    #ulist = [u.screenName for u in CurrentUser.query.filter_by(room_id=room_id).all()]
    #emit('update message', {'msg': session.get('name') + ' has left the room.','ulist':ulist}, room=room)
    emit('update message', {'msg': session.get('name') + ' has left the room...'}, room=room)

@socketio.on('launched_service', namespace='/chat')
def service_launch(service_name):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    emit('update message', {'msg': username + ' has launched the '+service_name}, room=room)

@socketio.on('connect', namespace='/chat')
def test_connect():
    print('in events: session:', session)
    session['sid'] = request.sid
    room_id = session.get('room_id')
    current_user = CurrentUser(room_id=room_id, sid=request.sid, screenName=session.get('name'))
    db.session.add(current_user)
    db.session.commit()

    print('num_users: ', CurrentUser.query.filter_by(room_id=room_id).count())
    ulist = [u.screenName for u in CurrentUser.query.filter_by(room_id=room_id).all()]
    print('\nusers_list',ulist)
    record_event(room_id, 'uj', event_details=session['sid'][:4])
    emit('update message', {'msg': session.get('name') + ' joined the room','ulist':ulist}, room=room_id)

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    CurrentUser.query.filter_by(sid=request.sid).delete()
    db.session.commit()
    room_id = session.get('room_id')
    ulist = [u.screenName for u in CurrentUser.query.filter_by(room_id=room_id).all()]
    record_event(room_id, 'ul', event_details=session['sid'][:4])
    emit('update message', {'msg': session.get('name') + ' has left the room.','ulist':ulist}, room=room_id)
