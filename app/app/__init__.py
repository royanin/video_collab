import os, secrets, json
#from .run_mode import env_var, POSTGRES_conn
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore#, login_required, SQLAlchemySessionUserDatastore
from flask_mail import Mail
from redis import Redis
import rq
#from flask_bootstrap import Bootstrap
from itsdangerous import URLSafeTimedSerializer
from gevent import monkey
monkey.patch_all()


socketio = SocketIO()
#basedir = os.path.abspath(os.path.dirname(__file__))

project_folder = os.path.expanduser(os.path.abspath(os.path.dirname(__file__)))
load_dotenv(os.path.join(project_folder, '../../.env'))

POSTGRES_conn = 'postgresql://{}:{}@{}:{}/{}'.format(os.getenv("POSTGRES_USER"),
    os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_HOST"), os.getenv("POSTGRES_PORT"),
    os.getenv("POSTGRES_DB"))

#from .main.models import db, user_datastore, User, Role, CurrentUser,  RoomEvents
from .main.models import db, user_datastore, CurrentUser#, User, Role, CurrentUser,  RoomEvents
migrate = Migrate()

mail = Mail()



def create_app(debug=(os.getenv("debug_opt") == 'true')):
    """Create an application."""
    app = Flask(__name__)
    app.debug = (os.getenv("debug_opt") == 'true')
    app.config['RUN_MODE'] = os.getenv("run_mode")
    app.config['SECRET_KEY'] = os.getenv("secret_key")
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, '../data/app_data.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_conn
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping':True, "pool_recycle": 300,}
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL') or 'redis://'


    app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
    app.config.update(dict(PREFERRED_URL_SCHEME = 'https'))

    app.config['SECURITY_EMAIL_SUBJECT_PASSWORDLESS']="Your Magic Link to log on ZipSync.us"
    #app.config['SECURITY_REGISTERABLE']=True
    app.config['SECURITY_PASSWORDLESS']=True
    app.config['SECURITY_TRACKABLE']=True
    #app.config['SECURITY_UNIFIED_SIGNIN']=True
    #app.config['SECURITY_US_ENABLED_METHODS'] = [ "email"]
    #app.config['SECURITY_TOKEN_MAX_AGE'] = '600 seconds'
    app.config['SECURITY_LOGIN_WITHIN'] = '600 seconds'
    app.config['SECURITY_DEFAULT_REMEMBER_ME'] = True
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_CONFIRM_EMAIL_WITHIN'] = '30 minutes'
    #app.config['SECURITY_LOGIN_USER_TEMPLATE'] = "/security/send_login.html"
    #app.config['SECURITY_LOGIN_URL']="/send_login"
    app.config['SECURITY_PASSWORD_SALT']=secrets.token_hex(16)
    #app.config['SECURITY_TOTP_SECRETS'] = {1: os.getenv('secret_key')}
    #app.config['SECURITY_TOTP_ISSUER'] = "ZipSync"

    app.config['srlzr'] = URLSafeTimedSerializer(os.getenv("secret_key"))

    app.config['COUPON_CODES'] = json.loads(os.getenv("COUPON_CODES"))
    app.config['COUPON_CODE_TO_USERTYPE'] =  json.loads(os.getenv("COUPON_CODE_TO_USERTYPE"))

    app.config['room_alive_dict'] = {'d2edu':600, 'da':7200, 'd2long':2700,
                    'dmed':1500, 'dmedlong':3600} #in seconds
    app.config['room_access_lifespan_dict'] = {'d2edu':1600, 'da':864000,
                    'd2long':864000, 'dmed':864000, 'dmedlong':864000}
    #this doesn't really work because how the room_alive_dict is enforced
    app.config['room_cap_dict'] = {'d2edu':2, 'da': 8, 'd2long': 2,
                        'dmed':5, 'dmedlong':5} #in number of connections

    app.config['usertype_to_roomtype'] = { k:k for k in app.config['room_alive_dict'].keys()}
    app.config['usertype_to_roomtype'][None] = 'd2edu'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #MAIL_config:
    app.config['MAIL_SERVER']=os.getenv("MAIL_SERVER")
    app.config['MAIL_PORT']=587 #os.getenv("MAIL_PORT")
    app.config['MAIL_USE_TLS']=(os.getenv("MAIL_USE_TLS") == 'true')
    app.config['MAIL_USE_SSL']=(os.getenv("MAIL_USE_SSL") == 'true')
    app.config['MAIL_USERNAME']=os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD']=os.getenv("MAIL_PASSWORD")


    socketio.init_app(app, async_mode='gevent',
                            message_queue= app.config['REDIS_URL'],
                             logger=(os.getenv("debug_opt") == 'true'),
                            engineio_logger=(os.getenv("debug_opt") == 'true'))


    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

    #from .main.models import db, User, Role, CurrentUser,  RoomEvents

    #db = SQLAlchemy(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup Flask-Security
    #user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)

    #user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)


    @app.before_first_request
    def init_db():
        try:
            CurrentUser.__table__.drop(db.engine)
        except Exception:
                pass
        #CurrentUser.__table__.create(db.engine)


    '''
    from .main.models import CurrentUser

    try:
        CurrentUser.__table__.drop(db.enginee)
    except Exception:
        pass
    CurrentUser.__table__.create(db.engine)
    '''


    mail.init_app(app)

    #Bootstrap(app)

    #If the CurrentUser table already exists, drop it and recreate it:


    return app
