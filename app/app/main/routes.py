from flask import session, redirect, url_for, render_template, request, current_app
from . import main
from .forms import NewMeetingForm, JoinMeetingForm, CustomRegistrationForm
import sqlite3, json, os, secrets
from .utils import record_room_create, parse_url, validate_newname,\
validate_newroom, clean_url, get_guest_stat_msg,\
handle_email_signup, check_token
from .models import *
import uuid
from flask_security.forms import RegisterForm
from flask_security.confirmable import confirm_user
from flask_security import login_user, auth_required, current_user

#from ..run_mode import env_var
'''
@main.route('/du', methods=['GET'])
def delete():
    if current_app.config['RUN_MODE'] == 'dev':
        ulist = ['royanin@gmail.com', 'anindyar@mit.edu']
        for u_email in ulist:
            try:
                u_ = user_datastore.find_user(email=u_email)
                print('Now deleting {}'.format(u_.email))
                user_datastore.delete_user(u_)
            except Exception as e:
                pass
            db.session.commit()
        return "deleting users"
    else:
        return "Happy discovery!"
'''

'''
    if not user_datastore.find_user(email="royanin@gmail.com"):
        #uid = uuid.uuid4()
        user_datastore.create_user(password=secrets.token_hex(16), confirmed_at=None,
         email="royanin@gmail.com")
        #user_datastore.create_user(email="royanin@gmail.com")
    else:
        u_ = user_datastore.find_user(email="royanin@gmail.com")
        print(u_.__dict__)
        #print(user_registered(user=u_))
        db.session.commit()
'''
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    #form = CustomRegistrationForm(request.form, meta={'csrf': False})
    form = CustomRegistrationForm(request.form)
    if request.method=='POST' and form.validate_on_submit():
        #print('form validated')
        #print(request.form)
        email = form.email.data
        coupon_code = form.coupon_code.data
        #Check if we can register this email. Send confirmation email if so etc.
        msg_ = handle_email_signup(email, coupon_code=coupon_code)
        return render_template("response_signup.html", msg=msg_)

    elif request.method=='POST' and not form.validate_on_submit():
        #print(request.form)
        #print(print('form did not validate'))
        msg_ = "Form did not validate. Please try again!"
        return render_template("signup.html", form=form, msg=msg_)

    else:
        msg_=""
        #print(print('GET request'))
        return render_template("signup.html", form=form, msg=msg_)

@main.route('/confirm_token/<token>')
def confirm_token(token):
    expired, invalid, user, data = check_token(token, return_data=True)
    if invalid:
        msg_ = "Invalid token"
        return render_template("response_signup.html", msg=msg_)

    elif expired and (not invalid):
        msg_ = "Token expired. Resend confirmation?"
        return render_template("response_signup.html", msg=msg_)

    elif (not invalid) and user:
        #confirm user and login user:
        confirm_user(user)
        db.session.commit()

        login_user(user, remember=True, authn_via=['email'])
        #user_datastore.commit()
        #db.session.commit()

        return redirect(url_for('main.index'))

    #print(expired, invalid, user, data)

    return redirect(url_for("signup"))


@main.route('/')
#@auth_required()
def index():
    if current_user.is_authenticated:
        suggested_name = (current_user.email).split('@')[0]
    else:
        suggested_name = None
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})
    return render_template('index.html', form=form, form2=form2, msg='', suggested_name=suggested_name)


#@main.route('/register', methods=['GET', 'POST'])
#def register():
    '''
    if not user_datastore.find_user(email="royanin@gmail.com"):
        #uid = uuid.uuid4()
        user_datastore.create_user(password=secrets.token_hex(16), email="royanin@gmail.com")
    db.session.commit()
    '''
    '''
    register_user_form = RegisterForm()
    if request.method=='POST':
        print(request.form)
        return render_template('/security/register_user.html', register_user_form=register_user_form)
    else:
        return render_template('/security/register_user.html', register_user_form=register_user_form)
    '''
@main.route('/new_meeting', methods=['POST'])
#@auth_required()
def new_meeting():
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})
    if form.validate_on_submit():
        name = form.name.data
        session['name'] = name
        u = uuid.uuid4()
        room = u.hex
        try:
            if current_user.is_authenticated:
                room_type=current_app.config['usertype_to_roomtype'][current_user.user_type]
            else:
                room_type='d2edu'
        except Exception as e:
            room_type='d2edu'
        room_id, ts = record_room_create(room, room_type=room_type)
        room_alive_seconds = current_app.config['room_alive_dict'][room_type]
        #store the room_id in redis, and not as a client session variable!
        current_app.redis.set('{}_id'.format(room), room_id)


        #session['room'], session['room_id'], session['room_ts'] = room, room_id, ts + room_alive_seconds
        session['room'], session['room_ts'] = room, ts + room_alive_seconds
        session['joint'] = "{}.{}".format(room, name)
        session['guest_stat'] = get_guest_stat_msg(name, room)
        return redirect(url_for('main.chat', room=room, _external = True, _scheme=os.getenv("http_scheme")))
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
        room_string = clean_url(room_url)
        return redirect(url_for('main.chat', room=room_string, _external = True, _scheme=os.getenv("http_scheme")))

    else:
        msg = "The room/name is not valid. Try again!"
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
        room_id, room_type, ts = validate_newroom(room)
        if room_id != None:
            try:
                room_alive_seconds = current_app.config['room_alive_dict'][room_type]
            except Exception as e:
                room_alive_seconds = current_app.config['room_alive_dict']['d2edu']
            session['room'], session['room_ts'] = room, ts + room_alive_seconds
            print(room_alive_seconds)
            session['joint'] = "{}.{}".format(room, session['name'])
            session['guest_stat'] = get_guest_stat_msg(session['name'], room)
            #return render_template('room.html', room=room, room_url=room_url)
            return render_template('room.html', room=room, room_url=room_url)
        else:
            msg = "Are you sure this is the correct room link? This room doesn't exist/expired/too full."
            return render_template("chooseName.html", form=form, msg=msg)
    elif request.method=='POST' and not(form.validate_on_submit()):
        msg = "That screenname didn't work. Try a boring one, e.g., star_1_blue sky?"
        return render_template("chooseName.html", form=form, msg=msg)
    elif request.method == 'GET':
        name = session.get('name', '')
        room_id, room_type, ts = validate_newroom(room)
        print(current_app.config['room_cap_dict'])
        #get the number of guests
        num_guests = len(current_app.redis.smembers('{}_occ'.format(room)))
        num_allowed_guests = current_app.config['room_cap_dict'][room_type]
        if (num_guests >= num_allowed_guests) or room_id is None:
            msg = "Are you sure this is the correct room link? This room doesn't exist/expired/too full."
            #print(num_guests, num_allowed_guests, msg)
            return render_template("response_signup.html", msg=msg)
            #return render_template("chooseName.html", form=form, msg=msg)

        elif name == "" or joint != "{}.{}".format(room, name):
            return render_template("chooseName.html", form=form, msg="Entering room {}".format(room))

        else:
            session['guest_stat'] = get_guest_stat_msg(name, room)
            #return render_template('room.html', room=room, room_url=room_url)
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
