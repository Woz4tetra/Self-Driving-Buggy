import serial
from sys import platform as _platform
import os
import time
from constants import *

class Communicator():
    def __init__(self, delay=0.006):  # corresponds to delay(3) on arduino
        self.serialRef = self._findPort()
        self._handshake()

        self.currentPacket = ""
        self.delay = delay

    def _handshake(self):
        readFlag = self.serialRef.read()

        print("Waiting for ready flag...")
        time.sleep(0.5)
        while readFlag != 'R':
            print repr(readFlag)
            readFlag = self.serialRef.read()

        self.serialRef.write("P")
        self.serialRef.flushInput()
        self.serialRef.flushOutput()
        print("Arduino initialized!")

    def _findPort(self, baudrate=115200):
        address = None
        serial_ref = None
        for possible_address in self._possibleAddresses():
            try:
                serial_ref = serial.Serial(port=possible_address,
                                           baudrate=baudrate)
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
        print "ping!"
        # print "in waiting send:", repr(self.serialRef.inWaiting())

        self.serialRef.write('x')
        time.sleep(self.delay)

    def write(self, packet):
        self.currentPacket = packet
        self.serialRef.flushInput()
        self.serialRef.flushOutput()

        print "writing current_packet:", repr(self.currentPacket)
        print "in waiting send:", repr(self.serialRef.inWaiting())

        self.serialRef.write(self.currentPacket)

        print "in waiting send:", repr(self.serialRef.inWaiting())
        time.sleep(self.delay)

    def read(self, recurses=0):
        if recurses > 10:
            raise Exception("Attemped read failed!! Tried too many times")
        self.ping()

        buffer = ''
        print "in waiting read:", repr(self.serialRef.inWaiting())
        if self.serialRef.inWaiting():
            buffer = self.serialRef.readline()
        print repr(buffer)
        if buffer == None or len(buffer) == 0:
            self.read(recurses + 1)
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
            length = 4
        elif packet_type == PACKET_TYPES['send data array']:
            length = None
        else:
            length = 0

        T = Communicator.format_element(packet_type)
        N = Communicator.format_element(node)
        I = Communicator.format_element(command_id)
        P = Communicator.format_element(payload, length)
        if quality == None:
            Q = Communicator.format_element((packet_type ^ node ^ command_id ^ payload) & 0xff)
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
                    packet_type == PACKET_TYPES['request data array'] or
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
            (packet_type ^ node ^ command_id ^ payload) & 0xff)

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
