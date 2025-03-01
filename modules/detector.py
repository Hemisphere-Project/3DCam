import cv2


def make_detector(min_area=1000, max_area=7000):
  
  # Setup SimpleBlobDetector parameters.
  params = cv2.SimpleBlobDetector_Params()

  params.filterByColor = False
  params.blobColor = 0
  
  # Change thresholds
  params.minThreshold = 1;
  params.maxThreshold = 255;
  
  # Filter by Area.
  params.filterByArea = True
  params.minArea = min_area
  params.maxArea = max_area
  
  # Filter by Circularity
  params.filterByCircularity = False
  params.minCircularity = 0.01
  
  # Filter by Convexity
  params.filterByConvexity = False
  params.minConvexity = 0
  
  # Filter by Inertia
  params.filterByInertia = False
  params.minInertiaRatio = 0

  return cv2.SimpleBlobDetector_create(params)