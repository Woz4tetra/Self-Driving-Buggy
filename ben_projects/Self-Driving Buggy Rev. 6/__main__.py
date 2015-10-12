'''
Written by Ben Warwick

Self-Driving Buggy Rev. 6 for Self-Driving Buggy PRoject
Version 9/15/2015
=========

This program controls the self-driving buggy. It manages computer vision,
microcontroller control and data collection, PID feedback, encoder to x, y
algorithms, path finding, GPS algorithms, and IMU algorithms. Each of these is
implemented in its own file.

Usage
-----
python __main__.py
- or - (in folder directory):
python Self-Driving\ Buggy\ Rev.\ 6

'''

from binder import Binder
from pid import PID

def run():
    binder = Binder()
    pid = PID()

    while True:
        pid.update(binder.bind())

        # bind gps and encoder to track
        # apply PID, send command to servo


if __name__ == '__main__':
    print __doc__
    run()
