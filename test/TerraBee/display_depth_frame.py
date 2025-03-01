#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from openni import openni2
import platform
import numpy as np
import cv2
import sys

# Initialize OpenNI
if platform.system() == "Windows":
    openni2.initialize("C:/Program Files/OpenNI2/Redist")  # Specify path for Redist
else:
    openni2.initialize("../Redist")  # can also accept the path of the OpenNI redistribution

# Connect and open device
dev = openni2.Device.open_any()

# Create depth stream
depth_stream = dev.create_depth_stream()
depth_stream.start()

# Set up the detector with default parameters.
params = cv2.SimpleBlobDetector_Params()    
params.minThreshold = 10;     # Change thresholds
params.maxThreshold = 300;    
params.filterByArea = True    # Filter by Area.
params.minArea = 200
params.maxArea = 600    
params.filterByCircularity = False   # Filter by Circularity
params.minCircularity = 0.1
params.maxCircularity = 1    
params.filterByConvexity = False    # Filter by Convexity
params.minConvexity = 0.87
params.maxConvexity = 2    
params.filterByInertia = False     # Filter by Inertia
params.minInertiaRatio = 0.01
params.maxInertiaRatio = 0.1
detector = cv2.SimpleBlobDetector_create(params)

# Windows
cv2.namedWindow("Depth View", cv2.WINDOW_NORMAL)
cv2.namedWindow("Keypoints", cv2.WINDOW_NORMAL)

while cv2.waitKey(1) == -1 and cv2.getWindowProperty("Depth View", cv2.WND_PROP_FULLSCREEN) != -1:
    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    
    #
    # RGB color map
    #
    
    depth_array = np.asarray(frame_data).copy().reshape((60, 80))
    
    # Trimming depth_array
    max_distance = 4000
    min_distance = 0
    out_of_range = depth_array > max_distance
    too_close_range = depth_array < min_distance
    depth_array[out_of_range] = max_distance
    depth_array[too_close_range] = min_distance

    # Scaling depth array
    depth_scale_factor = 255.0 / (max_distance - min_distance)
    depth_scale_offset = -(min_distance * depth_scale_factor)
    depth_array_norm = depth_array * depth_scale_factor + depth_scale_offset
    
    rgb_frame = cv2.applyColorMap(depth_array_norm.astype(np.uint8), cv2.COLORMAP_JET)

    # Replacing invalid pixel by black color
    rgb_frame[np.where(depth_array == 0)] = [0, 0, 0]

    # Display image
    rgb_frame = cv2.resize(rgb_frame, (1024, 768), interpolation=cv2.INTER_AREA)
    cv2.imshow("Depth View", rgb_frame)   
    
    # 
    # Blob detection
    #
    
    depth_array2 = np.asarray(frame_data).copy().reshape((60, 80))
    
    # Treshold
    treshold_distance = 1000
    far_range = depth_array2 > treshold_distance
    close_range = depth_array2 <= treshold_distance
    error_range = depth_array2 == 0
    depth_array2[far_range] = 255
    depth_array2[close_range] = 0
    # depth_array2[error_range] = 255
    
    # Greyscale
    grayImage = cv2.cvtColor(depth_array2.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    
    # Invert image
    # grayImage = cv2.bitwise_not(grayImage) 
        
    # Detect blobs.
    keypoints = detector.detect(grayImage)
    
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(grayImage, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    # Show keypoints
    cv2.imshow("Keypoints", im_with_keypoints)
    
    # 
    # Raw depth
    #
    # raw_array = np.asarray(frame_data).copy().reshape((60, 80))
    # with np.printoptions(threshold=sys.maxsize, linewidth=1000):
    #     print(raw_array)
        
    

depth_stream.stop()
openni2.unload()
