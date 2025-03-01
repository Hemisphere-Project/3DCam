from openni import openni2
from pathlib import Path
import numpy as np
import os, sys

from modules.frame import Frame

class Camera:
    def __init__(self, fake=False):
        
        self.fake = fake
        self.seq = 0
        self.dev = None
        self.stream = None
        self.frame = None
        
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
            # create a random depth array of size 4800 and type uint16
            depth_raw = np.random.randint(0, 2**16, size=4800, dtype=np.uint16)
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
        max_distance = 3800            ################################################################
        min_distance = 1000            ################################################################
        
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
        self.frame = Frame(self.norm, scale=1, size=(80, 60))
        
        ######## Save BLOBS data
        ########
        self.blobs = self.frame.blobs().export()
        
        
        
        
    
    
    def stop(self):
        if not self.fake:
            self.stream.stop()
            openni2.unload()    