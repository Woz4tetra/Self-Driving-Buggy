from Camera import Analyzer
import cv2, numpy
import bisect
from PlaneTracker import PlaneTracker
import time, copy

class StreetAnalyzer(Analyzer):
    def __init__(self, priority, arduino, showSelectedPoints):
        self.dirtRange1 = (21, 45, 45), (40, 255, 255)
        self.dirtRange2 = (210, 30, 45), (255, 255, 255)
        self.greenRange = (45, 25, 25), (127, 255, 255)

        self.sampleWidth = None
        self.sampleStart = None
        self.sampleEnd = None

        self.confidence = 1.0

        self.arduino = arduino

        self.showSelectedPoints = showSelectedPoints

        Analyzer.__init__(self, self.analyzeFrame, priority)

    def analyzeFrame(self, frame, enableDraw):
        """
        Abides by the Camera.Analyzer format. Takes the input frame and finds the street edges and commands the
        appropriate value to the Arduino.

        :param frame: A 3D numpy array containing the image
        :param enableDraw: If window isn't being shown, no need to draw on the frame
        :return: The modified frame showing the street edges (if enableDraw == True)
        """

        height, width = frame.shape[0:2]

        frameHSV = cv2.GaussianBlur(frame, (35, 35), 5)
        # frameHSV = cv2.medianBlur(frame, 35)  # blur to remove noise from road and grass
        frameBGR = copy.copy(frameHSV)

        frameHSV = cv2.cvtColor(frameHSV, cv2.COLOR_BGR2HSV_FULL)  # convert to hue, saturation, value color space
        markers = numpy.zeros((height, width), numpy.int32)  # create markers for watershed algorithm

        # A portion of the road is always within y% of the image vertically and an x% of the image
        # horizontally. Take the colors that appear there and find them in the rest of the image. These points should
        # mark a good portion of the road. Mark them on the watershed marker image as "1"
        if self.sampleWidth is None and self.sampleStart is None and self.sampleEnd is None:
            self.sampleWidth = width / 8
            self.sampleStart = [4 * height / 5, width / 2 - self.sampleWidth / 2]
            self.sampleEnd = [height, width / 2 + self.sampleWidth / 2]

        if self.confidence < 0.08:
            self.sampleStart[0] -= 5
        else:
            self.sampleStart[0] += 5

        if self.sampleStart[0] < height / 4:
            self.sampleStart[0] = height / 4
        if self.sampleStart[0] >= 4 * height / 5:
            self.sampleStart[0] = 4 * height / 5
        streetPoints = StreetAnalyzer.getPointsWithSimilarColors(frameBGR, self.sampleStart, self.sampleEnd, 1)
        markers[streetPoints] = 1

        # find the points on the image that are green
        # mark them on the watershed marker image as "2"
        markers[StreetAnalyzer.pointsInRange(frameHSV, *self.greenRange)] = 2

        markers[StreetAnalyzer.pointsInRange(frameHSV, *self.dirtRange1)] = 2
        markers[StreetAnalyzer.pointsInRange(frameHSV, *self.dirtRange2)] = 2

        if self.showSelectedPoints is True:
            frame = StreetAnalyzer.getEdgesUsingMarkers(frameBGR, markers, self.showSelectedPoints)
        else:
            # Apply the watershed algorithm and threshold it to get the road
            edges = StreetAnalyzer.getEdgesUsingMarkers(frameBGR, markers, self.showSelectedPoints)
            contours = StreetAnalyzer.getSignificantContours(edges)[-1:]  # get the largest contour
            if enableDraw == True:
                cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

            if len(contours) > 0:
                # extract the points that accurately mark the edges of the road
                leftPoints, rightPoints = StreetAnalyzer.getLeftAndRightPoints(contours[0], width, height)

                if len(leftPoints) > 0 and len(rightPoints) > 0:
                    # flip the x and y axis (the center of the road is a function of its horizontal edges)
                    leftPoints = numpy.roll(leftPoints, 1, 1)
                    rightPoints = numpy.roll(rightPoints, 1, 1)

                    # get best quadratic approximation using left and right edges
                    leftCoeffs = StreetAnalyzer.getQuadraticFit(leftPoints)
                    rightCoeffs = StreetAnalyzer.getQuadraticFit(rightPoints)

                    if leftCoeffs is not None and rightCoeffs is not None:
                        combined = numpy.append(leftCoeffs, rightCoeffs).reshape((2, 3))
                        combinedCoeffs = numpy.average(combined, axis=0)

                        self.confidence = float(leftPoints[:, 0].max(0) - leftPoints[:, 0].min(0)) / height

                        if enableDraw == True:
                            StreetAnalyzer.plotQuadratic(frame, leftPoints, leftCoeffs, axis=1)
                            StreetAnalyzer.plotQuadratic(frame, rightPoints, rightCoeffs, axis=1)
                            StreetAnalyzer.plotQuadratic(frame, rightPoints, combinedCoeffs, axis=1)

                            # linLeftCoeffs = StreetAnalyzer.getLinearRegression(leftPoints)
                            # linRightCoeffs = StreetAnalyzer.getLinearRegression(rightPoints)
                            #
                            # leftPlotBounds = [leftPoints[:, 0].min(0), leftPoints[:, 0].max(0)]
                            # rightPlotBounds = [leftPoints[:, 0].min(0), leftPoints[:, 0].max(0)]
                            # StreetAnalyzer.plotLine(frame, linLeftCoeffs, axis=1, xPlotStart=leftPlotBounds[0],
                            # xPlotEnd=leftPlotBounds[1])
                            # StreetAnalyzer.plotLine(frame, linRightCoeffs, axis=1, xPlotStart=rightPlotBounds[0],
                            #                         xPlotEnd=rightPlotBounds[1])

                    else:  # Enter therapy. Self confidence is zero...
                        self.confidence = 0.0

        if enableDraw == True:
            cv2.rectangle(frame, (self.sampleStart[1], self.sampleStart[0]),
                          (self.sampleEnd[1], self.sampleEnd[0]), (255, 100, 100), 2)
            return frame
        else:
            return None

    def signalServo(self, servoVal):
        if servoVal < 0:
            servoVal = 0

        if servoVal > 179:
            servoVal = 179

        self.arduino._sendCommand("steering", servoVal)

    @staticmethod
    def getLinearRegression(points):
        n = len(points)
        x = points[:, 0]
        y = points[:, 1]

        slope = (n * numpy.sum(x * y) - numpy.sum(x) * numpy.sum(y)) / (n * numpy.sum(x ** 2) - numpy.sum(x) ** 2)
        offset = (numpy.sum(y) - slope * numpy.sum(x)) / n

        return slope, offset

    @staticmethod
    def plotLine(frame, xxx_todo_changeme, axis=0, color=(0, 100, 255), xPlotStart=None,
                 xPlotEnd=None):
        (slope, offset) = xxx_todo_changeme
        xPlotPoints = [0, 100]  # [points[:, 0].min(0), points[:, 0].max(0)]  # find the start and end points to plot
        if xPlotStart is not None:
            xPlotPoints[0] = xPlotStart

        if xPlotEnd is not None:
            xPlotPoints[1] = xPlotEnd

        for x in range(*xPlotPoints):
            estY = int(slope * x + offset)

            # axis indicates if the points were flipped or not
            if axis == 0:
                point = (x, estY)
            else:
                point = (estY, x)

            # draw the calculated point
            cv2.circle(frame, point, 1, color, 2)


    @staticmethod
    def plotQuadratic(frame, points, xxx_todo_changeme1, axis=0, color=(0, 100, 255), xPlotStart=None,
                      xPlotEnd=None):
        """
        Plots a quadratic on the input frame using the input coefficients

        :param frame: A 3D numpy array. The image on which the quadratic will be drawn
        :param points: The data used to derive the quadratic. Only used to get default start and end points of plot
        :param axis: axis 0 indicates x and y have not been flipped. axis 1 does
        :param color: the BGR color space value to color the quadratic points
        :param xPlotStart: override plot start by providing a value here
        :param xPlotEnd: override plot end by providing a value here
        :return: the points used to plot quadratic
        """
        (cCoeff, xCoeff, x2Coeff) = xxx_todo_changeme1
        quadratic = []

        xPlotPoints = [points[:, 0].min(0), points[:, 0].max(0)]  # find the start and end points to plot
        if xPlotStart is not None:
            xPlotPoints[0] = xPlotStart

        if xPlotEnd is not None:
            xPlotPoints[1] = xPlotEnd

        for x in range(*xPlotPoints):
            # use calculated coefficients to get estimated street edge
            estY = int(x2Coeff * (x ** 2) + xCoeff * x + cCoeff)

            # axis indicates if the points were flipped or not
            if axis == 0:
                point = (x, estY)
            else:
                point = (estY, x)

            # draw the calculated point
            cv2.circle(frame, point, 1, color, 2)
            quadratic.append(point)

        return numpy.array(quadratic)

    @staticmethod
    def getQuadraticFit(points):
        """
        Finds the best quadratic approximation given the points provided

        :param points: a 2D numpy array containing the x and y coordinates to be used
        :return: returns the coefficients of the quadratic in this order: constant, x, and x^2
        """
        y = numpy.sum(points[:, 1])
        xy = numpy.sum(points[:, 0] * points[:, 1])
        x_2y = numpy.sum((points[:, 0] ** 2) * points[:, 1])

        x = numpy.sum(points[:, 0])
        x_2 = numpy.sum(points[:, 0] ** 2)
        x_3 = numpy.sum(points[:, 0] ** 3)
        x_4 = numpy.sum(points[:, 0] ** 4)
        coeffs = numpy.array([[len(points), x, x_2],
                              [x, x_2, x_3],
                              [x_2, x_3, x_4]]
        )
        knowns = numpy.array([y, xy, x_2y])

        try:
            return numpy.linalg.solve(coeffs, knowns)  # determinant of matrix 0, no quadratic exists
        except:
            return None

    @staticmethod
    def getPointsWithSimilarColors(frame, sampleStart, sampleEnd, reduction=1):
        """
        Takes the unique colors that appear within the bounding points (sampleStart and sampleEnd) and returns all
        occurrences of those colors in the frame. The actual color finding occurs in getLocationsOfColorsWithFrame.
        This method is meant to reduce CPU impact by reducing the frame's resolution first.

        :param frame: A 3D numpy array. sampleStart and sampleEnd take sections from this image
        :param sampleStart: a tuple with the (x, y) position of the sample start
        :param sampleEnd: a tuple with the (x, y) position of the sample end
        :param reduction: the amount to reduce the image by. 8 seems to be best for (1280, 720) by experiment
        :return: an array of tuples containing all occurrences of unique colors within sample size in the frame
        """
        sampleArea = numpy.array(frame[sampleStart[0]:sampleEnd[0], sampleStart[1]:sampleEnd[1]], dtype=numpy.uint8)
        sampleHeight, sampleWidth = sampleArea.shape[0:2]
        height, width = frame.shape[0:2]
        if (sampleWidth / reduction * sampleHeight / reduction) > 100:
            sampleArea = cv2.resize(sampleArea, (sampleWidth / reduction, sampleHeight / reduction))

        smallFrame = cv2.resize(frame, (width / reduction, height / reduction))
        points = StreetAnalyzer.getLocationsOfColorsWithFrame(smallFrame, sampleArea)
        streetPoints = [None, None]
        streetPoints[0] = reduction * numpy.array(points[0])
        streetPoints[1] = reduction * numpy.array(points[1])

        return streetPoints

    @staticmethod
    def imageStats(image):
        (r, g, b) = cv2.split(image)

        (rMean, rStd) = (r.mean(), r.std())
        (gMean, gStd) = (g.mean(), g.std())
        (bMean, bStd) = (b.mean(), b.std())
        return (rMean, rStd, gMean, gStd, bMean, bStd)

    lower = numpy.array([150, ] * 3, dtype=numpy.uint8)
    upper = numpy.array([200, ] * 3, dtype=numpy.uint8)

    @staticmethod
    def getLocationsOfColorsWithFrame(frame, innerFrame, standardDeviations=0.7):
        """
        Takes the unique colors that appear within the innerFrame and returns all occurrences of those colors in the
        frame.

        :param frame: A 3D numpy array. The image to be searched
        :param innerFrame: A 3D numpy array. The image from which unique colors will be found
        :return: a numpy array containing all occurrences of unique colors within sample size in the frame
        """
        (rMean, rStd, gMean, gStd, bMean, bStd) = StreetAnalyzer.imageStats(innerFrame)
        rMin, rMax = rMean - rStd * standardDeviations, rMean + rStd * standardDeviations
        gMin, gMax = gMean - gStd * standardDeviations, gMean + gStd * standardDeviations
        bMin, bMax = bMean - bStd * standardDeviations, bMean + bStd * standardDeviations
        lower = numpy.array([rMin, gMin, bMin])
        upper = numpy.array([rMax, gMax, bMax])

        if numpy.all(lower < StreetAnalyzer.lower):
            StreetAnalyzer.lower = lower.astype(numpy.uint8)
        if numpy.all(upper > StreetAnalyzer.upper):
            StreetAnalyzer.upper = upper.astype(numpy.uint8)

        threshold = cv2.inRange(frame, StreetAnalyzer.lower, StreetAnalyzer.upper)

        points = numpy.where(threshold == 255)
        # print (int(rMean), int(gMean), int(bMean)), (int(rStd), int(gStd), int(bStd))

        return points[:2]

    @staticmethod
    def pointsInRange(frame, lowerColor, upperColor):
        """
        Returns the points that have a color space value between lowerColor and upperColor

        :param frame:
        :param lowerColor: a tuple or array of length 3 containing the color values of the lower bound
        :param upperColor: a tuple or array of length 3 containing the color values of the upper bound
        :return: a numpy array containing all points at which the range is satisfied
        """
        lowerColor = numpy.array(lowerColor)
        upperColor = numpy.array(upperColor)

        points = numpy.where((lowerColor[0] <= frame[:, :, 0]) & (frame[:, :, 0] <= upperColor[0]) &
                             (lowerColor[1] <= frame[:, :, 1]) & (frame[:, :, 1] <= upperColor[1]) &
                             (lowerColor[2] <= frame[:, :, 2]) & (frame[:, :, 2] <= upperColor[2]))
        return points

    @staticmethod
    def getLeftAndRightPoints(points, width, height, edgeThreshold=5, lengthThreshold=None, heightThreshold=None):
        """
        Using the contours found and contained within points, this method will return points that are most likely
        to mark the street edges using the following constraints:
            the point doesn't come within edgeThreshold pixels of the edges (street edge is off screen)
            (deprecated:) line length is greater than lengthThreshold (jagged contours can cause overlap errors)
            the start of line is on the left side of the image and end of the line is on the right side of the image

        :param points: the points found by contour algorithm
        :param width: the width of the image
        :return: two arrays containing the likely left and right street edge points (encased in a tuple)
        """
        if lengthThreshold is None:
            lengthThreshold = width / 3
        if heightThreshold is None:
            heightThreshold = height / 3

        points0 = points[:, 0]
        points1 = numpy.roll(points0, 1, 0)

        streetLines = []

        streetLines.extend(StreetAnalyzer.getIntersectingLines(points0, points1))
        points1 = numpy.roll(points0, -1, 0)
        streetLines.extend(StreetAnalyzer.getIntersectingLines(points0, points1))

        leftPoints = []
        rightPoints = []

        for x0, x1, y in sorted(streetLines, key=lambda element: element[2]):
            if (edgeThreshold < x0 < (width - edgeThreshold) and edgeThreshold < x1 < (width - edgeThreshold)
                and ((abs(
                            x1 - x0) > lengthThreshold and y > heightThreshold) or y <= heightThreshold)):  # and (x1 <= width / 2 < x0 or x0 <= width / 2 < x1)):
                if x1 > x0:
                    leftPoints.append((x0, y))
                    rightPoints.append((x1, y))
                else:
                    leftPoints.append((x1, y))
                    rightPoints.append((x0, y))
        leftPoints = numpy.array(leftPoints, dtype=object)
        rightPoints = numpy.array(rightPoints, dtype=object)

        return leftPoints, rightPoints

    @staticmethod
    def getIntersectingLines(points0, points1):
        """
        points0 and points1 together form line segment coordinates
        Example:
            points0:
            [[ 859  159]
             [ 858  160]
             [ 824  160]
             [ 823  161]]
            points1:
            [[ 823  161]
             [ 859  159]
             [ 858  160]
             [ 824  160]]

        Takes the points found by a contour algorithm and returns an array of horizontal line segments.
        These line segments have end points that intersect with a part of the contour on the other side of the screen

        :param points0: The start points of the contour line segments
        :param points1: The end points of the contour line segments
        :return: The coordinates of each line as an array of tuples: [(x start, x end, y)]
        """
        lines = []
        points = numpy.concatenate((points0, points1), axis=1)
        for x, y in points0:
            lineSegIndex = numpy.where((points0[:, 1] < y) & (y < points1[:, 1]))[0]
            if len(points[lineSegIndex]) > 0:
                x0, y0, x1, y1 = points[lineSegIndex][0]
                xIntersect = StreetAnalyzer.getIntersectionPointUsingY2(x0, y0, x1, y1, y)
                if xIntersect is not None:
                    lines.append((x, xIntersect, y))
        return lines

    @staticmethod
    def getIntersectionPointUsingY2(x0, y0, x1, y1, y2):
        """
        Given a line in the form x0, y0, x1, y1, this function will return the x value the horizontal line y2 intersects
        :return: the integer x value that the horizontal line intersects the input line
        """
        try:
            slope = float(y1 - y0) / float(x1 - x0)
            conversion = float(y2 - y0) / slope
        except:
            conversion = 0
        x2 = conversion + x0
        return int(x2)

    @staticmethod
    def getEdgesUsingMarkers(frame, markers, showSelectedPoints=False):
        """
        Apply the watershed algorithm on frame and markers to find the sections of the image.
        Markers is the same size as frame except it's color values only vary from 0 to 8 (instead of (0, 0, 0) to
        (255, 255, 255)). In this application, only 0, 1, and 2 are used. 2 indicates the grass and 1 indicates road.
        The road will be white and the grass will be black after the threshold.

        :param frame: A 3D numpy array in the BGR color space
        :param markers: A 2D numpy array the same size as frame with values from 0 to 8
        :return: A binary image marking the edges of the road read for a contouring algorithm
        """
        if showSelectedPoints is False:
            cv2.watershed(frame, markers)

        colors = numpy.int32(list(numpy.ndindex(2, 2, 2))) * 255
        overlay = colors[numpy.where(markers >= 0, markers, 0)]
        if showSelectedPoints is True:
            edges = cv2.addWeighted(frame, 0.7, overlay, 0.3, 1, dtype=cv2.CV_8UC3)
        else:
            background = numpy.zeros(overlay.shape, dtype=numpy.int32)
            edges = cv2.add(background, overlay, dtype=cv2.CV_8UC3)
            edges = cv2.cvtColor(edges, cv2.COLOR_BGR2GRAY)

            edges = cv2.threshold(edges, 128, 255, cv2.THRESH_BINARY_INV)[1]

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            edges = cv2.erode(edges, kernel, iterations=2)
            edges = cv2.dilate(edges, kernel, iterations=2)

        return edges

    @staticmethod
    def getSignificantContours(frame, epsilon=None):
        """
        Find the contours of an image and return an array of them sorted by increasing perimeter size.

        :param frame: The binary image that contours are to be calculated
        :param epsilon: If specified the approxPolyDP algorithm will be applied to the result.
                        Recommended value is 0.001
        :return: A 2D numpy array of the contours
        """
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        significantContours = []
        perimeters = []

        for contour in contours:
            perimeter = cv2.arcLength(contour, closed=False)
            index = bisect.bisect(perimeters, perimeter)
            if epsilon is not None:
                approx = cv2.approxPolyDP(contour, epsilon * perimeter, False)
                significantContours.insert(index, approx)
            else:
                significantContours.insert(index, contour)
            perimeters.insert(index, perimeter)

        return significantContours


class ObjectAnalyzer(Analyzer):  # works as a scene analyzer
    def __init__(self, targetImage, priority, actionOnData=None):
        self.tracker = PlaneTracker()
        self.target = cv2.imread("images/" + targetImage)

        self.actionOnData = actionOnData

        self.height, self.width = self.target.shape[0:2]
        rect = (0, 0, self.width, self.height)

        self.tracker.clear()
        self.tracker.add_target(self.target, rect)

        Analyzer.__init__(self, self.analyzeFrame, priority)

    @staticmethod
    def getCenter(points):
        (x0, y0) = points[0]
        (x1, y1) = points[1]
        (x2, y2) = points[2]
        (x3, y3) = points[3]

        (xMid1, yMid1) = (abs(x2 - x0) / 2 + min(x2, x0), abs(y2 - y0) / 2 + min(y2, y0))
        (xMid2, yMid2) = (abs(x3 - x1) / 2 + min(x3, x1), abs(y3 - y1) / 2 + min(y3, y1))

        return (abs(xMid2 - xMid1) / 2 + min(xMid2, xMid1), abs(yMid2 - yMid1) / 2 + min(yMid2, yMid1))

    @staticmethod
    def getArea(points):
        (x0, y0) = points[0]
        (x1, y1) = points[1]
        (x2, y2) = points[2]
        (x3, y3) = points[3]

        area1 = abs(x0 * (y2 - y1) + x1 * (y1 - y0) + x2 * (y0 - y2))
        area2 = abs(x0 * (y3 - y2) + x2 * (y2 - y0) + x3 * (y0 - y2))

        return area1 + area2

    def analyzeFrame(self, frame, enableDraw):
        tracked = self.tracker.track(frame)
        objectCenters = []
        objectAreas = []
        numMatches = 0

        if len(tracked) > 0:
            numMatches = len(tracked[0].p0)

        for tr in tracked:
            if enableDraw == True:
                cv2.polylines(frame, [numpy.int32(tr.quad)], True, (255, 255, 255), 2)
                for (x, y) in numpy.int32(tr.p1):
                    cv2.circle(frame, (x, y), 4, (255, 255, 255), 2)

            objectCenters.append(ObjectAnalyzer.getCenter(tr.quad))
            objectAreas.append(ObjectAnalyzer.getArea(tr.quad))

        if self.actionOnData is not None:
            self.actionOnData((self.width, self.height), objectCenters, objectAreas, numMatches)

        return frame


class VideoRecorder(Analyzer):
    def __init__(self, name, videoFPS, priority, includeTimeInName=True):
        videoFormat = "mov"
        self.fourcc = cv2.cv.CV_FOURCC(*'mp4v')
        if includeTimeInName == True:
            if name != "":
                name = " " + name
            self.videoName = "videos/" + time.strftime("%c").replace(":", "_") + name + "." + videoFormat
        else:
            self.videoName = "videos/" + name + "." + videoFormat
        self.videoFPS = videoFPS
        self.video = None
        self.fpsSamples = []
        Analyzer.__init__(self, self.recordFrame, priority)

    def recordFrame(self, frame, enableDraw):
        height, width = frame.shape[0:2]
        if self.video == None:
            self.video = cv2.VideoWriter()
            self.video.open(self.videoName, self.fourcc, self.videoFPS, (width, height), True)
        else:
            self.video.write(frame)
