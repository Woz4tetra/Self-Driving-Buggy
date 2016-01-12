from __future__ import print_function
import serial
import time

def handshake(serial_ref):
    char = serial_ref.read()
    while char != 'P':
        serial_ref.write('R')
        char = serial_ref.read()
        print(char, end='')

if __name__ == '__main__':
    serial_ref = serial.Serial('/dev/cu.usbmodem1412', 9600, timeout=0.001)
    handshake(serial_ref)
    
    print("\n\nhandshake complete")
    
    while True:
#        for _ in xrange(100):
        serial_ref.write('a')

#        serial_ref.write('t')        
#        char = serial_ref.read()
#        print("get char type: ", end="")
#        while char != '\n':
#            serial_ref.write('t')
#            print(char, end='')
#            char = serial_ref.read()
        
        serial_ref.write('p')
        char = serial_ref.read()
        if char != '':
            print(ord(char), end="")

        time.sleep(0.01)
