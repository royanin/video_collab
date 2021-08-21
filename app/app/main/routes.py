from flask import session, redirect, url_for, render_template, request, current_app,\
flash, Markup
import traceback
from . import main
from .forms import NewMeetingForm, JoinMeetingForm, CustomRegistrationForm,CustomLoginForm,\
CustomConfirmForm
from .emails import send_email
import sqlite3, json, os, secrets, random
from .utils import record_room_create, parse_url, validate_newname,\
validate_newroom, clean_url, get_guest_stat_msg,\
handle_email_checkin, check_token, record_current_room_user,\
remove_current_room_user, change_user_nickname, get_room_alive_seconds,\
get_room_cap, record_video_loading
from .models import *
import uuid
from flask_security.forms import RegisterForm
#from flask_security.confirmable import confirm_user
from flask_security import login_user, auth_required, current_user
from werkzeug.exceptions import InternalServerError

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

class BigException(Exception):
    pass

@main.route('/simulate_error', methods=['GET'])
def make_error():
    raise BigException("Something bad happened here..")
    return "Welcome to error simulation!"
'''
@main.errorhandler(404)
def not_found_error(e):
    #print('in 404 error handler')
    flash(Markup("Oops! The requested page does not exist. <a class=brand-link href=")\
    +url_for('main.index')+Markup(">Go somewhere nice instead.</a>"))
    return render_template('response.html'), 404

@main.errorhandler(InternalServerError)
def handle_500(e):
    db.session.rollback()
    #print('in error_handler')
    error_stacktrace = traceback.format_exc()
    #print(error_stacktrace)
    try:
        from_email = current_app.config['notif_email']
        to_email = current_app.config['MAIL_SENDER'] #goes to hello@zipsync.us
        email_sub = "ZipSync Server error"
        resp = send_email(from_email, to_email, email_sub, error_stacktrace)
    except Exception as exc:
        #print(exc.message)
        pass
    #return current_app.finalize_request(e, from_error_handler=True)
    flash(Markup("Oops! Something went wrong. <a class=brand-link href=")\
    +url_for('main.index')+Markup(">Go somewhere nice instead.</a>"))
    return render_template('response.html'), 500

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    form = CustomLoginForm(request.form)
    if request.method=='POST' and form.validate_on_submit():
        email = form.email.data
        #Check if we can register this email. Send confirmation email if so etc.
        msg_ = handle_email_checkin(email, coupon_code=None)
        return render_template("response.html", msg=msg_)

    elif request.method=='POST' and not form.validate_on_submit():
        error = "Form did not validate. Please try again!"
        return render_template("login.html", form=form, error=error)

    else:
        if current_user.is_authenticated:
            flash("You are already logged in!")
            return redirect(url_for('main.index'))
        #print(print('GET request'))
        return render_template("login.html", form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = CustomRegistrationForm(request.form)
    if request.method=='POST' and form.validate_on_submit():
        email = form.email.data
        coupon_code = form.coupon_code.data
        #Check if we can register this email. Send confirmation email if so etc.
        msg_ = handle_email_checkin(email, coupon_code=coupon_code)
        return render_template("response.html", msg=msg_)

    elif request.method=='POST' and not form.validate_on_submit():
        error = "Form did not validate. Please try again!"
        return render_template("signup.html", form=form, error=error)

    else:
        if current_user.is_authenticated and current_user.confirmed_at!=None:
            flash("You are already logged in!")
            return redirect(url_for('main.index'))
        return render_template("signup.html", form=form)

@main.route('/confirm_token/<token>')
def confirm_token(token):
    expired, invalid, user, data = check_token(token, return_data=True)
    if invalid:
        flash("Invalid token")
        return render_template("response.html")

    elif expired and (not invalid):
        flash("Token expired. Resend link?")
        return render_template("response.html")

    elif (not invalid) and user:
        #confirm user and login user:
        db.session.commit()
        login_user(user, remember=True, authn_via=['email'])
        flash("Token confirmed. You are signed in.")
        return redirect(url_for('main.index'))

    #print(expired, invalid, user, data)

    return redirect(url_for("signup"))


@main.route('/')
#@auth_required()
def index():
    if current_user.is_authenticated:
        suggested_name = current_user.preferred_nick
    else:
        suggested_name = "user{}".format(random.randint(100, 999))
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})
    return render_template('index.html', form=form, form2=form2, msg='', suggested_name=suggested_name)

@main.route('/new_meeting', methods=['POST'])
#@auth_required()
def new_meeting():
    form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})
    if form.validate_on_submit():
        name = form.name.data
        session['name'] = name

        if not current_user.is_authenticated:
            #room_type='d2edu'
            flash("You need an account before you can create a room")
            return redirect(url_for("signup")) #redirect user to sign up before creating room

        elif current_user.is_authenticated:
            #room_type=current_app.config['usertype_to_roomtype'][current_user.user_type]
            if name != current_user.preferred_nick:
                if validate_newname(name):
                    change_user_nickname(name)
                else:
                    flash("A screen name can have letters and numbers only; 4-15 characters long")
                    return render_template("index.html", form=form,  form2=form2)
            #now we can create a room
            u = uuid.uuid4()
            room = u.hex
            room_type = current_app.config['usertype_to_roomtype'][current_user.user_type]
            room_alive_seconds = get_room_alive_seconds(room_type)

            room_id, ts = record_room_create(room_string = room,
                            room_type = room_type,
                            room_creator_uid = current_user.id)

            current_app.redis.set('{}_id'.format(room), room_id)

            session['room'], session['room_ts'] = room, ts + room_alive_seconds
            session['joint'] = "{}.{}".format(room, name)
            session['guest_stat'] = get_guest_stat_msg(name, room)
            return redirect(url_for('main.chat', room=room, _external = True, _scheme=os.getenv("http_scheme")))
    else:
        flash("Something went wrong. Try again?")
        return render_template("index.html", form=form,  form2=form2)


@main.route('/join_meeting', methods=['POST'])
def join_meeting():
    #form = NewMeetingForm(request.form, meta={'csrf': False})
    form2 = JoinMeetingForm(request.form, meta={'csrf': False})

    if form2.validate_on_submit():
        name = form2.name_join_room.data
        session['name'] = name
        room_url = form2.url.data
        #just extract the room id:
        room_string = clean_url(room_url)
        return redirect(url_for('main.chat', room=room_string, _external = True, _scheme=os.getenv("http_scheme")))

    else:
        flash("The room/name is not valid. Try again!")
        return redirect(url_for('main.index'))
        #return render_template("index.html", form=form,  form2=form2, msg=msg)


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
            room_alive_seconds = get_room_alive_seconds(room_type)
            session['room'], session['room_ts'] = room, ts + room_alive_seconds
            session['joint'] = "{}.{}".format(room, session['name'])
            session['guest_stat'] = get_guest_stat_msg(session['name'], room)
            return render_template('room.html', room=room, room_url=room_url)
        else:
            #bad room id
            flash("Please check the room link. This room doesn't exist/expired/too full.")
            return redirect(url_for('main.index'))
    elif request.method=='POST' and not(form.validate_on_submit()):
        msg = "That screenname didn't work. Try a boring one, e.g., user01?"
        #change: return redirect to /chat/<room> instead?
        return render_template("chooseName.html", form=form, msg=msg)
    elif request.method == 'GET':
        if current_user.is_authenticated:
            name = current_user.preferred_nick
        else:
            name = session.get('name', '')

        room_id, room_type, ts = validate_newroom(room)
        #get the number of guests
        num_guests = len(current_app.redis.smembers('{}_occ'.format(room)))
        num_allowed_guests = get_room_cap(room_type)

        if (num_guests >= num_allowed_guests) or room_id is None:
            flash("Please check the room link. This room doesn't exist/expired/too full.")
            return redirect(url_for('main.index'))

        elif name == "" or joint != "{}.{}".format(room, name):
            #change: return redirect to /chat/<room> instead?
            return render_template("chooseName.html", form=form, msg="Entering room {}".format(room))

        else:
            session['guest_stat'] = get_guest_stat_msg(name, room)
            return render_template('room.html', room=room, room_url=room_url)


@main.route('/editor/<room>',  methods=['GET'])
def editor(room):

    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    joint = session.get('joint', '')
    #Check if this roomId exists and if it's active
    #To be implemented. For now assume it's OK:
    session['room'] = room
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

    url_type, url_key = parse_url(url_input)
    print('parsed_url:', url_type, url_key)
    if url_type != None and url_key != None:
        vid_dict = {'type':url_type, 'key':url_key}
        record_video_loading("{}_:_{}".format(url_type, url_key))
        return json.dumps(vid_dict)

    else:
        return json.dumps({'type':"", 'key':""})
