
#include "SerialPacket.h"
#include "defines.h"

SerialPacket Packet;

bool fake_led = false;
uint8_t fake_sensor_8bit = 0;
uint16_t fake_sensor_16bit = 0;
uint8_t fake_gps[8];

uint8_t command_id = 0;
uint8_t payload = 0;

void setup()
{
    Packet.begin(115200, 2);
    handshake();
}

void loop()
{
    delay(3);
}

/*
    SerialEvent occurs whenever a new data comes in the
    hardware serial RX.  This routine is run between each
    time loop() runs, so using delay inside loop can delay
    response.  Multiple bytes of data may be available.
*/

void serialEvent()
{
    int result = Packet.readSerialData();
    if (result == 1)
    {
        command_id = Packet.getCommandID();
        payload = Packet.getPayload();
        
        while (Serial.read() > 0) {  }
        Serial.flush();
    }
    else if (result == 2)
    {
        if (command_id == FAKE_LED)
        {
            fake_led = (bool)payload;
            Packet.sendCommandReply(command_id, (uint8_t)(fake_led));
        }
        if (command_id == FAKE_SENSOR_8BIT)
        {
            Packet.sendData8bit(command_id, fake_sensor_8bit);
            
            fake_sensor_8bit = (fake_sensor_8bit + 1) & 0xff;
        }
        if (command_id == FAKE_SENSOR_16BIT)
        {
            Packet.sendData16bit(command_id, fake_sensor_16bit);
            
            if (fake_sensor_16bit == 0) {
                fake_sensor_16bit = 1;
            }
            else {
                fake_sensor_16bit = (fake_sensor_16bit * 2) & 0xffff;
            }
        }
    }
//    Packet.readSerialData();
//    if (Packet.readSerialData())
//    {
//        command_id = Packet.getCommandID();
//        payload = Packet.getPayload();
//    }
//    Serial.print(", command_id:");
//    Serial.print(command_id);
//    
//    Serial.print(", payload:");
//    Serial.print(payload);
//    
//    Serial.print(", 8bit:");
//    Serial.print(fake_sensor_8bit);
//    
//    Serial.print(", 16bit:");
//    Serial.println(fake_sensor_16bit);
}

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}