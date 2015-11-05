'''
Written by Ben Warwick

Self-Driving Buggy Rev. 6 for Self-Driving Buggy Project
Version 11/3/2015
=========

A test of the line following portion of the Self-Driving Buggy project.

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
    v - start/stop create video (saved in camera/Videos/ directory)
    h - toggle enable draw (hide/show video feed)
'''

import sys
import cv2
import os
import numpy as np
import math

import time

from camera import capture
from camera import analyzers

def run_session(file, test_function, center_line_x, center_line_angle, loop_video):
    camera1 = capture.Capture(window_name="line follow test: " + file,
                              cam_source=file,
                              # width=720, height=450,
                              # width=427, height=240,
                              # frame_skip=25,
                              loop_video=loop_video,
                              # start_frame=1035
                              )

    capture_properties = dict(
        paused=False,
        apply_filters=True,
        enable_draw=True,
        currentFrame=camera1.currentFrameNumber(),
        write_video=False,
        slideshow=False,
        burst_mode=False,
    )
    
    frame1 = camera1.updateFrame(readNextFrame=False)
    height, width = frame1.shape[0:2]
    
    if center_line_x == None:
        center_line_x = width / 2
    if center_line_angle == None:
        center_line_angle = math.pi / 2
    
    line_follower = analyzers.LineFollower(center_line_x, center_line_angle)
    
    time_start = time.time()
    
    while camera1.isRunning:
        if capture_properties['paused'] == False or capture_properties[
            'currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()
            
            if frame1 == None:
                continue

            capture_properties['currentFrame'] = camera1.currentFrameNumber()

            if capture_properties['apply_filters']:
                test_function(frame1, line_follower, capture_properties['currentFrame'])

            if capture_properties['enable_draw'] is True:
                camera1.showFrame(frame1)

            if capture_properties['write_video'] == True:
                camera1.writeToVideo(frame1)

        if capture_properties['slideshow'] == True:
            capture_properties['paused'] = True

        if capture_properties['burst_mode'] == True and capture_properties[
                'paused'] == False:
            camera1.saveFrame(frame1, burst_mode=True)

        if capture_properties['enable_draw'] is True:
            key = camera1.getPressedKey()
            if key == 'q' or key == "esc":
                camera1.stopCamera()
            elif key == ' ':
                if capture_properties['paused']:
                    print time.time() - time_start, ": ...Video unpaused"
                else:
                    print time.time() - time_start, ": Video paused..."
                capture_properties['paused'] = not capture_properties['paused']
            elif key == 'o':
                capture_properties['apply_filters'] = not capture_properties[
                    'apply_filters']
                print(
                    "Applying filters is " + str(
                        capture_properties['apply_filters']))
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
                print("Burst mode is " + str(capture_properties['burst_mode']))
            elif key == 'p':  # debug print
                print "Frame #:", capture_properties['currentFrame']

def assert_correct_result(result, expected_x, expected_angle,
                          x_error=None, angle_error=None):
    if expected_x == None and expected_angle == None:
        assert result == (None, None)
    else:
        assert result[0] != None
        assert result[1] != None
        assert (result[0] - expected_x) == x_error
        assert (result[1] - expected_angle) == angle_error

def test_blank(frame, line_follower, frame_num):
    assert_correct_result(line_follower.update(frame), None, None)

def test_binary(frame, line_follower, frame_num):
    assert_correct_result(line_follower.update(frame),
                          (frame_num - 1) * 10, math.pi / 2,
                          1, 0)   # 1 px, 0 degrees of error

def test_binary_blurry(frame, line_follower, frame_num):
    assert_correct_result(line_follower.update(frame),
                          -(frame_num - 1) * 10, math.pi / 2,
                          3, math.pi / 180)  # 3 px, 1 degree of error

def test_binary_angle(frame, line_follower, frame_num):
    assert_correct_result(line_follower.updateFrame(frame,
                          frame_num * 25,
                          math.pi / 2 - (5 * math.pi / 180 * (frame_num - 1)),
                          3, 3 * math.pi / 180))  # 3 px, 3 degrees of error

def test_all():
    run_session("line_follow_test_blank.mov", test_blank, None, None, False)
    run_session("line_follow_test_bw1.mov", test_binary, None, None, False)
    run_session("line_follow_test_bw2.mov", test_binary_blurry, None, None, True)
    run_session("line_follow_test_bw3.mov", test_binary_angle, None, None, True)
    

if __name__ == '__main__':
    print __doc__
    
    test_all()
