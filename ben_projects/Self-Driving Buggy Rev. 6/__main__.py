'''
Written by Ben Warwick

Self-Driving Buggy Rev. 6 for Self-Driving Buggy PRoject
Version 9/15/2015
=========

(temp description)
This program controls the self-driving buggy. It manages computer vision,
microcontroller control and data collection, PID feedback, encoder to x, y
algorithms, path finding, GPS algorithms, and IMU algorithms. Each of these is
implemented in its own file.

Usage
-----
python __main__.py

- or - (in folder directory):
python Self-Driving\ Buggy\ Rev.\ 6

Keys
----
    q, ESC - exit
    SPACE - play/pause video
    o - toggle show original video feed
    left - read previous frame
    right - read next frame
    s - save frame as image (in camera/Images/ directory)
    v - start/stop create video (saved in camera/Videos/ directory)
    h - toggle enable draw (hide/show video feed)
'''

from board import serial_comm
from board import serial_parser
from board.common import *

from sensors import gps

import math


def run():
    parser = serial_parser.Parser()
    communicator = serial_comm.Communicator()

    track = gps.parse(gps.output)
    binding_accuracy = 0.0000002

    accel_x, accel_y, accel_z, gyro_yaw, gyro_pitch, gyro_roll = [0] * 6
    longitude, latitude, gps_speed, gps_angle, satellites, fix_quality = [0] * 6
    encoder_counts1 = 0
    encoder_counts0 = 0

    encoder_position = [0, 0]
    gps_position = [0, 0]

    while True:
        # ----- get imu -----
        packet = communicator.makePacket(PACKET_TYPES['request data'],
                                         ARDUINO_COMMAND_IDS['accel gyro'])
        communicator.write(packet)
        received = communicator.read()
        if parser.verify(packet, received):
            accel_x, accel_y, accel_z, gyro_yaw, gyro_pitch, gyro_roll = \
                parser.parse(received,
                             markers=PARSE_MARKERS['accel gyro'],
                             out=PARSE_OUT_FORMATS['accel gyro'])

        # ----- get encoder -----

        packet = communicator.makePacket(PACKET_TYPES['request data'],
                                         ARDUINO_COMMAND_IDS['encoder'])
        communicator.write(packet)
        received = communicator.read()

        if parser.verify(packet, received):
            encoder_counts1 = parser.parse(packet,
                                           out=PARSE_OUT_FORMATS['encoder'])

        # ----- get gps -----

        packet = communicator.makePacket(PACKET_TYPES['request data'],
                                         ARDUINO_COMMAND_IDS['gps'])
        communicator.write(packet)
        received = communicator.read()

        if parser.verify(packet, received):
            longitude, latitude, gps_speed, \
                gps_angle, satellites, fix_quality = \
                parser.parse(packet,
                             markers=PARSE_MARKERS['gps'],
                             out=PARSE_OUT_FORMATS['gps'])

        encoder_position[0] += math.cos(gyro_yaw) * (
            encoder_counts1 - encoder_counts0)
        encoder_position[1] += math.sin(gyro_yaw) * (
            encoder_counts1 - encoder_counts0)
        encoder_counts0 = encoder_counts1

        (new_pos, num_bind) = gps.bind(track, (longitude, latitude),
                                       binding_accuracy)
        gps_position[0] = new_pos[0] - longitude
        gps_position[1] = new_pos[1] - latitude



if __name__ == '__main__':
    print __doc__

    run()
