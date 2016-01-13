"""
    Written by Ben Warwick
    
    scripts, written for RoboQuasar1.0
    Version 1/12/2015
    =========
    
    A test of the computer vision portion of the selectionf-Driving Buggy project.
    
    Usage
    -----
    python __main__.py
    - or - (in folder directory):
    python selectionf-Driving\ Buggy\ Rev.\ 6

    Keys
    ----
        q, ESC - exit
        SPACE - play/pause video
        o - toggle show original video feed
        left - read previous frame
        right - read next frame
        s - save frame as image (in camera/Images/ directory)
        h - toggle enable draw (hide/show video feed)
        v - start/stop create video (saved in camera/Videos/ directory)
        b - burst mode. Save every frame as an image into camera/Images

    unpaused - write background image move to next frame
    hit space or click - pause
    drag - draw rectangle
    hit space - go to unpaused
    hit enter - write image in rectangle, move to next frame

"""

import sys
import cv2

sys.path.insert(0, '../')

import config

from camera import capture

drag_start = None
selection = (0, 0, 0, 0)
camera1 = capture.Capture(window_name="camera",
                          cam_source="Ascension 10-17 roll 3-2.mov",
                          # width=720, height=450,
                          # width=427, height=240,
                          frame_skip=25,
                          # loop_video=True,
                          # start_frame=1035
                          )
paused = False


def on_mouse(event, x, y, flags, param):
    global drag_start, selection
    if event == cv2.EVENT_LBUTTONDOWN:
        drag_start = x, y
        selection = 0, 0, 0, 0
    elif event == cv2.EVENT_LBUTTONUP:
        drag_start = None
    elif drag_start:
        if flags & cv2.EVENT_FLAG_LBUTTON:
            minpos = min(drag_start[0], x), min(drag_start[1], y)
            maxpos = max(drag_start[0], x), max(drag_start[1], y)
            selection = minpos[0], minpos[1], maxpos[0], maxpos[1]

            camera1.showFrame(cv2.rectangle(camera1.frame.copy(),
                                            (selection[0], selection[1]),
                                            (selection[2], selection[3]),
                                            (255, 255, 255), 1))

        else:
            drag_start = None


def run():
    global paused
    cv2.setMouseCallback(camera1.windowName, on_mouse)
    while camera1.isRunning:
        if paused == False:
            camera1.getFrame()
            camera1.showFrame()
        else:
            camera1.saveFrame(
                directory=config.get_dir(":images") + "negatives/")

        if camera1.frame is None:
            continue

        key = camera1.getPressedKey()
        if key == 'q' or key == "esc":
            camera1.stopCamera()
            break
        elif key == ' ':
            if paused:
                print("...Video unpaused")
            else:
                print("Video paused...")
            paused = not paused

        elif key == 'enter' and paused:
            cropped = camera1.frame[selection[1]: selection[3],
                                    selection[0]: selection[2]]
            camera1.saveFrame(cropped,
                    directory=config.get_dir(":images") + "positives/")
            camera1.incrementFrame()

            camera1.getFrame()
            camera1.showFrame(cv2.rectangle(camera1.frame.copy(),
                                            (selection[0], selection[1]),
                                            (selection[2], selection[3]),
                                            (255, 255, 255), 1))
            print("Positive frame saved!")


if __name__ == '__main__':
    print(__doc__)

    arguments = sys.argv
    if "help" in arguments:
        raise NotImplementedError
    else:
        run()
