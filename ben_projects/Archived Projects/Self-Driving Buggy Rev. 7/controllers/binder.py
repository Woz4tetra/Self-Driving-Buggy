
from map import map_maker

class Binder:
    def __init__(self, map, accuracy=0.000002):
        self.map = map
        self.accuracy = accuracy
        self.prevBind = 0

    def bind(self, position):
        if self.prevBind >= len(self.map) or self.prevBind < 0:
            raise Exception("bind outside track")

        for index in xrange(self.prevBind, len(self.map)):
            if self.isNear(index, position):
                self.prevBind = index
                return index + 1

        for index in xrange(len(self.map)):
            if self.isNear(index, position):
                self.prevBind = index
                return index + 1

        return False

    def isNear(self, index, position):
        dist_lat = abs(float(self.map[index][0]) - position[0])
        dist_lng = abs(float(self.map[index][1]) - position[1])
        dist = ((dist_lat ** 2) + (dist_lng ** 2) ** (0.5))

        if dist > self.accuracy:
            return False

        elif dist <= self.accuracy:
            return True


def test():
    map = map_maker.get_map("Test.csv")
    # map_maker.write_map(map, "Test")
    binder = Binder(map)

    pos = binder.bind((40.44149,-79.948))
    pre_bind = binder.prevBind
    print binder.map[pre_bind]
    print pos

if __name__ == '__main__':
    test()


