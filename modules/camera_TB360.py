from openni import openni2
from pathlib import Path
import numpy as np
import os, sys

from modules.frame import Frame
from modules.detector import make_detector

class Camera:
    
    _fps = 5
    _dmin = 1000
    _dmax = 3800
    
    def __init__(self, fake=False):
        
        self.fake = fake
        self.seq = 0
        self.dev = None
        self.stream = None
        self.frame = None
        
        self.size = (80, 60)
        
        # Detector
        self.detector = make_detector(min_area=350, max_area=6000)    ################### SIZE OF DETECTED BLOB ####################
        
        self.data_raw = None
        self.data_norm = None
        
        if not self.fake:
            path = Path(__file__)

            # Init OpenNI
            openni2.initialize(os.path.join(path.parent.parent, 'Redist')) 
            
            # Connect and open device
            self.dev = openni2.Device.open_any()
            
            # Create depth stream
            self.stream = self.dev.create_depth_stream()
            self.stream.start()
        
        
    def read(self):
        
        # Read FAKE data
        if self.fake:
            # Fake data
            # create a random depth array of size w*h and type uint16
            depth_raw = np.random.randint(0, 2**16, size=self.size[0]*self.size[1], dtype=np.uint16)
            depth_raw[0] = self.seq
        
        # Read REAL data
        else:
            # Read depth frame
            frame = self.stream.read_frame()
            depth_raw = np.asarray( frame.get_buffer_as_uint16() )
        
        # Print sequence number
        if (self.seq % 60 == 0):
            print(f'DATA: [{self.seq}]', len(depth_raw))
            sys.stdout.flush()
            
        self.seq += 1
        
        ######## Save RAW data
        ########
        self.raw = depth_raw.copy()
        
        # Trimming
        depth_raw[ depth_raw == 0 ] = self._dmax
        depth_raw[ depth_raw < self._dmin ] = self._dmin
        depth_raw[ depth_raw > self._dmax ] = self._dmax
        
        # Normalize 255
        depth_scale_factor = 255.0 / (self._dmax - self._dmin)
        depth_scale_offset = -(self._dmin * depth_scale_factor)
        
        ######## Save NORM data
        ########
        self.norm = (depth_raw * depth_scale_factor + depth_scale_offset).astype(np.uint8)
        
        # make frame
        self.frame = Frame(self.norm, scale=1, size=self.size)
        
        ######## Save BLOBS data
        ########
        self.blobs = self.frame.blobs().export()
        
    
    def stop(self):
        if not self.fake:
            self.stream.stop()
            openni2.unload()    