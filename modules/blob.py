import time, math
import numpy as np


class Blob:
    def __init__(self, kp, liveness_max, z_smooth):
        self.z_cache = []
        self.liveness = 1
        self.liveness_max = liveness_max
        self.z_smooth = z_smooth
        self.prev_pos = None
        self.absorb(kp)
        
    def absorb(self, kp):
        self.x = kp.pt[0]
        self.y = kp.pt[1]
        self.size = kp.size
        if self.liveness < self.liveness_max:
            self.liveness += 2
        
    def decrease(self):
        if self.liveness > 0:
            self.liveness -= 1
    
    def in_range(self, kp):
        if type(kp) == Blob:
            if kp.alive():
                return math.sqrt((self.x - kp.x)**2 + (self.y - kp.y)**2) < self.size/2
            else:
                return math.sqrt((self.x - kp.x)**2 + (self.y - kp.y)**2) < self.size
        else:
            return math.sqrt((self.x - kp.pt[0])**2 + (self.y - kp.pt[1])**2) < (self.size + kp.size)
    
    def merge(self, b):
        self.x = (self.x + b.x)/2
        self.y = (self.y + b.y)/2
        self.size = (self.size + b.size)/2
        self.liveness = max(self.liveness, b.liveness)
    
    def alive(self):
        return self.liveness > self.liveness_max/3
    
    def dead(self):
        return self.liveness == 0
    
    def calc(self, frame):
        self.x = int(self.x)
        self.y = int(self.y)
        if self.alive():
            # Calc Z on RAW (80x60)
            xc = int(self.x/frame.scale)
            yc = int(self.y/frame.scale)
            radius = int(self.size/frame.scale)+1
            y_grid, x_grid = np.ogrid[-yc:frame.size[1]-yc, -xc:frame.size[0]-xc]
            mask = x_grid ** 2 + y_grid ** 2 > radius ** 2
            blob_frame = frame.raw().copy()
            blob_frame[mask] = 255
            
            z = int( (255-np.min(blob_frame)) * 2800 / 255 )
            if z > 0:
                self.z_cache.append(z)
                if (len(self.z_cache) > self.z_smooth):
                    self.z_cache.pop(0)
                self.z = int(np.mean(self.z_cache))
                
            # Calc on PROCESSED (800x600)
            # xc = int(self.x)
            # yc = int(self.y)
            # radius = int(self.size)+frame.scale
            # y_grid, x_grid = np.ogrid[-yc:60*frame.scale-yc, -xc:80*frame.scale-xc]
            # mask = x_grid ** 2 + y_grid ** 2 > radius ** 2
            # blob_frame = frame.processed().copy()
            # blob_frame[mask] = 0
            
            # z = int( np.max(blob_frame) * 3000 / 255 )
            # if z > 0:
            #     self.z_cache.append(z)
            #     if (len(self.z_cache) > self.z_smooth):
            #         self.z_cache.pop(0)
            #     self.z = int(np.mean(self.z_cache))
        else:
            self.z = 0
            self.z_cache = []
            
            
    def coord(self):
        return { 'x':self.x, 'y':self.y, 'z':self.z, 'r': int(self.size/2) }
      

##
# Blobs pool with smoothing
#
      
class BlobsPool():
  
    def __init__(self, liveness=10, z_smooth=1):
      self.liveness_max = liveness
      self.z_smooth = z_smooth
      self.allblobs = []
    
    
    def update(self, frame):
      
      # Decreament liveness
      for b in self.allblobs:
          b.decrease()
      
      # Update new keypoints from detector
      for kp in frame.keypoints():
          found = False
          for b in self.allblobs:
              if b.in_range(kp):
                  b.absorb(kp)
                  found = True
                  break
          if not found:
              self.allblobs.append(Blob(kp, self.liveness_max, self.z_smooth))
      
      # Remove dead blobs
      for b in self.allblobs:
          if b.dead():
              self.allblobs.remove(b)
              
      # Merge blobs
      for b in self.allblobs:
          if b.alive():
              for b2 in self.allblobs:
                  if b != b2 and b2.in_range(b): # and b2.alive():
                      b.merge(b2)
                      self.allblobs.remove(b2)
      
      # Blob update
      for b in self.allblobs:
          b.calc(frame)
                
      return self.allblobs
    
    
    def export(self):
      return [ b.coord() for b in self.allblobs if b.alive() ]