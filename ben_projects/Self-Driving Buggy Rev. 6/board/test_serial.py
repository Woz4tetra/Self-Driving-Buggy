import serial_comm
import serial_parser
import time

from constants import *

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

def make_custom_packet(packet_type, node, command_id, payload, quality=None):
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

    T = format_element(packet_type)
    N = format_element(node)
    I = format_element(command_id)
    P = format_element(payload, length)
    if quality == None:
        Q = format_element((packet_type ^ node ^ command_id ^ payload) & 0xff)
    else:
        Q = format_element(quality)

    packet = "T{}N{}I{}P{}Q{}\r\n".format(T, N, I, P, Q)

    return packet

'''
if __debug__:
   if not expression: raise AssertionError

- or -

assert

__debug__ is true if -O is not passed
'''

if __name__ == '__main__':
    import traceback

    board_type = 'arduino'

    communicator = serial_comm.Communicator(board_type=board_type, upload=False)
    parser = serial_parser.Parser()

    try:
        communicator.start()

        if board_type == 'pyboard':
            # ---- Command and reply LED 1 ----
            packet = communicator.makePacket(PACKET_TYPES['command'],
                                             PYBOARD_COMMAND_IDS['built-in led 1'], ON)
            communicator.put(packet)
            time.sleep(0.001)
            assert parser.parse(communicator.get()) == \
                   make_custom_packet(PACKET_TYPES['command reply'], NODE_BOARD,
                                      PYBOARD_COMMAND_IDS['built-in led 1'], ON)

            # ---- Command and reply servo 1 ----
            servo_angle = 80.0
            packet = communicator.makePacket(PACKET_TYPES['command'],
                                             PYBOARD_COMMAND_IDS['servo 1'],
                                             int(servo_angle * 255 / 180))
            # servos command degrees
            communicator.put(packet)
            time.sleep(1)
            assert parser.parse(communicator.get()) == \
                   make_custom_packet(PACKET_TYPES['command reply'], NODE_BOARD,
                                      PYBOARD_COMMAND_IDS['Servo 1'],
                                      int(servo_angle * 255 / 180))

            # ---- Request data from switch ----
            packet = communicator.makePacket(PACKET_TYPES['request data'],
                                             PYBOARD_COMMAND_IDS['built-in switch'])
            expected = make_custom_packet(
                PACKET_TYPES['send 8-bit data'], NODE_BOARD,
                PYBOARD_COMMAND_IDS['Built-in Switch'], ON)
            received = ""
            communicator.put(packet)
            time0 = time.time()
            while (time.time() - time0 < 2) or received != expected:  # seconds
                time.sleep(0.001)
                received = parser.parse(communicator.get())

            assert received == expected

            # ---- Request data from accelerometer ----
            packet = communicator.makePacket(PACKET_TYPES['request data array'],
                                             PYBOARD_COMMAND_IDS['built-in accelerometer'])
            communicator.put(packet)
            received = parser.parse(communicator.get())
            assert received != None
            node, command_id, payload = received
            assert node == NODE_BOARD
            assert command_id == PYBOARD_COMMAND_IDS['built-in accelerometer']
            assert 0 <= payload <= 0xffffffffffff


        elif board_type == 'arduino':
            # ---- Command and reply fake LED ----
            packet = communicator.makePacket(PACKET_TYPES['command'],
                                             ARDUINO_COMMAND_IDS[
                                                 'fake led'], OFF)
            print "packet:", repr(packet)
            communicator.put(packet)

            in_packet = communicator.get()
            print "in_packet:", repr(in_packet)
            assert in_packet == \
                   make_custom_packet(PACKET_TYPES['command reply'], NODE_BOARD,
                                      ARDUINO_COMMAND_IDS['fake led'], OFF)

            # ---- Request data from fake sensor 8 bit ----
            packet = communicator.makePacket(PACKET_TYPES['request data'],
                                             ARDUINO_COMMAND_IDS[
                                                 'fake sensor 8 bit'])
            print "packet:", repr(packet)
            communicator.put(packet)
            for counter in xrange(256):
                in_packet = parser.parse(communicator.get())
                node, command_id, payload = in_packet
                print(in_packet)
                print payload, counter
                assert node == NODE_BOARD
                assert ARDUINO_COMMAND_IDS['fake sensor 8 bit']
                assert payload == counter

    except Exception, err:
        communicator.serialRef.write(make_custom_packet(0xff, 0, 0, 0))
        print(traceback.format_exc())
