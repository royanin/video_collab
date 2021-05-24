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

conn = psycopg2.connect(dbname="test_db2", host="localhost", port="5432", user="postgres", password="example")
cur = conn.cursor()

def load_data_insert():
    cur.execute("""INSERT INTO "Events" (timestamp, room_id, event_type, event_details) VALUES (%s, %s, %s, %s);""", (1234567890, 4, 'abc', 'akjnkajn'))




t1 = time.time()
for i in range (0, 2000):
    load_data_insert()
conn.commit()
t2 = time.time()

cur.close()
conn.close()

#results: 1000 ~ 3 seconds, 2000 ~6 seconds

print('total time taken {} seconds'.format(t2 - t1))
