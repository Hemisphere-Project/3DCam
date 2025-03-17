from pathlib import Path
import numpy as np
import os, sys, json
import pyrealsense2 as rs2
import time

from modules.frame import Frame
from modules.detector import make_detector
from modules.blob import BlobsPool

class Camera:
    
    _conf = {
        'fps': 10,
        'z_range': (100, 1200),
        'borders': ((0,0), (0,0)),
        'blob_range': (350, 50000),          # needs reinit of self.detector
        'blob_liveness': 4,                  # needs reinit of self._blobs
        'blob_z_smooth': 4,                  # needs reinit of self._blobs
        'flip': (0, 0),
        'erode': 0,
        'dilate': 0,
    }
    
    def __init__(self, conffile=None, fake=False):
        
        self.fake = fake
        self.seq = 0
        self.pipe = None
        self.profile = None
        # self.colorizer = rs2.colorizer()
        
        self.size = (640, 480) 
        
        # If no borders are set, use the whole frame
        if self._conf['borders'] == ((0,0), (0,0)):
            self._conf['borders'] = ((0, 0), (self.size[0], self.size[1]))
       
        self._lastTime = 0
        self.data_raw = None
        self.data_norm = None
        
        # Detector
        self.detector = make_detector(self._conf['blob_range'])    ################### SIZE OF DETECTED BLOB ####################
        
        # Blobs
        self._blobs = BlobsPool( liveness=self._conf['blob_liveness'], z_smooth=self._conf['blob_z_smooth'] )
        
        # Load conf
        if conffile:
            self.conffile = conffile 
            try:
                with open(conffile, 'r') as f:
                    c = json.load(f)
                self.conf(c)
            except:
                print(f'Error loading conf file {conffile}')                
        
        if not self.fake:
            # Start the pipeline
            self.pipe = rs2.pipeline()
            cfg = rs2.config()
            cfg.enable_stream(rs2.stream.depth, self.size[0], self.size[1], rs2.format.z16, 30)
            self.profile = self.pipe.start(cfg)
        
    def read(self):
        
        # Limit FPS
        currTime = time.time()
        elapsedTime = currTime - self._lastTime
        sleepTime = 1.0/self._conf['fps'] - elapsedTime
        if sleepTime > 0:
            # print(f'Sleeping for {sleepTime}')
            sys.stdout.flush()
            time.sleep(sleepTime)
        self._lastTime = time.time()
        
        # Read FAKE data
        if self.fake:
            # Fake data
            # create a random depth array of size w*h and type uint16
            depth_raw = np.random.randint(0, 2**16, size=self.size[0]*self.size[1], dtype=np.uint16)
            depth_raw[0] = self.seq
        
        # Read REAL data
        else:
            # Read depth frame
            frameset = self.pipe.wait_for_frames()
            depth_frame = frameset.get_depth_frame()
            depth_raw = np.asanyarray(depth_frame.get_data()).flatten()  
            
        # Print sequence number
        if (self.seq % 60 == 0):
            print(f'DATA: [{self.seq}]', len(depth_raw))
            sys.stdout.flush()
            
        self.seq += 1
        
        ######## Save RAW data
        ########
        self.raw = depth_raw.copy()
        
        # Trimming
        depth_raw[ depth_raw == 0 ] = self._conf['z_range'][1]                       # 0 means too far
        depth_raw[ depth_raw < self._conf['z_range'][0] ] = self._conf['z_range'][1] # too close: send faraway
        depth_raw[ depth_raw > self._conf['z_range'][1] ] = self._conf['z_range'][1] # too far: send faraway
        
        # Normalize 255
        depth_scale_factor = 255.0 / (self._conf['z_range'][1] - self._conf['z_range'][0])
        depth_scale_offset = -(self._conf['z_range'][0] * depth_scale_factor)
        
        ######## Save NORM data
        ########
        self.norm = (depth_raw * depth_scale_factor + depth_scale_offset).astype(np.uint8)
        
        ######## FRAME
        self.frame = Frame(self.norm, size=self.size, conf=self._conf)
        
        ######## KEYPOINTS (inside _borders)
        # detector.empty()
        self.keypoints = list(self.detector.detect( self.frame.processed() ))
        self.keypoints = [kp for kp in self.keypoints if self.frame.conf['borders'][0][0] < kp.pt[0] < self.frame.conf['borders'][1][0] and self.frame.conf['borders'][0][1] < kp.pt[1] < self.frame.conf['borders'][1][1]]
        
        ######## BLOBS
        self._blobs.update(self.frame, self.keypoints)
        
        
    def stop(self):
        if not self.fake:
            self.pipe.stop()
            
    def blobs(self):
        return self._blobs.export()       
    
    def view(self):
        return self.frame.render(self._blobs, self.keypoints, self._conf['borders'])
    
    def conf(self, data=None):
        if type(data) == dict:
            for k,v in data.items():
                if k in self._conf:
                    self._conf[k] = v
                    if k == 'blob_range':
                        self.detector = make_detector(v)
                    if k == 'blob_liveness' or k == 'blob_z_smooth':
                        self._blobs = BlobsPool( liveness=self._conf['blob_liveness'], z_smooth=self._conf['blob_z_smooth'] )
            print('CONF', self._conf)
            try:
                with open(self.conffile, 'w') as f:
                    # pretty print the dictionary
                    json.dump(self._conf, f, indent=4)
            except:
                print('Error saving conf file', self.conffile)
        return self._conf