from board import serial_comm
from board import serial_parser
from board.common import *
import time

'''
if __debug__:
   if not expression: raise AssertionError

- or -

assert

__debug__ is true if -O is not passed
'''

import random



def test_imu():
    print("test imu...")
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     0x01)
    communicator.write(packet)

    for _ in xrange(20):
        received = communicator.read()

        if len(received) > 0:
            print parser.parse(received,
                               markers="#### #### #### #### #### ####",
                               out='dec')
    print("Passed!")


def test_encoder():
    print("test encoder...")
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     0x00)
    communicator.write(packet)
    for _ in xrange(100):
        received = communicator.read()
        if len(received) > 0:
            if parser.verify(packet, received):
                print(parser.parse(received, out='dec'))


def test_gps():
    print("test gps...")
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     0x02)
    communicator.write(packet)

    received = communicator.read()
    if len(received) > 0:
        if parser.verify(packet, received):
            print parser.parse(received,
                               verbose=True,
                               markers="######## ######## ######## ######## ## ##",
                               out='ffffdd')


def test_led13():
    print("test led 13...")
    # led_state = True
    for _ in xrange(30):
        packet = communicator.makePacket(PACKET_TYPES['command'],
                                         0x04,
                                         random.randint(0, 1))
                                         # int(led_state))
        communicator.write(packet)
        recv_packet = communicator.read()
        if parser.verify(packet, recv_packet):
            print(parser.parse(packet, out='bool'))

        # led_state = not led_state
        time.sleep(0.01)

def test_servo():
    print("test servo...")
    servo_value = 0
    forward = True
    
    for _ in xrange(36):
        packet = communicator.makePacket(PACKET_TYPES['command'],
                                         0x03,
                                         servo_value)
        communicator.write(packet)
        recv_packet = communicator.read()
        if parser.verify(packet, recv_packet):
            print(parser.parse(packet))
        
        if forward == True:
            servo_value += 10
        else:
            servo_value -= 10
        
        if servo_value > 180:
            forward = False
        elif servo_value < 0:
            forward = True
        time.sleep(0.01)
        


if __name__ == '__main__':
    parser = serial_parser.Parser()
    communicator = serial_comm.Communicator()
    communicator.start()
    while True:
        # test_switching()
        # test_pinging()
        # test_verify()
        # test_servo()
        # test_encoder()
        # test_imu()
        test_led13()
        # for _ in xrange(100):
        #     test_gps()

        # print("All tests passed!!!")
        # print "lets go again!!!"
        # time.sleep(1)
