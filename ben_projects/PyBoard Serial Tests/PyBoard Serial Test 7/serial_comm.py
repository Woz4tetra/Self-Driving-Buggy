import threading
from Queue import Queue
from constants import PACKET_TYPES
import pyboard
import serial
import time


class PyBoardThread(threading.Thread):
    def __init__(self, address):
        self.address = address

        self.daemon = True
        super(PyBoardThread, self).__init__()

    def run(self):
        pyboard.execfile("board/main.py", device="/dev/tty.usbmodem1452")

class Communicator(threading.Thread):
    def __init__(self, address):
        self.address = address

        self.sendQueue = Queue()
        self.receiveQueue = Queue()

        self.delay = 0.001
        self.daemon = True

        self.serialRef = serial.Serial(port=address)
        time.sleep(0.25)

        super(Communicator, self).__init__()

    def run(self):
        while True:
            self.sendPacket()
            self.getPacket()

    def getPacket(self):
        packet = self.serialRef.readline()
        if len(packet) > 0:
            print self.receiveQueue.qsize(),
            print(repr(packet)),
            self.receiveQueue.put(packet)
            print self.receiveQueue.qsize()
        time.sleep(self.delay)

    def sendPacket(self):
        if not self.sendQueue.empty():
            print self.sendQueue.qsize(),
            self.serialRef.write(self.sendQueue.get())
            print self.sendQueue.qsize()
            time.sleep(self.delay)

    def put(self, packet):
        self.sendQueue.put(packet)

    def get(self):
        return self.receiveQueue.get()

    def makePacket(self, packet_type, command_id, payload=0):
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

            T = self.format_element(packet_type)
            N = self.format_element(0)
            I = self.format_element(command_id)
            P = self.format_element(payload, length)
            Q = self.format_element((packet_type ^ 0x00 ^ command_id ^ payload) & 0xff)

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