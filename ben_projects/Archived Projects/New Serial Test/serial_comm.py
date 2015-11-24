"""
Send data packet: [sensor_id]\r\n
Receive data packet: [node]\t[sensor_id]\t[data]\t[parity]\r\n

Send command packet: [command_id]\t[data]\t[parity]\r\n
Receive command packet: [node]\t[command_id]\t[parity]\r\n
"""

from __future__ import print_function
from sys import platform as _platform
import os
import threading
from Queue import Queue
import serial
import time

#
import random
import string

class SimulatedSerial():
    def __init__(self, delay):
        self.delay = delay

    def write(self, data):
        print("to serial:", repr(data))

        if self.delay > 0:
            time.sleep(self.delay)

    def readline(self, timeout=3):
        # Make sure the object_id ordering matches the order you initialize
        # the sensors.

        node = "2"
        object_id = random.randint(0, 2)
        data = ""
        if object_id == 0 or object_id == 1 or object_id == 2:
            while len(data) < 36:
                data += string.hexdigits[random.randint(0, 15)]
        elif object_id == 3:
            while len(data) < 12:
                data += string.hexdigits[random.randint(0, 15)]
        elif object_id == 4:
            while len(data) < 4:
                data += string.hexdigits[random.randint(0, 15)]
        assert data != ""

        object_id = hex(object_id)[2:]

        data = "\t".join([node,
                          object_id,
                          data,
                          self.makeParity(node, object_id, data)])
        if self.delay > 0:
            time.sleep(self.delay)

        return data

    def makeParity(self, node, object_id, data):
        parity = int(node, 16) ^ int(object_id, 16)

        for index in xrange(len(data) - 1, -1, 2):
            parity ^= int(data[index: index - 2], 16)

        return hex(parity)[2:]


class SerialRef():
    def __init__(self, baud_rate, delay):
        self.address = None
        self.serialRef = self._findPort(baud_rate)

        self._handshake()

        self.delay = delay

    def _findPort(self, baud_rate):

        serial_ref = None
        for possible_address in self._possibleAddresses():
            try:
                serial_ref = serial.Serial(port=possible_address,
                                           baudrate=baud_rate)
                self.address = possible_address
            except:
                pass
        if self.address is None:
            raise Exception(
                "No boards could be found! Did you plug it in? Try \
entering the address manually.")
        else:
            return serial_ref

    def _handshake(self):
        read_flag = self.serialRef.read()

        print("Waiting for ready flag...")
        time.sleep(0.5)
        while read_flag != 'R':
            print(read_flag, end="")
            read_flag = self.serialRef.read()

        self.serialRef.write("P")
        self.serialRef.flushInput()
        self.serialRef.flushOutput()
        print("Arduino initialized on port '%s'!" % self.address)

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

    def write(self, data):
        print("writing:", repr(data))
        self.serialRef.write(data)

        if self.delay > 0:
            time.sleep(self.delay)

    def readline(self, timeout=3):
        # time_start = time.time()
        # data = ""
        # while time.time() - time_start < timeout and ('\n' not in data):
        #     data += self.serialRef.read()
        data = self.serialRef.readline()

        if self.delay > 0:
            time.sleep(self.delay)

        return data


class CommandThread(threading.Thread):
    def __init__(self, serial_ref):
        threading.Thread.__init__(self)

        self.writeQueue = Queue()

        self.sentPacket = ""
        self.serialRef = serial_ref

        self.exit_flag = False

    def stop(self):
        self.exit_flag = True

    def run(self):
        while self.exit_flag == False:
            if not self.writeQueue.empty():
                command = self.writeQueue.get()
                self.serialRef.write(str(command))

    def put(self, command, value):
        command.set(value)
        self.writeQueue.put(command)


class DataThread(threading.Thread):
    def __init__(self, serial_ref, sensors):
        threading.Thread.__init__(self)

        self.readQueue = Queue()

        self.receivedPacket = ""
        self.serialRef = serial_ref

        self.exit_flag = False

        self.sensors = sensors
        self.index = 0

    def stop(self):
        self.exit_flag = True

    def run(self):
        while True:
            self.serialRef.write(self.sensors[self.index].sensor_id)

            packet = self.serialRef.readline()
            print(repr(packet))

            for index in xrange(len(self.sensors)):
                data = self.sensors[index].parse(packet)
                if data != None:
                    self.sensors[index].update(data)
                    break

            self.index = (self.index + 1) % len(self.sensors)
