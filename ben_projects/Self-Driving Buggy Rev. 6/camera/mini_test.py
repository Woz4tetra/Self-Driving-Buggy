"""
The minimum code required to run the camera module
"""

import camera

def run():
    camera1 = camera.Capture(windowName="camera",
                         # camSource=0,
                         )

    while True:
        frame1 = camera1.updateFrame()
        camera1.showFrame(frame1)
        camera1.getPressedKey()


if __name__ == '__main__':
    run()
