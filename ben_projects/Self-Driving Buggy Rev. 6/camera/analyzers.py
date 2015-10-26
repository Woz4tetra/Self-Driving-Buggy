import bisect

from opencv_samples.common import draw_keypoints
from opencv_samples.plane_tracker import PlaneTracker
import numpy as np
import cv2


def contrast(image, scale):
    # mask = np.ones_like(image, dtype=np.float32) * scale
    return np.uint8(np.clip(np.int64(image) * scale, 0, 255))


def getSignificantContours(frame, epsilon=None):
    """
    Find the contours of an image and return an array of them sorted by increasing perimeter size.

    :param frame: The binary image that contours are to be calculated
    :param epsilon: If specified the approxPolyDP algorithm will be applied to the result.
                    Recommended value is 0.001
    :return: A 2D np array of the contours ordered from largest to smallest
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


def drawContours(frame, edges, length=0, epsilon=0.001):
    # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # edges = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY_INV)[1]
    # threshVal, edges = cv2.threshold(frame_gray, 0, 255,
    #                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours = getSignificantContours(edges, epsilon)[-length:]
    return cv2.drawContours(frame, contours, -1, (255, 100, 100), 2)


def erode_filter(frame, kernel=(5, 5)):
    kernel = np.ones(kernel, np.uint8)
    return cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)


class SceneTracker:
    def __init__(self, scenes):
        # self.height, self.width = scene[0].shape[0:2]

        self.tracker = PlaneTracker()

        self.tracker.clear()
        for scene in scenes:
            self.tracker.add_target(scene)

    @staticmethod
    def centroid(quad):
        x = quad[:, 0]
        y = quad[:, 1]
        return np.average(x), np.average(y)

    def update(self, frame, enableDraw=True):
        tracked = self.tracker.track(frame)
        if enableDraw == True:
            for index in xrange(len(tracked)):
                cv2.polylines(frame, [np.int32(tracked[index].quad)], True,
                              (255 * float(index) / (len(tracked)),
                               255 * float(index) / (len(tracked)),
                               255 * float(index) / (len(tracked))), 2)

                draw_keypoints(frame, self.tracker.frame_points)

        if len(tracked) > 0:
            print self.centroid(tracked[0].quad)
        # delta = [self.width / 2 - centroid[0],
        #          self.height / 2 - centroid[1]]

        return frame#, delta
