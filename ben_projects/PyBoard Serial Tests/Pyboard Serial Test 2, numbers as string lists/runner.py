import serial
import time


def make_list(data):
    byte_list = list(str(data))
    byte_list.insert(0, chr(0))
    byte_list.append(chr(1))
    return byte_list

def write_buffer(serial_ref, byte_list):
    for byte in byte_list:
        serial_ref.write(byte)

def read_number(byte_list):
    data = 0
    
    while len(byte_list) > 0:
        length = len(byte_list) - 1
        datum = byte_list.pop(0)
        data += int(datum) * 10 ** length
    return data

def read_buffer(serial_ref):
    char = serial_ref.read()
    byte_list = []
    
    while ord(char) != 0:
        char = serial_ref.read()
    
    char = serial_ref.read()
    while ord(char) != 1:
        byte_list.append(int(char))
        char = serial_ref.read()
    return byte_list

def handshake(serial_ref):
    char = serial_ref.read()
    while char != 'P':
        serial_ref.write('R')
        char = serial_ref.read()
        print char,

if __name__ == '__main__':
    ser = serial.Serial('/dev/cu.usbmodem1452', 9600, timeout=0.1)
    handshake(ser)
    
    number = 1
    while True:
        write_buffer(ser, make_list(number))
        if ser.inWaiting() > 0:
            time.sleep(0.001)
            number = read_number(read_buffer(ser))
            print "number:", number