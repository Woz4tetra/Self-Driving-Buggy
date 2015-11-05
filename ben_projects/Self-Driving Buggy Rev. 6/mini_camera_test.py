"""
The minimum code required to run the camera module
"""
import config

from camera import capture

def run():
    camera1 = capture.Capture(window_name="camera")

    while True:
        frame1 = camera1.updateFrame()
        camera1.showFrame(frame1)
        camera1.getPressedKey()


if __name__ == '__main__':
    run()
