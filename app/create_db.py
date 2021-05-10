#import psycopg2
#from app.run_mode import POSTGRES_conn
#from app.main.models import Room, CurrentUser, RoomEvents
from dotenv import load_dotenv
import os
from app.main.models import *
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

project_folder = os.path.expanduser(os.path.abspath(os.path.dirname(__file__)))
load_dotenv(os.path.join(project_folder, '../../.env'))

POSTGRES_conn = 'postgresql://{}:{}@{}:{}/{}'.format(os.getenv("POSTGRES_USER"),
    os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_HOST"), os.getenv("POSTGRES_PORT"),
    os.getenv("POSTGRES_DB"))

try:
    engine = create_engine(POSTGRES_conn)

except Exception as e:
    print('exception {}'.format(e))

if not database_exists(engine.url):
    create_database(engine.url)


#Create all these tables:
try:
    Room.__table__.create(engine)
except Exception as e:
    pass


try:
    Role.__table__.create(engine)
except Exception as e:
    pass

try:
    User.__table__.create(engine)
except Exception as e:
    pass

try:
    RolesUsers.__table__.create(engine)
except Exception as e:
    print(e)
    pass

try:
    CurrentUser.__table__.create(engine)
except Exception as e:
    pass
try:
    RoomEvents.__table__.create(engine)
except Exception as e:
    pass
try:
    VideoLoaded.__table__.create(engine)
except Exception as e:
    pass

#if not user_datastore.find_user(email="royanin@gmail.com"):
#        user_datastore.create_user(email="royanin@gmail.com")
#db.session.commit()
