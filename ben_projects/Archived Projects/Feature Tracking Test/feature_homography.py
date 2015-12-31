#!/usr/bin/env python

'''
Feature homography
==================

Example of using features2d framework for interactive video homography matching.
ORB features and FLANN matcher are used. The actual tracking is implemented by
PlaneTracker class in plane_tracker.py

Inspired by http://www.youtube.com/watch?v=-ZNYoL8rzPY

video: http://www.youtube.com/watch?v=FirtmYcC0Vc

Usage
-----
feature_homography.py [<video source>]

Keys:
   SPACE  -  pause video

Select a textured planar object to track by drawing a box with a mouse.
'''

import numpy as np
import cv2

# local modules
import video
import common
from common import getsize, draw_keypoints
from plane_tracker import PlaneTracker


class App:
    def __init__(self, src):
        print src
        self.cap = video.create_capture(src)
        
        self.tracker = PlaneTracker()
        self.proceed = True
        
        cv2.namedWindow('plane')
        
        success, self.frame = self.cap.read()
        w, h = getsize(self.frame)
        
        self.position = [w / 2, h / 2]
        
        self.tracker.clear()
        self.tracker.add_target(self.frame)
    
    @staticmethod
    def centroid(quad):
        x = quad[:, 0]
        y = quad[:, 1]
        return np.average(x), np.average(y)
    
    @staticmethod
    def drawPosition(frame, width, height, position, reverse=True):
        color = position[0] % 256, position[1] % 256, \
                np.random.randint(0, 255)
        if reverse == True:
            position = width - int(position[0]), height - int(position[1])
        else:
            position = int(position[0]), int(position[1])
        return cv2.circle(frame, position, 4, color, 2)
    
    def run(self):
        while True:
            if self.proceed == True:
                success, self.frame = self.cap.read()
                if not success:
                    break
                
                w, h = getsize(self.frame)
                vis = np.zeros((h, w*2, 3), np.uint8)
                vis[:h,:w] = self.frame
                if len(self.tracker.targets) > 0:
                    target = self.tracker.targets[0]
                    vis[:,w:] = target.image
                    draw_keypoints(vis[:,w:], target.keypoints)
                    x0, y0, x1, y1 = target.rect
                    cv2.rectangle(vis, (x0+w, y0), (x1+w, y1), (0, 255, 0), 2)
                
                tracked = self.tracker.track(self.frame)
                if len(tracked) > 0:
                    tracked = tracked[0]
                    cv2.polylines(vis, [np.int32(tracked.quad)], True, (255, 255, 255), 2)
                    for (x0, y0), (x1, y1) in zip(np.int32(tracked.p0), np.int32(tracked.p1)):
                        cv2.line(vis, (x0+w, y0), (x1, y1), (0, 255, 0))
                    
                    draw_keypoints(vis, self.tracker.frame_points)
                    
                    centroid = App.centroid(tracked.quad)
                    delta = [w / 2 - centroid[0], h / 2 - centroid[1]]
                    self.position[0] += delta[0]
                    self.position[1] += delta[1]
                    
                    App.drawPosition(vis, w, h, self.position)
                    print self.position
                    
                self.tracker.clear()
                self.tracker.add_target(self.frame)
                
                cv2.imshow('plane', vis)
            
#            self.proceed = False
            
            ch = cv2.waitKey(1)
            if ch == ord(' '):
                self.proceed = True
            if ch == ord('c'):
                self.tracker.clear()
                self.tracker.add_target(self.frame)
#                vis[:,w:] = target.image
            if ch == 27:
                break


if __name__ == '__main__':
    print __doc__

    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    App(video_src).run()
