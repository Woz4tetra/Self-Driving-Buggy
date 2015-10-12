
#include "SerialPacket.h"
#include "defines.h"
#include <typeinfo>

SerialPacket Packet;

uint8_t sensorValue=1;
uint8_t commandValue=1;

#define MYCOMMAND1 1
#define MYCOMMAND2 1

#define MYDATA1 1
#define MYDATA2 1

void setup()
{
    Packet.begin(115200, 0);
}

void loop()
{
    if (Serial.available() > 0) {
        char inByte = Serial.read();

        if (inByte == '1') {
            Packet.sendDataByte(sensorValue);
        }

        if (inByte == '2') {
            Packet.sendDataByte(sensorValue * 2);
        }

        if (inByte == 'a') {
            Packet.sendCommand(commandValue);
        }

        if (inByte == 'b') {
            Packet.sendCommand(commandValue * 2);
        }
    }
}