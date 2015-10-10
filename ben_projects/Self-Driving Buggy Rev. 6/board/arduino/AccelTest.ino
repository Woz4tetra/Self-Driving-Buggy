
#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"

#include "SerialPacket.h"
#include "defines.h"

/* Command IDs */
#define ACCEL_GYRO 0x00
#define ENCODER 0x01
#define SERVO 0x02
#define GPS 0x03
#define LED13 0x04

/* IMU Globals */
MPU6050 accelgyro;
int pos;
//Servo servo1;
int16_t ax, ay, az;
int16_t gx, gy, gz;

uint8_t accel_array[12];


void setup()
{
    Wire.begin(); //I2C library
    accelgyro.initialize(); //IMU library
    
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
        if (command_id == LED_13)
        {
            digitalWrite(LED13_PIN, payload);
            Packet.sendCommandReply(command_id, payload);
        }
        else if (command_id == ACCEL_GYRO)
        {
            accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
            
            accel_array[0] = ax >> 8;
            accel_array[1] = ax & 0xffff;
            accel_array[2] = ay >> 8;
            accel_array[3] = ay & 0xffff;
            accel_array[4] = az >> 8;
            accel_array[5] = az & 0xffff;
            
            accel_array[6] = gx >> 8;
            accel_array[7] = gx & 0xffff;
            accel_array[8] = gy >> 8;
            accel_array[9] = gy & 0xffff;
            accel_array[10] = gz >> 8;
            accel_array[11] = gz & 0xffff;
            
            Packet.sendDataArray(accel_array, 12);
        }
    }
}

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}