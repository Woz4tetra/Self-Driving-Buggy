import time
import cv2
import os
import sys

projectDir = os.path.dirname(os.path.realpath(__file__))

def writeFromImages(fps=30, name="", includeTimestamp=True,
                          format='mp4v'):
    files = os.listdir(projectDir + "/Images")
    images = []
    width, height = None, None

    for file in files:
        if file[-3:] == "png":
            image = cv2.imread(projectDir + "/Images/" + file)
            if width is None and height is None:
                height, width = image.shape[0:2]
            else:
                image = cv2.resize(image, (width, height))
            images.append(image)
    
    print len(images)
    if len(images) == 0:
        print("No images found!")
        quit()

    videoName = name
    if name != "" and includeTimestamp == True:
        videoName += " "
    if name == "" or includeTimestamp == True:
        videoName += time.strftime("%c").replace(":", ";") + "." + format

    fourcc = cv2.VideoWriter_fourcc(*format)
    video = cv2.VideoWriter()
    video.open(projectDir + "/Videos/" + videoName, fourcc, fps,
                    (width, height), True)

    print "Initialized video named '%s'.\nIt will be written to:\n%s" % (
        videoName, projectDir + "/Videos/")

    for image in images:
        video.write(image)

    video.release()

if __name__ == '__main__':
    arguments = sys.argv
    
    if arguments[1].isdigit():
        writeFromImages(int(arguments[1]))
    else:
        writeFromImages()