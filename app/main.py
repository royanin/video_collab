#!/bin/env python
#from app.run_mode import env_var
import os
from gevent import monkey
monkey.patch_all()

from app import create_app, socketio


print('debug_opt:',os.getenv("debug_opt"))
app = create_app(debug=os.getenv("debug_opt"))

if __name__ == '__main__':
    if os.getenv("http_scheme")=="http":
        socketio.run(app, host="0.0.0.0", port=5000)
    else:
        socketio.run(app, host="0.0.0.0", port=5000,
                    #certfile=os.getenv("ssl_certfile") or None,
                    #keyfile=os.getenv("ssl_keyfile") or None
                    )
