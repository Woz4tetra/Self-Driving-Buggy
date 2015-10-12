
import pyb
from pyb import USB_VCP
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
    char = serial_ref.recv(1)
    byte_list = []
    
    while char != b'\x00':
        char = serial_ref.recv(1)

    while char != b'\x01':
        if b'0' <= char <= b'9':
            byte_list.append(int(char))
        char = serial_ref.recv(1)
#    print(byte_list)

    return byte_list

print("Starting...")

def handshake(serial_ref):
    char = serial_ref.recv(1)
    while char != b'R':
        char = serial_ref.recv(1)

    serial_ref.write('P')

serial_ref = USB_VCP()
led2 = pyb.LED(2)
handshake(serial_ref)

number = 0

while True:
    if serial_ref.any():
        number = read_number(read_buffer(serial_ref))
        time.sleep(0.001)
        write_buffer(serial_ref, make_list(number + 15))
        led2.toggle()
    else:
        led2.off()

#    if serial_ref.isconnected() == False:
#        serial_ref.close()
#    else:
#        serial_ref.open()

