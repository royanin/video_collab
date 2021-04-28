#import psycopg2
#from app.run_mode import POSTGRES_conn
#from app.main.models import Room, CurrentUser, RoomEvents

from app.main.models import *
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database



try:
    engine = create_engine(POSTGRES_conn)

except Exception as e:
    print('exception {}'.format(e))

if not database_exists(engine.url):
    create_database(engine.url)


#Create all these rooms:
try:
    Room.__table__.create(engine)
except Exception as e:
    pass
try:
    User.__table__.create(engine)
except Exception as e:
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
