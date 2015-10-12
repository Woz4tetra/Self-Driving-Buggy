"""
Written by Ben Warwick

Self-Driving Buggy Rev. 6 (serial_comm.py) for Self-Driving Buggy Project
Version 10/12/2015
=========

This module acts as a wrapper for serial_parser.py and serial_comm.py.
Usage
-----

"""

from board import serial_comm
from board import serial_parser
from board.common import *

parser = serial_parser.Parser()
communicator = serial_comm.Communicator()

def get_imu():
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['accel gyro'])
    communicator.write(packet)
    received = communicator.read()
    if parser.verify(packet, received):
        return parser.parse(received,
                            markers=PARSE_MARKERS['accel gyro'],
                            out=PARSE_OUT_FORMATS['accel gyro'])
    else:
        return [None] * 6


def get_encoder():
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['encoder'])
    communicator.write(packet)
    received = communicator.read()

    if parser.verify(packet, received):
        return parser.parse(packet, out=PARSE_OUT_FORMATS['encoder'])
    else:
        return None


def get_gps():
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['gps'])
    communicator.write(packet)
    received = communicator.read()

    if parser.verify(packet, received):
        return parser.parse(packet,
                            markers=PARSE_MARKERS['gps'],
                            out=PARSE_OUT_FORMATS['gps'])
    else:
        return [None] * 6


def set_servo(servo_value):
    packet = communicator.makePacket(PACKET_TYPES['command'],
                                     ARDUINO_COMMAND_IDS['servo'],
                                     servo_value)
    communicator.write(packet)
    received = communicator.read()

    return parser.verify(packet, received) and \
           parser.parse(packet, out=PARSE_OUT_FORMATS['servo'])
