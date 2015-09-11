import copy


class AStar(object):
    def __init__(self, inputMap):
        self.map = Map(inputMap)

        self.path = []

    def refresh(self, inputMap):
        self.map.refresh(inputMap)

    def search(self, start, end):
        # current = start
        # openset = set()
        # closedList = set()
        #
        # self.map[current].g = 0
        # self.map[current].h = heuristic(start, end, current)
        # # self.map.setParent([current], current)
        #
        # closedList.add(current)
        # openset.add(current)
        #
        # while (end in openset) == False:
        #     openset.remove(current)
        #     adjacent = self.adjacentNodes(current, closedList)
        #
        #     self.map.setG(adjacent, current)
        #     self.map.setH(current, heuristic(start, end, current))
        #     self.map.setParent(adjacent, current)
        #
        #     print openset,
        #     openset.update(adjacent)
        #     print openset
        #
        #     if len(openset) == 0:
        #         end = start
        #         break
        #
        #     current = self.map.minF(copy.copy(openset), current)
        #
        #     closedList.update(set(adjacent))
        #     closedList.add(current)
        # print(self.map)
        # return self.traceParents(start, end)
        closedset = set()
        openset = {start}

        self.map[start].g = 0
        self.map[start].h = heuristic(end, start)

        while len(openset) > 0:
            current = self.map.minF(copy.copy(openset))

            print(self.map)
            if current == end:
                return self.traceParents(start, end)

            openset.remove(current)
            closedset.add(current)

            for neighbor in self.adjacentNodes(current):
                if neighbor in closedset:
                    continue
                gScore = self.map[current].g + movementCost(current, neighbor)

                if (neighbor not in openset) or gScore < self.map[neighbor].g:
                    self.map[neighbor].parent = current
                    self.map[neighbor].g = gScore
                    self.map[neighbor].g = heuristic(end, neighbor)
                    openset.add(neighbor)
        return []


    def traceParents(self, start, end):
        current = end
        path = [current]
        while current != start:
            current = self.map[current].parent
            path.append(current)
        return path[::-1]

    def adjacentNodes(self, index):
        adjacent = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                gridX, gridY = x + index[0], y + index[1]

                if (0 <= gridX < self.map.width and 0 <= gridY < self.map.height and
                            (x, y) != (0, 0)):
                    adjacent.append((gridX, gridY))
        return adjacent


class Map(dict):
    def __init__(self, inputMap):
        map = {}
        self.blocked = []
        self.width, self.height = len(inputMap[0]), len(inputMap)

        for y in xrange(len(inputMap)):
            for x in xrange(len(inputMap[0])):
                map[(x, y)] = Node(inputMap[y][x])

                if map[(x, y)].blocked == True:
                    self.blocked.append((x, y))
        super(Map, self).__init__(map)

    def __getitem__(self, item):
        return dict.__getitem__(self, item)

    def setH(self, index, cost):
        self[index].h = cost

    def setG(self, indices, current):
        for index in indices:
            self[index].g += movementCost(current, index)

    def setParent(self, indices, parent):
        for index in indices:
            # if self[index].parent is None:
            self[index].parent = parent

    def minF(self, indices):
        minLocation = indices.pop()
        smallestF = self[minLocation]
        while len(indices) > 0:
            location = indices.pop()
            if self[location].f < smallestF:
                minLocation = location
                smallestF = self[location].f
        return minLocation


    def refresh(self, inputMap):
        dict.update(self, inputMap)

    def __str__(self):
        maxX, maxY = max(self.keys())
        output = "{\n"
        for y in xrange(maxY):
            output += "\t"
            for x in xrange(maxX):
                output += str(self[(x, y)]) + ", "
            output += "\n"
        return output + "}"


class Node(object):
    def __init__(self, blocked=False):
        self.g = 0
        self.h = 0
        self.blocked = blocked
        self.parent = None

    @property
    def f(self):
        return self.g + self.h

    def __repr__(self):
        # return "[%s, %s, %s, %s]" % (self.g, self.h, int(self.blocked), self.parent)
        return str(self.parent)
        # return str(self.f)


def movementCost(current, index):
    x, y = index[0] - current[0] + 1, index[1] - current[1] + 1
    pattern = [[14, 10, 14],
               [10, 00, 10],
               [14, 10, 14]]
    # print(current, index, pattern[y][x])
    return pattern[y][x]


def heuristic(end, index):
    return abs(index[0] - end[0]) + abs(index[1] - end[1])
