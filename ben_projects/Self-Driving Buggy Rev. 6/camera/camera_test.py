'''
Written by Ben Warwick

Self-Driving Buggy Rev. 6 for Self-Driving Buggy PRoject
Version 9/15/2015
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
    v - start/stop create video (saved in camera/Videos/ directory)
    h - toggle enable draw (hide/show video feed)
'''

import sys
import cv2
import numpy as np

import capture
import analyzers


def run():
    # camera1 = camera.Capture(windowName="camera",
    #                          cameraType="ELP",
    #                          # width=427, height=240,
    #                          # width=214, height=120,
    #                          sizeByFPS=31,
    #                          camSource=0
    #                          )
    camera1 = capture.Capture(windowName="camera",
                              camSource="Impulse 10-12-14 Roll 2.mov",
                              # width=720, height=450,
                              # width=427, height=240,
                              frameSkip=200,
                              loopVideo=True,
                              )

    captureProperties = dict(
        paused=False,
        showOriginal=False,
        enableDraw=True,
        currentFrame=0,
        writeVideo=False,
        slideshow=False,
    )

    frame1 = camera1.updateFrame(readNextFrame=False)
    height, width = frame1.shape[0:2]
    # position = [width / 2, height / 2]
    # tracker = analyzers.SimilarFrameTracker(frame1)
    # tracker = analyzers.OpticalFlowTracker(frame1)

    while True:
        # time0 = time.time()
        if captureProperties['paused'] is False or captureProperties[
            'currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()

            captureProperties['currentFrame'] = camera1.currentFrameNumber()

            if captureProperties['showOriginal'] is False:
                # frame_thresh = cv2.medianBlur(frame1, 5)
                # frame_thresh = analyzers.sobel_filter(frame_thresh)
                # frame_thresh = cv2.cvtColor(frame_thresh, cv2.COLOR_BGR2GRAY)
                # value, frame_thresh = cv2.threshold(frame_thresh, 20, 255,
                #                                     cv2.THRESH_BINARY)
                # frame_thresh = cv2.dilate(frame_thresh, (4, 4), iterations=2)
                # frame1 = analyzers.erode_filter(frame_thresh, kernel=(3, 3))
                # frame_thresh = analyzers.auto_canny(frame_thresh)

                frame1 = cv2.medianBlur(frame1, 3)
                frame1 = analyzers.auto_canny(frame1)
                frame1 = cv2.dilate(frame1, (4, 4), iterations=3)

                # frame1 = np.concatenate((frame_thresh, frame_canny), axis=0)
                # frame1 = cv2.resize(frame1, (width / 2, height))

                # frame1 = cv2.bitwise_and(frame_thresh, frame_canny)

                frame1 = analyzers.drawContours(frame1, 20, 0.01)

            if captureProperties['enableDraw'] is True:
                camera1.showFrame(frame1)

            if captureProperties['writeVideo'] == True:
                camera1.writeToVideo(frame1)

        if captureProperties['slideshow'] == True:
            captureProperties['paused'] = True

        if captureProperties['enableDraw'] is True:
            # time2 = time.time()
            key = camera1.getPressedKey()
            # print "key:", time.time() - time2

            if key == 'q' or key == "esc":
                camera1.stopCamera()
                break
            elif key == ' ':
                if captureProperties['paused']:
                    print "...Video unpaused"
                else:
                    print "Video paused..."
                captureProperties['paused'] = not captureProperties['paused']
            elif key == 'o':
                captureProperties['showOriginal'] = not captureProperties[
                    'showOriginal']
                print(
                "Show original is " + str(captureProperties['showOriginal']))
                frame1 = camera1.updateFrame(False)
            elif key == "right":
                camera1.incrementFrame()
            elif key == "left":
                camera1.decrementFrame()
            elif key == 's':
                camera1.saveFrame(frame1)
            elif key == 'h':
                captureProperties['enableDraw'] = not captureProperties[
                    'enableDraw']
            elif key == 'v':
                if captureProperties['writeVideo'] == False:
                    camera1.initVideoWriter()
                else:
                    camera1.stopVideo()
                captureProperties['writeVideo'] = not captureProperties[
                    'writeVideo']
                # elif key == 'c':
                #     position = [width / 2, height / 2]
                # print "    :", (time.time() - time0)


if __name__ == '__main__':
    print __doc__

    arguments = sys.argv
    if "help" in arguments:
        raise NotImplementedError
    else:
        run()