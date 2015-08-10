import cv2, numpy
import bisect
import copy
from matplotlib import pyplot

# dirtRange1 = (21, 45, 45), (40, 255, 255)
# dirtRange2 = (210, 30, 45), (255, 255, 255)
greenRange = (30, 60, 30), (127, 255, 255)

streetRange = [numpy.array([255, ] * 3, dtype=numpy.uint8),
               numpy.array([0, ] * 3, dtype=numpy.uint8)]

# --------------------------------------------------
# Public API
# --------------------------------------------------
def filterOutNonRoad(frame, showSelectedPoints=False):
    height, width = frame.shape[0:2]

    # frameHSV = cv2.GaussianBlur(frame, (35, 35), 5)
    frameHSV = cv2.medianBlur(frame, 35)  # blur to remove noise from road and grass
    frameBGR = copy.copy(frameHSV)

    frameHSV = cv2.cvtColor(frameHSV, cv2.COLOR_BGR2HSV_FULL)  # convert to hue, saturation, value color space

    markers = numpy.zeros((height, width), numpy.int32)  # create markers for watershed algorithm

    # ----- junk mark start -----

    # A portion of the road is always within y% of the image vertically and an x% of the image
    # horizontally. Take the colors that appear there and find them in the rest of the image. These points should
    # mark a good portion of the road. Mark them on the watershed marker image as "1"
    sampleWidth = width / 5
    sampleStart = [3 * height / 5, width / 2 - sampleWidth / 2]
    sampleEnd = [height, width / 2 + sampleWidth / 2]

    # streetPoints = getPointsWithSimilarColors(frameBGR, sampleStart, sampleEnd)
    # markers[streetPoints] = 1
    markers[sampleStart[0]:sampleEnd[0], sampleStart[1]:sampleEnd[1]] = 1
    markers[height / 4] = 2

    # find the points on the image that are green
    # mark them on the watershed marker image as "2"

    markers[pointsInRange(frameHSV, *greenRange)] = 2

    # markers[pointsInRange(frameHSV, *dirtRange1)] = 2
    # markers[pointsInRange(frameHSV, *dirtRange2)] = 2

    # -----  junk mark end  -----

    contours = []
    if showSelectedPoints is True:
        cv2.rectangle(frame, (sampleStart[1], sampleStart[0]), (sampleEnd[1], sampleEnd[0]), (200, 0, 0), 2)
        return getEdgesUsingMarkers(frame, markers, showSelectedPoints), contours
    else:
        # Apply the watershed algorithm and threshold it to get the road
        edges = getEdgesUsingMarkers(frameBGR, markers, showSelectedPoints)
        contours = getSignificantContours(edges, float(height) / (10 ** 6))[-1:]  # get the largest contour

        mask = numpy.zeros_like(frameBGR)  # Create mask where white is what we want, black otherwise
        cv2.drawContours(mask, contours, -1, (255, 255, 255), -1)  # Draw filled contour in mask
        frameBGR = numpy.zeros_like(frame)  # Extract out the object and place into output image

        originalFrame = copy.copy(frame)
        originalFrame[mask == 0] = frameBGR[mask == 0]

        return originalFrame, contours


def filterOutNonAsphalt(road):
    # roadHSV = cv2.cvtColor(road, cv2.COLOR_BGR2HSV)
    # roadBlurred = cv2.GaussianBlur(road, (25, 25), 3)
    roadBlurred = cv2.medianBlur(road, 25)
    # height, width = road.shape[0:2]

    sigColors = getSignificantColors(roadBlurred)
    print(sigColors)

    # # roadThreshold = cv2.inRange(roadHSV, tuple(mode * 1.3), (255,) * 3)
    # roadThreshold = cv2.inRange(roadHSV, tuple(mode * 0.8), tuple(mode * 1.25))
    #
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # roadThreshold = cv2.erode(roadThreshold, kernel, iterations=2)
    # roadThreshold = cv2.dilate(roadThreshold, kernel, iterations=2)
    #
    # roadThreshold = cv2.Canny(road, 0, 500)
    cv2.imshow("road", roadBlurred)

def findStreetCenterAndEdges(contours, xxx_todo_changeme):
    (height, width) = xxx_todo_changeme
    noEdgeFound = [lambda x: None, (0, 0), lambda x: None, (0, 0)]  # used in combineFilters()
    streetEdges = [noEdgeFound] * 3
    coeffs = [[], []]

    if len(contours) > 0:
        points = getLeftAndRightPoints(contours[0], width, height)
        for index in range(2):
            if len(points[index]) > 0:
                points[index] = numpy.roll(points[index], 1, 1)
                quadratic, coeffs[index] = getQuadraticFit(points[index])
                quadPlotRange = (points[index][:, 0].min(0), points[index][:, 0].max(0))

                streetEdges[index] = computeStreetEdgeData(quadratic, quadPlotRange, width, height)

        if len(coeffs[0]) > 0 and len(coeffs[1]) > 0 and len(points[1]) > 0:
            combined = numpy.append(coeffs[0], coeffs[1]).reshape((2, 3))
            combinedCoeffs = numpy.average(combined, axis=0)
            quadratic = lambda x: int(combinedCoeffs[2] * x ** 2 + combinedCoeffs[1] * x + combinedCoeffs[0])

            plotRange = (points[1][:, 0].min(0), points[1][:, 0].max(0))

            streetEdges[2] = computeStreetEdgeData(quadratic, plotRange, width, height)

    return streetEdges


def filterOutIncorrectLines(rawLines, streetLeft, streetCenter, streetRight):
    return []


def combineFilters(frame, contours, streetEdges, lines):
    cv2.drawContours(frame, contours, -1, (255, ) * 3, 1)

    # points = []
    for streetEdge in streetEdges:
        (quadratic, (xQuadStart, xQuadEnd), line, (xLinStart, xLinEnd)) = streetEdge
        plotQuadratic(quadratic, frame, xPlotStart=xQuadStart, xPlotEnd=xQuadEnd)
        # plotLine(frame, line, xPlotStart=xLinStart, xPlotEnd=xLinEnd)

        # points.insert(0, (line(xLinStart), xLinStart))
        # points.append((line(xLinEnd), xLinEnd))

    # points = numpy.float32(points[1:-1])
    # perspectiveWarpRoad(frame, points, frame.shape[0:2])
    # cv2.polylines(frame, numpy.int32([points]), True, (255, 0, 0), 3)

    # for line in lines:
    #     x0, y0, x1, y1 = line
    #     cv2.line(frame, (x0, y0), (x1, y1), (160, 100, 0), 2)
    return frame


def verticalFinishLineFound(lines):
    return


def checkForTransition(frame, current, protocols):
    return False


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

#       - - - - - - - - - - - - - - - - - - - - - - - - -
#                       filterOutNonRoad
#       - - - - - - - - - - - - - - - - - - - - - - - - -

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
    points = getLocationsOfColorsWithFrame(smallFrame, sampleArea)
    streetPoints = [None, None]
    streetPoints[0] = reduction * numpy.array(points[0])
    streetPoints[1] = reduction * numpy.array(points[1])

    return streetPoints


def getLocationsOfColorsWithFrame(frame, innerFrame, standardDeviations=0.7):
    """
    Takes the unique colors that appear within the innerFrame and returns all occurrences of those colors in the
    frame.

    :param frame: A 3D numpy array. The image to be searched
    :param innerFrame: A 3D numpy array. The image from which unique colors will be found
    :return: a numpy array containing all occurrences of unique colors within sample size in the frame
    """
    (rMean, rStd, gMean, gStd, bMean, bStd) = imageStats(innerFrame)
    rMin, rMax = rMean - rStd * standardDeviations, rMean + rStd * standardDeviations
    gMin, gMax = gMean - gStd * standardDeviations, gMean + gStd * standardDeviations
    bMin, bMax = bMean - bStd * standardDeviations, bMean + bStd * standardDeviations
    lower = numpy.array([rMin, gMin, bMin])
    upper = numpy.array([rMax, gMax, bMax])

    if numpy.all(lower < streetRange[0]):
        streetRange[0] = lower.astype(numpy.uint8)
    if numpy.all(upper > streetRange[1]):
        streetRange[1] = upper.astype(numpy.uint8)

    threshold = cv2.inRange(frame, *streetRange)

    points = numpy.where(threshold == 255)
    # print (int(rMean), int(gMean), int(bMean)), (int(rStd), int(gStd), int(bStd))

    return points[:2]


def imageStats(image):
    (r, g, b) = cv2.split(image)

    (rMean, rStd) = (r.mean(), r.std())
    (gMean, gStd) = (g.mean(), g.std())
    (bMean, bStd) = (b.mean(), b.std())
    return (rMean, rStd, gMean, gStd, bMean, bStd)


def pointsInRange(frame, lowerColor, upperColor, any=False):
    """
    Returns the points that have a color space value between lowerColor and upperColor

    :param frame:
    :param lowerColor: a tuple or array of length 3 containing the color values of the lower bound
    :param upperColor: a tuple or array of length 3 containing the color values of the upper bound
    :return: a numpy array containing all points at which the range is satisfied
    """
    lowerColor = numpy.array(lowerColor)
    upperColor = numpy.array(upperColor)

    if any is False:
        points = numpy.where((lowerColor[0] <= frame[:, :, 0]) & (frame[:, :, 0] <= upperColor[0]) &
                             (lowerColor[1] <= frame[:, :, 1]) & (frame[:, :, 1] <= upperColor[1]) &
                             (lowerColor[2] <= frame[:, :, 2]) & (frame[:, :, 2] <= upperColor[2]))
    else:
        points = numpy.where((lowerColor[0] <= frame[:, :, 0]) & (frame[:, :, 0] <= upperColor[0]) |
                             (lowerColor[1] <= frame[:, :, 1]) & (frame[:, :, 1] <= upperColor[1]) |
                             (lowerColor[2] <= frame[:, :, 2]) & (frame[:, :, 2] <= upperColor[2]))

    return points


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


#       - - - - - - - - - - - - - - - - - - - - - - - - -
#                     findStreetCenterAndEdges
#       - - - - - - - - - - - - - - - - - - - - - - - - -

def computeStreetEdgeData(quadratic, quadPlotRange, width, height):
    linPlotStart = quadPlotRange[1] - abs(quadPlotRange[1] - quadPlotRange[0]) / 2
    linRegDataPoints = plotQuadratic(quadratic, xPlotStart=linPlotStart, xPlotEnd=quadPlotRange[1])
    line, (slope, offset) = getLinearRegression(linRegDataPoints)

    linPlotEnd = height
    if slope is not None:
        if slope > 0:
            linPlotEnd = int((width - offset) / slope)
        elif slope < 0:
            linPlotEnd = int(-offset / slope)

    streetEdge = (quadratic, quadPlotRange, line, (linPlotStart, linPlotEnd))

    return streetEdge


def getLeftAndRightPoints(points, width, height, edgeThreshold=5):
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
    points0 = points[:, 0]
    points1 = numpy.roll(points0, 1, 0)

    streetLines = []

    streetLines.extend(getIntersectingLines(points0, points1))
    points1 = numpy.roll(points0, -1, 0)
    streetLines.extend(getIntersectingLines(points0, points1))

    leftPoints = []
    rightPoints = []

    for x0, x1, y in sorted(streetLines, key=lambda element: element[2]):
        if (edgeThreshold < x0 < (width - edgeThreshold) and edgeThreshold < x1 < (width - edgeThreshold)
            and ((1.5 * abs(x1 - x0) > y))):
            if x1 > x0:
                leftPoints.append((x0, y))
                rightPoints.append((x1, y))
            else:
                leftPoints.append((x1, y))
                rightPoints.append((x0, y))
    leftPoints = numpy.array(leftPoints, dtype=object)
    rightPoints = numpy.array(rightPoints, dtype=object)

    return [leftPoints, rightPoints]


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
            xIntersect = getIntersectionPointUsingY2(x0, y0, x1, y1, y)
            if xIntersect is not None:
                lines.append((x, xIntersect, y))
    return lines


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


def getQuadraticFit(points):
    """
    Finds the best quadratic approximation given the points provided

    :param points: a 2D numpy array containing the x and y coordinates to be used
    :return: returns the coefficients of the quadratic in this order: constant, x, and x^2
    """
    y = numpy.sum(points[:, 1])
    xy = numpy.sum(points[:, 0] * points[:, 1])
    x_2y = numpy.sum((points[:, 0] ** 2) * points[:, 1])

    x_1 = numpy.sum(points[:, 0])
    x_2 = numpy.sum(points[:, 0] ** 2)
    x_3 = numpy.sum(points[:, 0] ** 3)
    x_4 = numpy.sum(points[:, 0] ** 4)
    coeffs = numpy.array([[len(points), x_1, x_2],
                          [x_1, x_2, x_3],
                          [x_2, x_3, x_4]]
    )
    knowns = numpy.array([y, xy, x_2y])

    try:
        cCoeff, xCoeff, x_2Coeff = numpy.linalg.solve(coeffs, knowns)  # determinant of matrix 0, no quadratic exists
        return lambda x: int(x_2Coeff * x ** 2 + xCoeff * x + cCoeff), (cCoeff, xCoeff, x_2Coeff)
    except:
        return lambda x: None, []


def getLinearRegression(points):  # pearson correlation coefficient * std(x)/std(y)
    if len(points) > 0:
        y = points[:, 0]
        x = points[:, 1]

        x_avg = numpy.mean(x)
        y_avg = numpy.mean(y)

        x_error = x - x_avg
        y_error = y - y_avg

        var_x_sum = numpy.sum(x_error ** 2)
        var_y_sum = numpy.sum(y_error ** 2)

        if var_x_sum != 0 and var_y_sum != 0:
            pearson_r = numpy.sum(x_error * y_error) / ((var_x_sum ** 0.5) * (var_y_sum ** 0.5))

            slope = pearson_r * numpy.std(y) / numpy.std(x)
            offset = y_avg - slope * x_avg

            return lambda inputX: int(slope * inputX + offset), (slope, offset)
    return lambda inputX: None, (None, None)


#       - - - - - - - - - - - - - - - - - - - - - - - - -
#                       combineFilters
#       - - - - - - - - - - - - - - - - - - - - - - - - -

def plotLine(frame, linear, axis=1, color=(0, 100, 255), xPlotStart=None,
             xPlotEnd=None):
    if linear(0) is not None:
        xPlotPoints = [0, 100]  # [points[:, 0].min(0), points[:, 0].max(0)]  # find the start and end points to plot
        if xPlotStart is not None:
            xPlotPoints[0] = xPlotStart

        if xPlotEnd is not None:
            xPlotPoints[1] = xPlotEnd

        if axis == 0:
            point1 = (xPlotPoints[0], linear(xPlotPoints[0]))
            point2 = (xPlotPoints[1], linear(xPlotPoints[1]))
        else:
            point1 = (linear(xPlotPoints[0]), xPlotPoints[0])
            point2 = (linear(xPlotPoints[1]), xPlotPoints[1])
        cv2.line(frame, point1, point2, color, 2)


def plotQuadratic(quadratic, frame=None, axis=1, color=(161, 81, 50), xPlotStart=None,
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
    plottedPoints = []

    xPlotPoints = [0, 100]
    if xPlotStart is not None:
        xPlotPoints[0] = xPlotStart

    if xPlotEnd is not None:
        xPlotPoints[1] = xPlotEnd + 1

    for x in range(*xPlotPoints):
        # use calculated coefficients to get estimated street edge
        estY = quadratic(x)

        if estY is not None:
            # axis indicates if the points were flipped or not
            if axis == 0:
                point = (x, estY)
            else:
                point = (estY, x)

            # draw the calculated point
            if frame is not None:
                cv2.circle(frame, tuple(point), 1, color, 2)
            plottedPoints.append(point)

    if frame is None:
        return numpy.array(plottedPoints)

def perspectiveWarpRoad(road, points, xxx_todo_changeme1):
    (height, width) = xxx_todo_changeme1
    destinationPoints = numpy.float32([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ])

    M = cv2.getPerspectiveTransform(points, destinationPoints)
    cv2.warpPerspective(road, M, (width, height), road)


#       - - - - - - - - - - - - - - - - - - - - - - - - -
#                       filterOutNonAsphalt
#       - - - - - - - - - - - - - - - - - - - - - - - - -
sameColorStd = 7
def getSignificantColors(frame, numColors=10, stdThreshold=1):
    occurances = [numpy.bincount(x) for x in frame.reshape(-1, 3).T]

    minRowLength = min([len(row) for row in occurances])
    for index in range(len(occurances)):
        occurances[index] = occurances[index][0:minRowLength]
    occurances = numpy.array(occurances)

    sigColors = []

    while len(sigColors) <= numColors and not numpy.all(occurances == 0):
        sigColor = numpy.argmax(occurances, axis=1)
        chan1, chan2, chan3 = sigColor
        lower1, upper1 = chan1 - sameColorStd * stdThreshold, chan1 + sameColorStd * stdThreshold
        lower2, upper2 = chan2 - sameColorStd * stdThreshold, chan2 + sameColorStd * stdThreshold
        lower3, upper3 = chan3 - sameColorStd * stdThreshold, chan3 + sameColorStd * stdThreshold

        shouldAppend = True
        for color in sigColors:
            chan1, chan2, chan3 = color
            if lower1 <= chan1 <= upper1 or lower2 <= chan2 <= upper2 or lower3 <= chan3 <= upper3:
                shouldAppend = False
                break

        if shouldAppend is True:
            sigColors.append(sigColor)

        # print sigColor, occurances[0, sigColor[0]], occurances[1, sigColor[1]], occurances[2, sigColor[2]], occurances[:, sigColor]
        # occurances[:, sigColor] = 0# = numpy.delete(occurances, 0, 1)
        occurances[0, sigColor[0]], occurances[1, sigColor[1]], occurances[2, sigColor[2]] = 0, 0, 0

    print()
    return sigColors
    # color = ('r', 'g', 'b')
    # for i, col in enumerate(color):
    #     histr = cv2.calcHist([frame], [i], None, [256], [0, 256])
    #     minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame)
    #     pyplot.plot(histr, color=col)
    #     pyplot.xlim([0, 256])
    #
    # pyplot.show()