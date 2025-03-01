#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import socketio
import cv2
import time
from threading import Lock

# Windows
cv2.namedWindow("Depth View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Keypoints", cv2.WINDOW_NORMAL)


lock = Lock()
depth_stream = np.random.randint(1, size=4800)
dirty = False

image_stack = []

sio = socketio.Client()

@sio.on('3Dcam-ECHO')
def on_message(data):
    print('echo received:', data)

@sio.on('3Dcam-RAW')
def on_message(data):
    
    with lock:
        global depth_stream, dirty
        depth_stream = np.fromstring(data, dtype=np.uint16)
        print('data received:', len(depth_stream), depth_stream[0])
        dirty = True
    
    # # Trimming depth_array
    # max_distance = 4000
    # min_distance = 0
    # out_of_range = depth_array > max_distance
    # too_close_range = depth_array < min_distance
    # depth_array[out_of_range] = max_distance
    # depth_array[too_close_range] = min_distance
    
    # # Scaling depth array
    # depth_scale_factor = 255.0 / (max_distance - min_distance)
    # depth_scale_offset = -(min_distance * depth_scale_factor)
    # depth_array_norm = depth_array * depth_scale_factor + depth_scale_offset
    
    # rgb_frame = cv2.applyColorMap(depth_array_norm.astype(np.uint8), cv2.COLORMAP_JET)

    # # Replacing invalid pixel by black color
    # rgb_frame[np.where(depth_array == 0)] = [0, 0, 0]

    # # Display image
    # rgb_frame = cv2.resize(rgb_frame, (1024, 768), interpolation=cv2.INTER_AREA)
    # cv2.imshow("Depth View", rgb_frame)   
    
    
    

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('join', 'RAW')
    # sio.emit('Hello', {'foo': 'bar'})

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

sio.connect('http://100.101.146.77:8000')


while cv2.waitKey(1) == -1 and cv2.getWindowProperty("Depth View", cv2.WND_PROP_FULLSCREEN) != -1:
    
    while not dirty:
        time.sleep(0.01)
    
    with lock:
        depth_array = depth_stream.copy().reshape((60, 80))
    
    #
    # RGB color map
    #
    
    # Trimming depth_array
    max_distance = 3800
    min_distance = 100
    
    # error value 0
    error_range = depth_array == 0
    depth_array[error_range] = max_distance
    
    # too close value min
    too_close_range = depth_array < min_distance
    depth_array[too_close_range] = min_distance
    
    # too far value max
    out_of_range = depth_array > max_distance
    depth_array[out_of_range] = max_distance
    

    # Scaling depth array
    depth_scale_factor = 255.0 / (max_distance - min_distance)
    depth_scale_offset = -(min_distance * depth_scale_factor)
    depth_array_norm = depth_array * depth_scale_factor + depth_scale_offset
    
    
    rgb_frame = depth_array_norm.astype(np.uint8)
    # rgb_frame = cv2.applyColorMap(depth_array_norm.astype(np.uint8), cv2.COLORMAP_INFERNO)
    # rgb_frame = cv2.bitwise_not(rgb_frame)

    # Replacing invalid pixel by black color
    # rgb_frame[np.where(depth_array == 0)] = [0, 0, 0]
    
    # image_stack.append(rgb_frame)
    # if len(image_stack) > 40:
    #     image_stack.pop(0)
        
    # rgb_frame = np.mean(image_stack, axis=0).astype(np.uint8)
    
    


    # Display image
    rgb_frame = cv2.resize(rgb_frame, (800, 600), interpolation=cv2.INTER_AREA)
    cv2.imshow("Depth View", rgb_frame)  
