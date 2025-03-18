# -*- coding: utf-8 -*-
import os
import eventlet
eventlet.monkey_patch()

# from modules.camera_TB360 import Camera
from modules.camera_RSD4xx import Camera

from flask import *
from flask_socketio import *

CAM_RUNNING = True

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

@socketio.on('startCam')
def startCam():
    global CAM_RUNNING
    CAM_RUNNING = True
    print("CAM_RUNNING = True")

@socketio.on('stopCam')
def stopCam():
    global CAM_RUNNING
    CAM_RUNNING = False
    print("CAM_RUNNING = False")

@socketio.on('rebootCam')
def rebootCam():
    print("Rebooting the system...")
    os.system("reboot")
    

cam = Camera(fake=False, conffile='/data/3dcam.json')


def camread():
    print("\n============ 3DCAM SERVER STARTED ============\n")
    while True:
        if CAM_RUNNING:
            cam.read()
            
            if cam.frame:
                socketio.emit('3Dcam-BLOBS', cam.blobs(), room='BLOBS')
                socketio.emit('3Dcam-VISU-RAW', cam.frame.raw().tobytes(), room='VISU-RAW')
                socketio.emit('3Dcam-VISU-PROC', cam.view().tobytes(), room='VISU-PROC')
            
        else:
            eventlet.sleep(1)

eventlet.spawn(camread)


# Actually Start the App
if __name__ == '__main__':
    socketio.run(app, port=8888, host="0.0.0.0", debug=False)


cam.stop()
