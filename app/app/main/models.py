from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Room(db.Model):
    __tablename__ = "roomCreate"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float())
    room_id = db.Column(db.String(32), unique=True)

    def __init__(self, timestamp, room_id):
        self.timestamp = timestamp
        self.room_id = room_id

    def __repr__(self):
        return '<Room {}>'.format(self.room_id)


class CurrentUser(db.Model):
    __tablename__ = "currentUsers"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(32))
    sid = db.Column(db.String())
    screenName = db.Column(db.String(20))

    def __init__(self, room_id, sid, screenName):
    #No need to collect screenName, right?
    #def __init__(self, room_id, sid):
        self.room_id = room_id
        self.sid = sid
        self.screenName = screenName

    def __repr__(self):
        return '<CurrentUser {} in room {}>'.format(self.sid, self.room_id)
