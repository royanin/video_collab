from flask import session, redirect, url_for, render_template, request, current_app
from . import main
from .forms import LoginForm
#from .utils import read_chat, write_chat
import sqlite3, json
from .utils import write_chat, read_chat, parse_url, validate_newname, validate_newroom
import uuid


'''
@main.route('/', methods=['GET', 'POST'])
def index():

    #Login form to enter a room.
    form = LoginForm()
    #db_file = current_app.config['db_file']

    if form.validate_on_submit():
        session['name'] = form.name.data
        #session['room'] = form.room.data

        #assign room here:
        room = session.get('room', '')
        if room == '':
            u = uuid.uuid4()
            room = u.hex
            session['room'] = room
        session['joint'] = "{}.{}".format(room, session['name'])
        print('Hello {}, your room is {}'.format(session['name'], room))
        return redirect(url_for('.chat', room=room))

    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        #room = session.get('room', '')
        #form.room.data = session.get('room', '')

    return render_template('index.html', form=form, ret_list=[])
    '''
@main.route('/', methods=['GET'])
def index():

    return render_template('index.html')

@main.route('/changename', methods=['POST'])
def changeName():
    data = request.get_json()
    newName = data['name']
    newName, msg_ = validate_newname(newName)
    session['name'] = newName
    room = session.get('room', '')
    if room != '':
        session['joint'] = "{}.{}".format(room, session['name'])

    return json.dumps({'name':newName, 'msg':msg_})



@main.route('/changeroom', methods=['POST'])
def joinRoom():
    data = request.get_json()
    room = data['room']
    name = data['name']
    name, msg_ = validate_newname(name)
    if (name!= "") and (validate_newroom(room)):
        session['room'] = room
        session['name'] = name
        session['joint'] = "{}.{}".format(room, name)
        print(session)
        url = (url_for('.chat', room=room))
        #return redirect(url_for('.chat', room=newRoom))
        return json.dumps({'url':url,
        'msg':'Going to the room...'})

    elif (name!= "") and (validate_newroom(room)!=True):
        session['name'] = name
        return json.dumps({'msg':'Cannot go into this room. Either create a new one, or provide a valid room link.'})

    elif (name == ""):
        print('last elif block')
        return json.dumps({'msg':'You need a valid screen name to proceed'})

@main.route('/chat/<room>',  methods=['GET'])
def chat(room):

    """Chat room. The user's name and room must be stored in
    the session."""
    print(session)

    name = session.get('name', '')
    joint = session.get('joint', '')
    #Check if this roomId exists and if it's active
    #To be implemented. For now assume it's OK:
    session['room'] = room

    if name == '':
        return redirect(url_for('.index'))

    elif joint != "{}.{}".format(room, name):
        return redirect(url_for('.index'))

    else:
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
