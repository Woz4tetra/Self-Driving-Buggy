'''
    Written by Ben Warwick
    
    Self-Driving Buggy Rev. 7 for Self-Driving Buggy Project
    Version 11/20/2015
    =========
    
    This program controls the self-driving buggy. It manages computer vision,
    microcontroller control and data collection, PID feedback, encoder to x, y
    algorithms, path finding, GPS algorithms, and IMU algorithms. Each of these is
    implemented in its own file.
    
    Usage
    -----
    python __main__.py
    - or - (in folder directory):
    python Self-Driving\ Buggy\ Rev.\ 7
    
'''

import pygame
from controllers.joystick import *

from board.serial_comm import *

from data.recorder import Recorder

from controllers.binder import Binder
from controllers.pid import PID

from map import map_maker
import time
import math

def joystick_angle(position):
    if math.sqrt(position[0] ** 2 + position[1] ** 2) > 0.6:
#        angle = -math.degrees(math.atan2(position[1], position[0])) * 125 / 180
    
#        return int(angle) + 125
        return -int(math.degrees(math.atan2(position[1], position[0])) * 125 / 180)
    else:
        return -1

def run():
    pygame.display.init()
    pygame.joystick.init()
    joystick = BuggyJoystick()
    
    course = map_maker.get_map("Sun Nov  1 19;53;06 2015.csv")
    binder = Binder(course)
    pid = PID()
    
    recorder = Recorder()
    
    angle = 90
    send_command(6, angle)
    
    enc_distance = 0
    imu_data = [0, 0, 0]
    gps_data = [0.0, 0.0, 0.0, 0.0, 0, 0]
    
#    coordinates = [0, 0]
    data = []
    try:
        while joystick.done is False:
            joystick.update()
            for sensor_id in xrange(4, 6):
                if sensor_id <= 3:
                    imu_data[sensor_id - 1] = get_sensor(sensor_id, "#### #### ####", "int")
                elif sensor_id == 4:
                    enc_distance = get_sensor(sensor_id, "########", "uint")
                else:
                    gps_data = get_sensor(sensor_id, "######## ######## ######## ######## ## ##", 'ffffuu')
            if enc_distance == None:
                enc_distance = "-"
            if imu_data == None:
                imu_data = ["-", "-", "-"]
            if gps_data == None:
                gps_data = ["-", "-", "-", "-", "-", "-"]
            
            data.append([enc_distance] + imu_data + gps_data)
            
            if len(data) > 50:
                while len(data) > 0:
                    recorder.add_data(data.pop(0))
            angle = joystick_angle(joystick.mainStick)
            print angle
            if 0 <= angle <= 125:
                send_command(6, angle)
        
#        binder = Binder(course)
#        index_of_next = binder.bind(gps.coordinates)
#        
#        pid = PID()
#        lng, lat = coordinates
#        current_pos = (lng, lat, angle)
#        next_pos = course[index_of_next]
#        new_servo_angle = pid.update(current_pos,next_pos)
#        
#        angle = new_servo_angle
    except:
        pass
    finally:
        if len(data) > 0:
            for row in data:
                recorder.add_data(row)
        recorder.close()

if __name__ == '__main__':
    print __doc__
    run()
