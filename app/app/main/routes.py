from flask import session, redirect, url_for, render_template, request, current_app
from . import main
from .forms import NewMeetingForm, JoinMeetingForm
import sqlite3, json
from .utils import record_room_create, read_room_create, parse_url, validate_newname,\
validate_newroom, get_room_id_from_submitted_url, get_guest_stat_msg
from .models import db, Room, CurrentUser
import uuid
from ..run_mode import env_var


@main.route('/')
def index():
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})
    return render_template('index.html', form=form, form2=form2, msg='')

@main.route('/new_meeting', methods=['POST'])
def new_meeting():
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})
    if form.validate_on_submit():
        name = form.name.data
        session['name'] = name
        u = uuid.uuid4()
        room = u.hex
        session['room'] = room
        record_room_create(room)
        session['joint'] = "{}.{}".format(room, name)
        session['guest_stat'] = get_guest_stat_msg(name, room)
        return redirect(url_for('main.chat', room=room, _external = True, _scheme=env_var['http_scheme']))
    else:
        msg = "That screenname didn't work. Try a boring one, e.g., star_1_blue sky?"
        return render_template("index.html", form=form,  form2=form2, msg=msg)


@main.route('/join_meeting', methods=['POST'])
def join_meeting():
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})

    if form2.validate_on_submit():
        name = form2.name_join_room.data
        session['name'] = name
        room_url = form2.url.data
        #just extract the room id:
        room_id = get_room_id_from_submitted_url(room_url)
        session['room'] = room_id
        if validate_newroom(room_id) is True:
            session['joint'] = "{}.{}".format(room_id, name)
            session['guest_stat'] = get_guest_stat_msg(name, room_id)
            return redirect(url_for('main.chat', room=room_id, _external = True, _scheme=env_var['http_scheme']))
        else:
            msg = "The room link is not valid. Try again!"
            #return redirect(url_for('main.index'))
            return render_template("index.html", form=form,  form2=form2, msg=msg)

    else:
        msg = "The room/name is not valid. Try again!"
        #return redirect(url_for('main.index'))
        return render_template("index.html", form=form,  form2=form2, msg=msg)



@main.route('/chat/<room>',  methods=['GET','POST'])
def chat(room):

    """Chat room. The user's name and room must be stored in
    the session."""
    room_url = request.url
    form = NewMeetingForm(request.form, meta={'csrf': False})
    #Check if this roomId exists and if it's active
    #To be implemented. For now assume it's OK:
    joint = session.get('joint', '')
    session['room'] = room
    if request.method=='POST' and form.validate_on_submit():
        session['name'] = form.name.data
        if validate_newroom(room) is True:
            session['joint'] = "{}.{}".format(room, session['name'])
            session['guest_stat'] = get_guest_stat_msg(session['name'], room)
            return render_template('room.html', room=room, room_url=room_url)
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
            session['guest_stat'] = get_guest_stat_msg(name, room)
            return render_template('room.html', room=room, room_url=room_url)


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
