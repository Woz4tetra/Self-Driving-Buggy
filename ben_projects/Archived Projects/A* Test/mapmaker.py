
import time # strftime key guide: strftime.org
import os
import numpy

projectDir = os.path.dirname(os.path.realpath(__file__))

def write(grid):
    fileName = time.strftime("A* map %I-%M-%S %b %-d, %Y.txt", time.localtime(time.time()))
    with open(projectDir + "/maps/" + fileName, "w") as mapFile:
        mapFile.write(str(grid.tolist()))

def read():
    filePath = projectDir + "/maps/selected/"
    files = os.listdir(filePath)
    fileName = ""
    for file in files:
        if "A* map" in file:
            fileName = file
            break
    with open(filePath + fileName, "r") as mapFile:
        return numpy.array(eval(mapFile.read()), dtype=numpy.int8)