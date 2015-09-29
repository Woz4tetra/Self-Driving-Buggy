import serial
import time


def write_data(data):
    byte_list = []
        
    while data > 0 or len(byte_list) == 0:
        byte_list.insert(0, chr(data & 0xFF))
        data /= 0x100
    byte_list.insert(0, chr(len(byte_list)))
    return byte_list

def read_number(byte_list):
    size = ord(byte_list.pop(0))
    data = 0

    while len(byte_list) > 0:
        length = len(byte_list) - 1
        datum = byte_list.pop(0)
        data += ord(datum) << 8 * length
    return data

print read_number(write_data(65534))

if __name__ == '__main__':
    ser = serial.Serial('/dev/cu.usbmodem1452', 9600, timeout=0.1)

    while True:
        data = ""
        char = ser.read()
        while char != '\n':
            data += char
            char = ser.read()
        print data
        time.sleep(0.1)
        ser.write('a')