from flask import session, redirect, url_for, render_template, request, current_app
from . import main
from .forms import LoginForm
#from .utils import read_chat, write_chat
import sqlite3, json
from .utils import record_room_create, read_room_create, parse_url, validate_newname, validate_newroom
import uuid


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/createroom', methods=['POST'])
def createRoom():
    data = request.get_json()
    #room = data['room']
    name = data['name']
    name, msg_ = validate_newname(name)
    if (name!= ""):
        session['name'] = name
        u = uuid.uuid4()
        room = u.hex
        session['room'] = room
        record_room_create(room)
        session['joint'] = "{}.{}".format(room, name)
        session['msg'] = 'Success!'
        url = (url_for('.chat', room=room))
        return json.dumps({'url':url,
        'msg': session['msg']
        })

    elif (name == ""):
        #return json.dumps({'msg':'You need a valid screen name to proceed'})
        print("not a good name")
        session['name'] = ""
        session['room'] = ""
        session['joint'] = ""

        #url = (url_for('.index'))
        session['msg'] = 'You need a valid screen name to proceed'
        return json.dumps({
        'msg': session['msg']
        })


@main.route('/gotoroom', methods=['POST'])
def joinRoom():
    print("in join room function")
    data = request.get_json()
    room = data['room']
    name = data['name']
    print('joining a room:',room, name, session)
    name, msg_ = validate_newname(name)
    print('joining a room:',name, msg_)
    if (name!= "") and (validate_newroom(room) is True):
        session['room'] = room
        session['name'] = name
        session['joint'] = "{}.{}".format(room, name)
        print(session)
        session['msg'] = 'Success!'
        url = (url_for('.chat', room=room))
        #return redirect(url_for('.chat', room=newRoom))
        return json.dumps({'url':url,
        'msg':  session['msg']
        })

    elif (name!= "") and (validate_newroom(room) is False):
        session['name'] = name
        print("bad room name")
        session['msg'] = 'Cannot go into this room. Either create a new one, or provide a valid room link.'
        return json.dumps({
        'msg': session['msg']
        })

    elif (name == ""):
        print('last elif block')
        session['name'] = ""
        print("bad name")
        session['msg'] = 'You need a valid screen name to proceed'
        return json.dumps({'msg': session['msg']
        })

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
    print(session)
    if name == '':
        return render_template("chooseName.html")

    elif joint != "{}.{}".format(room, name):
        return render_template("chooseName.html")

    else:
        return render_template('room.html', room=room)


@main.route('/editor/<room>',  methods=['GET'])
def editor(room):

    """Chat room. The user's name and room must be stored in
    the session."""
    print(session)

    name = session.get('name', '')
    joint = session.get('joint', '')
    #Check if this roomId exists and if it's active
    #To be implemented. For now assume it's OK:
    session['room'] = room
    print(session)
    if name == '':
        return render_template("chooseName.html")

    elif joint != "{}.{}".format(room, name):
        return render_template("chooseName.html")

    else:
        return render_template('editor.html', room=room)

@main.route('/newvideourl', methods=['POST'])
def getURL():
    data = request.get_json()
    url_input = data['url']
    print('url_input:',url_input)
    url_type, url_key = parse_url(url_input)
    print('parsed_url:', url_type, url_key)
    if url_type != None and url_key != None:
        return json.dumps({'type':url_type, 'key':url_key})

    else:
        return json.dumps({'type':"", 'key':""})
