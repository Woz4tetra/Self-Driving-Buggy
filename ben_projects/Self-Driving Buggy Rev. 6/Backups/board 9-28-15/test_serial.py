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

    parser = serial_parser.Parser()

    try:
            # ---- Request data from fake sensor 8 bit ----
            current = 0
            while True:
                serial_comm.current_packet = current

                serial_comm.send()

                time.sleep(0.5)

                serial_comm.send('x')

                time.sleep(0.5)
                print repr(serial_comm.read())
                current = (current + 1) % 3



    except Exception, err:
        # communicator.serialRef.write(make_custom_packet(0xff, 0, 0, 0))
        # while not communicator.receivedQueue.empty():
        #     print communicator.receivedQueue.get()
        print(traceback.format_exc())
