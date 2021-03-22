import os
from .run_mode import env_var
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
#from flask_bootstrap import Bootstrap


socketio = SocketIO()
basedir = os.path.abspath(os.path.dirname(__file__))

def create_app(debug=env_var['debug_opt']):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, '../data/app_data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, logger=env_var['debug_opt'], engineio_logger=env_var['debug_opt'])
    from .main.models import db, CurrentUser
    db = SQLAlchemy(app)
    db.init_app(app)
    #Bootstrap(app)

    #If the CurrentUser table already exists, drop it and recreate it:
    CurrentUser.__table__.drop(db.engine)
    CurrentUser.__table__.create(db.engine)

    return app
