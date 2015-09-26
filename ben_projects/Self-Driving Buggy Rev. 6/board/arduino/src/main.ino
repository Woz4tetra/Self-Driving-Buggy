
#include "SerialPacket.h"
#include "defines.h"

SerialPacket Packet;

void setup()
{
    Packet.begin();
}

void loop()
{
    
}

/*
    SerialEvent occurs whenever a new data comes in the
    hardware serial RX.  This routine is run between each
    time loop() runs, so using delay inside loop can delay
    response.  Multiple bytes of data may be available.
*/

void serialEvent()
{
    Packet.readSerialData();
}