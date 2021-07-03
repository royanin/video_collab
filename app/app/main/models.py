from flask_security.models import fsqla_v2 as fsqla
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from datetime import datetime, timezone, timedelta

db = SQLAlchemy()


class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer, nullable=False)
    room_string = db.Column(db.Text, unique=True, nullable=False)
    room_type = db.Column(db.Text, nullable=False)
    room_creator_uid = db.Column(db.BigInteger, nullable=True)
    room_state = db.Column(db.Text, nullable=True) #active, archived etc.

    def __init__(self, timestamp, room_string, room_type, room_creator_uid,
     room_state):
        self.timestamp = timestamp
        self.room_string = room_string
        self.room_type = room_type
        self.room_creator_uid = room_creator_uid
        self.room_state = room_state

    def __repr__(self):
        return '<Room {}>'.format(self.room_string)


# Define models
fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
# Define models
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    description = db.Column(db.String())

class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = "user"
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.Integer)
    fs_uniquifier = db.Column(db.Text, unique=True, nullable=False)
    user_type = db.Column(db.Text, nullable=True) #demo, early-bird, enterprise, family
    auth_route = db.Column(db.Text, nullable=True) #e.g., fb, goog, shiboleth etc.
    last_login_at = db.Column(db.DateTime, nullable=True)
    current_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.Text, nullable=True)
    current_login_ip = db.Column(db.Text, nullable=True)
    login_count = db.Column(db.Integer, nullable=True)
    preferred_nick = db.Column(db.Text, nullable=True) #default is the part before @ in email
    preferred_theme = db.Column(db.Text, nullable=True) # for now it's default, None
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('user', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.email)
"""
class UserTypeDetails(db.Model):
    __tablename__ = "userTypeDetails"
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Text, nullable=False)
    room_type = db.Column(db.Text, nullable=False)

    def __init__(self, user_type, room_type):
        self.user_type = user_type
        self.room_type = room_type

    def __repr__(self):
        return '<User_type {} creates rooms with room_type {}>'.format(self.user_type,
        self.room_type)

class RoomTypeDetails(db.Model):
    __tablename__ = "roomTypeDetails"
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.Text, nullable=False)
    room_cap = db.Column(db.Integer, nullable=True) #in persons
    room_duration = db.Column(db.Integer, nullable=True) #in seconds
    room_char_other = db.Column(db.Text, nullable=True) #None, for now


    def __init__(self, room_type, room_cap, room_duration,
    room_char_other):
        self.room_type = room_type
        self.room_cap = room_cap
        self.room_duration = room_duration
        self.room_char_other = room_char_other

    def __repr__(self):
        return '<Room_type {} has a cap of {} persons and duration {} seconds\
        >'.format(self.room_type, self.room_cap, self.room_duration)
"""
class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column('user_id', db.BigInteger, db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer, db.ForeignKey('role.id'))


class VideoLoaded(db.Model):
    __tablename__ = "videoRecords"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer)
    room_id = db.Column(db.BigInteger)
    sid = db.Column(db.Text)
    videoURL = db.Column(db.Text)
    vloader_uid = db.Column(db.BigInteger, nullable=True)


    def __init__(self, timestamp, room_id, sid, videoURL):
        self.timestamp = timestamp
        self.room_id = room_id
        self.sid = sid
        self.videoURL = videoURL
        self.vloader_uid = current_user.id if current_user.is_authenticated else None

    def __repr__(self):
        return '<videoRecords {} in room {}>'.format(self.room_id, self.videoURL)


class RoomEvents(db.Model):
    __tablename__ = "roomEvents"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer)
    room_id = db.Column(db.BigInteger)
    event_type = db.Column(db.Text) #2-character max identifier of room events
    event_details = db.Column(db.Text, nullable=True)


    def __init__(self, timestamp, room_id, event_type, event_details):
        self.timestamp = timestamp
        self.room_id = room_id
        self.event_type = event_type
        self.event_details = event_details

    def __repr__(self):
        return '<Room event logs for room {}>'.format(self.room_id)

class SubscribeList(db.Model):
    __tablename__ = "subscribeList"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer)
    email = db.Column(db.Text, nullable=False)
    sub_type = db.Column(db.Text, nullable=True) #2-character max identifier of room events

    def __init__(self, email, sub_type):
        self.timestamp = datetime.now(timezone.utc).timestamp()
        self.email = email
        self.sub_type = sub_type

    def __repr__(self):
        return '<Email {} is subscribed to sub_type {}>'.format(self.email, self.sub_type)

class CouponCodeDetails(db.Model):
    __tablename__ = "couponCodeDetails"
    id = db.Column(db.BigInteger, primary_key=True)
    coupon_code = db.Column(db.Text, nullable=False, unique=True)
    user_type = db.Column(db.Text, nullable=False)
    if_valid = db.Column(db.Boolean, nullable=True)
    expires_on = db.Column(db.Integer, nullable=True)

    def __init__(self, coupon_code, user_type, expires_on):
        self.coupon_code = coupon_code
        self.user_type = user_type
        self.if_valid = if_valid
        self.expires_on = expires_on


    def __repr__(self):
        return '<Coupon code {} generates user_type {}>'.format(self.coupon_code, self.user_type)

class CouponUsed(db.Model):
    __tablename__ = "couponUsed"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer)
    email = db.Column(db.Text, nullable=False)
    coupon_code = db.Column(db.Text, nullable=False) #2-character max identifier of room events

    def __init__(self, email, coupon_code):
        self.timestamp = datetime.now(timezone.utc).timestamp()
        self.email = email
        self.coupon_code = coupon_code

    def __repr__(self):
        return '<Email {} has signed up with coupon code {}>'.format(self.email, self.coupon_code)


class ExpressInterest(db.Model):
    __tablename__ = "expressInterest"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer)
    email = db.Column(db.Text, nullable=False)
    other_details = db.Column(db.Text, nullable=True)

    def __init__(self, email, other_details):
        self.timestamp = datetime.now(timezone.utc).timestamp()
        self.email = email
        self.other_details = other_details

    def __repr__(self):
        return '<Eoi for email: {}>'.format(self.email)


class BouncedEmailList(db.Model):
    __tablename__ = "bouncedEmailList"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer) #when bounced first
    email = db.Column(db.Text, nullable=False)

    def __init__(self, email):
        self.timestamp = datetime.now(timezone.utc).timestamp()
        self.email = email

    def __repr__(self):
        return '<Bounced email: {}>'.format(self.email)

class LastEmailRecord(db.Model):
    __tablename__ = "lastEmailRecord"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer)
    email = db.Column(db.Text, nullable=False)
    last_email_reason = db.Column(db.Text, nullable=True)
    num_emails_total = db.Column(db.Integer, nullable=False)

    def __init__(self, email, last_email_reason, num_emails_total):
        self.timestamp = datetime.now(timezone.utc).timestamp()
        self.email = email
        self.last_email_reason = last_email_reason
        self.num_emails_total = num_emails_total

    def __repr__(self):
        return '<email sent to {} for {}>'.format(self.email, self.email_reason)


class CurrentUserRoomList(db.Model):
    __tablename__ = "currentUserRoomList"
    id = db.Column(db.BigInteger, primary_key=True)
    timestamp = db.Column(db.Integer) #when a user signs in to a room
    room_string = db.Column(db.Text, nullable=False)
    user_string = db.Column(db.Text, nullable=False) #either the email, or the sid
    if_user_auth = db.Column(db.Boolean, nullable=True) #if user is authenticated or guest

    def __init__(self, room_string, user_string, if_user_auth):
        self.timestamp = datetime.now(timezone.utc).timestamp()
        self.room_string = room_string
        self.user_string = user_string
        self.if_user_auth = if_user_auth

    def __repr__(self):
        return '<user {} joined room {}>'.format(self.user_string, self.room_string)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
