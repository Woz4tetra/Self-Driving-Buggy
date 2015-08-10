import numpy
import sys

import camera
import camera.analyzers
import arduino


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
                             camSource="IMG_0575.m4v"#"Sun Jul 26 13;22;56 2015.mp4v",
                             # width=427, height=240
                             )


    # imu = arduino.IMU()
    stepper = arduino.Stepper(1)

    captureProperties = dict(
        paused=True,
        showOriginal=False,
        enableDraw=True,
        currentFrame=0,
        writeVideo=False,
    )
    
    # if captureProperties['paused'] == True:
    frame1 = camera1.updateFrame(readNextFrame=False)

    tracker = camera.analyzers.SimilarFrameTracker(frame1)
    
    while True:
        # print imu.getData()

        key = camera1.getPressedKey()

        if captureProperties['paused'] is False or captureProperties[
            'currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()

            captureProperties['currentFrame'] = camera1.currentFrameNumber()

            if captureProperties['showOriginal'] is False:
                frame1 = tracker.update(frame1)
                # frame1 = camera.analyzers.drawContours(frame1)
                # frame1 = camera.analyzers.blur(frame1, 15)

            if captureProperties['writeVideo'] == True:
                camera1.writeToVideo(frame1)

            if captureProperties['enableDraw'] is True:
                camera1.showFrame(frame1)

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

if __name__ == '__main__':
    arguments = sys.argv
    if "help" in arguments:
        raise NotImplementedError
    else:
        run()



