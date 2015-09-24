#
# import pyboard
# import threading
# import serial
# import time
#
# address = "/dev/tty.usbmodem1452"
#
# class PyBoardThread(threading.Thread):
#     def run(self):
#         pyboard.execfile("board/main.py", device="/dev/tty.usbmodem1452")
#
# pyb_thread = PyBoardThread()
# pyb_thread.daemon = True
# pyb_thread.start()
#
# serial_ref = serial.Serial(port=address)
#
# led4on = packetmaker.create_packet(1, 0, 4, 1)
# led4off = packetmaker.create_packet(1, 0, 4, 0)
# pyb_exit = packetmaker.create_packet(0xff, 0, 0, 0)
# print(led4on)
#
# time.sleep(0.1)
#
# try:
#     while True:
#         serial_ref.write(led4on)
#         time.sleep(1)
#         serial_ref.write(led4off)
#         time.sleep(1)
# except KeyboardInterrupt:
#     serial_ref.write(pyb_exit)
# # serial_ref.write(packet)

import serial_comm
import serial_parser
import random
import time

communicator = serial_comm.Communicator()
parser = serial_parser.Parser()

communicator.start()

while True:
    packet = communicator.makePacket(random.randint(0, 7),
                                     random.randint(0, 255),
                                     random.randint(0, 255))
    print repr(packet)

    time.sleep(0.2)
    communicator.put(packet)
    print parser.parse(communicator.get())
    time.sleep(0.2)
