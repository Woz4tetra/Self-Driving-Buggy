
from pyb import UART

uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

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

while True:
    if uart.any():
