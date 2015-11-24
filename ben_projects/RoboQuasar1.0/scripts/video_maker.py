
'''
    Written by Ben Warwick
    
    video_maker.py, written for the Self-Driving Buggy Project
    Version 11/24/2015
    =========
    
    
'''

import time
import cv2
import os
import sys
import re

projectDir = os.path.dirname(os.path.realpath(__file__))

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def writeFromImages(fps=30, name="", includeTimestamp=True,
                          format='mp4v'):
    files = natural_sort(os.listdir(projectDir + "/Images"))
    
    images = []
    width, height = None, None
    
    print "Using files:"
    for file in files:
        if file[-3:] == "png":
            print file
            image = cv2.imread(projectDir + "/Images/" + file)
            if width is None and height is None:
                height, width = image.shape[0:2]
            else:
                image = cv2.resize(image, (width, height))
            images.append(image)
    
    print "Number of frames:", len(images)
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

