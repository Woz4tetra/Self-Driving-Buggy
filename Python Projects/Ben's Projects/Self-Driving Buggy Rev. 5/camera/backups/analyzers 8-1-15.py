from matplotlib import cm

import matplotlib
from matplotlib.ticker import LinearLocator
import matplotlib.pyplot as plt
import numpy
import cv2

matplotlib.interactive(True)


def contrast(image, scale):
    # mask = numpy.ones_like(image, dtype=numpy.float32) * scale
    return numpy.uint8(numpy.clip(numpy.int64(image) * scale, 0, 255))


def exaggerate(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    minVal = image[minLoc[1], minLoc[0]]
    maxVal = image[maxLoc[1], maxLoc[0]]
    image -= minVal

    return contrast(image, 255.0 / (maxVal - minVal))


class GrayScalePlot(object):
    def __init__(self, initialImage):
        '''
        Creates a 3D image of a grayscale image. May or may not be useful for
        visualizing peaks in an image to track

        :param initialImage:
        :return:
        '''
        initialImage = cv2.resize(initialImage, (50, 50))
        initialImage = cv2.cvtColor(initialImage, cv2.COLOR_RGB2GRAY)

        self.fig = plt.figure()
        self.ax = self.fig.gca(projection='3d')
        # self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.zaxis.set_major_locator(LinearLocator(10))

        X, Y, Z = self.getPlot(initialImage)
        self.surf = self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                                         cmap=cm.gist_gray,
                                         linewidth=0, antialiased=True, vmin=0,
                                         vmax=255)

        self.fig.colorbar(self.surf, shrink=0.5, aspect=5)

    def update(self, image):
        image = cv2.resize(image, (50, 50))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        self.surf.remove()

        X, Y, Z = self.getPlot(image)
        self.surf = self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                                         cmap=cm.gist_gray,
                                         linewidth=0, antialiased=True, vmin=0,
                                         vmax=255)

        plt.draw()

    def getPlot(self, image):
        X = numpy.linspace(0, image.shape[0], num=image.shape[0])
        Y = numpy.linspace(0, image.shape[1], num=image.shape[1])
        X, Y = numpy.meshgrid(X, Y)
        Z = image[0: image.shape[0], 0: image.shape[1]]
        return X, Y, Z


class MeanshiftTracker(object):
    def __init__(self, initialFrame):
        height, width = initialFrame.shape[0:2]
        self.track_window = (width / 2 - width / 5, height / 2 - width / 5,
                             width / 2 + width / 5, height / 2 + width / 5)
        x0, y0, x1, y1 = self.track_window
        roi = initialFrame[y0:y1, x0:x1]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, numpy.array((0., 60., 32.)),
                           numpy.array((180., 255., 255.)))
        self.roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)

        self.term_crit = (
        cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    def update(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)

        # apply meanshift to get the new location
        ret, self.track_window = cv2.meanShift(dst, self.track_window,
                                               self.term_crit)

        # Draw it on image
        x, y, w, h = self.track_window
        return cv2.rectangle(frame, (x, y), (x + w, y + h), 255, 2)


class GoodFeatureTracker(object):
    def __init__(self, initialFrame):
        self.feature_params = dict(maxCorners=50,
                                   qualityLevel=0.00005,
                                   minDistance=7,
                                   blockSize=3,
                                   useHarrisDetector=False)
        self.colors = numpy.random.randint(0, 255, (100, 3))
        self.old_frame = initialFrame
        self.old_gray = cv2.cvtColor(self.old_frame, cv2.COLOR_BGR2GRAY)

        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None,
                                          **self.feature_params)
        self.mask = numpy.zeros_like(self.old_frame)

    def reinit(self, initialFrame):
        self.old_frame = initialFrame
        self.old_gray = cv2.cvtColor(self.old_frame, cv2.COLOR_BGR2GRAY)

        self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask=None,
                                          **self.feature_params)
        # self.mask = numpy.zeros_like(self.old_frame)

    def update(self, frame, enableDraw=True):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.p0 is not None and len(self.p0) >= 10:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray,
                                                   self.p0, None,
                                                   winSize=(15, 15),
                                                   maxLevel=0,
                                                   criteria=(
                                                       cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                                                       10, 0.03))
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]

            if enableDraw == True:
                for i, (new,) in enumerate(zip(
                        good_new[:100])):  # enumerate(zip(good_new, good_old)):
                    a, b = new.ravel()
                    # c, d = old.ravel()
                    # self.mask = cv2.line(self.mask, (a, b), (c, d),
                    #                      self.colors[i].tolist(), 2)
                    frame = cv2.circle(frame, (a, b), 5,
                                       self.colors[i].tolist(), -1)

                frame = cv2.add(frame, self.mask)

            self.old_gray = frame_gray.copy()
            self.p0 = good_new.reshape(-1, 1, 2)

            if not numpy.any(
                    numpy.isnan(numpy.average(good_new - good_old, axis=0))):
                return frame, numpy.average(good_new - good_old, axis=0)
            else:
                return frame, numpy.zeros(2, )
        else:
            # self.mask = numpy.zeros_like(self.old_frame)
            p0 = cv2.goodFeaturesToTrack(frame_gray, mask=None,
                                         **self.feature_params)
            if p0 is not None and len(p0) > 0:
                self.p0 = numpy.append(self.p0, p0, axis=0)
            return frame, numpy.zeros(2, )


class ORBTracker(object):
    def __init__(self, initialFrame):
        self.orb = cv2.ORB_create(100)

        # find the keypoints with ORB
        self.p0 = self.orb.detect(initialFrame, None)

        # compute the descriptors with ORB
        self.p0, des = self.orb.compute(initialFrame, self.p0)

        self.old_frame = initialFrame
        self.old_gray = cv2.cvtColor(self.old_frame, cv2.COLOR_BGR2GRAY)
        self.mask = numpy.zeros_like(self.old_frame)
        self.colors = numpy.random.randint(0, 255, (100, 3))

        temp = []
        for point in self.p0:
            temp.append([point.pt])
        self.p0 = numpy.array(temp, dtype=numpy.float32)

    def reinit(self, initialFrame):
        # find the keypoints with ORB
        self.p0 = self.orb.detect(initialFrame, None)

        # compute the descriptors with ORB
        self.p0, des = self.orb.compute(initialFrame, self.p0)
        self.old_frame = initialFrame
        self.mask = numpy.zeros_like(self.old_frame)

    def update(self, frame, enableDraw=True):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.p0 is not None and len(self.p0) >= 10:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray,
                                                   self.p0, None,
                                                   winSize=(15, 15),
                                                   maxLevel=0,
                                                   criteria=(
                                                       cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                                                       10, 0.03))
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]

            if enableDraw == True:
                for i, (new,) in enumerate(zip(
                        good_new[:100])):  # enumerate(zip(good_new, good_old)):
                    a, b = new.ravel()
                    # c, d = old.ravel()
                    # self.mask = cv2.line(self.mask, (a, b), (c, d),
                    #                      self.colors[i].tolist(), 2)
                    frame = cv2.circle(frame, (a, b), 5,
                                       self.colors[i].tolist(), -1)

                frame = cv2.add(frame, self.mask)

            self.old_gray = frame_gray.copy()
            self.p0 = good_new.reshape(-1, 1, 2)

            if not numpy.any(
                    numpy.isnan(numpy.average(good_new - good_old, axis=0))):
                return frame, numpy.average(good_new - good_old, axis=0)
            else:
                return frame, numpy.zeros(2, )
        else:
            # find the keypoints with ORB
            p0 = self.orb.detect(frame, None)

            # compute the descriptors with ORB
            p0, des = self.orb.compute(frame, p0)

            temp = []
            for point in p0:
                temp.append([point.pt])
            p0 = numpy.array(temp, dtype=numpy.float32)

            if p0 is not None and len(p0) > 0:
                self.p0 = numpy.append(self.p0, p0, axis=0)

            return frame, numpy.zeros(2, )


class OpticalFlowTracker(object):
    def __init__(self, initialFrame):
        self.prevgray = cv2.cvtColor(contrast(initialFrame, 1.5), cv2.COLOR_BGR2GRAY)

    def update(self, frame):
        gray = cv2.cvtColor(contrast(frame, 1.5), cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(self.prevgray, gray, None, 0.5, 3,
                                            15, 3, 5, 1.2, 0)
        self.prevgray = gray

        return OpticalFlowTracker.draw_flow(gray, flow)
    
    @staticmethod
    def draw_flow(img, flow, step=16):
        h, w = img.shape[:2]

        y, x = numpy.mgrid[step / 2:h:step, step / 2:w:step].reshape(2, -1)
        fx, fy = flow[y, x].T
        lines = numpy.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
        lines = numpy.int32(lines + 0.5)
        vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.polylines(vis, lines, 0, (0, 255, 0))
        for (x1, y1), (x2, y2) in lines:
            cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
        return vis

class BlobTracker(object):
    def __init__(self):
        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 0
        params.maxThreshold = 255

        # # Filter by Area.
        # params.filterByArea = True
        # params.minArea = 1500
        #
        # # Filter by Circularity
        # params.filterByCircularity = True
        # params.minCircularity = 0.1
        #
        # # Filter by Convexity
        # params.filterByConvexity = True
        # params.minConvexity = 0.87
        #
        # # Filter by Inertia
        # params.filterByInertia = True
        # params.minInertiaRatio = 0.01

        self.detector = cv2.SimpleBlobDetector_create()

    def update(self, frame):
        keypoints = self.detector.detect(frame)
        return cv2.drawKeypoints(frame, keypoints, numpy.array([]), (0, 0, 255),
                                 cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

def drawContours(frame):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(frame_gray, 127, 255, 0)
    thresh, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    return cv2.drawContours(frame, contours, -1, (255, 100, 100), 2)

class PyramidFilter(object):
    def __init__(self):
        self.leveln = 6
        self.levels = [4, 6, 9, 10, 1, 1]#[1, 10, 10, 1, 1, 1]

    def update(self, frame):
        pyr = self.build_lappyr(frame, self.leveln)
        for i in xrange(self.leveln):
            pyr[i] *= self.levels[i]
        return self.merge_lappyr(pyr)

    def build_lappyr(self, frame, leveln=6, dtype=numpy.int16):
        frame = dtype(frame)
        levels = []
        for i in xrange(leveln - 1):
            next_img = cv2.pyrDown(frame)
            img1 = cv2.pyrUp(next_img, dstsize=(frame.shape[1], frame.shape[0]))
            levels.append(frame - img1)
            frame = next_img
        levels.append(frame)
        return levels

    def merge_lappyr(self, levels):
        img = levels[-1]
        for lev_img in levels[-2::-1]:
            img = cv2.pyrUp(img, dstsize=(lev_img.shape[1], lev_img.shape[0]))
            img += lev_img
        return numpy.uint8(numpy.clip(img, 0, 255))
