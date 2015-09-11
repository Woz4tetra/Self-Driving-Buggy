import copy
from math import pi
import astar_heading

import eventBasedAnimation
import astar

from Tkinter import NW
from Tkinter import SW

def createArray(initialValue, xSize, ySize):
    array = [[copy.copy(initialValue) for _ in xrange(xSize)] for _ in xrange(ySize)]
    return array


def init_Astar(data):
    data.selectedCell = (None, None)

    data.path = []
    data.grid = createArray(False, data.gridWidth, data.gridHeight)
    data.gridInfo = []

    if data.width < data.height:
        data.pxSize = data.width
        data.gridSize = data.gridWidth
    else:
        data.pxSize = data.height
        data.gridSize = data.gridHeight


def drawNode(canvas, data, xIndex, yIndex, color):
    x0 = float(xIndex) / data.gridSize * data.pxSize
    y0 = float(yIndex) / data.gridSize * data.pxSize

    x1 = float(xIndex + 1) / data.gridSize * data.pxSize
    y1 = float(yIndex + 1) / data.gridSize * data.pxSize

    canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)


def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red % 256, green % 256, blue % 256)

def drawGridInfo(canvas, data):
    for xIndex in xrange(data.gridWidth):
        for yIndex in xrange(data.gridHeight):
            x0 = float(xIndex) / data.gridSize * data.pxSize
            y0 = float(yIndex) / data.gridSize * data.pxSize

            if len(data.gridInfo) > 0:
                cellHalf = (data.pxSize / data.gridSize) / 2

                # fScore = data.gridInfo[yIndex][xIndex].f
                # if fScore > 0:
                #     canvas.create_text(x0, y0, text="%2.2f" % (fScore), anchor=NW, font="Avenir 9")


                # heading = data.gridInfo[yIndex][xIndex].heading
                # if heading is not None:
                #     canvas.create_text(x0, y0 + cellHalf * 2, text="%2.0f" % (heading * 180 / pi), anchor=SW, font="Avenir 9")

                if data.gridInfo[yIndex][xIndex].parent is not None:
                    x2, y2 = data.gridInfo[yIndex][xIndex].parent

                    x2 = float(x2) / data.gridSize * data.pxSize
                    y2 = float(y2) / data.gridSize * data.pxSize

                    canvas.create_line(x0 + cellHalf, y0 + cellHalf, x2 + cellHalf, y2 + cellHalf, fill="red")

                    radius = 5
                    canvas.create_oval(x2 + cellHalf - radius, y2 + cellHalf - radius,
                                       x2 + cellHalf + radius, y2 + cellHalf + radius,
                                       fill=rgbString((data.gridWidth - xIndex) * 255 / data.gridWidth,
                                                      0, 0))


def drawGridLines(canvas, data):
    for x in xrange(data.gridSize):
        x *= float(data.pxSize) / data.gridSize
        canvas.create_line(x, 0, x, data.pxSize)

    for y in xrange(data.gridSize):
        y *= float(data.pxSize) / data.gridSize
        canvas.create_line(0, y, data.pxSize, y)


def drawGrid(canvas, data):
    for xIndex in xrange(data.gridWidth):
        for yIndex in xrange(data.gridHeight):
            node = data.grid[yIndex][xIndex]
            color = "gray"
            if (xIndex, yIndex) == data.start:
                color = "green"
            elif (xIndex, yIndex) == data.end:
                color = "yellow"
            elif node == True:
                color = "red"
            drawNode(canvas, data, xIndex, yIndex, color)


def drawPath(canvas, data):
    for index in xrange(1, len(data.path)):
        x0, y0 = data.path[index - 1]
        x1, y1 = data.path[index]
        cellHalf = (data.pxSize / data.gridSize) / 2
        canvas.create_line(float(x0) * data.pxSize / data.gridSize + cellHalf,
                           float(y0) * data.pxSize / data.gridSize + cellHalf,
                           float(x1) * data.pxSize / data.gridSize + cellHalf,
                           float(y1) * data.pxSize / data.gridSize + cellHalf, width=2)


def draw_Astar(canvas, data):
    drawGrid(canvas, data)
    drawGridLines(canvas, data)
    drawGridInfo(canvas, data)
    drawPath(canvas, data)


def mouse_Astar(event, data):
    x, y = data.selectedCell

    if x is not None and y is not None and data.selectedCell != data.start and data.selectedCell != data.end:
        data.grid[y][x] = not data.grid[y][x]


def getSelectedCell(event, data):
    conversion = float(data.gridSize) / data.pxSize
    x, y = int(event.x * conversion), int(event.y * conversion)
    if x >= data.gridWidth:
        x = data.gridWidth - 1
    if x <= 0:
        x = 0
    if y >= data.gridHeight:
        y = data.gridHeight - 1
    if y <= 0:
        y = 0
    data.selectedCell = (x, y)


def mouseDrag_Astar(event, data):
    x, y = data.selectedCell
    if x is not None and y is not None:
        previousCell = data.selectedCell

        isBlocked = data.grid[y][x]

        getSelectedCell(event, data)

        x, y = data.selectedCell
        if previousCell != data.selectedCell and data.grid[y][x] != isBlocked:
            mouse_Astar(None, data)


def mouseMove_Astar(event, data):
    if event.x > data.pxSize or event.y > data.pxSize:
        data.selectedCell = (None, None)
    else:
        getSelectedCell(event, data)


def key_Astar(event, data):
    if (event.keysym == "s"):
        data.start = data.selectedCell
    elif (event.keysym == "e"):
        data.end = data.selectedCell
    elif (event.keysym == "space"):
        data.path, data.gridInfo = astar.search(data.grid, data.start, data.end)
        # data.path, data.gridInfo = astar.searchWithHeading(data.grid, data.start, data.end, 3 * pi / 2)
    elif (event.keysym == "Tab"):
        data.gridInfo = []
    elif (event.keysym == "c"):
        data.grid = createArray(False, data.gridWidth, data.gridHeight)


def run(start, end, gridWidth, gridHeight):
    eventBasedAnimation.run(
        initFn=init_Astar,
        drawFn=draw_Astar,
        mouseFn=mouse_Astar,
        mouseMoveFn=mouseMove_Astar,
        mouseDragFn=mouseDrag_Astar,
        # mouseReleaseFn=mouseRelease_Astar,
        keyFn=key_Astar,
        # keyReleaseFn=

        timerDelay=100,

        width=1000,
        height=720,

        start=start,
        end=end,
        gridWidth=gridWidth,
        gridHeight=gridHeight,
    )
