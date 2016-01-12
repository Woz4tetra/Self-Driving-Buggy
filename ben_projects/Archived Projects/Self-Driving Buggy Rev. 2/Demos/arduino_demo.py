
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Arduino import Arduino
import time

def run():
    arduino = Arduino(testMotor=(-100, 100), steering=(0, 179), button=None)

    count = 5
    for _ in xrange(count):
        for value in xrange(0, 180):
            arduino['steering'] = value
            time.sleep(0.005)

        for value in xrange(179, -1, -1):
            arduino['steering'] = value
            time.sleep(0.005)