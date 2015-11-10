"""
Written by Ben Warwick

Self-Driving Buggy Rev. 6 (serial_comm.py) for Self-Driving Buggy Project
Version 10/30/2015
=========

This module handles all communications with a serial device (currently only
arduino and pyboard). All communications are done through packets and pings.
Packets follow the format detailed in Serial Packet Convention 9-23-15.numbers
Send a packet following the guidelines and then ping for data. This opposed to
writing a packet every time data is required.

This module should be used in tandem with serial_parser.py and common.py

Dependencies
------------
PySerial - https://github.com/pyserial/pyserial
"""

from __future__ import print_function

import serial
from sys import platform as _platform
import os
import time
from common import *
from common import _makeParity


class Communicator:
    def __init__(self):
        self.currentPacket = ""

    def start(self, baud_rate, delay):
        self.delay = delay  # ms between each ping to serial
        
        self.serialRef = self._findPort(baud_rate)
        self._handshake()

    def _handshake(self):
        readFlag = self.serialRef.read()

        print("Waiting for ready flag...")
        time.sleep(0.5)
        while readFlag != 'R':
            print(readFlag, end="")
            readFlag = self.serialRef.read()

        self.serialRef.write("P")
        self.serialRef.flushInput()
        self.serialRef.flushOutput()
        print("Arduino initialized!")

    def _findPort(self, baud_rate):
        address = None
        serial_ref = None
        for possible_address in self._possibleAddresses():
            try:
                serial_ref = serial.Serial(port=possible_address,
                                           baudrate=baud_rate)
                address = possible_address
            except:
                pass
        if address is None:
            raise Exception(
                "No boards could be found! Did you plug it in? Try \
    entering the address manually.")
        else:
            return serial_ref

    @staticmethod
    def _possibleAddresses():
        '''
        An internal method used by _initSerial to search all possible
        USB serial addresses.
        Windows and Linux has not been implemented.

        :return: A list of strings containing all likely addresses
        '''
        if _platform == "darwin":  # OS X
            devices = os.listdir("/dev/")
            arduino_devices = []
            for device in devices:
                if device.find("cu.usbmodem") > -1 or \
                                device.find("tty.usbmodem") > -1:
                    arduino_devices.append("/dev/" + device)
            return arduino_devices
        elif _platform == "linux" or _platform == "linux2":  # linux
            raise NotImplementedError
            # return []
        elif _platform == "win32":  # Windows
            raise NotImplementedError
            # return []
        else:
            raise NotImplementedError

    def ping(self):
        # print "ping!"
        # print "in waiting send:", repr(self.serialRef.inWaiting())

        self.serialRef.write('x')

    def write(self, packet):
        self.currentPacket = packet
        self.serialRef.flushInput()
        self.serialRef.flushOutput()

        # print("writing current_packet:", repr(self.currentPacket))
        # print("in waiting send:", repr(self.serialRef.inWaiting()))

        self.serialRef.write(self.currentPacket)

        # print "in waiting send:", repr(self.serialRef.inWaiting())
        # time.sleep(self.delay)

    def read(self):
        time_start = time.time()
        buffer = ''
        while (time.time() - time_start) <= 3 and not bool(buffer):
            self.ping()

            # print("in waiting read:", repr(self.serialRef.inWaiting()))
            if self.serialRef.inWaiting():
                buffer = self.serialRef.readline()
            time.sleep(self.delay)
#            print(repr(buffer))
        if not bool(buffer):
            raise Exception("Attempted read failed!! Tried too many times.")
        return buffer

    @staticmethod
    def makeCustomPacket(packet_type, node, command_id, payload, quality=None):
        if (packet_type == PACKET_TYPES['command'] or
                    packet_type == PACKET_TYPES['command reply'] or
                    packet_type == PACKET_TYPES['send 8-bit data'] or
                    packet_type == PACKET_TYPES['request data'] or
                    packet_type == PACKET_TYPES['request data array'] or
                    packet_type == PACKET_TYPES['exit']):
            length = 2  # 4 * 2 = 8 bits
        elif packet_type == PACKET_TYPES['send 16-bit data']:
            length = 4  # 4 * 4 = 16 bits
        elif packet_type == PACKET_TYPES['send data array']:
            length = None  # determined by command id
        else:
            length = 0

        T = Communicator.format_element(packet_type)
        N = Communicator.format_element(node)
        I = Communicator.format_element(command_id)
        P = Communicator.format_element(payload, length)
        if quality == None:
            Q = Communicator.format_element(
                (_makeParity(packet_type, node, command_id, payload)))
        else:
            Q = Communicator.format_element(quality)

        packet = "T{}N{}I{}P{}Q{}\r\n".format(T, N, I, P, Q)

        return packet

    @staticmethod
    def makePacket(packet_type, command_id, payload=0):
        if (packet_type == PACKET_TYPES['command'] or
                    packet_type == PACKET_TYPES['command reply'] or
                    packet_type == PACKET_TYPES['send 8-bit data'] or
                    packet_type == PACKET_TYPES['request data'] or
                    packet_type == PACKET_TYPES['exit']):
            length = 2  # 4 * 2 = 8 bits
        elif packet_type == PACKET_TYPES['send 16-bit data']:
            length = 4
        elif packet_type == PACKET_TYPES['send data array']:
            length = None
        else:
            length = 0
        node = 1

        T = Communicator.format_element(packet_type)
        N = Communicator.format_element(node)
        I = Communicator.format_element(command_id)
        P = Communicator.format_element(payload, length)
        Q = Communicator.format_element(
            (_makeParity(packet_type, node, command_id, payload)))

        packet = "T{}N{}I{}P{}Q{}\r\n".format(T, N, I, P, Q)

        return packet

    @staticmethod
    def format_element(packet_element, digits=2):
        assert type(packet_element) == int
        if digits < 2 and digits != None:
            digits = 2
        if (packet_element < 16):
            return "0" + hex(packet_element)[-1:]
        elif digits == None:
            return hex(packet_element)[2:]
        else:
            return hex(packet_element)[-digits:]
