'''
This module contains an implementation of the a* path finding algorithm.

Use search and searchWaypoints.
'''

import time
import math
import numpy


def initGrid(inputGrid):
    '''
    For internal use. Converts a 2D or 3D list to a dictionary of tuple
    coordinates. The contents of inputGrid will be converted into instances
    of the Node class. (Subject to change:) The contents of inputGrid should be
    0 or 1 representing if the node is blocked or not.

    :param inputGrid: A 2D or 3D list
    :return: A tuple containing the dictionary of coordinates, width of grid,
        and height of grid
    '''
    grid = {}
    if type(inputGrid) != list:
        inputGrid = inputGrid.tolist()
    width, height = len(inputGrid[0]), len(inputGrid)
    for y in xrange(len(inputGrid)):
        for x in xrange(len(inputGrid[0])):
            grid[(x, y)] = Node(*inputGrid[y][x])
    return grid, width, height


def search(inputGrid, start, end):
    '''
    Using the start and end points provided, search the inputGrid for the most
    efficient path. The contents of inputGrid will be converted into instances
    of the Node class. (Subject to change:) The contents of inputGrid should be
    0 or 1 representing if the node is blocked or not.

    :param inputGrid: a 2D or 3D list
    :param start: a tuple containing the starting (x, y) coordinate
    :param end: a tuple containing the end (x, y) coordinate
    :return: a list of coordinates containing the path followed
    '''
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    grid, width, height = initGrid(inputGrid)
    return _search(grid, start, end, width, height)


def searchWaypoints(inputGrid, waypoints):
    '''
    Using the waypoints provided, search the inputGrid for the most
    efficient path. The contents of inputGrid will be converted into instances
    of the Node class. (Subject to change:) The contents of inputGrid should be
    0 or 1 representing if the node is blocked or not.

    :param inputGrid: a 2D or 3D list
    :param waypoints: a list of tuples containing the coordinates of the
            waypoints
    :return: a list of coordinates containing the path followed, a dictionary of
            tuple coordinates and nodes, and the time in seconds it took to
            search
            The second return element is there mostly for display purposes
            (drawing parent nodes, f values, etc.)
    '''
    path = []
    gridInfo = {}
    totalTime = 0
    
    grid, width, height = initGrid(inputGrid)
    
    for index in xrange(1, len(waypoints)):
        subPath, subInfo, subTime = _search(grid, waypoints[index - 1], waypoints[index], width, height)
        totalTime += subTime
        path.extend(subPath[:-1])
        gridInfo.update(subInfo)

    return path, gridInfo, totalTime


def _search(grid, start, end, width, height):  # works in O((width * height)^0.5) = O(n^2)
    '''
    An internal method containing the a* implementation.

    For more on a*, I'd recommend the following webpages:
    http://scriptogr.am/jdp/post/pathfinding-with-python-graphs-and-a-star
    https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode
    https://www.youtube.com/watch?v=KNXfSOx4eEE

    :param grid: a dictionary of tuple coordinates
    :param start: a tuple containing the (x, y) coordinate of the start position
    :param end: a tuple containing the (x, y) coordinate of the end position
    :param width: the width of the grid (since dictionaries don't have that info
            at the ready)
    :param height: the height of the grid
    :return: the path, the dictionary grid of tuple coordinates and nodes, and
            and the time in seconds it took to search
    '''
    time1 = time.time()

    closedset = set()
    openset = {start}

    grid[start].g = 0
    grid[start].h = heuristic(start, end)

    while len(openset) > 0:
        current = smallestF(grid, openset)

        if current == end:
            time2 = time.time()
            return traceParents(grid, start, end), grid, time2 - time1

        openset.remove(current)
        closedset.add(current)

        for neighbor in neighbors(current, width, height):
            if neighbor in closedset or grid[neighbor].blocked:
                continue
            gscore = grid[current].g + movementCost(current, neighbor)

            if (neighbor not in openset) or (gscore < grid[neighbor].g):
                grid[neighbor].parent = current
                grid[neighbor].g = gscore
                grid[neighbor].h = heuristic(neighbor, end)
                if neighbor not in openset:
                    openset.add(neighbor)
    time2 = time.time()
    return [], [], time2 - time1


def dictToList(grid):
    '''
    Convert a dictionary of nodes back into a 2D list

    :param grid: a dictionary of tuple coordinates and nodes
    :return: a 2D list
    '''
    lenX = max(grid.keys(), key=lambda element: element[0])[0] + 1
    lenY = max(grid.keys(), key=lambda element: element[1])[1] + 1
    output = [[None for _ in xrange(lenX)] for _ in xrange(lenY)]
    for x in xrange(lenX):
        for y in xrange(lenY):
            output[y][x] = grid[(x, y)]
    return output


def printGrid(grid):
    lenX = max(grid.keys(), key=lambda element: element[0])[0] + 1
    lenY = max(grid.keys(), key=lambda element: element[1])[1] + 1
    print "{"
    for x in xrange(lenX):
        for y in xrange(lenY):
            print "\t%3.2f" % grid[(x, y)].f,
        print
    print "}"


def neighbors(current, width, height):
    adjacent = []
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            gridX, gridY = x + current[0], y + current[1]
            if (x, y) != (0, 0) and 0 <= gridX < width and 0 <= gridY < height:
                adjacent.append((gridX, gridY))

    return adjacent


def smallestF(grid, indices):
    minLoc = None
    minF = Node
    for index in indices:
        if grid[index].f < minF or minF is None:
            minLoc = index
            minF = grid[index].f
    return minLoc


def traceParents(grid, start, end):
    current = end
    path = [current]
    while current != start:
        current = grid[current].parent
        path.append(current)

    return path[::-1]


def heuristic(index, end):
    return abs(index[0] - end[0]) + abs(index[1] - end[1])


def movementCost(current, adjacentIndex):
    x, y = adjacentIndex[0] - current[0], adjacentIndex[1] - current[1]
    if abs(x) == abs(y) == 1:
        return 14
    else:
        return 10


def movementCostHeading(current, adjacentIndex, heading):
    # amplitude * math.sin(heading - phase - math.pi/2) + offset
    x, y = adjacentIndex[0] - current[0], adjacentIndex[1] - current[1]
    return 15.0 * math.sin(heading - math.atan2(y, x) - math.pi) + 25.0


class Node(object):
    def __init__(self, blocked=False, height=0):
        self.g = 0
        self.h = 0
        self.blocked = blocked
        self.parent = None
        self.height = height

    @property
    def f(self):
        return self.g + self.h
