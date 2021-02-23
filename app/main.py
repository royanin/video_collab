#!/bin/env python
from app import create_app, socketio
#import os

#Check if the db already exists. If not, create the file and the table.
#This is totally hacky -- need to change once more persistence is required.
#if os.isfile("data/i")

app = create_app(debug=False)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80)
