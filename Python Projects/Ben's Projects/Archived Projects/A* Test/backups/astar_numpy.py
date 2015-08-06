import numpy
import collections

Index = collections.namedtuple('Index', 'x y')

class astar(object):
    def __init__(self, inputField, startIndex, endIndex):
        self.fieldData = numpy.array(inputField, dtype=object)  # contains z, passable values

        self.fieldValues = numpy.zeros((len(inputField), len(inputField[0]), 5))  # contains H, G, F, parent x, parent y
        self.fieldValues.fill(numpy.nan)

        self.start = Index(x=startIndex[0], y=startIndex[1])
        self.end = Index(x=endIndex[0], y=endIndex[1])

        self.xyIndices = list(numpy.ndindex(len(inputField), len(inputField[0])))
        hValues = numpy.apply_along_axis(astar.getHeuristic, 1, self.xyIndices, self.end)
        self.fieldValues[:, :, 0] = hValues.reshape((len(inputField), len(inputField[0])))

    def compute(self):
        current = self.start

        self.fieldValues[self.start.x, self.start.y, 1] = 0

        openList = numpy.array([current])
        while numpy.any(numpy.all(self.end == openList, axis=1)) == False:
            openList = numpy.delete(openList, numpy.where(numpy.all(openList == current, axis=1)), axis=0)
            connectedNodes, diagonalNodes = astar.getAdjacentNodes(current, self.fieldValues.shape)
            adjacentNodes = numpy.append(connectedNodes, diagonalNodes, axis=0)

            self.assignValues(diagonalNodes, connectedNodes, adjacentNodes, current)

            if len(openList) > 0:
                openList = numpy.append(openList, adjacentNodes, axis=0)
            else:
                openList = adjacentNodes

            if len(openList) == 0:
                self.end = self.start
                break

            current = Index(*self.smallestFCost(openList))
            astar.printField(self.fieldValues)
        return self.traceParentNodes()

    def traceParentNodes(self):
        index = self.end
        path = []

        while index != self.start:
            path.append(index)
            index = Index(*self.fieldValues[index.y, index.x][3:])
        path.append(self.start)
        return path

    def assignValues(self, diagonalNodes, connectedNodes, adjacentNodes, current):

        for y, x in adjacentNodes:
            if numpy.all(numpy.isnan(self.fieldValues[y, x][3:])):  # if parent node unassigned
                self.fieldValues[y, x, 3:5] = current  # assign parent node

        for y, x in connectedNodes:
            if numpy.all(numpy.isnan(self.fieldValues[y, x][1:2])):  # if HGF nodes unassigned
                self.fieldValues[y, x, 1] = 10
            else:
                self.fieldValues[y, x, 1] += 10

        for y, x in diagonalNodes:
            if numpy.all(numpy.isnan(self.fieldValues[y, x][1:2])):  # if HGF nodes unassigned
                self.fieldValues[y, x, 1] = 14
            else:
                self.fieldValues[y, x, 1] += 14

        self.fieldValues[:, :, 2] = self.fieldValues[:, :, 0] + self.fieldValues[:, :, 1]  # compute F total cost


    def smallestFCost(self, openList):
        smallestF = self.fieldValues[0, 0, 2]
        smallestF_index = openList[0]
        for index in openList:
            if self.fieldValues[index[0], index[1], 2] < smallestF:
                smallestF = self.fieldValues[index[0], index[1], 2]
                smallestF_index = index
        return smallestF_index

    @staticmethod
    def printField(field):
        converted = field.tolist()
        print "{"
        for row in converted:
            for col in row:
                print "\t" + str(col),
            print
        print "}"

    @staticmethod
    def getHeuristic(index, endIndex):
        stepCounter = 0

        stepCounter += abs(endIndex.x - index[0])
        stepCounter += abs(endIndex.y - index[1])

        return stepCounter

    @staticmethod
    def getAdjacentNodes(index, shape):
        yLen, xLen = shape[0:2]

        connected = numpy.array([[-1, 0], [1, 0], [0, 1], [0, -1]])
        diagonal = numpy.array([[-1, -1], [1, 1], [-1, 1], [1, -1]])

        connected += index
        diagonal += index

        connected = astar.trimArray(connected, 0, yLen, 0)
        connected = astar.trimArray(connected, 0, xLen, 1)

        diagonal = astar.trimArray(diagonal, 0, yLen, 0)
        diagonal = astar.trimArray(diagonal, 0, xLen, 1)

        return connected, diagonal

    @staticmethod
    def trimArray(array, minimum, maximum, axis):
        array = numpy.delete(array, numpy.where(array[:, axis] >= maximum), axis=0)
        array = numpy.delete(array, numpy.where(array[:, axis] < minimum), axis=0)
        return array