import cv2
import numpy as np

from modules.blob import BlobsPool
from modules.detector import make_detector


def maximize(data, depth=1):
    new_data = data.copy()
    for frame in maximize.frames:
        new_data = np.maximum(new_data, frame)
    maximize.frames.append(data.copy())
    if len(maximize.frames) > depth:
        maximize.frames.pop(0)
    return new_data
maximize.frames = []


def meanimize(data, depth=2):
    meanimize.frames.append(data.copy())
    if len(meanimize.frames) > depth:
        meanimize.frames.pop(0)
    return np.mean(meanimize.frames, axis=0).astype(np.uint8)
meanimize.frames = []


# Common detector
#
detector = make_detector(min_area=350, max_area=6000)    ################### SIZE OF DETECTED BLOB ####################

# Common BlobsPool
#
blobs = BlobsPool( liveness=4, z_smooth=4)    ############################# LIVENESS OF BLOB + Z_SMOOTH ##############


class Frame:
  
  def __init__(self, data_norm, scale, size, seq):
    self.scale = scale
    self.size = size
    rs_size = (size[1], size[0])
    
    # Raw data
    self._raw_data = data_norm.copy()
    self._raw_data = self._raw_data.reshape( rs_size )
    # self._raw_data = np.fliplr(self._raw_data)
    # self._raw_data = np.flipud(self._raw_data)

    # Raw frame    
    self._frame_raw =  data_norm.copy()
    # self._frame_raw = maximize(self._frame_raw, 1)              ################################### NUMBER OF FRAMES TO MAXIMIZE AGAINST ##############
    # self._frame_raw = meanimize(self._frame_raw, 1)           ################################### NUMBER OF FRAMES TO AVERAGE AGAINST  ##############
    self._frame_raw = self._frame_raw.reshape( rs_size )
    self._frame_raw = np.fliplr(self._frame_raw)
    # self._frame_raw = np.flipud(self._frame_raw)
    

    # Processed frame
    self._frame_proc = self._frame_raw.copy()
    self._frame_proc = cv2.bitwise_not(self._frame_proc)  # Invert
    self._frame_proc = self._frame_proc.astype(np.uint8)  # Convert to 8bit
    
    # self._frame_proc = cv2.erode(self._frame_proc, np.ones((2,2),np.uint8) ,iterations = 1)   ############# ERODE SIZE & ITERATIONS ############
    # self._frame_proc = cv2.dilate(self._frame_proc,np.ones((1,1),np.uint8) ,iterations = 1)   ############# DILATE SIZE & ITERATIONS ############
    
    if scale != 1:
      self._frame_proc = cv2.resize(self._frame_proc, (size[1]*scale, size[0]*scale), interpolation=cv2.INTER_AREA)  # Resize

    if (seq % 60 == 0):
      print('_raw_data:', self._raw_data.shape)
      print('_frame_raw:', self._frame_raw.shape)
      print('_frame_proc:', self._frame_proc.shape)
      print('------------------')
    
    # KEYPOINTS
    # detector.empty()
    self._keypoints = []
    self._keypoints = list(detector.detect( self._frame_proc ))

    # Y_MIN (remove projection screen)
    self.y_min = 30            ################################################ IGNORE BLOBS BELOW Y_MIN ##############################
    self._keypoints = [kp for kp in self._keypoints if kp.pt[1] > self.y_min]
    
    # BLOBS
    blobs.update(self)
  
  
  def keypoints(self):
    return self._keypoints
  
  def raw(self):
    return self._frame_raw
    
  def processed(self):
    return self._frame_proc
  
  def blobs(self):
    return blobs
  
  def detector(self):
    return detector
  
  def render(self):
    
    
    # Draw detected keypoints as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    frame_with_keypoints = cv2.drawKeypoints( self._frame_proc, self._keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    # Draw y_min line
    # print((0, self.y_min), (self.size[0]*self.scale, self.y_min), frame_with_keypoints.shape)
    frame_with_keypoints = cv2.line(frame_with_keypoints, (0, self.y_min), (self.size[0]*self.scale, self.y_min), (0,0,255), 1)    

    # Detected blobs 
    for c, b in enumerate(blobs.export()):
        # print ('blob'+str(c), b)

        # Draw as green circles.
        frame_with_keypoints = cv2.circle(frame_with_keypoints, (int(b['x']), int(b['y'])), 10, (0, 255, 0) , 2)
        frame_with_keypoints = cv2.putText(frame_with_keypoints, str(b['x'])+' '+str(b['y'])+' '+str(b['z']), (int(b['x'])+15, int(b['y'])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        
    return frame_with_keypoints        