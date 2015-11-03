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

import time

from camera import capture
from camera import analyzers

def test_all():
    

def test_blank():
    

if __name__ == '__main__':
    print __doc__
    
    if "help" in arguments:
        raise NotImplementedError
    else:
        test_all()
