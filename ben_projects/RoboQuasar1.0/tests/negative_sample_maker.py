"""
    Written by Ben Warwick
    
    scripts, written for RoboQuasar1.0
    Version 1/12/2015
    =========
    
    A test of the computer vision portion of the Self-Driving Buggy project.
    
    Usage
    -----
    python __main__.py
    - or - (in folder directory):
    python Self-Driving\ Buggy\ Rev.\ 6

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
"""

import sys
import cv2
import os
import numpy as np
import time

sys.path.insert(0, '../')

import config

from camera import capture
from camera import analyzers


def run():
    camera1 = capture.Capture(window_name="camera",
                              cam_source="Ascension 10-17 roll 3-2.mov",
                              # width=720, height=450,
                              # width=427, height=240,
                              frame_skip=25,
                              # loop_video=True,
                              # start_frame=1035
                              )

    capture_properties = dict(
        paused=False,
        apply_filters=False,
        enable_draw=True,
        currentFrame=camera1.currentFrameNumber(),
        write_video=False,
        slideshow=False,
        burst_mode=False,
        make_negative_samples=True
    )

#    project_dir = os.path.dirname(os.path.realpath(__file__))
#    project_name = "Self-Driving Buggy Rev. 6"
#    project_dir = project_dir[:project_dir.rfind(project_name) + len(
#        project_name)]
#
#    scenes = []
#    for file_name in os.listdir(project_dir + "/camera/Images"):
#        if file_name.rfind(".png") != -1:
#            scenes.append(
#                cv2.imread(project_dir + "/camera/Images/" + file_name))
#
#    scene_tracker = analyzers.SceneTracker(scenes)
    frame1 = camera1.updateFrame(readNextFrame=False)
    height, width = frame1.shape[0:2]

    time_start = time.time()

    while camera1.isRunning:
        if capture_properties['paused'] == False or capture_properties[
            'currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()
            
            if frame1 == None:
                continue

            capture_properties['currentFrame'] = camera1.currentFrameNumber()

            if capture_properties['apply_filters']:
                pass
            if capture_properties['enable_draw'] is True:
                camera1.showFrame(frame1)

            if capture_properties['write_video'] == True:
                camera1.writeToVideo(frame1)

        if capture_properties['slideshow'] == True:
            capture_properties['paused'] = True

        if capture_properties['burst_mode'] == True and capture_properties[
                'paused'] == False:
            camera1.saveFrame(frame1, burst_mode=True)
        elif capture_properties['burst_mode'] == False and capture_properties[
                'make_negative_samples']:
            camera1.saveFrame(frame1, burst_mode=True, directory=config.get_dir(":images") + "negatives/")

        if capture_properties['enable_draw'] is True:
            key = camera1.getPressedKey()
            if key == 'q' or key == "esc":
                camera1.stopCamera()
                break
            elif key == ' ':
                if capture_properties['paused']:
                    print(time.time() - time_start, ": ...Video unpaused")
                else:
                    print(time.time() - time_start, ": Video paused...")
                capture_properties['paused'] = not capture_properties['paused']
            elif key == 'o':
                capture_properties['apply_filters'] = not capture_properties[
                    'apply_filters']
                print((
                    "Applying filters is " + str(
                        capture_properties['apply_filters'])))
                frame1 = camera1.updateFrame(False)
            elif key == "right":
                camera1.incrementFrame()
            elif key == "left":
                camera1.decrementFrame()
            elif key == 's':
                camera1.saveFrame(frame1)
            elif key == 'h':
                capture_properties['enable_draw'] = not capture_properties[
                    'enable_draw']
            elif key == 'v':
                if capture_properties['write_video'] == False:
                    camera1.initVideoWriter()
                else:
                    camera1.stopVideo()
                capture_properties['write_video'] = not capture_properties[
                    'write_video']
            elif key == 'b':  # burst photo mode
                capture_properties['burst_mode'] = not capture_properties[
                    'burst_mode']
                print(("Burst mode is " + str(capture_properties['burst_mode'])))
            elif key == 'p':  # debug print
                print("Frame #:", camera1.currentFrameNumber())


if __name__ == '__main__':
    print(__doc__)

    arguments = sys.argv
    if "help" in arguments:
        raise NotImplementedError
    else:
        run()
