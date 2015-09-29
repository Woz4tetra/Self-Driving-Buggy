import serial
from sys import platform as _platform
import os
import time
from constants import *


def _handshake(serialRef):
    readFlag = serialRef.read()

    print("Waiting for ready flag...")
    time.sleep(0.5)
    while readFlag != 'R':
        print repr(readFlag)
        readFlag = serialRef.read()

    serialRef.write("P")
    serialRef.flushInput()
    serialRef.flushOutput()
    print("Arduino initialized!")


def findPort(baudrate=115200):
    address = None
    serial_ref = None
    for possible_address in _possibleAddresses():
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
        # return []# return []


serialRef = findPort()
_handshake(serialRef)
current_packet = ""

def send(packet=''):
    if packet == '':
        global current_packet
        if current_packet == 2:
            current_packet = "T06N01I03P00Q04\r\n"
        elif current_packet == 1:
            current_packet = "T06N01I02P00Q05\r\n"
        elif current_packet == 0:
            current_packet = "T01N01I01P01Q00\r\n"

        print "writing current_packet:", repr(current_packet)
        print "in waiting send:", repr(serialRef.inWaiting())
        if serialRef.inWaiting() > 20:
            serialRef.flushInput()
            serialRef.flushOutput()

        serialRef.write(current_packet)
        current_packet = current_packet

        # while serialRef.inWaiting() > 0:
        #     serialRef.read()
    else:
        print "writing packet:", repr(packet)
        print "in waiting send:", repr(serialRef.inWaiting())
        serialRef.write(packet)

    print "in waiting send:", repr(serialRef.inWaiting())

def read():
    # char = ''
    buffer = ''
    print "in waiting read:", repr(serialRef.inWaiting())
    if serialRef.inWaiting():
        # while char != '\n':
        #     char = serialRef.read()
        #     buffer += char
        buffer = serialRef.readline()
    time.sleep(0.001)

    print repr(buffer)
    return buffer

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

    T = format_element(packet_type)
    N = format_element(node)
    I = format_element(command_id)
    P = format_element(payload, length)
    Q = format_element(
        (packet_type ^ node ^ command_id ^ payload) & 0xff)

    packet = "T{}N{}I{}P{}Q{}\r\n".format(T, N, I, P, Q)

    return packet

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


