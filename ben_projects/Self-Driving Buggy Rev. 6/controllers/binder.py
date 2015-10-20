
from map import map_maker

class Binder:
    def __init__(self, map, accuracy=0.000002):
        self.map = map
        self.accuracy = accuracy
        self.prev_bind = 0

    def bind(self, position):
        if self.prev_bind >= len(self.map) or self.prev_bind < 0:
            raise Exception("bind outside track")

        for i in xrange(self.prev_bind, len(self.map)):
            if self.near(i, position):
                self.prev_bind = i
                return self.map[i]

        for i in xrange(len(self.map)):
            if self.near(i, position):
                self.prev_bind = i
                return self.map[i]

        return False

    def near(self, index, position):
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
    pre_bind = binder.prev_bind
    print binder.map[pre_bind]
    print pos

if __name__ == '__main__':
    test()


