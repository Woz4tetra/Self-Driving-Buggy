import sys
import time

import camera
import camera.analyzers
import arduino

import thread
import time


def run():
    arduino.initBoard(disabled=True, sketchDir="arduino/Serial Box")
    # camera1 = camera.Capture(windowName="camera",
    #                          cameraType="ELP",
    #                          # width=427, height=240,
    #                          # width=214, height=120,
    #                          sizeByFPS=31,
    #                          camSource=1
    #                          )
    camera1 = camera.Capture(windowName="camera",
                             camSource="IMG_0582.m4v",
                             # camSource="Sun Jul 26 13;21;49 2015.m4v",
                             width=640, height=360,
                             # width=427, height=240
                             # frameSkip=5,
                             loopVideo=False,
                             )


    # imu = arduino.IMU()
    stepper = arduino.Stepper(1)

    captureProperties = dict(
        paused=False,
        showOriginal=False,
        enableDraw=False,
        currentFrame=0,
        writeVideo=False,
    )

    # if captureProperties['paused'] == True:
    frame1 = camera1.updateFrame(readNextFrame=False)

    height, width = frame1.shape[0:2]
    position = [width / 2, height / 2]

    # tracker = camera.analyzers.SimilarFrameTracker(frame1)
    tracker = camera.analyzers.OpticalFlowTracker(frame1)

    while True:
        time0 = time.time()

        if captureProperties['paused'] is False or captureProperties[
            'currentFrame'] != camera1.currentFrameNumber():
            # time1 = time.time()
            frame1 = camera1.updateFrame()
            # print "update:", time.time() - time1

            captureProperties['currentFrame'] = camera1.currentFrameNumber()

            if captureProperties['showOriginal'] is False:
                frame1, delta = tracker.update(frame1, False)
                position[0] += delta[0]
                position[1] += delta[1]
                print "%s\t%s" % (position[0], position[1]),

                if captureProperties['enableDraw'] is True:
                    frame1 = camera.analyzers.drawPosition(frame1, width, height,
                                                           position, reverse=False)

            if captureProperties['writeVideo'] == True:
                camera1.writeToVideo(frame1)

            if captureProperties['enableDraw'] is True:
                camera1.showFrame(frame1)

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
            elif key == 't':
                if stepper.position == 0:
                    stepper.moveTo(1000)
                else:
                    stepper.moveTo(0)
            elif key == 'p':
                position = [width / 2, height / 2]

        print time.time() - time0, camera1.currentFrameNumber()


if __name__ == '__main__':
    arguments = sys.argv
    if "help" in arguments:
        raise NotImplementedError
    else:
        run()
