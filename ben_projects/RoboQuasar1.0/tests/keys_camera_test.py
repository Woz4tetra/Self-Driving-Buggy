"""
The minimum code required to run the camera module
"""
import sys

sys.path.insert(0, '../')

import config
from camera import capture


def run():
    camera1 = capture.Capture(window_name="camera", camera_type="ps3eye")
    while True:
        frame1 = camera1.updateFrame()
        camera1.showFrame(frame1)
        key = camera1.getPressedKey()
        if key > -1:
            print(key)


if __name__ == '__main__':
    run()
