import serial_comm
import serial_parser
from constants import *
import time

'''
if __debug__:
   if not expression: raise AssertionError

- or -

assert

__debug__ is true if -O is not passed
'''

def test_switching():
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

    print "lets go again!!!"

def test_pinging():
    motor_value = 0
    led_state = True
    
    for _ in xrange(10):
        communicator.write(communicator.makePacket(PACKET_TYPES['command'],
                                ARDUINO_COMMAND_IDS['led 13'],
                                int(led_state)))
        print parser.parse(communicator.read())

        led_state = not led_state
        time.sleep(1)

    for _ in xrange(20):
        communicator.write(communicator.makePacket(PACKET_TYPES['command'],
                                ARDUINO_COMMAND_IDS['fake led'],
                                int(led_state)))
        print parser.parse(communicator.read())

        led_state = not led_state
    
    communicator.write(communicator.makePacket(PACKET_TYPES['request data'],
                                ARDUINO_COMMAND_IDS['fake sensor 8 bit']))
    for _ in xrange(20):
        print parser.parse(communicator.read())
    
    communicator.write(communicator.makePacket(PACKET_TYPES['request data'],
                                ARDUINO_COMMAND_IDS['fake sensor 16 bit']))
    
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

if __name__ == '__main__':
    parser = serial_parser.Parser()
    communicator = serial_comm.Communicator()

    # ---- Request data from fake sensor 8 bit ----
    

    

    while True:
#        test_switching()
#        test_pinging()
        test_verify()

        print "lets go again!!!"
        time.sleep(1)
        
