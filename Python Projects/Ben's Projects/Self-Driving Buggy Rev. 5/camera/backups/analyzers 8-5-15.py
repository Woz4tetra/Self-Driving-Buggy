import numpy
import cv2
import bisect
from PlaneTracker import PlaneTracker

def contrast(image, scale):
    # mask = numpy.ones_like(image, dtype=numpy.float32) * scale
    return numpy.uint8(numpy.clip(numpy.int64(image) * scale, 0, 255))


def getSignificantContours(frame, epsilon=None):
    """
    Find the contours of an image and return an array of them sorted by increasing perimeter size.

    :param frame: The binary image that contours are to be calculated
    :param epsilon: If specified the approxPolyDP algorithm will be applied to the result.
                    Recommended value is 0.001
    :return: A 2D numpy array of the contours ordered from largest to smallest
    """
    frame, contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
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

def drawContours(frame):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # edges = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY_INV)[1]
    threshVal, edges = cv2.threshold(frame_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours = getSignificantContours(edges, 0.001)[-3:]
    return cv2.drawContours(frame, contours, -1, (255, 100, 100), 2)

class ImageTracker(object):
    def __init__(self, initialFrame):
        self.tracked = initialFrame
        
#        cv2.imshow("tracking", self.tracked)
        
        height, width = self.tracked.shape[0:2]
        
        rects = []
        x_divisions, y_divisions = 2, 1
        
        for x_division in xrange(x_divisions):
            for y_division in xrange(y_divisions):
                rects.append((int(x_division * float(width) / x_divisions),
                              int(y_division * float(height) / y_divisions),
                              int((x_division + 1) * float(width - 1) / x_divisions),
                              int((y_division + 1) * float(height - 1) / y_divisions)))
        
        print rects, (width, height)
        self.tracker = PlaneTracker()
        self.tracker.clear()
        
        for rect in rects:
            print self.tracked[rect[1]:rect[3], rect[0]:rect[2]].shape, rect
            self.tracker.add_target(self.tracked[rect[1]:rect[3], rect[0]:rect[2]])
    
    def update(self, frame):
        addNewTarget = False
        
        targetsFound = self.tracker.track(frame)
        if len(targetsFound) <= 1:
            addNewTarget = True
        for target in self.tracker.track(frame):
            cv2.polylines(frame, [numpy.int32(target.quad)], True, (255, 255, 255), 2)
            for (x, y) in numpy.int32(target.p1):
                cv2.circle(frame, (x, y), 4, (255, 255, 255), 2)
            if len(target.p1) <= 15:
                addNewTarget = True
        if addNewTarget == True:
            height, width = frame.shape[0:2]
            self.tracker.add_target(frame[:,0: width / 2])
        
        return frame


