import cv2
import time
import os

# --- Configuration Constants ---
SAVE_PATH = './picturesTrain'
CAMERA_INDEX = 0
NUMBER_OF_IMAGES_TO_CAPTURE = 300

cap = cv2.VideoCapture(CAMERA_INDEX)
number_img = NUMBER_OF_IMAGES_TO_CAPTURE
savePath = SAVE_PATH
lenpath = len(os.listdir(savePath))

while True:
    for imgnum in range (number_img):
        print('Collecting image {}'.format(lenpath+imgnum))
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from camera in GetCapture.py. Exiting.")
            break 
        frame = cv2.resize(frame, (640, 480))
        cv2.imshow('frame', frame)
        imgname = os.path.join(savePath, 'image_{}.jpg'.format(lenpath+imgnum))
        cv2.imwrite(imgname, frame)
        time.sleep(3)
    
    break

cap.release()
cv2.destroyAllWindows()