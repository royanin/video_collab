from flask import session, redirect, url_for, render_template, request, current_app
from . import main
from .forms import LoginForm
#from .utils import read_chat, write_chat
import sqlite3, json
from .utils import write_chat, read_chat, parse_url



@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    #db_file = current_app.config['db_file']

    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form, ret_list=[])


@main.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    print(session)

    #sid = socketio.eio.sid
    #print('socket id: {}'.format(sid))

    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))

    return render_template('room.html', name=name, room=room)

@main.route('/morechat', methods=['POST'])
def getchat():
    num_messages = 5
    #print(request.json['data'])
    data = request.get_json()
    tstamp = None
    try:
        tstamp = float(data['tstamp'])
        msg = "Showing {} previous messages".format(num_messages)
    except Exception as e:
        msg = "Can't load more messages..."

    name = session.get('name', '')
    room = session.get('room', '')

    #Get messages from the database and send them as the ajax call response
    if tstamp != None:
        db_file = current_app.config['db_file']
        conn = sqlite3.connect(db_file)

        #get a list of num_messages recent chats:
        ret_list = []
        ret_list = read_chat(conn, room, limit_=num_messages, timestamp_= tstamp)
        #print(ret_list)
        return json.dumps(ret_list)
        #emit('message', {'msg': username + ':' + message['msg']}, room=room)
        #emit('message', {'who': username,'when':ts,
        #                'msg':text_}, room=room)

    else:
        return(msg)


@main.route('/newvideourl', methods=['POST'])
def getURL():
    data = request.get_json()
    url_input = data['url']
    url_type, url_key = parse_url(url_input)

    if url_type != None and url_key != None:
        return json.dumps({'type':url_type, 'key':url_key})

    else:
        return None
