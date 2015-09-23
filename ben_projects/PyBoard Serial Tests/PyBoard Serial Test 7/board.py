import pyb
from pyb import USB_VCP
import packetparser
import sys

serial_ref = USB_VCP()
blue = pyb.LED(4)

# packets = []

while True:
    packet = serial_ref.readline()

    if packet != None:
        result = packetparser.parse(packet.decode("utf-8")[:-2])
        if result != 0:
            command_type, node_id, command_id, payload = result

            # packets.append(result)

            if command_type == 1:
                if node_id == 0:
                    if command_id == 4:
                        if payload == 0:
                            blue.off()
                        else:
                            blue.on()
            if command_type == 0xff:
                sys.exit(1)

    # if packet == b'\t':
    #     print(packets)

    pyb.delay(1)