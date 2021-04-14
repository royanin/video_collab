import psycopg2
from app.run_mode import POSTGRES_conn
#from app.main.models import Room, CurrentUser, RoomEvents
from app.main.models import *
from sqlalchemy import create_engine


try:
    engine = create_engine(POSTGRES_conn)

except Exception as e:
    print('exception {}'.format(e))


#Create all these rooms:
Room.__table__.create(engine)
User.__table__.create(engine)
CurrentUser.__table__.create(engine)
RoomEvents.__table__.create(engine)
VideoLoaded.__table__.create(engine)
