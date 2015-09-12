import math
import time

INITIAL_TICK = time.time()


class EncoderSimulated(object):
    def __init__(self, current=0.0):
        self._current = current
        self.previous = self._current

        self._previousTick = INITIAL_TICK

    @staticmethod
    def x_plus_sinx():
        scale_factor = 50
        t = (time.time() - INITIAL_TICK) * 1000.0  # in milliseconds
        return t + scale_factor * math.sin(t / scale_factor)

    @staticmethod
    def constant():
        return (time.time() - INITIAL_TICK) * 1000.0

    def _update(self):
        self.previous = self._current
        self._current = EncoderSimulated.x_plus_sinx()

    @property
    def current(self):
        self._update()
        return self._current

    @property
    def delta(self):
        self._update()
        return self._current - self.previous


class ServoSimulated(object):
    def __init__(self):
        self._heading = 0.0

    @staticmethod
    def sinx():
        scale_factor = 1000
        t = (time.time() - INITIAL_TICK) * 1000  # in milliseconds
        return math.cos(t / scale_factor) * math.pi

    def _update(self):
        self._heading = ServoSimulated.sinx()

    @property
    def heading(self):
        self._update()
        return self._heading


encoder = EncoderSimulated()
servo = ServoSimulated()

position = [0.0, 0.0]

for _ in xrange(300):
    # print "%s\t%s" % (time.time() - INITIAL_TICK, encoder.current)
    # print "%s\t%s" % (time.time() - INITIAL_TICK, servo.heading)
    position[0] += math.cos(servo.heading) * encoder.delta
    position[1] += math.sin(servo.heading) * encoder.delta
    print "%s\t%s\t%s\t%s\t%s" % (
        time.time() - INITIAL_TICK, position[0], position[1], servo.heading,
        encoder.current)
    time.sleep(0.01)
# print(time.time() - INITIAL_TICK)
