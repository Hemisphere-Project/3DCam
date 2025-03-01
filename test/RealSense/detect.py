import pyrealsense2 as rs
import numpy as np
import cv2

# Initialisation de la caméra RealSense
pipeline = rs.pipeline()
config = rs.config()

colorizer = rs.colorizer()

# Active la caméra RGB et la profondeur
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Démarrer le flux
pipeline.start(config)

# Charger le modèle pré-entraîné de détection de personnes (HOG + SVM d'OpenCV)
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

try:
    while True:
        # Obtenir les images de la caméra
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        
        if not color_frame or not depth_frame:
            continue

        # Convertir en tableau numpy
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        colorized_depth_frame = np.asanyarray(colorizer.colorize(depth_frame).get_data())

        # Détection des personnes
        boxes, _ = hog.detectMultiScale(color_image, winStride=(4,4), padding=(8,8), scale=1.05)

        # Dessiner les rectangles sur les personnes détectées
        for (x, y, w, h) in boxes:
            cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Récupérer la profondeur moyenne de la personne détectée
            depth = depth_image[y:y+h, x:x+w]
            avg_depth = np.mean(depth[depth > 0])  # Exclure les valeurs nulles
            cv2.putText(color_image, f"Depth: {avg_depth:.2f}mm", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Log
            print(f"Person detected at ({x}, {y}), depth: {avg_depth:.2f}mm")

        # Draw image to /tmp/stream.jpg
        # cv2.imwrite('/tmp/stream.jpg', color_image)
        cv2.imshow('Realsense Color Image', color_image)
        cv2.imshow('Realsense Depth Image', colorized_depth_frame)
        
        

        # Quitter avec la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Arrêter le pipeline
    pipeline.stop()
    cv2.destroyAllWindows()