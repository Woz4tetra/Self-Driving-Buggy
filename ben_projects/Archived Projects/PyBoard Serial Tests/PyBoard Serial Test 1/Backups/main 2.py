
from pyb import UART

uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

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
        print datum
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



while True:
    if uart.any():
        number = read_number(read_buffer(uart))
        number += 5
        write_buffer(make_list(number))