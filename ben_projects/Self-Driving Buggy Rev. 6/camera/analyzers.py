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



def sobel_filter(frame):
    # laplacian = cv2.Laplacian(frame, cv2.CV_64F, ksize=3)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    sobelx64f = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
    abs_sobel64f = np.absolute(sobelx64f)
    sobel_8u = np.uint8(abs_sobel64f)
    return sobel_8u

def threshold_filter(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # value, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)
    # value, frame = cv2.threshold(frame, 18, 255, cv2.THRESH_BINARY)
    frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY_INV, 9, 4)
    return frame

def auto_canny(frame, sigma=0.33):
    frame_canny = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_canny = cv2.GaussianBlur(frame_canny, (3, 3), 0)

    v = np.median(frame_canny)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(frame_canny, lower, upper)

def erode_filter(frame, kernel=(5, 5)):
    kernel = np.ones(kernel, np.uint8)
    return cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

class OpticalFlowTracker(object):
    def __init__(self, initialFrame):
        height, width = initialFrame.shape[0:2]
        self.feature_params = dict(maxCorners=100,
                                   qualityLevel=0.3,
                                   minDistance=7,
                                   blockSize=7)
        self.lk_params = dict(winSize=(width, height),
                              maxLevel=5,
                              criteria=(
                                  cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                                  10, 0.03))
        self.color = np.random.randint(0, 255, (100, 3))

        self.old_frame = initialFrame
        self.old_gray = cv2.cvtColor(self.old_frame, cv2.COLOR_BGR2GRAY)
        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None,
                                          **self.feature_params)

        self.benchmarkP0len = len(self.p0) / 2
        self.mask = np.zeros_like(self.old_frame)

    def update(self, frame, enableDraw=True):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray,
                                               self.p0, None,
                                               **self.lk_params)

        # Select good points
        good_new = p1[st == 1]
        good_old = self.p0[st == 1]

        # draw the tracks
        #        for i, (new, old) in enumerate(zip(good_new, good_old)):
        #            a, b = new.ravel()
        #            c, d = old.ravel()
        #            self.mask = cv2.line(self.mask, (a, b), (c, d),
        #                                 self.color[i].tolist(), 2)
        #            frame = cv2.circle(frame, (a, b), 5, self.color[i].tolist(), -1)
        if enableDraw == True:
            for i, new in enumerate(good_new):
                new = int(new[0]), int(new[1])
                frame = cv2.circle(frame, new, 5, self.color[i].tolist(), -1)

        self.old_gray = frame_gray.copy()
        self.p0 = good_new.reshape(-1, 1, 2)

        if len(self.p0) < self.benchmarkP0len:
            newP0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None,
                                            **self.feature_params)
            self.p0 = np.append(self.p0, newP0, axis=0)[:100]

        return cv2.add(frame, self.mask), tuple(
            np.median(good_new - good_old, axis=0))


class SimilarFrameTracker(object):
    def __init__(self, initialFrame):
        self.height, self.width = initialFrame.shape[0:2]

        self.tracker = PlaneTracker()

        self.tracker.clear()
        self.tracker.add_target(initialFrame)

    @staticmethod
    def centroid(quad):
        x = quad[:, 0]
        y = quad[:, 1]
        return np.average(x), np.average(y)

    def update(self, frame, enableDraw=True):
        tracked = self.tracker.track(frame)
        if len(tracked) == 0:
            self.tracker.clear()
            self.tracker.add_target(frame)

            return frame, (0, 0)
        else:
            tracked = tracked[0]
            if enableDraw == True:
                cv2.polylines(frame, [np.int32(tracked.quad)], True,
                              (255, 255, 255), 2)

                draw_keypoints(frame, self.tracker.frame_points)

            centroid = SimilarFrameTracker.centroid(tracked.quad)
            delta = [self.width / 2 - centroid[0],
                     self.height / 2 - centroid[1]]

            self.tracker.clear()
            self.tracker.add_target(frame)

            return frame, delta


def drawMinMax(frame):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    color = np.array([np.random.randint(0, 255),
                         np.random.randint(0, 255),
                         np.random.randint(0, 255)])
    frame = cv2.circle(frame, max_loc, 4, color, 2)
    frame = cv2.circle(frame, min_loc, 4, 255 - color, 2)
    return frame


def blurriness(frame):
    fft = np.fft.fft2(frame)
    print np.mean(np.ndarray.flatten(np.abs(fft)))


def drawPosition(frame, width, height, position, reverse=True):
    color = position[0] % 256, position[1] % 256, \
            np.random.randint(0, 255)
    if reverse == True:
        position = width - int(position[0]), height - int(position[1])
    else:
        position = int(position[0]), int(position[1])
    return cv2.circle(frame, position, 4, color, 2)
