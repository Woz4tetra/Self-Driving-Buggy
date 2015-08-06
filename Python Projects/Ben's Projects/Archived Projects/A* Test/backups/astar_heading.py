import time
import math

def search(inputGrid, start, end, heading):
    time1 = time.time()
    grid = {}

    width, height = len(inputGrid[0]), len(inputGrid)
    for y in xrange(len(inputGrid)):
        for x in xrange(len(inputGrid[0])):
            grid[(x, y)] = Node(inputGrid[y][x])

    grid[start].g = 0
    grid[start].h = heuristic(start, end)
    grid[start].heading = heading

    closedset = set()
    openset = {start}

    while len(openset) > 0:
        current = smallestF(grid, openset)

        # printGrid(grid)

        if current == end:
            time2 = time.time()
            print(time2 - time1)
            return traceParents(grid, start, end), dictToList(grid)

        openset.remove(current)
        closedset.add(current)

        for neighbor in neighbors(current, width, height):
            x, y = neighbor[0] - current[0], neighbor[1] - current[1]
            angle = math.atan2(y, x) + math.pi / 2

            if neighbor in closedset or grid[neighbor].blocked or (
                        (grid[current].heading + angle) % (2 * math.pi)) >= math.pi:
                continue
            gscore = grid[current].g + movementCost(current, neighbor, grid[current].heading)

            if (neighbor not in openset) or (gscore < grid[neighbor].g):

                grid[neighbor].parent = current
                grid[neighbor].heading = (grid[current].heading + (grid[current].heading - angle) / 2) % (2 * math.pi)
                grid[neighbor].g = gscore
                grid[neighbor].h = heuristic(neighbor, end)
                if neighbor not in openset:
                    openset.add(neighbor)
    return [], []


def dictToList(grid):
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


def movementCost(current, adjacentIndex, heading):
    # amplitude * math.sin(heading - phase - math.pi/2) + offset
    x, y = adjacentIndex[0] - current[0], adjacentIndex[1] - current[1]
    return 15.0 * math.sin(heading - math.atan2(y, x) - math.pi) + 25.0


class Node(object):
    def __init__(self, blocked=False):
        self.g = 0
        self.h = 0
        self.blocked = blocked
        self.parent = None
        self.heading = None

    @property
    def f(self):
        return self.g + self.h
