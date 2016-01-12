
import pyb
from pyb import USB_VCP
import time

# ---- start pyboard, pc similarity ----

start_char = chr(0)
end_char = chr(1)
char_range = [2, 256] # [2, 256) (2...256 exclusive)

def to_digits(n, b):
    """Convert a positive number n to its digit representation in base b."""
    if n == 0:
        return [char_range[0]]
    digits = []

    if n < 0:
        digits.insert(0, "-")
        n = abs(n)

    while n > 0:
        digits.insert(0, chr(n % b + char_range[0]))
        n = n // b
    return digits

def make_instructions(data):
    byte_list = [start_char]
    byte_list += reversed(to_digits(data, char_range[1] - char_range[0]))
    byte_list.append(end_char)
    return byte_list

def unwrap_instructions(byte_list):
    data = 0
    for index in xrange(len(byte_list)):
        data += (ord(byte_list[index]) - char_range[0]) * (char_range[1] - char_range[0]) ** index
    return data

def write_instructions(serial_ref, byte_list):
    for byte in byte_list:
        serial_ref.write(byte)

# ---- end pyboard, pc similarity ----

def reversed(input_list):
    return input_list[::-1]

def read_instructions(serial_ref):
    char = serial_ref.read(1)
    while char != bytes(start_char):
        char = serial_ref.read(1)
    
    byte_list = []
    while char != bytes(end_char):
        char = serial_ref.read(1)
        byte_list.append(char)
    return byte_list

def handshake(serial_ref):
    char = serial_ref.read(1)
    while char != b'R':
        char = serial_ref.read(1)
        time.sleep(0.001)
    serial_ref.write('P')

def read_flag(serial_ref):
    char = serial_ref.read(1)
    if char != None and len(char) > 0:
        return char
    else:
        return ''

if __name__ == '__main__':
    print("Starting... 2")

    serial_ref = USB_VCP()
    led2 = pyb.LED(2)
    handshake(serial_ref)
    
    print("handshake complete")

    number = 0

    while True:
        flag = read_flag(serial_ref)
        if flag == b'a':
            number += 15
        if flag == b'p':
            write_instructions(serial_ref, make_instructions(number))
        time.sleep(0.001)

