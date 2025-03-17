import cv2
import numpy as np




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



class Frame:
  
  def __init__(self, data_norm, size, conf):
    self.conf = conf
    
    if 'flip' not in self.conf: self.conf['flip'] = (False, False)
    if 'erode' not in self.conf: self.conf['erode'] = 0
    if 'dilate' not in self.conf: self.conf['dilate'] = 0
    
    self.size = size
    self.scale = 1
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
    if self.conf['flip'][0]:
      self._frame_raw = np.fliplr(self._frame_raw)
    if self.conf['flip'][1]:
      self._frame_raw = np.flipud(self._frame_raw)

    # Processed frame
    self._frame_proc = self._frame_raw.copy()
    self._frame_proc = cv2.bitwise_not(self._frame_proc)  # Invert
    self._frame_proc = self._frame_proc.astype(np.uint8)  # Convert to 8bit
    
    if self.conf['erode'] > 0:
      self._frame_proc = cv2.erode(self._frame_proc, np.ones((2,2),np.uint8) ,iterations = self.conf['erode'])   ############# ERODE SIZE & ITERATIONS ############
    if self.conf['dilate'] > 0:
      self._frame_proc = cv2.dilate(self._frame_proc,np.ones((2,2),np.uint8) ,iterations = self.conf['dilate'])   ############# DILATE SIZE & ITERATIONS ############
    
    if self.scale != 1:
      self._frame_proc = cv2.resize(self._frame_proc, (size[1]*self.scale, size[0]*self.scale), interpolation=cv2.INTER_AREA)  # Resize
    
  
  def raw(self):
    return self._frame_raw
    
  def processed(self):
    return self._frame_proc
  
  def render(self, blobs, keypoints=[], borders=((0,0), (0,0))):
    
    # Draw detected keypoints as blue circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    frame_with_keypoints = cv2.drawKeypoints( self._frame_proc, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    # Draw inner borders
    borders = ((borders[0][0]*self.scale, borders[0][1]*self.scale), (borders[1][0]*self.scale-1, borders[1][1]*self.scale-1))
    frame_with_keypoints = cv2.rectangle(frame_with_keypoints, borders[0], borders[1], (0,0,255), 1)

    # Detected blobs 
    for c, b in enumerate(blobs.export()):
        # print ('blob'+str(c), b)

        # Draw as green circles.
        frame_with_keypoints = cv2.circle(frame_with_keypoints, (int(b['x']), int(b['y'])), 10, (0, 255, 0) , 2)
        frame_with_keypoints = cv2.putText(frame_with_keypoints, str(b['x'])+' '+str(b['y'])+' '+str(b['z']), (int(b['x'])+15, int(b['y'])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        
    return frame_with_keypoints        