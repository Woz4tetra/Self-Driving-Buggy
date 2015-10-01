'''
Written by Ben Warwick

Self-Driving Buggy Rev. 6 for Self-Driving Buggy PRoject
Version 9/15/2015
=========

(temp description)
This program controls the self-driving buggy. It manages computer vision,
microcontroller control and data collection, PID feedback, encoder to x, y
algorithms, path finding, GPS algorithms, and IMU algorithms. Each of these is
implemented in its own file.

Usage
-----
python __main__.py

- or - (in folder directory):
python Self-Driving Buggy Rev. 6

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

from camera import capture
from camera import analyzers


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
                             # camSource="0.33 sec, 7...8 in high, 19 in long.m4v",
                             # width=720, height=450,
                             # width=427, height=240,
                             # frameSkip=15,
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
    # height, width = frame1.shape[0:2]
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
                # frame1 = analyzers.contrast(frame1, 2.1)
                frame1 = analyzers.blur(frame1, 7)
                frame1 = analyzers.threshold_filter(frame1)
                # frame1 = analyzers.sobel_filter(frame1)

                # frame1, delta = tracker.update(frame1, enableDraw=True)
                # position[0] += delta[0]
                # position[1] += delta[1]
                # print "%s\t%s" % (position[0], position[1])

                # if captureProperties['enableDraw'] is True:
                #     frame1 = analyzers.drawPosition(frame1, width,
                #                                            height,
                #                                            position,
                #                                            reverse=True)

            if captureProperties['writeVideo'] == True:
                camera1.writeToVideo(frame1)

            if captureProperties['enableDraw'] is True:
                camera1.showFrame(frame1)

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
