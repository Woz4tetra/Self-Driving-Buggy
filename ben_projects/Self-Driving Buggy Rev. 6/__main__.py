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
import time

baud_rates = [9600, 19200, 38400, 57600, 74880, 115200, 230400, 250000]

def run():
    gps_map = map_maker.get_map("Sun Nov  1 19;53;06 2015.csv")
    binder = Binder(gps_map)
    # pid = PID()

    angle_sensor = AngleSensor()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=156)
    led13 = Led13()

    # angle_sensor.disable()
    gps.disable()
    encoder.disable()
    servo.disable()
#    led13.disable()

    initialize("SerialBox.ino", baud_rate=baud_rates[2], delay=0.004)
    
    encoder.position = gps.get()

    while True:
        roll, pitch, yaw = angle_sensor.get()
        print(roll, pitch, yaw)
        # print encoder.get(yaw)
        led13.toggle()
        # gps.get()
        # print gps.coordinates, gps.angle, gps.speed
        # servo.set((servo.value + 1) % 156)
        # servo.toggle('min', 'max')
        # time.sleep(0.01)


# bind gps and encoder to track
# apply PID, send command to servo


if __name__ == '__main__':
    print __doc__
    run()
