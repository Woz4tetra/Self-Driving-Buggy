"""
Written by Ben Warwick

Self-Driving Buggy Rev. 6 (serial_parser.py) for Self-Driving Buggy Project
Version 9/29/2015
=========

The modules contained here deal with all interaction with a connected serial
device (for now, only arduino and pyboard). serial_comm.py deals with the
transfer of data over serial. serial_parser.py handles all data interpretation
and verification. common.py contains information that both modules require.

Usage
-----
from board import serial_comm
from board import serial_parser

communicator = serial_comm.Communicator()
parser = serial_parser.Parser()

led_state = True
packet = communicator.makePacket(PACKET_TYPES['command'],
                                ARDUINO_COMMAND_IDS['led 13'],
                                int(led_state))
communicator.write(packet)

received_packet = communicator.read()  # pings automatically when called

assert parser.verify(packet, received_packet)
"""