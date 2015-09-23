
import sys
import time

import camera
from camera import analyzers


def run():
    camera1 = camera.Capture(windowName="camera",
                         camSource="Down camera, Course Run 1, 4.5 ft, 9-2-15, 30 fps.m4v",
                         # camSource="0.33 sec, 7...8 in high, 19 in long.m4v",
                         # width=720, height=450,
                         # width=427, height=240,
                         # frameSkip=15,
                         loopVideo=False,
                         )

    while True:
        frame1 = camera1.updateFrame()

        camera1.showFrame(frame1)
        
        key = camera1.getPressedKey()


if __name__ == '__main__':
    run()
