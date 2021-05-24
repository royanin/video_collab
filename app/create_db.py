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
table_list = [Role, User, RolesUsers, Room, RoomEvents, VideoLoaded,
ExpressInterest, CouponUsed, SubscribeList, LastEmailRecord, CurrentUserRoomList]

for table_ in table_list:
    try:
        table_.__table__.create(engine)
    except Exception as e:
        pass

"""
#to speifically create a table:
try:
    Role.__table__.create(engine)
except Exception as e:
    pass

"""
