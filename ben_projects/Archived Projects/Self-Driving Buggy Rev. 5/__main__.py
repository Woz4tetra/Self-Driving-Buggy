import sys
import time

import camera
from camera import analyzers
import arduino


def run():
    arduino.initBoard(disabled=True, sketchDir="arduino/Serial Box")
    # camera1 = camera.Capture(windowName="camera",
    #                          cameraType="ELP",
    #                          # width=427, height=240,
    #                          # width=214, height=120,
    #                          sizeByFPS=31,
    #                          camSource=0
    #                          )
    camera1 = camera.Capture(windowName="camera",
                             camSource="Down camera, Course Run 1, 4.5 ft, 9-2-15, 30 fps.m4v",
                             # camSource="0.33 sec, 7...8 in high, 19 in long.m4v",
                             # width=720, height=450,
                             # width=427, height=240,
                             # frameSkip=15,
                             loopVideo=False,
                             )

    captureProperties = dict(
        paused=False,
        showOriginal=True,
        enableDraw=True,
        currentFrame=0,
        writeVideo=False,
        slideshow=False,
    )

    frame1 = camera1.updateFrame(readNextFrame=False)
    height, width = frame1.shape[0:2]
    position = [width / 2, height / 2]
    tracker = analyzers.SimilarFrameTracker(frame1)
    # tracker = analyzers.OpticalFlowTracker(frame1)

    while True:
        # time0 = time.time()
        if captureProperties['paused'] is False or captureProperties[
                'currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()

            captureProperties['currentFrame'] = camera1.currentFrameNumber()

            if captureProperties['showOriginal'] is False:
                # frame1 = analyzers.sobel_filter(frame1)
                frame1, delta = tracker.update(frame1, enableDraw=True)
                position[0] += delta[0]
                position[1] += delta[1]
                print "%s\t%s" % (position[0], position[1])

                if captureProperties['enableDraw'] is True:
                    frame1 = analyzers.drawPosition(frame1, width,
                                                           height,
                                                           position,
                                                           reverse=True)

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
            elif key == 'c':
                position = [width / 2, height / 2]
        # print "    :", (time.time() - time0)


if __name__ == '__main__':
    arguments = sys.argv
    if "help" in arguments:
        raise NotImplementedError
    else:
        run()
