from Camera import Camera
from Arduino import Arduino
import Analyzers
import Commands
import sys


def run():

    Commands.arduino = Arduino(disabled=True, testMotor=(-100, 100), steering=(0, 179), button=None)
#    camera1 = Camera(windowName="camera",
#                     cameraType="ELP180",
#    )
    camera1 = Camera(windowName="camera",
                     camSource="Orca 11-2-14 Roll 5.mp4",
                     crop=(50, None, None, None),
                     width=427, height=240
                     )
#    camera1 = Camera(windowName="camera",
#                    camSource="IMG_0524.m4v",
#                    width=320, height=240
#    )

    Commands.knownDepth_meters, Commands.frameY_px = 50, camera1.height / 2
    Commands.knownWidth_meters, Commands.frameWidth_px = 30, camera1.width

    captureProperties = dict(
        paused=False,
        showOriginal=False,
        enableDraw=True,
        currentFrame=0,
        enableCamera2=False
    )

    if captureProperties['enableCamera2'] is True:
        camera2 = Camera(windowName="camera 2", cameraType="ELP")
    else:
        camera2 = None
    protocols = ["hill 1", " hill 2", "hill 2 transition", "hill 3 left 1", "hill 3 cross section 1", "hill 3 right",
                 "hill 3 cross section 2", "hill 3 left 2", "transition to chute", "chute", "transition to hill 4",
                 "hill 4", "hill 5"]

    current = 0
    courseFinished = False

    keys = ['q', "esc", ' ', 'o', "right", "left", 's', 'h']

    frame1 = None

    while courseFinished == False:
        key = camera1.getPressedKey()

        if captureProperties['paused'] is False or captureProperties['currentFrame'] != camera1.currentFrameNumber():
            frame1 = camera1.updateFrame()
            if captureProperties['enableCamera2'] is True:
                frame2 = camera2.updateFrame()
                frame1 = Analyzers.overlayCameras(frame1, frame2)

            height, width = frame1.shape[0:2]
            captureProperties['currentFrame'] = camera1.currentFrameNumber()

            road, contours = Analyzers.filterOutNonRoad(frame1, showSelectedPoints=False)
            road = Analyzers.balanceFrame(road)

            # rawLines = Analyzers.filterOutNonAsphalt(road)
            road = Analyzers.filterOutNonAsphalt(road)
            rawLines = None

            streetLeft, streetRight, streetCenter = Analyzers.findStreetCenterAndEdges(contours, (height, width))
            lines = Analyzers.filterOutIncorrectLines(rawLines, streetLeft, streetCenter, streetRight)

            if captureProperties['enableDraw'] is True:
                if captureProperties['showOriginal'] is False:
                    frame1 = Analyzers.combineFilters(road, contours, (streetLeft, streetCenter, streetRight), lines)
                camera1.showFrame(frame1)
                # camera2.showFrame(frame2)

            if protocols[current] == "hill 1" or protocols[current] == "hill 2":
                Commands.centerSelfBetweenTwoLines(lines)

            elif protocols[current] == "hill 2 transition":
                Commands.offsetFromRoadEdgeBy(streetCenter, -3)

            elif protocols[current] == "hill 3 left 1":
                Commands.stayAwayFromLeftLineBy(lines, 0.3)

            elif protocols[current] == "hill 3 cross section 1":
                Commands.offsetFromRoadEdgeBy(streetRight, -0.3)

            elif protocols[current] == "hill 3 right":
                Commands.stayAwayFromRightLineBy(lines, 0.3)

            elif protocols[current] == "hill 3 cross section 2":
                Commands.offsetFromRoadEdgeBy(streetLeft, 0.3)

            elif protocols[current] == "hill 3 left 2":
                Commands.stayAwayFromLeftLineBy(lines, 0.3)

            elif protocols[current] == "transition to chute":
                Commands.driveTowardsStoredLandmark()

            elif protocols[current] == "chute" or protocols[current] == "transition to hill 4":
                Commands.offsetFromRoadEdgeBy(streetRight, -0.3)

            elif protocols[current] == "hill 4":
                Commands.offsetFromRoadEdgeBy(streetCenter, 0)

            elif protocols[current] == "hill 5":
                Commands.offsetFromRoadEdgeBy(streetCenter, 0)
                if Analyzers.verticalFinishLineFound(lines):
                    courseFinished = True

            if Analyzers.checkForTransition(frame1, current, protocols) is True:
                current += 1

            if 0 < camera1.getVideoFPS() < 3:
                captureProperties['paused'] = True

        if key in keys:
            if key == 'q' or key == "esc":
                camera1.stopCamera()
                courseFinished = True
            elif key == ' ':
                captureProperties['paused'] = not captureProperties['paused']
            elif key == 'o':
                captureProperties['showOriginal'] = not captureProperties['showOriginal']
                frame1 = camera1.updateFrame(False)
            elif key == "right":
                camera1.incrementFrame()
            elif key == "left":
                camera1.decrementFrame()
            elif key == 's':
                camera1.saveFrame(frame1)
            elif key == 'h':
                captureProperties['enableDraw'] = not captureProperties['enableDraw']

                # camera.delay(5)

if __name__ == "__main__":
    arguments = sys.argv
    if "help" in arguments or "h" in arguments:
        print """run, r, or no parameters runs the program"""
    if "arduino" in arguments:
        from Demos import arduino_demo
        arduino_demo.run()
    if len(arguments) == 1 or "run" in arguments or "r" in arguments:
        run()