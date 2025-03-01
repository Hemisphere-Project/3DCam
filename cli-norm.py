#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import socketio
import cv2
import time, math
from threading import Lock

from modules.frame import Frame

# Windows
cv2.namedWindow("Depth View", cv2.WINDOW_NORMAL)

lock = Lock()
depth_stream = None
dirty = False

sio = socketio.Client()

@sio.on('3Dcam-ECHO')
def on_message(data):
    print('echo received:', data)

@sio.on('3Dcam-NORM')
def on_message(data):
    
    with lock:
        global depth_stream, dirty
        try:
            depth_stream = np.frombuffer(data, dtype=np.uint8)
            # print('data received:', len(depth_stream), depth_stream[0])
            dirty = True
        except:
            print('data error')

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('join', 'NORM')
    # sio.emit('Hello', {'foo': 'bar'})

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

sio.connect('http://100.101.146.77:8000')


######
# RUN
######

while cv2.waitKey(1) == -1 and cv2.getWindowProperty("Depth View", cv2.WND_PROP_FULLSCREEN) != -1:
    
    while not dirty:
        time.sleep(0.1)
    
    with lock:
        dirty = False
        if depth_stream.shape[0] == 4800:
            depth_data = depth_stream.copy()
        else:
            continue
        
    # Frame 
    frame = Frame(depth_data, scale=10)
    
    # Display image
    cv2.imshow("Depth View", frame.render())  

