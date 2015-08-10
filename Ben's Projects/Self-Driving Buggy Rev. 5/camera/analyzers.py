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

def blur(frame, size):
    # return cv2.GaussianBlur(frame, (size, size), 0)
    return cv2.medianBlur(frame, size)

class OpticalFlowTracker(object):
    def __init__(self, initialFrame):
        self.feature_params = dict(maxCorners=100,
                                   qualityLevel=0.3,
                                   minDistance=7,
                                   blockSize=7)
        self.lk_params = dict(winSize=(15, 15),
                              maxLevel=2,
                              criteria=(
                              cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                              10, 0.03))
        self.color = numpy.random.randint(0, 255, (100, 3))

        self.old_frame = initialFrame
        self.old_gray = cv2.cvtColor(self.old_frame, cv2.COLOR_BGR2GRAY)
        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None, **self.feature_params)

        self.mask = numpy.zeros_like(self.old_frame)

    def update(self, frame):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None,
                                               **self.lk_params)

        # Select good points
        good_new = p1[st == 1]
        good_old = self.p0[st == 1]

        # draw the tracks
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            self.mask = cv2.line(self.mask, (a, b), (c, d), self.color[i].tolist(), 2)
            frame = cv2.circle(frame, (a, b), 5, self.color[i].tolist(), -1)

        self.old_gray = frame_gray.copy()
        self.p0 = good_new.reshape(-1, 1, 2)

        return cv2.add(frame, self.mask)

class SimilarFrameTracker(object):
    def __init__(self, initialFrame):
        self.tracker = PlaneTracker()

        self.tracker.clear()
        self.tracker.add_target(initialFrame)

    def update(self, frame):
        tracked = self.tracker.track(frame)
        for found in tracked:
            cv2.polylines(frame, [numpy.int32(found.quad)], True, (255, 255, 255),
                          2)
            for (x, y) in numpy.int32(found.p1):
                cv2.circle(frame, (x, y), 4, (255, 255, 255), 2)
        if len(tracked) == 0:
            self.tracker.clear()
            self.tracker.add_target(frame)
        # else:
        #     print(tracked[0].quad)
        return frame