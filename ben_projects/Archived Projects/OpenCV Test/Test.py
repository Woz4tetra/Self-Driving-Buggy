import numpy as np
import cv2
import time

# from matplotlib import pyplot


def timeOperation(function):
    time1 = time.time()
    function()
    time2 = time.time()
    return time2 - time1


def showPlainCamera():
    cap = cv2.VideoCapture(0)
    # numFrames = 0

    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        frame = cv2.flip(frame, 1)
        # Display the resulting frame
        cv2.imshow('frame', frame)  # gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def showCamera():
    cap = cv2.VideoCapture(1)
    
    width, height = 640, 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    while (True):
        # Capture frame-by-frame
        time0 = time.time()
        ret, frame = cap.read()
        print time.time() - time0
        
        # Display the resulting frame
#        cv2.imshow('frame', frame)  # gray)
        cv2.waitKey(1)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break


    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

showCamera()

resolutions = {
    8: (1920, 1080),
    12: (1440, 810),
    23: (960, 540),
    30: (480, 270),
    31: (240, 135)
}


def fpsTest():
    cap = cv2.VideoCapture(0)

    (width, height) = resolutions[31]

    cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, height)

    frameData = []

    while (True):
        time1 = time.time()

        ret, frame = cap.read()

        frame = cv2.flip(frame, 1)

        cv2.imshow('frame', frame)

        time2 = time.time()

        frameData.append(1 / float(time2 - time1))
        if len(frameData) > 100:
            frameData.pop(0)

        key = cv2.waitKey(1)
        if key == ord(' '):
            (width, height) = (width * 2, height * 2)
            cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, height)
            frameData = []

        elif key == ord('p'):
            print (width, height), sum(frameData) / len(frameData)

        elif key == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()



def gettingStartedWithImages():
    img = cv2.imread('Irrelevant Images/Dragon Curve.jpg', cv2.IMREAD_COLOR)
    cv2.imshow('image', img)

    k = cv2.waitKey(0)
    if k == 27:  # wait for ESC key to exit
        cv2.destroyAllWindows()
    elif k == ord('s'):  # wait for 's' key to save and exit
        cv2.imwrite('Irrelevant Images/Dragon Curve.jpg', img)
        cv2.destroyAllWindows()


def playVideoFromFile():
    cap = cv2.VideoCapture('IMG_0076.m4v')

    while (cap.isOpened()):
        ret, frame = cap.read()

        # gray = cv2.cvtColor(frame, cv2.COLOR_R)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def writeAVideo():
    camera = cv2.VideoCapture(0)

    fps = 23
    format = 'mp4v'
    videoName = time.strftime("%c").replace(":", ";") + "." + format

    (width, height) = resolutions[fps]
    fourcc = cv2.VideoWriter_fourcc(*format)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    video = cv2.VideoWriter()
    video.open(videoName, fourcc, fps, (width, height), True)

    time1 = time.time()
    while True:
        f, img = camera.read()
        video.write(img)
        cv2.imshow("webcam", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    time2 = time.time()
    print "Video recording time:", time2 - time1

def writeAVideoFromImages():
    videoName = time.strftime("%c").replace(":", ";") + ".mov"

    images = ["Street 1.png", "Street 2.png", "Street 3.png", "Street 4.png"]

    frame = cv2.imread(images[0])
    (width, height) = frame.shape[0:2]

    fourcc = cv2.cv.CV_FOURCC(*"mp4v")

    video = cv2.VideoWriter()
    video.open(videoName, fourcc, 1, (height, width), True)

    for image in images:
        frame = cv2.imread(image)
        frame = cv2.resize(frame, (height, width))
        video.write(frame)

    video.release()


def basicOperationsOnImages():
    image = cv2.imread('Robot.jpg')  # very slow (0.05 secs)
    thing = image[280: 340, 330:390]
    image[273:333, 100:160] = thing
    cv2.imwrite('Robot2.jpg', image)  # very slow (0.05 secs)


def makeBorder():
    image = cv2.imread('Irrelevant Images/Robot.jpg')
    image = cv2.copyMakeBorder(image, 100, 100, 100, 100, cv2.BORDER_REFLECT, value=[255, 100, 0])
    cv2.imwrite('Robot border.jpg', image)


def pyplotTest():
    BLUE = [255, 0, 0]

    img1 = cv2.imread('Robot.jpg')

    replicate = cv2.copyMakeBorder(img1, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
    reflect = cv2.copyMakeBorder(img1, 10, 10, 10, 10, cv2.BORDER_REFLECT)
    reflect101 = cv2.copyMakeBorder(img1, 10, 10, 10, 10, cv2.BORDER_REFLECT_101)
    wrap = cv2.copyMakeBorder(img1, 10, 10, 10, 10, cv2.BORDER_WRAP)
    constant = cv2.copyMakeBorder(img1, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=BLUE)

    pyplot.subplot(231), pyplot.imshow(img1), pyplot.title('ORIGINAL')
    pyplot.subplot(232), pyplot.imshow(replicate), pyplot.title('REPLICATE')
    pyplot.subplot(233), pyplot.imshow(reflect), pyplot.title('REFLECT')
    pyplot.subplot(234), pyplot.imshow(reflect101), pyplot.title('REFLECT_101')
    pyplot.subplot(235), pyplot.imshow(wrap), pyplot.title('WRAP')
    pyplot.subplot(236), pyplot.imshow(constant), pyplot.title('CONSTANT')
    pyplot.show()


def imageBlending():
    image1 = cv2.imread('Irrelevant Images/Robot.jpg')
    image2 = cv2.imread('Irrelevant Images/Dragon Curve.jpg')

    image1 = image1[0:image2.shape[0], 0:image2.shape[1]]

    addedImage = cv2.addWeighted(image1, 0.7, image2, 1, 0)

    cv2.imshow("addedImage", addedImage)
    cv2.waitKey()
    cv2.destroyWindow("addedImage")


def testingPerformance():
    img1 = cv2.imread('Robot.jpg')

    e1 = cv2.getTickCount()
    for i in xrange(5, 49, 2):
        img1 = cv2.medianBlur(img1, i)
    e2 = cv2.getTickCount()
    t = (e2 - e1) / cv2.getTickFrequency()
    cv2.imwrite('Robot performance test.jpg', img1)
    print t


def cornerHarrisTest():
    filename = 'Irrelevant Images/Robot.jpg'

    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)

    # result is dilated for marking the corners, not important
    dst = cv2.dilate(dst, None)

    # Threshold for an optimal value, it may vary depending on the image.
    img[dst > 0.01 * dst.max()] = [0, 0, 255]

    # pyplot.imshow(img)
    # pyplot.show()
    cv2.imshow("image", img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()


def tomasiCornerDetector():
    img = cv2.imread('Robot.jpg')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(gray, 1000, 0.01, 10, blockSize=2)
    corners = np.int0(corners)

    for i in corners:
        x, y = i.ravel()
        cv2.circle(img, (x, y), 3, [255, 0, 255], -1)

    # cv2.imshow("", img)
    cv2.imwrite('Robot tomasi corners.jpg', img)

    # if cv2.waitKey(0) & 0xff == 27:
    # cv2.destroyAllWindows()


def siftTest():
    img = cv2.imread('Street 1.png')
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT()

    kp = sift.detect(img, None)

    img = cv2.drawKeypoints(img, kp)

    cv2.imwrite('sift_keypoints.jpg', img)


def surfTest():
    image = cv2.imread('Charizard Tile.png', 0)
    surf = cv2.SURF(50000)
    surf.extended = True
    kp, des = surf.detectAndCompute(image, None)
    print len(kp)
    # surf.hessianThreshold = 50000

    img2 = cv2.drawKeypoints(image, kp, None, (255, 0, 0), 4)
    pyplot.imshow(img2), pyplot.show()


def fastFeatureTest():
    img = cv2.imread('Robot.jpg', 0)

    # Initiate FAST object with default values
    fast = cv2.FastFeatureDetector()

    # find and draw the keypoints
    kp = fast.detect(img, None)
    img2 = cv2.drawKeypoints(img, kp, color=(255, 0, 0))

    # Print all default params
    print "Threshold: ", fast.getInt('threshold')
    print "nonmaxSuppression: ", fast.getBool('nonmaxSuppression')
    print "neighborhood: ", fast.getInt('type')
    print "Total Keypoints with nonmaxSuppression: ", len(kp)

    cv2.imwrite('fast_true.png', img2)

    # Disable nonmaxSuppression
    fast.setBool('nonmaxSuppression', 0)
    kp = fast.detect(img, None)

    print "Total Keypoints without nonmaxSuppression: ", len(kp)

    img3 = cv2.drawKeypoints(img, kp, color=(255, 0, 0))

    cv2.imwrite('fast_false.png', img3)


def drawMatches(img1, kp1, img2, kp2, matches):
    """
    My own implementation of cv2.drawMatches as OpenCV 2.4.9
    does not have this function available but it's supported in
    OpenCV 3.0.0

    This function takes in two images with their associated
    keypoints, as well as a list of DMatch data structure (matches)
    that contains which keypoints matched in which images.

    An image will be produced where a montage is shown with
    the first image followed by the second image beside it.

    Keypoints are delineated with circles, while lines are connected
    between matching keypoints.

    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """

    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1, rows2]), cols1 + cols2, 3), dtype='uint8')

    # Place the first image to the left
    out[:rows1, :cols1, :] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2, cols1:cols1 + cols2, :] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:
        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx

        # x - columns
        # y - rows
        (x1, y1) = kp1[img1_idx].pt
        (x2, y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        cv2.circle(out, (int(x1), int(y1)), 4, (255, 0, 0), 1)
        cv2.circle(out, (int(x2) + cols1, int(y2)), 4, (255, 0, 0), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(x1), int(y1)), (int(x2) + cols1, int(y2)), (255, 0, 0), 1)

    return out


def featureMatchingTest():
    img1 = cv2.imread('Street 1.png', 0)  # queryImage

    img2 = cv2.imread('Street 3.png', 0)  # trainImage

    # Initiate SIFT detector
    orb = cv2.ORB()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1, des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key=lambda x: x.distance)

    # Draw first 10 matches.
    img3 = drawMatches(img1, kp1, img2, kp2, matches[:10])

    pyplot.imshow(img3), pyplot.show()


def meanShiftTest():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    # setup initial location of window
    r, h, c, w = 250, 90, 400, 125  # simply hardcoded the values
    track_window = (c, r, w, h)

    # set up the ROI for tracking
    roi = frame[r:r + h, c:c + w]
    hsv_roi = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

    while (1):
        ret, frame = cap.read()

        if ret == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

            # apply meanshift to get the new location
            ret, track_window = cv2.CamShift(dst, track_window, term_crit)

            # Draw it on image
            topLeft = tuple(np.int8(ret[0]))
            bottomRight = tuple(np.int8(ret[1]))

            # img2 = cv2.polylines(frame, [pts], True, 255, 2)
            cv2.rectangle(frame, topLeft, bottomRight, [255, 0, 0])

            cv2.imshow('img2', frame)

            k = cv2.waitKey(60) & 0xff
            if k == 27:
                break
            else:
                cv2.imwrite(chr(k) + ".jpg", frame)

        else:
            break

    cv2.destroyAllWindows()
    cap.release()


def backgroundSubtractionTest():
    # cap = cv2.VideoCapture('vtest.avi')
    image = cv2.imread('Robot.jpg')

    fgbg = cv2.BackgroundSubtractorMOG()

    fgmask = fgbg.apply(image)

    # cv2.imshow('frame', fgmask)
    pyplot.imshow(fgmask)
    pyplot.show()

    # cv2.waitKey(0)

    # cv2.destroyAllWindows()


def liveBackgroundSubtractionTest():
    cam = cv2.VideoCapture(0)

    fgbg = cv2.BackgroundSubtractorMOG()

    # iteration = 0
    while (cam.isOpened):
        # if iteration % 2 == 0:
        # fgbg = cv2.BackgroundSubtractorMOG2()

        # iteration += 1

        f, img = cam.read()
        if f == True:
            img = cv2.flip(img, 1)
            # img=cv2.medianBlur(img,3)
            fgmask = fgbg.apply(img)
            cv2.imshow('track', fgmask)
        if (cv2.waitKey(27) != -1):
            cam.release()
            cv2.destroyAllWindows()
            break


def houghTransformTest():
    image = cv2.imread("Street 4 threshold.png")

    edges = cv2.Canny(image, 100, 100)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 150, minLineLength=0, maxLineGap=100)[0].tolist()
    for index in range(len(lines)):
        cv2.line(image, tuple(lines[index][0:2]), tuple(lines[index][2:4]), [255, 255, 0], 2)

    cv2.imwrite('Street 4 Edges.jpg', edges)
    cv2.imwrite('Street 4 Lines.jpg', image)

    # pyplot.subplot(121), pyplot.imshow(image, cmap='gray')
    #
    # pyplot.title('Original Image'), pyplot.xticks([]), pyplot.yticks([])
    # pyplot.subplot(122), pyplot.imshow(edges, cmap='gray')
    # pyplot.title('Edge Image'), pyplot.xticks([]), pyplot.yticks([])
    #
    # pyplot.show()


def contoursTest():
    image = cv2.imread('Street 4 threshold.png')

    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
    # cnt = contours[4]
    # image = cv2.drawContours(image, [cnt], 0, (0, 255, 0), 3)

    cv2.imwrite('Street 4 contours.png', image)


def floodFillTest():
    image = cv2.imread("Street 1.png")
    point = (100, 100)
    threshold = 5

    height, width = image.shape[0:2]

    mask = np.zeros((height + 2, width + 2), np.uint8)

    # color = image[point[0]][point[1]]
    # lower = color - threshold
    # lower = int(lower[0]), int(lower[1]), int(lower[2])
    # upper = (255,)*3#color + threshold
    # upper = int(upper[0]), int(upper[1]), int(upper[2])

    flippedPoint = (point[1], point[0])
    cv2.floodFill(image, mask, flippedPoint, (255, 255, 255), loDiff=(threshold,)*3, upDiff=(255,)*3)

    cv2.imwrite("Street 1 floodfill.png", image)
