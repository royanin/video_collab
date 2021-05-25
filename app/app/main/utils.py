import sqlite3, json, secrets, hashlib, uuid, bcrypt
from datetime import datetime, timezone, timedelta
import random, string
from urllib.parse import urlparse, parse_qs
from flask import session, current_app, url_for, flash
#from .models import db, Room, CurrentUser, RoomEvents
from .models import *
from .emails import send_email
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.local import LocalProxy
from flask_security import current_user

srlzr = LocalProxy(lambda: current_app.config['srlzr'])

'''
def write_chat(conn, ts, room_id, username, text):
    c = conn.cursor()
    sql_ = """INSERT INTO chat (timestamp, room_id, username, text)
     VALUES (?,?,?,?)"""
    c.execute(sql_, (ts, room_id, username, text))
    conn.commit()
    c.close()

    return ()

def read_chat(conn, room_id, limit_=25, timestamp_=datetime.now(timezone.utc).timestamp()):
    c = conn.cursor()
    #get chats for a room
    sql_ = """SELECT * FROM chat WHERE room_id='{}' AND timestamp < {}
    ORDER BY timestamp DESC LIMIT {}""".format(room_id, timestamp_, limit_)
    print(sql_)
    c.execute(sql_)
    ret_list = []
    ret_list = c.fetchall()
    if len(ret_list)>0:
        ret_list_json = [{'who': item[2],'when':item[0],
                        'msg':item[3]} for item in ret_list ]
    else:
        ret_list_json = []
    c.close()

    return (ret_list_json)

'''

'''def parse_url(url_input):
    if url_input != None:
        return ("yt", "-Qr8QrMG3CQ")

    else:
        return (None, None)
'''
def hash_salt_encode(phrase, kind):
    '''
    phrase: a plaintext password or an email id
    kind: "password" or "email"
    '''
    #salted_encoded_phrase = (phrase + current_app.config['SECURITY_PASSWORD_SALT']).encode("utf8")
    #return bcrypt.hashpw(hashlib.sha512(salted_encoded_phrase).hexdigest())
    if kind == "password":
        return bcrypt.hashpw(phrase.encode("utf8"), bcrypt.gensalt())
    elif kind == "email":
        salted_encoded_phrase = (phrase + current_app.config['SECURITY_PASSWORD_SALT']).encode("utf8")
        return hashlib.sha512(salted_encoded_phrase).hexdigest()

def generate_token(email, fs_uq):
    return srlzr.dumps([str(fs_uq), hash_salt_encode(email, kind="email")], salt=current_app.config['SECURITY_PASSWORD_SALT'])

def check_token(token, max_age=None, return_data=False):
    #srlzr = current_app.config['srlzr']
    time_window = (current_app.config['CONFIRM_EMAIL_WITHIN']).split()
    td = timedelta(**{time_window[1]: int(time_window[0])}) # x units, e.g., 10 minutes
    max_age = td.seconds + td.days * 24 * 3600
    user, data = None, None
    expired, invalid = False, False

    try:
        data = srlzr.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=max_age)
    except SignatureExpired:
        d, data = srlzr.loads_unsafe(token)
        expired = True
    except (BadSignature, TypeError, ValueError):
        invalid = True

    if data:
        print('in utils: data from token:', data)
        user = user_datastore.find_user(fs_uniquifier=data[0])
        if user.confirmed_at == None:
            user.confirmed_at = datetime.now(timezone.utc).timestamp()

    expired = expired and (user is not None)

    if return_data:
        return expired, invalid, user, data
    else:
        return expired, invalid, user

def ret_msg(response, msg_success, msg_failure, default_success="success"):
    if response == default_success:
        return msg_success
    else:
        return msg_failure



def send_link(email, fs_uq, link_type_msg):
    #first check if the user exists,
    #then send an email (or not) with the same message
    #"A confirmation email has been sent if the user is registered"

    if not check_last_email_within(email, ts_period=300):
        #check if user is confirmed
        token = generate_token(email, fs_uq)
        link = url_for("main.confirm_token", token=token, _external=True)
        print('link:', link)
        print('token:', token)
        response = send_email(current_app.config['accounts_email'], email, link_type_msg, link)

        if response=="success":
            flash("Check your email for a magic link to log in")
            record_last_email_sent(email, 'ml') #ml: magic_link
        else:
            flash("Oops. This is unexpected. Please try again in a bit.")

    else:
        flash("Sometimes it takes a while for the emails to reach. Also, check your spam folder!")

    return

def check_email_eligible(email, coupon_code=None):
    email_tld = email.split(".")[-1]
    email_domain = email.split("@")[-1]

    if (coupon_code):
        if (db.session.query(CouponCodeDetails.id).filter_by(coupon_code=coupon_code).first()):
            cc = db.session.query(CouponCodeDetails).filter_by(coupon_code=coupon_code).first()
            if (cc.if_valid):
                store_coupon_code(email,  coupon_code = coupon_code) #store the coupon code
                return True, cc.user_type
            else:
                return False, None
        else:
            return False, None
    elif email_tld in ['edu']:
        return True, 'd2edu'
    else:
        return False, None

def store_eoi_email(email, other_details=None):
    '''Emails for those who want to join'''
    #check if email exists; else add:
    eoi_email = ExpressInterest(email, other_details)
    db.session.add(eoi_email)
    db.session.commit()

def store_sub_email(email, sub_type=None):
    '''Emails for those who subscribed to email list. This is for test.
    Disable it before actual email blasts.'''
    sub_email = SubscribeList(email, sub_type)
    db.session.add(sub_email)
    db.session.commit()

def store_coupon_code(email, coupon_code):
    '''Emails for those who used a coupon code to join'''
    cc = CouponUsed(email, coupon_code = coupon_code)
    db.session.add(cc)
    db.session.commit()


def handle_email_checkin(email, coupon_code=None):
    #This is unified signin/signup module
    #0. Check if the email is allowed:
    print('email supplied:', email)
    #for whatever reason, the user is already registered, but may or may not be confirmed:
    u_ = user_datastore.find_user(email=email)
    if (u_):
        fs_uq = u_.fs_uniquifier
        link_type_msg = "Check your email for a magic link to sign in."
        msg_outcome = send_link(email, fs_uq, link_type_msg=link_type_msg)
        return msg_outcome

    elif not user_datastore.find_user(email=email):
        user_eligible, user_type = check_email_eligible(email, coupon_code=coupon_code)
        if  user_eligible == False:
            #reject -- store the emails and date etc.
            if db.session.query(ExpressInterest.id).filter_by(email=email).first() is None:
                store_eoi_email(email, other_details=None)
            flash("Thank you for your interest! We will email you when ZipSync is ready for more users.")
            if db.session.query(SubscribeList.id).filter_by(email=email).first() is None:
                store_sub_email(email, sub_type=None)
            #return "Sorry, ZipSync is not yet ready for you. We'll email you soon!"
            return
        else:
            #register unconfirmed user
            password = secrets.token_hex(16)
            hashed_password = hash_salt_encode(password, kind="password")
            fs_uq = uuid.uuid4().hex
            preferred_nick=email.split("@")[0]
            user_datastore.create_user(password=hashed_password, confirmed_at=None,
                email=email, fs_uniquifier=fs_uq, user_type=user_type,
                preferred_nick=preferred_nick)
            db.session.commit()

            #resend confirmation email
            link_type_msg = "Check your email to confirm your account and sign in."
            msg_outcome = send_link(email, fs_uq, link_type_msg=link_type_msg)
            return msg_outcome


def get_current_users_in_room(room_url):
    #returns (num_guests, ulist)
    try:
        occ_set = set(current_app.redis.smembers('{}_occ'.format(room_url)))
        ulist = [ str(u, 'utf-8') for u in occ_set ]
        print('from utils. ulist:', ulist)
        return len(occ_set), ulist
    except Exception as e:
        return 0, []


def get_guest_stat_msg(name, room_url):
    num_guests, ulist = get_current_users_in_room(room_url)
    if name not in ulist:
        num_guests += 1
        ulist.append(name)
    if num_guests==1:
        guest_stat_msg = "You are the only one in the room"
    else:
        guest_string_ = (", ".join(ulist))
        if len(guest_string_)>30:
            guest_string = guest_string_[:30]+'...'
        else:
            guest_string = guest_string_
        guest_stat_msg ='{} guests: {}'.format(num_guests, guest_string)

    return guest_stat_msg

def record_room_create(room_string, room_type, room_creator_uid = None,
                        room_state = 'a'):
    #room_type: 'd2' is demo for 2, 'da' -> demo for any, 'd2edu30': demo for edu with 30 min. time limit
    #room_state: 'a' for active; could be inactive, read-only, secure etc. etc.
    ts = datetime.now(timezone.utc).timestamp()

    #room_creator_uid = current_user.id
    #room_type = current_app['usertype_to_roomtype'][current_user.user_type]
    new_room = Room(timestamp=ts, room_string=room_string, room_type=room_type,
                        room_creator_uid = room_creator_uid, room_state = room_state)

    db.session.add(new_room)
    db.session.commit()
    return new_room.id, ts

def get_user_string_auth_stat():
    if current_user.is_authenticated:
        user_string = current_user.email
        if_user_auth = True
    else:
        user_string = session.get('sid')
        if_user_auth = False

    return user_string, if_user_auth

def get_room_alive_seconds(room_type):
    return current_app.config['room_type_details'][room_type]['room_duration']

def get_room_cap(room_type):
    return current_app.config['room_type_details'][room_type]['room_cap']


def record_current_room_user(room_string):
    #this function will record when a new user joins a room,
    #this row will be removed when the user leaves the room or the room expires
    user_string, if_user_auth = get_user_string_auth_stat()
    print('in record_current_room_user\n')
    print(user_string, if_user_auth)
    if (db.session.query(CurrentUserRoomList).filter(CurrentUserRoomList.room_string==room_string).\
        filter(CurrentUserRoomList.user_string==user_string).first() is None):
        current_room_user = CurrentUserRoomList(room_string, user_string, if_user_auth)
        db.session.add(current_room_user)
        db.session.commit()

def remove_current_room_user(room_string):
    user_string, if_user_auth = get_user_string_auth_stat()
    print('in remove_current_room_user\n')
    print(user_string, if_user_auth)
    (db.session.query(CurrentUserRoomList).filter(CurrentUserRoomList.room_string==room_string).\
        filter(CurrentUserRoomList.user_string==user_string).delete())
    '''
    try:
        (db.session.query(CurrentUserRoomList).filter(CurrentUserRoomList.room_string==room_string).\
            filter(CurrentUserRoomList.user_string==user_string).first()).delete()
        db.session.commit()
    except:
        pass
    '''


def check_last_email_within(email, ts_period=300): #if emails sent within last 300 seconds
    time_now = datetime.now(timezone.utc).timestamp()
    if (db.session.query(LastEmailRecord).filter(LastEmailRecord.email==email).\
            filter(LastEmailRecord.timestamp>time_now-ts_period).first() is not None):
        return True
    else:
        return False

def record_last_email_sent(email, reason):
    last_email = db.session.query(LastEmailRecord).filter_by(email=email).first()
    if not last_email:
        num_emails_total=1
        last_email = LastEmailRecord(email=email, last_email_reason=reason,
                            num_emails_total=num_emails_total)
        db.session.add(last_email)

    else:
        print(last_email.id, last_email.email, last_email.timestamp, last_email.num_emails_total)
        last_email.timestamp = datetime.now(timezone.utc).timestamp()
        last_email.email_reason=reason
        last_email.num_emails_total += 1

    db.session.commit()


def record_event(room, event_type, event_details=None):
    '''
    dictionary for event_type, event_details
    'rc': 'room created',
    'uj':'user joined', 'sid'
    'ul':'user left', 'sid'
    'tc':'text sent', 'sid'
    'vl':'video chat launched', 'sid'
    'vd':'video chat dismissed', 'sid'
    'es':'editor toggle', 'sid'
    'wl':'online video loaded',
    'wp':'watching paused', 'timstamp'
    'ws':'watching started/resumed', 'timstamp'
    'wf':'watching speed changed', 'new speed'
    'wh':'watching on hold', 'timestamp' #video play state other than 1 or 2
    'ep':'emoji panel toggled', 'sid'
    'et':'editor timestamp insert used', 'sid'
    'en':'editor username insert used', 'sid'
    'qs':'quick start clicked', 'sid'
    '''
    #This is a temporary implementation -- should be written with a buffer?
    ts = datetime.now(timezone.utc).timestamp()

    #Get the room_id from redis:
    room_id = int(current_app.redis.get('{}_id'.format(room)))
    new_event = RoomEvents(timestamp=ts, room_id = room_id,
                        event_type = event_type, event_details = event_details)
    db.session.add(new_event)
    db.session.commit()
    return ()


def parse_url(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        #Youtube:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

        #Panopto:
        'xyz.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=abd...'
        'https://xyz.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=401da229-c9a6-49e4-aeab-ab91015553f6'

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """


    #if url.startswith(('youtu', 'www')):
    #    url = 'http://' + url
    if not url.startswith(("http://", "https://")):
        url = "http://"+url


    if url != "http://":
        query = urlparse(url)
    try:
        if 'youtube' in query.hostname:
            if query.path == '/watch':
                return ("yt", parse_qs(query.query)['v'][0])
            elif query.path.startswith(('/embed/', '/v/')):
                return ("yt", query.path.split('/')[2])
        elif 'youtu.be' in query.hostname:
            return ("yt", query.path[1:])
        elif 'hosted.panopto.com' in query.hostname:
            return ("pt", (query.netloc, parse_qs(query.query)['id'][0]))
        else:
            raise ValueError
    except Exception as e:
        return None, None

def clean_url(room_url):
    if room_url[-1]=='/':
        room_url.rstrip('/')
    room_string = room_url.split("/")[-1]
    return room_string
    '''
    room = Room.query.filter_by(room_string=room_string).first()
    if room != None:
        return room.room_string, room.id, room.room_type, room.timestamp
    else:
        return None, None
    '''

def change_user_nickname(name):
    current_user.preferred_nick=name
    db.session.add(current_user)
    db.session.commit()
    flash("Name change successful.")
    return

def validate_newname(name):

    if len(name)>=4 and len(name)<=15 and name.isalnum():
        return True
    else:
        return False

def validate_newroom(room_string):
    #time_window = 600 for certain room type?
    room = Room.query.filter_by(room_string=room_string).first()
    if room != None:
        return room.id, room.room_type, room.timestamp
    else:
        return None, None, None
