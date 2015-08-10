import numpy
import cv2
import bisect

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