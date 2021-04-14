from flask_sqlalchemy import SQLAlchemy
#from ..run_mode import room_string_length

db = SQLAlchemy()

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


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    time_joined = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.Text, unique=True, nullable=False)
    user_type = db.Column(db.Text, nullable=True) #demo, early-bird, enterprise, family
    auth_route = db.Column(db.Text, nullable=True) #e.g., fb, goog, shiboleth etc.
    last_login =  db.Column(db.Integer, nullable=True)


    def __init__(self, time_joined, email, user_type, auth_route, last_login):
        self.time_joined = time_joined
        self.user_email = user_email
        self.user_type = user_type
        self.auth_route = auth_route
        self.last_login = last_login

    def __repr__(self):
        return '<User {}>'.format(self.email)

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
