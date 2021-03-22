#!/bin/env python
from app.run_mode import env_var
from app import create_app, socketio

#import os

#Check if the db already exists. If not, create the file and the table.
#This is totally hacky -- need to change once more persistence is required.
#if os.isfile("data/i")

print('debug_opt:',env_var['debug_opt'])
app = create_app(debug=env_var['debug_opt'])

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
