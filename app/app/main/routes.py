from flask import session, redirect, url_for, render_template, request, current_app
from . import main
from .forms import NameForm
#from .utils import read_chat, write_chat
import sqlite3, json
from .utils import record_room_create, read_room_create, parse_url, validate_newname, validate_newroom
import uuid


@main.route('/', methods=['GET','POST'])
def index():
    form = NameForm(request.form, meta={'csrf': False})
    if form.validate_on_submit():
        name = form.name.data
        session['name'] = name
        u = uuid.uuid4()
        room = u.hex
        session['room'] = room
        record_room_create(room)
        session['joint'] = "{}.{}".format(room, name)
        return redirect(url_for('main.chat', room=room))
    elif request.method=='POST' and not(form.validate_on_submit()):
        msg = "That screenname didn't work. Try a boring one, e.g., star_1_blue sky?"
        return render_template("index.html", form=form, msg=msg)

    elif request.method == 'GET':
        return render_template('index.html', form=form, msg='')



@main.route('/chat/<room>',  methods=['GET','POST'])
def chat(room):

    """Chat room. The user's name and room must be stored in
    the session."""
    form = NameForm(request.form, meta={'csrf': False})
    #Check if this roomId exists and if it's active
    #To be implemented. For now assume it's OK:
    joint = session.get('joint', '')
    session['room'] = room
    if request.method=='POST' and form.validate_on_submit():
        session['name'] = form.name.data
        if validate_newroom(room) is True:
            session['joint'] = "{}.{}".format(room, session['name'])
            return render_template('room.html', room=room)
        else:
            msg = "Are you sure this is the correct room link? This room doesn't exist or not accessible."
            return render_template("chooseName.html", form=form, msg=msg)
    elif request.method=='POST' and not(form.validate_on_submit()):
        msg = "That screenname didn't work. Try a boring one, e.g., star_1_blue sky?"
        return render_template("chooseName.html", form=form, msg=msg)
    elif request.method == 'GET':
        name = session.get('name', '')
        if name == "" or joint != "{}.{}".format(room, name) or validate_newroom(room) is False:
            return render_template("chooseName.html", form=form, msg="Entering room {}".format(room))

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
