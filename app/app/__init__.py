import os
from flask import Flask
from flask_socketio import SocketIO

#socketio = SocketIO(cors_allowed_origins=["https://wesync.ojar-expt.com/","http://wesync.ojar-expt.com/"
# "http://localhost:5000"])
socketio = SocketIO()
basedir = os.path.abspath(os.path.dirname(__file__))

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    app.config['db_file'] = os.path.join(basedir, '../data/rooms_created.sqlite')
    #print(app.config['db_file'])

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, logger=False, engineio_logger=False)
    return app
