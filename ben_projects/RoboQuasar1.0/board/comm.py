"""
    Written by Ben Warwick

    comm.py, written for RoboQuasar1.0
    Version 11/28/2015
    =========

    Handles direct serial communications with the arduino.

    This class is a subclass of threading.Thread. It constantly updates the
    SensorData (constructor parameter) object with new data received from
    serial. It will also send any commands put on the CommandQueue (also a
    constructor parameter).
    
    This library follows a home-baked serial packet protocol. data.py handles
    all data conversion. Please refer to objects.py for proper usage tips and
    data.py for details of the sensor and command packet protocol.
"""

from __future__ import print_function
import serial
import time
import os
import sys
import glob
import threading
import random

exit_flag = False
use_simulated = False


class Communicator(threading.Thread):
    def __init__(self, baud_rate, command_queue, sensors_pool):
        if use_simulated:
            self.serialRef = SimulatedSerial()
            self.serialRef.start()
        else:
            self.serialRef = self._findPort(baud_rate)
            self._handshake()

        self.sensor_pool = sensors_pool
        self.command_queue = command_queue

        super(Communicator, self).__init__()

    def run(self):
        while exit_flag == False:
            packet = ""
            incoming = self.serialRef.read()
            while incoming != '\n':
                if incoming != None:
                    packet += incoming
                incoming = self.serialRef.read()

            for index in xrange(len(packet)):
                sensor_id, data = packet.split('\t')
                self.sensor_pool.update(int(sensor_id, 16), data, packet)

            if not self.command_queue.is_empty():
                command = self.command_queue.get()
                self.serialRef.write(command)

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
                "No boards could be found! Did you plug it in? Try "
                "entering the address manually.")
        else:
            return serial_ref

    @staticmethod
    def _possibleAddresses():
        """
        An internal method used by _initSerial to search all possible
        USB serial addresses.
        
        :return: A list of strings containing all likely addresses
        """
        if sys.platform.startswith('darwin'):  # OS X
            devices = os.listdir("/dev/")
            arduino_devices = []
            for device in devices:
                if device.find("cu.usbmodem") > -1 or \
                                device.find("tty.usbmodem") > -1:
                    arduino_devices.append("/dev/" + device)
            return arduino_devices

        elif (sys.platform.startswith('linux') or
                  sys.platform.startswith('cygwin')):  # linux

            return glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('win'):  # Windows
            return ['COM' + str(i + 1) for i in range(256)]

        else:
            raise EnvironmentError('Unsupported platform')


class SimulatedSerial(threading.Thread):
    def __init__(self):

        self.input_queue = []
        self.output_queue = []

        self.outgoing = ""

        super(SimulatedSerial, self).__init__()

    def write(self, string):
        self.input_queue.append(string)

    def read(self):
        if len(self.outgoing) == 0:
            if len(self.output_queue) > 0:
                self.outgoing = self.output_queue.pop(0)
            else:
                return None

        character = self.outgoing[0]
        self.outgoing = self.outgoing[1:]
        return character

    def flushInput(self):
        self.input_queue = []

    def flushOutput(self):
        self.output_queue = []

    def generate_hex(self, number):
        hex_data = ""
        for counter in xrange(number):
            hex_data += hex(random.randint(0, 15))[2:]

        return hex_data

    def run(self):
        sensor_index = 0

        self.encoder = 1

        while exit_flag == False:
            if len(self.input_queue) > 0:
                packet = self.input_queue.pop(0)
                command_id, data_len, data = packet[:-1].split("\t")
                assert int(data_len, 16) == len(data)

                command_id = int(command_id, 16)
                if command_id == 0:
                    print("servo:", data)
                elif command_id == 1:
                    print("led13:", data)

            sensor_packet = "0" + hex(sensor_index)[
                                  2:] + "\t"  # if this exceeds 15, what am I doing with my life
            if sensor_index == 0:
                sensor_packet += self.generate_hex(2 * 18)
            elif sensor_index == 1:
                sensor_packet += self.generate_hex(8 * 4 + 2 * 2)
            elif sensor_index == 2:
                hex_encoder = hex(self.encoder)[2:]
                sensor_packet += "0" * (16 - len(hex_encoder)) + hex_encoder

            self.encoder += 1  # overflow problems? but it's a simulator so who cares

            self.output_queue.append(sensor_packet + "\n")
            sensor_index = random.randint(0, 2)  # (sensor_index + 1) % 3

            # sleep = random.random()
            # time.sleep(sleep + 1)
            # print("sleep:", sleep)
