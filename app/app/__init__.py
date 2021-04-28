import os
#from .run_mode import env_var, POSTGRES_conn
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_bootstrap import Bootstrap


socketio = SocketIO()
#basedir = os.path.abspath(os.path.dirname(__file__))

project_folder = os.path.expanduser(os.path.abspath(os.path.dirname(__file__)))
load_dotenv(os.path.join(project_folder, '../../.env'))

POSTGRES_conn = 'postgresql://{}:{}@{}:{}/{}'.format(os.getenv("POSTGRES_USER"),
    os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_HOST"), os.getenv("POSTGRES_PORT"),
    os.getenv("POSTGRES_DB"))

migrate = Migrate()

def create_app(debug=os.getenv("debug_opt")):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = os.getenv("secret_key")
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, '../data/app_data.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_conn
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
    app.config.update(dict(PREFERRED_URL_SCHEME = 'https'))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, logger=(os.getenv("debug_opt") == 'true'), engineio_logger=(os.getenv("debug_opt") == 'true'))
    from .main.models import db, CurrentUser, RoomEvents
    db = SQLAlchemy(app)
    db.init_app(app)
    migrate.init_app(app, db)

    #Bootstrap(app)

    #If the CurrentUser table already exists, drop it and recreate it:
    try:
        CurrentUser.__table__.drop(db.engine)
    except Exception:
        pass
    CurrentUser.__table__.create(db.engine)

    return app
