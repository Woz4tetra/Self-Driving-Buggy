# handles direct serial communications
from __future__ import print_function

import serial
import time
import os
from sys import platform as _platform
import threading

exit_flag = True

class Communicator(threading.Thread):
    def __init__(self, baud_rate, command_queue, sensors_pool):
        self.serialRef = self._findPort(baud_rate)
        self._handshake()

        self.sensor_pool = sensors_pool
        self.command_queue = command_queue

        super(Communicator, self).__init__()

    def run(self):
        while exit_flag == False:
            packet = self.serialRef.readline()

            for index in xrange(len(packet)):
                sensor_id, data = packet.split('\t')
                self.sensor_pool.update(int(sensor_id, 16), data)

            if not self.command_queue.is_empty():
                self.serialRef.write(self.command_queue.get())

    def _handshake(self):
        read_flag = self.serialRef.read()

        print("Waiting for ready flag...")
        time.sleep(0.5)
        while read_flag != 'R':
            print(read_flag, end="")
            read_flag = self.serialRef.read()

        self.serialRef.write("\n")
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
            devices = []
            for counter in xrange(32):
                devices.append("COM" + str(counter))
            return devices
        else:
            raise NotImplementedError
