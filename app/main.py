#!/bin/env python
#from app.run_mode import env_var
import os
from gevent import monkey
monkey.patch_all()

from app import create_app, socketio


print('debug_opt:',os.getenv("debug_opt") == 'true')
app = create_app(debug=os.getenv("debug_opt") == 'true')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
