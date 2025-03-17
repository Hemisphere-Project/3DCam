import cv2


def make_detector(area_range=(1000, 7000)):
  
  # Setup SimpleBlobDetector parameters.
  params = cv2.SimpleBlobDetector_Params()

  params.filterByColor = False
  params.blobColor = 0
  
  # Change thresholds
  params.minThreshold = 1;
  params.maxThreshold = 255;
  
  # Filter by Area.
  params.filterByArea = True
  params.minArea = area_range[0]
  params.maxArea = area_range[1]
  
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