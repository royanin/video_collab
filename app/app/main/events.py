from flask import session, current_app, request
from flask_security import current_user
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from datetime import datetime,timezone
import sqlite3
from .utils import record_event, parse_url, get_current_users_in_room,\
record_current_room_user, remove_current_room_user
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
    room = session.get('room')
    username = session.get('name')
    ts = datetime.now(timezone.utc).timestamp()
    text_ = message['msg']

    record_event(room, 'tc', event_details=session.get('sid')[:4])
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
    room = session.get('room')
    username = session.get('name')
    message['who'] = username
    message['what'] = 'playpause'
    message['when'] = message['ptime']
    #print(message)
    if message['pstate'] == 1:
        event_type = 'ws'
    elif message['pstate'] == 2:
        event_type = 'wp'
    else:
        event_type = 'wh' #'watching on hold? like, getting ready etc.'
    record_event(room, event_type, event_details=message['ptime'])
    emit('update state', message, room=room, broadcast=True, include_self=False)

@socketio.on('state update speed', namespace='/chat')
def speedchange(message):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    message['who'] = username
    message['what'] = 'speed'
    message['when'] = message['ptime']
    #print(message)
    record_event(room, 'wf', event_details=message['pspeed'])
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

    emit('update message', {'msg': session.get('name') + ' has left the room...'}, room=room)

@socketio.on('launched_service', namespace='/chat')
def service_launch(service_name):
    ts = datetime.now(timezone.utc).timestamp()
    room = session.get('room')
    username = session.get('name')
    emit('update message', {'msg': username + ' has launched the '+service_name}, room=room)

@socketio.on('connect', namespace='/chat')
def test_connect():
    session['sid'] = request.sid
    room_url = session.get('room')

    #create redis key for the occupants in the room:
    room_occ_key = "{}_occ".format(room_url)
    #this will have all current authenticated and guest users in list
    record_current_room_user(room_url)

    #keep all room guests by room name:
    current_app.redis.sadd(room_occ_key, session.get('name'))
    num_guests, ulist = get_current_users_in_room(room_url)

    record_event(room_url, 'uj', event_details=session['sid'][:4])
    emit('update message', {'msg': session.get('name') + ' joined the room','ulist':ulist}, room=room_url)

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():

    room_id = session.get('room_id')
    room_url = session.get('room')
    #for redis
    room_occ_key = "{}_occ".format(room_url)
    current_app.redis.srem(room_occ_key, session.get('name')) #make them screennames
    #record current user's removal from the room in the current_room_user table
    remove_current_room_user(room_url)

    num_guests, ulist = get_current_users_in_room(room_url)
    if num_guests == 0:
        #remove the room from current room list:
        current_app.redis.srem('room_list', room_url)
        #remove the room cretor from current room creator list:

    record_event(room_url, 'ul', event_details=session['sid'][:4])
    emit('update message', {'msg': session.get('name') + ' has left the room.','ulist':ulist}, room=room_url)
