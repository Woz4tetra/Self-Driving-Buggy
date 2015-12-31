
'''
This module is a helper to the astar module. It works in the /maps directory and
allows astar to save and recall maps.

Dependencies:
- numpy: http://www.numpy.org
'''

import time # strftime key guide: strftime.org
import os
import numpy

projectDir = os.path.dirname(os.path.realpath(__file__))

def write(grid, start=(0, 0), end=(0, 0)):
    '''
    Write a map text file to the /maps directory.
    If a map were 3x3, start = (0, 0), and end = (2, 2), the output file would
    look like:
        [[0, 0, 1],
         [0, 0, 1],
         [1, 1, 1]]
        (0, 0)
        (2, 2)

    :param grid: a 2D numpy array
    :param start:  a tuple containing the starting (x, y) coordinate
    :param end:  a tuple containing the end (x, y) coordinate
    :return: None
    '''
    fileName = time.strftime("A* map %b %-d, %Y, %-I-%M%p %Ss.txt", time.localtime(time.time()))
    print "wrote: " + str(fileName)
    with open(projectDir + "/maps/" + fileName, "w") as mapFile:
        mapFile.write(str(grid.tolist()))
        mapFile.write("\n" + str(start))
        mapFile.write("\n" + str(end))

def read():
    '''
    Read the first file in the /maps/selected directory sorted alphabetically.

    :return: a tuple containg a 2D numpy array containing the grid info,
            start coordinate, and end coordinate
    '''
    filePath = projectDir + "/maps/selected/"
    files = os.listdir(filePath)
    fileName = ""
    for file in sorted(files):
        if "A* map" in file:
            fileName = file
            break
    with open(filePath + fileName, "r") as mapFile:
        mapString, start, end = mapFile.read().split("\n")
        start = eval(start)
        end = eval(end)
        return numpy.array(eval(mapString), dtype=numpy.int8), start, end

def make(width, height, blocked=None, heightFunc=None):
    if blocked is not None:
        raise NotImplementedError
    if heightFunc is not None:
        raise NotImplementedError
    return numpy.zeros((width, height, 2))