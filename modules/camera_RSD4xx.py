from pathlib import Path
import numpy as np
import os, sys
import pyrealsense2 as rs2
import cv2

from modules.frame import Frame

class Camera:
    def __init__(self, fake=False):
        
        self.fake = fake
        self.seq = 0
        self.pipe = None
        self.profile = None
        self.colorizer = rs2.colorizer()
        
        self.size = (640, 480)
        
        self.data_raw = None
        self.data_norm = None
        
        if not self.fake:
            # Start the pipeline
            self.pipe = rs2.pipeline()
            cfg = rs2.config()
            cfg.enable_stream(rs2.stream.depth, self.size[0], self.size[1], rs2.format.z16, 30)
            self.profile = self.pipe.start(cfg)
        
    def read(self):
        
        # Read FAKE data
        if self.fake:
            # Fake data
            # create a random depth array of size 4800 and type uint16
            depth_raw = np.random.randint(0, 2**16, size=self.size[0]*self.size[1], dtype=np.uint16)
            depth_raw[0] = self.seq
        
        # Read REAL data
        else:
            # Read depth frame
            frameset = self.pipe.wait_for_frames()
            depth_frame = frameset.get_depth_frame()
            # depth_raw = np.array([depth_frame.get_distance(x, y) for x in range(self.size[0]) for y in range(self.size[1])]).flatten()           
            depth_raw = np.asanyarray(depth_frame.get_data()).flatten()  
            
        # Print sequence number
        if (self.seq % 60 == 0):
            print(f'DATA: [{self.seq}]', len(depth_raw))
            sys.stdout.flush()
            
        self.seq += 1
        
        ######## Save RAW data
        ########
        self.raw = depth_raw.copy()
        
        # print min and max and average
        # print(f"min: {np.min(depth_raw)}, max: {np.max(depth_raw)}, avg: {np.mean(depth_raw)}")
        
        # Trimming
        max_distance = 1200            ################################################################
        min_distance = 100            ################################################################
        
        depth_raw[ depth_raw == 0 ] = max_distance
        depth_raw[ depth_raw < min_distance ] = min_distance
        depth_raw[ depth_raw > max_distance ] = max_distance
        
        # Normalize 255
        depth_scale_factor = 255.0 / (max_distance - min_distance)
        depth_scale_offset = -(min_distance * depth_scale_factor)
        
        ######## Save NORM data
        ########
        self.norm = (depth_raw * depth_scale_factor + depth_scale_offset).astype(np.uint8)
        
        # make frame
        self.frame = Frame(self.norm, scale=1, size=self.size, seq=self.seq)
        
        ######## Save BLOBS data
        ########
        self.blobs = self.frame.blobs().export()
        
    def stop(self):
        if not self.fake:
            self.pipe.stop()
        cv2.destroyAllWindows()