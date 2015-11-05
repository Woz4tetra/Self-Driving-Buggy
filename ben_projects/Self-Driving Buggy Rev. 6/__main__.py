'''
    Written by Ben Warwick
    
    Self-Driving Buggy Rev. 6 for Self-Driving Buggy PRoject
    Version 11/2/2015
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

from controllers.binder import Binder
# from controllers.pid import PID
from map import map_maker
from controllers.user_objects import *

def run():
    gps_map = map_maker.get_map("Sun Nov  1 19;53;06 2015.csv")
    binder = Binder(gps_map)
    # pid = PID()

    angle_sensor = AngleSensor()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=156)
    led13 = Led13()

    initialize("SerialBox.ino")

    encoder.position = gps.get()

    while True:
        roll, pitch, yaw = angle_sensor.get()
        print encoder.get(yaw), gps.get()
        led13.toggle()
        print gps.get()
        # servo.toggle('min', 'max')


# bind gps and encoder to track
# apply PID, send command to servo


if __name__ == '__main__':
    print __doc__
    run()
