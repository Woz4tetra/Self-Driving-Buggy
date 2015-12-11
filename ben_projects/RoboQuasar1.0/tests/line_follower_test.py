'''
Written by Ben Warwick
With line analysis portion added by Elim Zhang

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
    d - show average lines on screen
    a - show all lines found on screen within number tolerance
'''

import sys
import cv2
import os
import numpy as np
import math

import time

sys.path.insert(0, '../')
from camera import capture
from camera import analyzers

def run_session(file, assert_fn, expected, y_bottom, loop_video=False):
    camera1 = capture.Capture(window_name="line follow test: " + file,
                              cam_source= 'Orca 10-10 roll 4.mov',
                              loop_video=False)

    capture_properties = dict(
        paused=False,
        apply_filters=True,
        enable_draw=enable_draw_global,
        draw_avg=True, 
        draw_all=False,
        currentFrame=camera1.currentFrameNumber(),
        write_video=False,
        slideshow=False,
        burst_mode=False,
    )
    
    frame1 = camera1.updateFrame(readNextFrame=False)
    height, width = frame1.shape[0:2] 

    
    line_follower = analyzers.LineFollower(expected, y_bottom, width, height)
    
    time_start = time.time()
    
    while camera1.isRunning:
        if capture_properties['paused'] == False or capture_properties[
            'currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()
            
            if frame1 is None:
                continue

            capture_properties['currentFrame'] = camera1.currentFrameNumber()

            if capture_properties['apply_filters']:
                # ============================== #
                # ===== line follower code ===== #
                # ============================== #
                
                frame1, result = line_follower.update(frame1, 
                    capture_properties['draw_avg'], 
                    capture_properties['draw_all'])
                assert_fn(result, expected, capture_properties['currentFrame'])

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
                print "KEY TO STOP"
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

            elif key == 'd':
                capture_properties['draw_avg'] = not capture_properties[
                    'draw_avg']
            elif key == 'a':
                capture_properties['draw_all'] = not capture_properties[
                    'draw_all']

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

def assert_result((result_angle, result_x), 
                  (expected_angle, expected_x),
                  (error_angle, error_x)):
    if expected_angle != None and expected_x != None:
        assert abs(result_angle - expected_angle) < error_angle and \
            abs(result_x - expected_x) < error_x

def test_blank(result, expected, frame_num):
    assert_result(result, expected, (0, 0))

def test_bw1(result, expected, frame_num):
    expected[0] -= frame_num * 10  # rho decreases by 10 each frame
    assert_result(result, expected, (math.pi / 180, 5))

def test_bw2(result, expected, frame_num):
    expected[0] -= frame_num * 10
    assert_result(result, expected, (5 * math.pi / 180, 10))

def test_bw3(result, expected, frame_num):
    expected[1] -= 5 * math.pi / 180 * frame_num  # theta decreases by 5 degrees each frame
    assert_result(result, expected, (0, 0))


def test_all():
    run_session("line_follow_test_blank.mov", test_blank,
                (None, None), 360)
#     run_session("line_follow_test_bw1.mov", test_blank,
#                # (640 / 2, 0), 360)
#                 (None, None), 360)
#     run_session("line_follow_test_bw2.mov", test_blank,
# #                (640 / 2, 0), 360)
#                 (None, None), 360)
#     run_session("line_follow_test_bw3.mov", test_blank,
# #                (640 / 2, 0), 360, True)
#                 (None, None), 360)
    

# if __name__ == '__main__':
#     print __doc__
    
#     enable_draw_global = True
    
#     test_all()
enable_draw_global = True
test_all()
