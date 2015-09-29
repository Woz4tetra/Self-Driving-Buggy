'''

Dependencies:
- pygame: http://www.pygame.org/news.html
- numpy: http://www.numpy.org
- astar: internal
- mapmaker: internal
'''

import math
import time

import numpy

import pygame

import mapmaker
import astar

class Drawer(object):
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    WHITE = (255, 255, 255)
    YELLOW = (255, 230, 0)
    LIGHTGREEN = (0, 255, 0)
    GREEN = (0, 150, 0)
    BLUE = (0, 70, 200)
    RED = (200, 0, 0)

    def __init__(self, gridWidth, gridHeight, width, height, start, end,
                 grid=None):
        self.width = width
        self.height = height
        self.margin = 1

        self.initGridDisplay(gridWidth, gridHeight)

        self.start = start
        self.end = end

        if grid is None:
            self.grid = numpy.zeros(
                (self.gridHeight, self.gridWidth, 2))  # init empty grid
        else:
            self.grid = grid

        self.updateVisible()  # initialized the cropped grid

        self.done = False  # done flag

        self.brushMode = False  # what value to paint the grid (blocked or unblocked)
        self.brushSize = 1  # radius of the brush

        self.mouseDown = False

        self.showFull = False

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        self.particleAccel = [0, 0]

        pygame.display.set_caption("A*")

        self.time0 = time.time()

    def initGridDisplay(self, gridWidth, gridHeight):
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight

        self.cellSize = min(self.width / self.gridWidth,
                            self.width / self.gridHeight,
                            self.height / self.gridWidth,
                            self.height / self.gridHeight)  # get cell size that fits the screen
        if self.cellSize <= 9:  # if the cells are less than 9 pixels, don't draw grid lines
            self.margin = 0
            if self.cellSize <= 0:
                self.cellSize = 1

        self.window = (80, 80)  # how much of the grid to show at a time
        self.offset = [0, 0]  # location of visible grid window
        # self.delOffset = (20, 20)  # how much to move the window by when the arrow keys are pressed

        self.path = []  # the plotted a* path
        self.bezierXvals, self.bezierYvals = [], []
        self.waypoints = []  # points selected by user between start and end
        self.gridInfo = {}  # contains the objects used by the astar module. Used for drawing later

    def getCellIndex(self):
        pos = pygame.mouse.get_pos()  # get mouse coordinates
        gridX = int(pos[0] / self.cellSize)  # convert pixels to grid indices
        gridY = int(pos[1] / self.cellSize)

        # constrain the indices to the grid bounds
        if gridY < 0:
            gridY = 0
        if gridY >= self.gridHeight:
            gridY = self.gridHeight - 1
        if gridX < 0:
            gridX = 0
        if gridX >= self.gridWidth:
            gridX = self.gridWidth - 1
        return gridX, gridY

    def drawCell(self, cellX, cellY, color):
        pygame.draw.rect(self.screen, color,
                         [self.cellSize * cellX + self.margin,
                          self.cellSize * cellY + self.margin,
                          self.cellSize - self.margin,
                          self.cellSize - self.margin])  # convert index to pixels and apply margin

    def updateVisible(self):
        self.visibleGrid = self.grid[
                           self.offset[1]:self.offset[1] + self.window[1],
                           self.offset[0]:self.offset[0] + self.window[
                               0]]  # crop grid

    def connectCells(self, cellX0, cellY0, cellX1, cellY1, color=(0, 0, 0),
                     width=2):
        # draw a line between the centers of two cells (for drawing paths)
        pygame.draw.line(self.screen, color,
                         (cellX0 * self.cellSize + self.cellSize / 2,
                          cellY0 * self.cellSize + self.cellSize / 2),
                         (cellX1 * self.cellSize + self.cellSize / 2,
                          cellY1 * self.cellSize + self.cellSize / 2), width)

    @staticmethod
    def pythagoreanDist(x0, y0, x1, y1):
        return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

    def enumerateGrid(self):
        if self.showFull == False:
            return numpy.ndenumerate(self.visibleGrid[:, :, 0])
        else:
            return numpy.ndenumerate(self.grid[:, :, 0])

    def updateNode(self, cellX, cellY, height, blocked):
        if 0 <= cellX < self.gridWidth and 0 <= cellY < self.gridHeight:
            self.grid[cellY, cellX, 0] = int(blocked)
            self.grid[cellY, cellX, 1] = height
        #        print (cellY, cellX), self.grid[cellY, cellX]

    def loop(self):
        self.screen.fill(Drawer.GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseDown = True
                gridX, gridY = self.getCellIndex()

                # set the brush mode to the opposite of the selected cell
                self.brushMode = not self.grid[gridY, gridX, 0]
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseDown = False

            elif event.type == pygame.MOUSEMOTION:
                self.offset = list(self.getCellIndex())
                self.offset[0] -= self.window[0] / 2
                self.offset[1] -= self.window[1] / 2

                if self.offset[0] + self.window[0] >= self.gridWidth:
                    self.offset[0] = self.gridWidth - self.window[0]
                if self.offset[1] + self.window[1] >= self.gridHeight:
                    self.offset[1] = self.gridHeight - self.window[1]

                if self.offset[0] < 0:
                    self.offset[0] = 0
                if self.offset[1] < 0:
                    self.offset[1] = 0
                self.updateVisible()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if len(self.waypoints) == 0:
                        self.path, self.gridInfo, plotTime = astar.search(
                            self.grid, self.start,
                            self.end)  # find a path between the start and end
                    else:
                        self.path, self.gridInfo, plotTime = astar.searchWaypoints(
                            self.grid, [self.start] + self.waypoints + [
                                self.end])  # find a path between the start, waypoints, and the end

                    print "a* time:", plotTime

                # change the brush size (only squares)
                elif event.key == pygame.K_EQUALS:
                    self.brushSize += 1
                    print(self.brushSize)

                elif event.key == pygame.K_MINUS:
                    self.brushSize -= 1
                    if self.brushSize < 1:
                        self.brushSize = 1
                    print(self.brushSize)

                # if key is a numbered key, change brush size to that key
                elif 0 <= event.key - ord('0') <= 9:
                    self.brushSize = int(event.key - ord('0'))
                    if self.brushSize < 1:
                        self.brushSize = 1
                    print(self.brushSize)

                # set start position to the position of the mouse
                elif event.key == pygame.K_s:
                    self.start = self.getCellIndex()
                    self.grid[self.start[1], self.start[0], 0] = 0

                # set end position to the position of the mouse
                elif event.key == pygame.K_e:
                    self.end = self.getCellIndex()
                    self.grid[self.end[1], self.end[0], 0] = 0

                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.done = True
                    break

                # change the visible window by self.delOffset depending on the direction of arrow keys
                # elif pygame.K_UP <= event.key <= pygame.K_LEFT:
                #     if event.key == pygame.K_UP:
                #         self.offset[1] -= self.delOffset[1]
                #         if self.offset[1] < 0:
                #             self.offset[1] = 0
                #     elif event.key == pygame.K_DOWN:
                #         self.offset[1] += self.delOffset[1]
                #         if self.offset[1] + self.window[1] >= self.gridHeight:
                #             self.offset[1] = self.gridHeight - self.window[1]
                #     elif event.key == pygame.K_LEFT:
                #         self.offset[0] -= self.delOffset[0]
                #         if self.offset[0] < 0:
                #             self.offset[0] = 0
                #     elif event.key == pygame.K_RIGHT:
                #         self.offset[0] += self.delOffset[0]
                #         if self.offset[0] + self.window[0] >= self.gridWidth:
                #             self.offset[0] = self.gridWidth - self.window[0]
                #     self.updateVisible()

                # Fill the entire grid
                elif event.key == pygame.K_f:
                    self.grid = numpy.ones((self.gridHeight, self.gridWidth, 2))
                    self.grid[:, :, 1] = 0
                    self.grid[self.start[1], self.start[0], 0] = 0
                    self.grid[self.end[1], self.end[0], 0] = 0
                    self.updateVisible()

                # reveal the entire grid
                elif event.key == pygame.K_TAB:
                    self.showFull = True

                # reset grid to initial state
                elif event.key == pygame.K_c:
                    self.grid = numpy.zeros(
                        (self.gridHeight, self.gridWidth, 2))
                    self.path = []
                    self.waypoints = []
                    self.gridInfo = {}
                    self.updateVisible()

                # add a waypoint to current mouse position
                elif event.key == pygame.K_w:
                    cellX, cellY = self.getCellIndex()
                    self.waypoints.append((cellX, cellY))

                # delete waypoint nearest to mouse
                elif event.key == 8:  # delete key
                    cellX, cellY = self.getCellIndex()
                    closestPoint = 0
                    shorestDist = None

                    for index, (wpY, wpX) in enumerate(self.waypoints):
                        distance = Drawer.pythagoreanDist(wpX, wpY, cellX,
                                                          cellY)
                        if distance < shorestDist or shorestDist is None:
                            shorestDist = distance
                            closestPoint = index

                    print self.waypoints.pop(closestPoint)

                # save map data to text file or load map data from text file if map is empty
                elif event.key == pygame.K_RETURN:
                    if numpy.all(self.grid[:, :, 0] == 0):
                        self.grid, self.start, self.end = mapmaker.read()
                        self.initGridDisplay(self.grid.shape[1],
                                             self.grid.shape[0])
                        self.updateVisible()
                    else:
                        mapmaker.write(self.grid, self.start, self.end)

                elif pygame.K_i <= event.key <= pygame.K_l:
                    if event.key == pygame.K_i:
                        self.particleAccel[1] -= 1
                    elif event.key == pygame.K_j:
                        self.particleAccel[0] -= 1
                    elif event.key == pygame.K_k:
                        self.particleAccel[1] += 1
                    elif event.key == pygame.K_l:
                        self.particleAccel[0] += 1


            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:
                    self.showFull = False

            if self.mouseDown == True:
                clickedX, clickedY = self.getCellIndex()
                radius = int(round(float(self.brushSize) / 2))
                for gridY in xrange(
                        max(clickedY - radius + self.brushSize % 2, 0),
                        min(clickedY + radius, self.gridHeight)):
                    for gridX in xrange(
                            max(clickedX - radius + self.brushSize % 2, 0),
                            min(clickedX + radius, self.gridWidth)):
                        self.grid[gridY, gridX, 0] = self.brushMode

                self.updateVisible()

        for (cellY, cellX), element in self.enumerateGrid():
            if self.showFull == False:
                cellX += self.offset[0]
                cellY += self.offset[1]
            color = Drawer.WHITE
            if element == 1:
                color = Drawer.GREEN

            self.drawCell(cellX, cellY, color)

        self.drawCell(self.start[0], self.start[1], Drawer.RED)
        self.drawCell(self.end[0], self.end[1], Drawer.BLUE)

        for (cellX, cellY) in self.waypoints:
            self.drawCell(cellX, cellY, Drawer.BLACK)

        for (cellY, cellX), element in self.enumerateGrid():
            if self.showFull == False:
                cellX += self.offset[0]
                cellY += self.offset[1]
            if len(self.gridInfo) > 0:
                parent = self.gridInfo[(cellX, cellY)].parent
                if parent is not None:
                    self.connectCells(cellX, cellY,
                                      parent[0], parent[1], Drawer.RED, 1)
        for index in xrange(1, len(self.path)):
            self.connectCells(self.path[index - 1][0],
                              self.path[index - 1][1],
                              self.path[index][0],
                              self.path[index][1])
        for (x, y) in zip(self.bezierXvals, self.bezierYvals):
            self.screen.fill(Drawer.BLUE, ((self.cellSize * (x + 0.5), self.cellSize * (
                y + 0.5)), (1, 1)))

        pygame.draw.rect(self.screen, Drawer.BLACK,
                         [0, 0, self.cellSize * self.gridWidth,
                          self.cellSize * self.gridHeight], 1)

    def getAccel(self):
        data = self.particleAccel + [0, 0, 0, 0, time.time() - self.time0]
        self.time0 = time.time()
        return data

    def update(self):
        self.clock.tick(60)
        pygame.display.flip()

    def drawParticle(self, cellX, cellY):
        self.drawCell(cellX, cellY, Drawer.LIGHTGREEN)

    def deinit(self):
        pygame.quit()
