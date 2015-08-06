import cv2
import numpy
import copy
import time
import os

projectDir = os.path.dirname(os.path.realpath(__file__))

class Camera(object):
    excludedSources = set()
    increaseFPSActions = []

    resolutions = {
        "logitech": {
            8: (1920, 1080),
            12: (1440, 810),
            23: (960, 540),
            30: (480, 270),
            31: (240, 135),
            "default": 30
        },
        "ELP": {
            10: (2048, 1536),
            12: (1600, 1200),
            30: (1280, 720),
            31: (640, 480),
            32: (320, 240),
            "default": 30
        },
        "ELP180": {
            6: (1920, 1080),
            9: (1280, 720),
            21: (800, 600),
            30: (640, 480),
            31: (352, 288),
            32: (320, 240),
            "default": 30
        }
    }

    macKeyCodes = {
        63232: "up",
        63233: "down",
        63234: "left",
        63235: "right",
        27: "esc",
        13: "enter"
    }

    def __init__(self, windowName=None, camSource=None, width=None, height=None, sizeByFPS=None, cameraType=None,
                 crop=(None,) * 4, autoSelect=False):
        time1 = time.time()
        self.windowName = windowName
        self.camSource = camSource
        if self.windowName is None:
            self.enableDraw = False
        else:
            self.enableDraw = True

        self.sizeByFPS = sizeByFPS

        self.isRunning = True
        self.analysisApplied = False

        self.cameraType = cameraType

        self.cameraFPS = None

        self.trackbarName = "Frame"

        self.crop = list(crop)

        if cameraType is not None:
            self.resolutions = Camera.resolutions[cameraType]
        else:
            self.resolutions = Camera.resolutions["logitech"]

        if windowName is not None:
            cv2.namedWindow(windowName)
        
        if camSource is not None:
            if type(camSource) == str:
                self.loadVideo(camSource)
            else:
                self.loadCamera(camSource)
        else:
            if autoSelect is True:
                capture = self.searchForCamera()
            else:
                capture = self.cameraSelector()
            self.loadCamera(capture)

        if width is not None and height is not None:
            self.width, self.height = width, height
        elif self.sizeByFPS is not None:
            if (self.sizeByFPS in self.resolutions.keys()) is False:
                self.sizeByFPS = self.findClosestRes(sizeByFPS)
            self.width, self.height = self.resolutions[self.sizeByFPS]
        else:
            if type(self.camSource) == int:
                self.sizeByFPS = self.resolutions["default"]
                self.width, self.height = self.resolutions[self.sizeByFPS]
            else:
                self.width, self.height = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH), self.camera.get(
                    cv2.CAP_PROP_FRAME_HEIGHT)

        if type(self.camSource) == int:
            Camera.increaseFPSActions.append(self.increaseFPS)
            if len(Camera.increaseFPSActions) >= 2:
                for increaseFPS in Camera.increaseFPSActions:
                    increaseFPS()
                Camera.increaseFPSActions = []

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if self.crop[0] is None:
            self.crop[0] = 0
        if self.crop[1] is None:
            self.crop[1] = 0
        if self.crop[2] is None:
            self.crop[2] = self.width
        if self.crop[3] is None:
            self.crop[3] = self.height

        time2 = time.time()
        print str(self.camSource) + " loaded in " + str(time2 - time1) + " seconds. Capture size is " + \
              str(int(self.width)) + "x" + str(int(self.height))
    
    def cameraSelector(self):        
        shape = None
        windowName = "camera #"
        capture = 0
        
        def updateCapture(windowName, video, capture, delta=None, newCapture=None):
            print str(capture) + " ---> ",
            cv2.destroyWindow(windowName + str(capture))
            if delta is not None:
                capture += delta
            elif newCapture is not None:
                capture = newCapture
            print capture
            
            video = cv2.VideoCapture(capture)
            
            video.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
            video.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)
            
            return video, capture
        
        video = cv2.VideoCapture(capture)
            
        video.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        video.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)
        
        while True:
            key = self.getPressedKey(5)
            if key == "left":
                video, capture = updateCapture(windowName, video, capture, delta=-1)
            elif key == "right":
                video, capture = updateCapture(windowName, video, capture, delta=+1)
            elif type(key) == str and key.isdigit():
                video, capture = updateCapture(windowName, video, capture, newCapture=int(key))
            elif key == "enter":
                cv2.destroyWindow(windowName + str(capture))
                return capture
            elif key == 'q' or key == "esc":
                quit()
            
            success, frame = video.read()
            
            if success is True and frame is not None:
                cv2.imshow(windowName + str(capture), frame)
                shape = frame.shape
            else:
                cv2.imshow(windowName + str(capture), numpy.zeros(shape))
            
    
    def searchForCamera(self):
        success, frame = False, None
        capture = 0
        while True:
            temp = cv2.VideoCapture(capture)
            success, frame = temp.read()
            if (success is True or capture > 10) and (capture in Camera.excludedSources) == False:
                break
            capture += 1

        if success is False:
            capture = -1
            while True:
                temp = cv2.VideoCapture(capture)
                success, frame = temp.read()
                if (success is True or capture > 10) and (capture in Camera.excludedSources) == False:
                    break
                capture -= 1
        if success is False:
            raise Exception("Camera could not be found")

        return capture

    def loadCamera(self, capture):
        print "loading camera " + str(capture) + " into window named '" + str(self.windowName) + "'..."
        self.camera = cv2.VideoCapture(capture)
        self.camSource = capture
        Camera.excludedSources.add(capture)

    def loadVideo(self, camSource):
        print "loading video into window named '" + str(self.windowName) + "'..."
        self.camera = cv2.VideoCapture(projectDir + "/videos/" + camSource)
        print "video loaded!"

        self.cameraFPS = self.camera.get(cv2.CAP_PROP_FPS)

        cv2.createTrackbar(self.trackbarName, self.windowName, 0,
                           int(self.camera.get(cv2.CAP_PROP_FRAME_COUNT)), self.onSlider)

    def findClosestRes(self, sizeByFPS):
        possibleFPSs = numpy.array(self.resolutions.keys())
        minuend = copy.copy(possibleFPSs)
        minuend.fill(sizeByFPS)
        difference = possibleFPSs - minuend
        difference = numpy.absolute(difference)
        minimum = numpy.min(difference)
        index = numpy.where(difference == minimum)[0][0]
        return possibleFPSs[index]

    def stopCamera(self):
        self.isRunning = False
        self.camera.release()
        cv2.destroyWindow(self.windowName)

    def setFrame(self, frameNumber):
        if frameNumber >= self.camera.get(cv2.CAP_PROP_FRAME_COUNT):
            frameNumber = 0
        if type(self.camSource) == str and frameNumber >= 0:
            self.camera.set(cv2.CAP_PROP_POS_FRAMES, frameNumber)

    def incrementFrame(self):
        self.setFrame(self.camera.get(cv2.CAP_PROP_POS_FRAMES) + 1)

    def decrementFrame(self):
        self.setFrame(self.camera.get(
            cv2.CAP_PROP_POS_FRAMES) - 1.8)  # huh??? Refuses to go back otherwise. frames numbers aren't integers?!
        # cv2.CAP_PROP_POS_FRAMES) - 1)

    def saveFrame(self, frame):
        cv2.imwrite("images/" + time.strftime("%c").replace(":", "_") + ".png", frame)

    def increaseFPS(self):
        possibleFPSs = sorted(self.resolutions.keys())
        index = possibleFPSs.index(self.sizeByFPS)
        if (index + 1) < len(possibleFPSs):
            index += 1

        self.sizeByFPS = possibleFPSs[index]
        self.width, self.height = self.resolutions[self.sizeByFPS]
        self.setCameraSize(self.width, self.height)

    def setCameraSize(self, width=None, height=None):
        if self.width != None:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.width = width
        if self.height != None:
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.height = height

    def onSlider(self, frameIndex):
        if frameIndex != self.currentFrameNumber():
            self.camera.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
            self.showFrame(self.updateFrame(False))

    def getPressedKey(self, delay=1):
        key = cv2.waitKey(delay)
        if key in Camera.macKeyCodes:
            return Camera.macKeyCodes[key]
        elif key > -1:
            return chr(key)
        else:
            return key

    @staticmethod
    def delay(delay):
        cv2.waitKey(delay)

    def showFrame(self, frame):
        cv2.imshow(self.windowName, frame)

    def currentFrameNumber(self):
        return self.camera.get(cv2.CAP_PROP_POS_FRAMES)

    def getVideoFPS(self):
        return self.camera.get(cv2.CAP_PROP_FPS)

    def updateFrame(self, readNextFrame=True):
        if self.isRunning is False:
            self.stopCamera()
            return

        if readNextFrame is False:
            self.decrementFrame()

        success, frame = self.camera.read()
        if success is False or frame is None:
            if type(self.camSource) == int:
                raise Exception("Failed to read from camera!")
            else:
                self.setFrame(0)
                success, frame = self.camera.read()
        if frame.shape[0:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

        if self.crop is not None:
            x0, y0, x1, y1 = self.crop
            frame = frame[y0:y1, x0:x1]

        if readNextFrame is True:
            if type(self.camSource) == str:
                cv2.setTrackbarPos(self.trackbarName, self.windowName,
                                   int(self.camera.get(cv2.CAP_PROP_POS_FRAMES)))

        return frame