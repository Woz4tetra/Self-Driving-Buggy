import math

arduino = None

(knownDepth_meters, frameY_px), (knownWidth_meters, frameWidth_px) = (0, 0), (0, 0)

def centerSelfBetweenTwoLines(lines):
    pass


def offsetFromRoadEdgeBy(streetEdge, meters):
    global knownDepth_meters, frameY_px, knownWidth_meters, frameWidth_px
    (quadratic, (xQuadStart, xQuadEnd), line, (xLinStart, xLinEnd)) = streetEdge

    x0 = quadratic(frameY_px)

    yStart = line(xLinStart)
    yEnd = line(xLinEnd)
    if yStart is not None and yEnd is not None:
        edgeAngle_radians = math.atan2(yEnd - yStart, xLinEnd - xLinStart)

        d = (frameWidth_px / 2 - x0) * knownWidth_meters / frameWidth_px
        dActual = -knownDepth_meters * math.tan(edgeAngle_radians) + d

        command = -int(dActual)
        if command < -90:
            command = -90
        if command >= 90:
            command = 89
        command += 90

        arduino["steering"] = command

def stayAwayFromLeftLineBy(lines, meters):
    pass


def stayAwayFromRightLineBy(lines, meters):
    pass


def driveTowardsStoredLandmark():
    pass