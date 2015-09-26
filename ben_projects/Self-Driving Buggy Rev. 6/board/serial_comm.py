import threading
from constants import PACKET_TYPES
# from constants import PYBOARD_COMMAND_IDS
import pyboard
import serial
import time
from sys import platform as _platform
import os
import inspect


class PyBoardThread(threading.Thread):
    def __init__(self, address, directory="pyboard/main.py"):
        self.address = address
        self.directory = directory

        super(PyBoardThread, self).__init__()
        self.daemon = True

    def run(self):
        pyboard.execfile(self.directory, device=self.address)


class Communicator(threading.Thread):
    def __init__(self, address=None, delay=0.001, board_type='pyboard',
                 upload=True):
        if address == None:
            self.serialRef = self.findPort()
        else:
            self.serialRef = serial.Serial(port=address, baudrate=115200)
        time.sleep(1)  # ensure connection settles

        self.currentPacket = ""
        self.receivedPacket = ""

        self.delay = delay

        super(Communicator, self).__init__()

        self.daemon = True

        if board_type == 'pyboard':
            self.pyb_thread = PyBoardThread(self.serialRef)
            self.pyb_thread.start()
        elif board_type == 'arduino':
            if upload:
                os.system('cd arduino && platformio run --target upload')
            self._handshake()

    def findPort(self, baudrate=115200):
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

    def _handshake(self):
        readFlag = self.serialRef.read()

        print("Waiting for ready flag...")
        time.sleep(1)
        while readFlag != 'R':
            print repr(readFlag)
            readFlag = self.serialRef.read()

        self.serialRef.write("P")
        self.serialRef.flushInput()
        self.serialRef.flushOutput()
        time.sleep(0.1)
        print("Arduino initialized!")

    def run(self):
        while True:
            self.sendPacket()
            # self.getPacket()
            time.sleep(self.delay)

    def getPacket(self):
        print "in waiting:", self.serialRef.inWaiting()
        if self.serialRef.inWaiting() > 0:
            # char = self.serialRef.read()
            # packet = ""
            # while char != '\n':
            #     packet += char
            #     char = self.serialRef.read()
            #     print char,
            print time.time(), "getting packet"
            packet = self.serialRef.readline()
            print time.time(), "got: ", repr(packet)
            if len(packet) > 0:
                # print self.receiveQueue.qsize(),
                print(repr(packet))
                self.receivedPacket = packet
                # print self.receiveQueue.qsize()
            time.sleep(self.delay)

    def sendPacket(self):
        if len(self.currentPacket) > 0:
            print time.time(), "writing: ", repr(self.currentPacket)
            self.serialRef.write(self.currentPacket)
            print time.time(), "wrote: ", repr(self.currentPacket)

    def put(self, packet):
        print time.time(), "putting: ", repr(packet)
        self.currentPacket = packet
        print time.time(), "put: ", repr(packet)

    def get(self):
        self.getPacket()
        return self.receivedPacket

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


