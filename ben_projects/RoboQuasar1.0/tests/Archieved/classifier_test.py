"""
The minimum code required to run the camera module
"""
import sys

sys.path.insert(0, '../')

import config
from camera import capture
import cv2


def run():
    camera1 = capture.Capture(window_name="camera", cam_source=0)
    face_cascade = cv2.CascadeClassifier(
            '/Users/Woz4tetra/Downloads/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(
            '/Users/Woz4tetra/Downloads/opencv-3.1.0/data/haarcascades/haarcascade_eye.xml')

    while True:
        frame1 = camera1.getFrame()
        gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.5, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame1[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh),
                              (0, 255, 0), 2)
            camera1.showFrame(roi_color)
        key = camera1.getPressedKey()

        if key == 'q' or key == "esc":
            camera1.stopCamera()


if __name__ == '__main__':
    run()
