from flask_security.models import fsqla_v2 as fsqla
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
#from sqlalchemy.ext.hybrid import hybrid_property
#from ..run_mode import room_string_length

db = SQLAlchemy()

# Setup Flask-Security
#security = Security(current_app, user_datastore)


class Room(db.Model):
    __tablename__ = "roomCreate"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer, nullable=False)
    room_string = db.Column(db.Text, unique=True, nullable=False)
    room_type = db.Column(db.Text, nullable=True)
    room_creator_uid = db.Column(db.Integer, nullable=True)
    room_state = db.Column(db.Text, nullable=True) #active, archived etc.

    def __init__(self, timestamp, room_string, room_type, room_creator_uid, room_state):
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
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)
    description = db.Column(db.String())

class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.Text, unique=True, nullable=False)
    user_type = db.Column(db.Text, nullable=True) #demo, early-bird, enterprise, family
    auth_route = db.Column(db.Text, nullable=True) #e.g., fb, goog, shiboleth etc.
    last_login_at = db.Column(db.DateTime, nullable=True)
    current_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.Text, nullable=True)
    current_login_ip = db.Column(db.Text, nullable=True)
    login_count = db.Column(db.Integer, nullable=True)
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('user', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.email)

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))



class CurrentUser(db.Model):
    __tablename__ = "currentUsers"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer)
    sid = db.Column(db.Text)
    screenName = db.Column(db.Text)

    def __init__(self, room_id, sid, screenName):
    #No need to collect screenName, right?
    #def __init__(self, room_id, sid):
        self.room_id = room_id
        self.sid = sid
        self.screenName = screenName

    def __repr__(self):
        return '<CurrentUser {} in room {}>'.format(self.sid, self.room_id)


class VideoLoaded(db.Model):
    __tablename__ = "videoRecords"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    room_id = db.Column(db.Integer)
    sid = db.Column(db.Text)
    videoURL = db.Column(db.Text)
    vloader_uid = db.Column(db.Integer, nullable=True)


    def __init__(self, timestamp, room_id, sid, videoURL):
        self.timestamp = timestamp
        self.room_id = room_id
        self.sid = sid
        self.videoURL = videoURL
        self.vloader_uid = vloader_uid

    def __repr__(self):
        return '<videoRecords {} in room {}>'.format(self.room_id, self.videoURL)


class RoomEvents(db.Model):
    __tablename__ = "roomEvents"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    room_id = db.Column(db.Integer)
    event_type = db.Column(db.Text) #2-character max identifier of room events
    event_details = db.Column(db.Text, nullable=True)


    def __init__(self, timestamp, room_id, event_type, event_details):
        self.timestamp = timestamp
        self.room_id = room_id
        self.event_type = event_type
        self.event_details = event_details

    def __repr__(self):
        return '<Room event logs for room {}>'.format(self.room_id)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
