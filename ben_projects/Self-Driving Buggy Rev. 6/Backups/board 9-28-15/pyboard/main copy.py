import pyb
from pyb import USB_VCP
import serial_parser

serial_ref = USB_VCP()
blue = pyb.LED(4)

parser = serial_parser.Parser()

while True:
    raw_packet = serial_ref.readline()

    if raw_packet != None:
        packet = parser.parse(raw_packet.decode("utf-8"))
        if packet != None:
            node_id, command_id, payload = packet

            # packets.append(result)

            if node_id == 0:
                if command_id == 4:
                    if payload == 0:
                        blue.off()
                    else:
                        blue.on()


    # if packet == b'\t':
    #     print(packets)

    pyb.delay(1)