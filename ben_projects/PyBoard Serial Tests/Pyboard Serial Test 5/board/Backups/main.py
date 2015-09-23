
import pyb
from pyb import USB_VCP
import time

#import parser
#import packet_maker

serial_ref = USB_VCP()
led2 = pyb.LED(2)

output_file = open("output.txt", "w")

packet = 0

while True:
#     packet = serial_ref.readline()
#     packet = parser.parse(packet)
     output_file.write(str(packet))
     packet += 1
     time.sleep(0.001)

output_file.close()