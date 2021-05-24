from dotenv import load_dotenv
import os, time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

project_folder = os.path.expanduser(os.path.abspath(os.path.dirname(__file__)))
load_dotenv(os.path.join(project_folder, '../../.env'))

POSTGRES_conn = 'postgresql://postgres:example@localhost:5432/test_db2'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = sqla(app)

class Events(db.Model):
    __tablename__ = "Events"
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

print(POSTGRES_conn)

engine = create_engine(POSTGRES_conn)

if not database_exists(engine.url):
    create_database(engine.url)


#Create all these tables:
try:
    Events.__table__.drop(engine)
except Exception as e:
    pass
Events.__table__.create(engine)

def load_data_sa_ind():
    new_event = Events(timestamp=1234567890, room_id = 4,
                        event_type = 'abc', event_details = 'akjnkajn')
    db.session.add(new_event)


t1 = time.time()
for i in range (0, 2000):
    load_data_sa_ind()
db.session.commit()
t2 = time.time()

#results: 1000 ~ 3 seconds, 2000 ~6 seconds

print('total time taken {} seconds'.format(t2 - t1))
