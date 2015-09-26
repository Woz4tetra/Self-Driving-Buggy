
#include "SerialPacket.h"
#include "defines.h"

SerialPacket Packet;

bool fake_led = false;
uint8_t fake_sensor_8bit = 0;
uint16_t fake_sensor_16bit = 0;
uint8_t fake_gps[8];

void setup()
{
    Packet.begin();
    handshake();
}

void loop()
{
    uint8_t command_id = Packet.getCommandID();
    uint8_t payload = Packet.getPayload();
    
    if (command_id == FAKE_LED)
    {
        fake_led = (bool)payload;
        Packet.sendCommandReply(command_id, (uint8_t)(fake_led));
    }
    else if (command_id == FAKE_SENSOR_8BIT) {
        Packet.sendData8bit(fake_sensor_8bit);
        
        fake_sensor_8bit = (fake_sensor_8bit + 1) % 256;
    }
//    else if (command_id == FAKE_SENSOR_16BIT) {
//        <#statements#>
//    }
//    else if (command_id == FAKE_GPS) {
//        <#statements#>
//    }
//    else {
//        <#statements#>
//    }
    delay(1);
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
//    char in_char = Serial.read();
//    String read_string = "";
//    while (in_char != '\n')
//    {
//        read_string += in_char;
//        in_char = Serial.read();
//    }
//    Serial.println(read_string);
}

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0)
    {
        delay(10);
    }
    
    Serial.flush();
    delay(10);
}