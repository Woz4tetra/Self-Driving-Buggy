import serial_comm
import serial_parser
from common import *
import time

'''
if __debug__:
   if not expression: raise AssertionError

- or -

assert

__debug__ is true if -O is not passed
'''

import random

def test_switching():
    print("test switching...")
    motor_value = 0
    led_state = True

    communicator.write(communicator.makePacket(PACKET_TYPES['command'],
                                               ARDUINO_COMMAND_IDS['led 13'],
                                               int(led_state)))

    print parser.parse(communicator.read())

    communicator.write(communicator.makePacket(PACKET_TYPES['command'],
                                               ARDUINO_COMMAND_IDS['fake led'],
                                               int(led_state)))

    print parser.parse(communicator.read())

    communicator.write(communicator.makePacket(PACKET_TYPES['request data'],
                                               ARDUINO_COMMAND_IDS[
                                                   'fake sensor 8 bit']))

    print parser.parse(communicator.read())

    communicator.write(communicator.makePacket(PACKET_TYPES['request data'],
                                               ARDUINO_COMMAND_IDS[
                                                   'fake sensor 16 bit']))

    print parser.parse(communicator.read())

    communicator.write(
        communicator.makePacket(PACKET_TYPES['command'],
                                ARDUINO_COMMAND_IDS[
                                    'fake motor'],
                                motor_value))
    motor_value += 1

    print parser.parse(communicator.read())


def test_pinging():
    print("test pinging...")

    motor_value = 0
    led_state = True

    for _ in xrange(10):
        communicator.write(communicator.makePacket(PACKET_TYPES['command'],
                                                   ARDUINO_COMMAND_IDS[
                                                       'led 13'],
                                                   int(led_state)))
        print parser.parse(communicator.read())

        led_state = not led_state
        time.sleep(1)

    for _ in xrange(20):
        communicator.write(communicator.makePacket(PACKET_TYPES['command'],
                                                   ARDUINO_COMMAND_IDS[
                                                       'fake led'],
                                                   int(led_state)))
        print parser.parse(communicator.read())

        led_state = not led_state

    communicator.write(communicator.makePacket(PACKET_TYPES['request data'],
                                               ARDUINO_COMMAND_IDS[
                                                   'fake sensor 8 bit']))
    for _ in xrange(20):
        print parser.parse(communicator.read())

    communicator.write(communicator.makePacket(PACKET_TYPES['request data'],
                                               ARDUINO_COMMAND_IDS[
                                                   'fake sensor 16 bit']))

    for _ in xrange(20):
        print parser.parse(communicator.read())

    for _ in xrange(255):
        communicator.write(
            communicator.makePacket(PACKET_TYPES['command'],
                                    ARDUINO_COMMAND_IDS[
                                        'fake motor'],
                                    motor_value))
        motor_value += 1

        print parser.parse(communicator.read())


def test_verify():
    print("test verify...")

    motor_value = 0
    led_state = True

    # ---- test led 13 ----
    for _ in xrange(10):
        packet = communicator.makePacket(PACKET_TYPES['command'],
                                         ARDUINO_COMMAND_IDS['led 13'],
                                         int(led_state))
        communicator.write(packet)
        assert parser.verify(packet, communicator.read())

        led_state = not led_state
        time.sleep(1)

    # ---- test fake led ----

    for _ in xrange(20):
        packet = communicator.makePacket(PACKET_TYPES['command'],
                                         ARDUINO_COMMAND_IDS['fake led'],
                                         int(led_state))
        communicator.write(packet)
        assert parser.verify(packet, communicator.read())

        led_state = not led_state

    # ---- test fake 8-bit sensor ----

    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['fake sensor 8 bit'])
    communicator.write(packet)
    for _ in xrange(20):
        assert parser.verify(packet, communicator.read())

    # ---- test fake 16-bit sensor ----

    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['fake sensor 16 bit'])
    communicator.write(packet)

    for _ in xrange(20):
        assert parser.verify(packet, communicator.read())

    # ---- test fake motor ----

    for _ in xrange(255):
        packet = communicator.makePacket(PACKET_TYPES['command'],
                                         ARDUINO_COMMAND_IDS['fake motor'],
                                         motor_value)
        communicator.write(packet)

        motor_value += 1

        communicator.write(packet)
        assert parser.verify(packet, communicator.read())
    print("Passed!")


def test_imu():
    print("test imu...")
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['accel gyro'])
    communicator.write(packet)

    for _ in xrange(20):
        received = communicator.read()

        if len(received) > 0:
            print parser.parse(received,
                               markers=PARSE_MARKERS['accel gyro'],
                               out=PARSE_OUT_FORMATS['accel gyro'])
    print("Passed!")


def test_encoder():
    print("test encoder...")
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['encoder'])
    communicator.write(packet)

    for _ in xrange(100):
        received = communicator.read()

        if len(received) > 0:
            if parser.verify(packet, received):
                print(parser.parse(packet, out=PARSE_OUT_FORMATS['encoder']))


def test_gps():
    print("test gps...")
    packet = communicator.makePacket(PACKET_TYPES['request data'],
                                     ARDUINO_COMMAND_IDS['gps'])
    communicator.write(packet)

    received = communicator.read()
    if len(received) > 0:
        if parser.verify(packet, received):
            print parser.parse(received,
                               verbose=True,
                               markers=PARSE_MARKERS['gps'],
                               out=PARSE_OUT_FORMATS['gps'])


def test_led13():
    print("test led 13...")
    # led_state = True
    for _ in xrange(30):
        packet = communicator.makePacket(PACKET_TYPES['command'],
                                         ARDUINO_COMMAND_IDS['led 13'],
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
                                         ARDUINO_COMMAND_IDS['servo'],
                                         servo_value)
        communicator.write(packet)
        recv_packet = communicator.read()
        if parser.verify(packet, recv_packet):
            print(parser.parse(packet, out=PARSE_OUT_FORMATS['servo']))
        
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

    while True:
        # test_switching()
        # test_pinging()
        # test_verify()
        test_servo()
        test_encoder()
        # test_imu()
        test_led13()
        # for _ in xrange(100):
        #     test_gps()

        # print("All tests passed!!!")
        # print "lets go again!!!"
        # time.sleep(1)
