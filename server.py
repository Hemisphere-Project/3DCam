# -*- coding: utf-8 -*-

import eventlet
eventlet.monkey_patch()

# from modules.camera_TB360 import Camera
from modules.camera_RSD4xx import Camera

from flask import *
from flask_socketio import *

# import modules.blob as blob

# Init the server
app = Flask(__name__, static_folder='www')

app.config['SECRET_KEY'] = 'yo rasta'
socketio = SocketIO(app, logger=False, cors_allowed_origins="*")

# Root
@app.route('/')
def root():    
    return app.send_static_file('index.html')

# Client connected
@socketio.on('connect')
def connect():
    print('Client connected')
    socketio.emit('3Dcam-CONF', cam.conf())

# Join a room    
@socketio.on("join")
def on_join(room):
    print(f'Client joined room {room}')
    join_room(room)

# Receive a message -> Echo it back
@socketio.server.on('*')   
def message_recieved(event, sid, *args):
    print(f'catch_all(event={event}, sid={sid}, args={args})')
    socketio.emit('3Dcam-ECHO', {'event': event, 'args': args})   

# Conf
@socketio.on('3Dcam-CONF')
def conf(data):
    print('3Dcam-CONF', data)
    cam.conf(data)
    

cam = Camera(fake=False, conffile='/data/3dcam.json')


def camread():
    while True:
        
        # Read RAW
        cam.read()
        
        # Send DATA                
        # socketio.emit('3Dcam-RAW', cam.raw.tobytes(), room='RAW')
        # socketio.emit('3Dcam-NORM', cam.norm.tobytes(), room='NORM')
        
        if cam.frame:
            socketio.emit('3Dcam-BLOBS', cam.blobs(), room='BLOBS')
            socketio.emit('3Dcam-VISU-RAW', cam.frame.raw().tobytes(), room='VISU-RAW')
            socketio.emit('3Dcam-VISU-PROC', cam.view().tobytes(), room='VISU-PROC')
        
        eventlet.sleep(1/33)

eventlet.spawn(camread)


# Actually Start the App
if __name__ == '__main__':
    socketio.run(app, port=8888, host="0.0.0.0", debug=False)


cam.stop()
